import json
import base64
import uuid
import asyncio # 👈 新增：异步并发核心库
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from cachetools import TTLCache
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from interviewer import AIInterviewer
from fastapi import File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
import os

from stt_aliyun import speech_to_text
from audio_analysis import prepare_for_interview
from tts_edge import text_to_speech

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [AI_Engine] %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Mock Interview Engine API", description="提供面试模拟、对话分析和报告生成的后端服务接口")

os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

sessions = TTLCache(maxsize=100, ttl=3600)

class StartRequest(BaseModel):
    target_role: str = Field(default="Java后端开发工程师", description="面试岗位短名称，用于题库检索")
    mode: Literal["exam", "coach"] = "coach"
    # 新增：接收前端传来的简历和真实JD
    resume_text: Optional[str] = Field(default="", description="候选人的真实简历文本")
    job_description: Optional[str] = Field(default="", description="真实岗位JD详细要求")

class B_SpeechMeta(BaseModel):
    speed: Literal["正常", "过快", "过慢"] = Field(..., description="语速状态")
    pause_count: int = Field(..., ge=0, description="停顿次数")

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="后端生成的全局唯一会话ID")
    user_text: str = Field(..., description="用户回答的文本")
    speech_meta: Optional[B_SpeechMeta] = Field(default=None, description="提取的语音特征")

class ReportRequest(BaseModel):
    session_id: str = Field(..., description="后端生成的全局唯一会话ID")


# ==========================================
# 核心业务接口
# ==========================================

@app.post("/start")
async def start_interview(req: StartRequest):
    session_id = str(uuid.uuid4())
    role_mapping = {
        "java": "Java后端开发工程师",
        "python": "Python后端开发工程师（AI方向）",
        "frontend": "Web前端工程师"
    }
    display_role = role_mapping.get(req.target_role.strip().lower(), req.target_role)
    ai_engine = AIInterviewer(
        target_role=display_role, 
        mode=req.mode,
        resume_text=req.resume_text,
        job_description=req.job_description 
    )
    sessions[session_id] = ai_engine
    
    first_question = await asyncio.to_thread(ai_engine.ask_next_main_question)
    logger.info(f"[{session_id}] 正在生成开场白语音: {first_question[:20]}...")
    
    try:
        reply_audio_path = await text_to_speech(first_question, session_id)
    except Exception as e:
        logger.error(f"[{session_id}] 开场白语音生成失败: {e}", exc_info=True)
        reply_audio_path = None
        
    return {
        "status": "success", 
        "session_id": session_id, 
        "message": f"已开启 {req.mode} 模式面试",
        "reply_text": first_question, 
        "reply_audio_url": f"/{reply_audio_path}".replace("\\", "/") if reply_audio_path else None,
        "next_action": "作答",
        "question_number": ai_engine.asked_main_questions_count,
        "total_questions": len(ai_engine.question_pool),
        "is_finished": False,
    }


@app.post("/chat")
async def chat_with_ai(req: ChatRequest):
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在或已过期，请重新开始")   
    ai_engine = sessions[req.session_id]
    
    try:
        logger.info(f"[{req.session_id}] 收到纯文本回复，正在进行多模态RAG分析...")
        # 兼容处理 speech_meta
        speech_meta_data = req.speech_meta.model_dump() if req.speech_meta else {}
        
        result = await asyncio.to_thread(
            ai_engine.process_turn,
            user_text=req.user_text, 
            speech_meta=speech_meta_data
        )
        # ==========================================
        # 🔴 关键：给纯文本回复也加上语音合成 (TTS)
        # ==========================================
        ai_reply_text = result.get("reply_to_user", "")
        logger.info(f"[{req.session_id}] AI 思考完毕，正在生成 Edge-TTS 语音...")
        
        try:
            # 尝试生成语音
            reply_audio_path = await text_to_speech(ai_reply_text, req.session_id)
            
            # 成功后拼接 URL
            audio_url = f"/{reply_audio_path}".replace("\\", "/") if reply_audio_path else None
            
        except Exception as e:
            # 兜底：如果语音生成失败，直接降级，不抛出500错误
            logger.error(f"[{req.session_id}] ⚠️ 语音合成失败，已自动降级为纯文本模式: {e}")
            reply_audio_path = ""
            audio_url = None
            
        # 把生成的音频链接塞进 result 里
        result["reply_audio_url"] = audio_url
        result["question_number"] = ai_engine.asked_main_questions_count
        result["total_questions"] = len(ai_engine.question_pool)
        result["is_finished"] = bool(
            ai_engine.is_interview_finished or result.get("next_action") == "结束"
        )
        # ==========================================

        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"[{req.session_id}] 对话处理崩溃: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="对话引擎分析异常")

@app.post("/report")
async def generate_report(req: ReportRequest):
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在或已过期")
    
    ai_engine = sessions[req.session_id]   
    try:
        if not ai_engine.history:
            return {
                "status": "warning", 
                "message": "暂无面试数据，无法生成报告",
                "report_markdown": "您尚未进行任何实质性面试问答。",
                "radar_data": None,
                "interview_history": []
            }

        logger.info(f"[{req.session_id}] 面试结束，正在生成评估报告...")
        report_markdown = await asyncio.to_thread(ai_engine.generate_final_report)
        
        radar_scores = {
            "resume_fit": 0, "accuracy": 0, "depth": 0, "logic": 0, 
            "communication": 0, "non_verbal": 0 
        }
        valid_turns = 0
        for turn in ai_engine.history:
            if "evaluation" in turn and "scores" in turn["evaluation"]:
                s = turn["evaluation"]["scores"]
                radar_scores["resume_fit"] += s.get("resume_fit", 0) 
                radar_scores["accuracy"] += s.get("accuracy", 0)
                radar_scores["depth"] += s.get("depth", 0)
                radar_scores["logic"] += s.get("logic", 0)
                radar_scores["communication"] += s.get("communication", 0)
                radar_scores["non_verbal"] += s.get("non_verbal", 0)
                valid_turns += 1
                
        if valid_turns > 0:
            for key in radar_scores:
                radar_scores[key] = int(radar_scores[key] / valid_turns)
                
        history_data = ai_engine.history
        
        #生成完报告后，立刻把表现极佳的面经存入反思记忆库
        await asyncio.to_thread(ai_engine.save_reflection_memory)
        
        del sessions[req.session_id]
        logger.info(f"[{req.session_id}] 报告生成完毕，系统资源已安全回收。平均得分: {radar_scores}")
        return {
            "status": "success", 
            "report_markdown": report_markdown, 
            "radar_data": radar_scores,          
            "interview_history": history_data
        }
    except Exception as e:
        logger.error(f"[{req.session_id}] 报告生成崩溃: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="报告生成异常")

@app.post("/chat_with_audio", summary="核心：处理语音流与实时截图，多模态时序流水线版")
async def chat_with_audio(
    session_id: str = Form(..., description="后端生成的全局唯一会话ID"), 
    audio_file: UploadFile = File(..., description="用户回答的录音文件(.wav等)"),
    image_files: Optional[List[UploadFile]] = File(default=None, description="前端传来的实时截图文件(.jpg/.png)")
):
    if session_id not in sessions:
        logger.warning(f"检测到非法或已过期的语音会话请求: {session_id}")
        raise HTTPException(status_code=404, detail="会话不存在或已过期，请重新 /start")
        
    req_uuid = uuid.uuid4().hex
    user_audio_path = f"temp_{session_id}_{req_uuid}.wav"
    
    try:
        # 1. 保存录音
        with open(user_audio_path, "wb") as f:
            f.write(await audio_file.read())
        # 高并发感知层 (STT + 视觉)
        # 高并发感知层 (STT + 视觉)
        async def task_stt():
            try:
                # 真正调用底层语音模型的地方
                result = await asyncio.to_thread(speech_to_text, user_audio_path)
                
                # 🚨🚨 核心修改 1：不管成功还是失败，把底层原始吐出来的东西强行打印出来！
                logger.info(f"🚨🚨🚨 STT 模型底层真实返回内容: [{result}] 🚨🚨🚨")
                
                # 如果模型输出是空字符串（被 VAD 过滤了），手动抛出明确的错误
                if not result or str(result).strip() == "":
                    return "识别失败: 模型输出为空字符串(可能是时长太短或被判定为噪音)"
                    
                return result
            except Exception as e:
                # 🚨🚨 核心修改 2：如果底层代码抛出异常（比如 API 欠费、格式不兼容），把堆栈炸出来！
                logger.error(f"🚨🚨🚨 STT 底层代码抛出异常: {str(e)} 🚨🚨🚨", exc_info=True)
                return f"识别失败: 内部报错 {str(e)}"
            
        async def task_images():
            images_list = []
            if image_files is not None:
                for img in image_files:
                    if img.filename:
                        img_bytes = await img.read()
                        base64_str = base64.b64encode(img_bytes).decode("utf-8")
                        images_list.append(base64_str)
            return images_list

        logger.info(f"[{session_id}] 正在并发提取：语音文本 与 视觉图像...")
        stt_result, images_list = await asyncio.gather(
            task_stt(), 
            task_images()
        )      
        if "识别失败" in stt_result:
            logger.error(f"[{session_id}] ❌ 语音流水线被迫中断，原因: {stt_result}")
            return {"status": "error", "message": stt_result}
            
        user_text = stt_result
        logger.info(f"[{session_id}] STT识别完毕: {user_text[:15]}...")

        logger.info(f"[{session_id}] 文本已就绪，正在呼叫本地 V3 多模态大脑进行特征融合...")
        speech_meta = await asyncio.to_thread(prepare_for_interview, user_audio_path, user_text)
        
        logger.info(f"[{session_id}] V3 大脑提取完毕！情绪: {speech_meta.get('emotion')}，卡顿: {speech_meta.get('pause_count')}次")
        # 云端业务判决 (ZhipuAI + 数学干预)
        ai_engine = sessions[session_id]
        logger.info(f"[{session_id}] 正在进行面试官核心逻辑与跨模态打分...")
        brain_result = await asyncio.to_thread(
            ai_engine.process_turn,
            user_text=user_text, 
            speech_meta=speech_meta,
            image_base64_list=images_list
        )
        ai_reply_text = brain_result["reply_to_user"]
        # TTS 语音生成       
        logger.info(f"[{session_id}] AI 思考完毕，正在生成 Edge-TTS 语音...")
        try:
            reply_audio_path = await text_to_speech(ai_reply_text, session_id)
        except Exception as e:
            logger.error(f"[{session_id}] 语音生成失败，将降级为纯文本返回: {e}", exc_info=True)
            reply_audio_path = None
            
        return {
            "status": "success",
            "user_text": user_text,           
            "scores": brain_result.get("scores", {}), 
            "thought_process": brain_result.get("thought_process", ""),
            "think_aloud": brain_result.get("think_aloud", {}),
            "suggestion": brain_result.get("suggestion", ""),
            "analysis": brain_result.get("analysis", {}),
            "reply_text": ai_reply_text,      
            "reply_audio_url": f"/{reply_audio_path}".replace("\\", "/") if reply_audio_path else None,
            "next_action": brain_result.get("next_action", "追问"),
            "question_number": ai_engine.asked_main_questions_count,
            "total_questions": len(ai_engine.question_pool),
            "is_finished": bool(
                ai_engine.is_interview_finished or brain_result.get("next_action") == "结束"
            ),
            "multimodal_features": {
                # 模型算出的宏观和微观情绪轨迹(如："总体平静 ➔ 害怕 ➔ 平静")
                "emotion_trajectory": speech_meta.get("emotion", "暂无"),
                # 模型算出的连续概率字典 
                "emotion_probs": speech_meta.get("emotion_probs", {}),
                "is_cmci_triggered": "CMCI" in brain_result.get("thought_process", "")
            }
        }

    except Exception as e:
        logger.error(f"[{session_id}] 核心链路处理崩溃: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="对话引擎分析异常")
        
    finally:
        if os.path.exists(user_audio_path):
            os.remove(user_audio_path)
            logger.info(f"[{session_id}] 临时录音文件已安全销毁: {user_audio_path}")


import os
import uvicorn
import json
import httpx
## ==========================================
# 🔴 升级版：AI 定制 7 天练习计划接口 (深度结合 Markdown 报告)
# ==========================================
class PlanRequest(BaseModel):
    weak_dimension: str = Field(..., description="前端算出来的用户短板维度")
    report_markdown: str = Field(default="", description="最新一次面试的完整诊断报告Markdown")

def _get_fallback_plan(weak_dimension: str):
    # 你的兜底函数写在这里，直接返回默认字典即可
    return {"status": "error", "message": "生成失败，触发兜底"}

# ⚠️ 注意：这里的路径是 /generate_plan，供后端 8001 内部调用
@app.post("/generate_plan", tags=["AI 计划"], summary="根据报告和短板生成7天专属计划")
async def generate_practice_plan(req: PlanRequest):
    weak_dimension = req.weak_dimension
    report_markdown = req.report_markdown
    
    logging.info(f"[{weak_dimension}] 收到生成计划请求，正在结合详尽报告定制药方...")
    

    # 🔴 核心质变：在 Prompt 里强行塞入用户的真实诊断报告！让 AI 照方抓药！
    system_prompt = f"""
    你是一个资深的阿里 P9 面试官和技术导师。
    现在有一位候选人刚完成模拟面试，他的核心短板/总体诊断是：【{weak_dimension}】。
    
    下面是他最新一次面试的【详细诊断报告】。请你务必认真阅读报告中的“定制化通关攻略与评估建议 (Action Items)”部分：
    
    ----------------------
    {report_markdown}
    ----------------------
    
    请你严格基于上面这份诊断报告里的具体建议（例如它提到的具体技术点、STAR法则、3秒停顿法等），为候选人定制一份可落地的 7 天突击练习计划，以及 2-3 条个性化提升建议。
    每天的任务必须具体，并且与报告中的 Action Items 强相关！
    
    ⚠️【严格限制】：
    你必须且只能输出一个合法的 JSON 字符串，不要包含任何额外的问候语、Markdown 标记（如 ```json）或解释说明。
    JSON 的数据结构必须严格如下：
    {{
        "suggestions": [
            {{ "title": "建议的小标题", "description": "建议的详细描述内容" }}
        ],
        "planData": [
            {{ "day": 1, "title": "第1天任务标题", "desc": "第1天任务详细描述(结合报告)" }},
            {{ "day": 2, "title": "第2天任务标题", "desc": "第2天任务详细描述(结合报告)" }},
            {{ "day": 3, "title": "第3天任务标题", "desc": "第3天任务详细描述(结合报告)" }},
            {{ "day": 4, "title": "第4天任务标题", "desc": "第4天任务详细描述(结合报告)" }},
            {{ "day": 5, "title": "第5天任务标题", "desc": "第5天任务详细描述(结合报告)" }},
            {{ "day": 6, "title": "第6天任务标题", "desc": "第6天任务详细描述(结合报告)" }},
            {{ "day": 7, "title": "第7天任务标题", "desc": "第7天任务详细描述(结合报告)" }}
        ]
    }}
    """

    try:
        api_key = os.environ.get("ZHIPUAI_API_KEY", "") 
        if not api_key:
            logging.warning("未检测到 ZHIPUAI_API_KEY，将使用本地兜底降级方案。")
            raise ValueError("Missing API Key")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "glm-4",
            "messages": [{"role": "user", "content": system_prompt}],
            "temperature": 0.7
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "[https://open.bigmodel.cn/api/paas/v4/chat/completions](https://open.bigmodel.cn/api/paas/v4/chat/completions)", 
                headers=headers, 
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
        llm_text = result['choices'][0]['message']['content'].strip()
        
        # 清理大模型可能手贱加上的 Markdown 符号
        if llm_text.startswith("```json"): 
            llm_text = llm_text[7:]
        elif llm_text.startswith("```"): 
            llm_text = llm_text[3:]
            
        if llm_text.endswith("```"): 
            llm_text = llm_text[:-3]
            
        llm_text = llm_text.strip()
        
        # 解析为真实 JSON
        plan_json = json.loads(llm_text)
        logger.info(f"[{req.weak_dimension}] AI 专属计划生成成功！")
        
        return {
            "status": "success",
            "data": plan_json
        }

    except json.JSONDecodeError as je:
        logger.error(f"大模型返回的数据不是合法的 JSON: {je}. 原始文本: {llm_text}")
        return _get_fallback_plan(weak_dimension)
    except Exception as e:
        logger.error(f"AI 生成计划失败，已触发本地安全兜底: {e}")
        return _get_fallback_plan(weak_dimension)


# ==========================================
# 核心启动区块
# ==========================================
if __name__ == "__main__":
    import uvicorn
    # AI 模块应该跑在 8000 端口
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
