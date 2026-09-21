import json
import httpx
from pathlib import Path
import logging

AI_MODULE_BASE_URL = "http://127.0.0.1:8000"

class InterviewService:
    GATEWAY_URL = "http://127.0.0.1:8001"

    @staticmethod
    def _append_full_url(data: dict):
        if data and "reply_audio" in data and data["reply_audio"]:
            path = data["reply_audio"]
            if not path.startswith("http"):
                data["reply_audio"] = f"{AI_MODULE_BASE_URL}/{path}"
        return data

    @staticmethod
    async def call_ai_start(payload: dict):
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(f"{AI_MODULE_BASE_URL}/start", json=payload)
                result = response.json()
                if result.get("status") == "success":
                    result["sessionId"] = result.get("session_id")
                    audio_url = result.get("reply_audio_url")
                    if audio_url and not audio_url.startswith("http"):
                        result["reply_audio_url"] = f"{AI_MODULE_BASE_URL}/{audio_url.lstrip('/')}"
                return result
            except Exception as e:
                return {"status": "error", "message": str(e)}

    @staticmethod
    async def call_ai_chat(payload: dict):
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(f"{AI_MODULE_BASE_URL}/chat", json=payload)
                result = response.json()
                if result.get("status") == "success":
                    result["data"] = InterviewService._append_full_url(result.get("data", {}))
                return result
            except Exception as e:
                return {"status": "error", "message": f"AI服务文字接口异常: {str(e)}"}

    @staticmethod
    async def call_ai_chat_with_audio(session_id: str, audio_file_path: str = None, audio_file=None, image_file=None, user_text: str = ""):
        files = []
        if audio_file_path and Path(audio_file_path).exists():
            file_size = Path(audio_file_path).stat().st_size
            with open(audio_file_path, "rb") as f:
                audio_data = f.read()
            files.append(("audio_file", ("audio.wav", audio_data, "audio/wav")))
        elif audio_file:
            await audio_file.seek(0)
            audio_data = await audio_file.read()
            files.append(("audio_file", (audio_file.filename, audio_data, audio_file.content_type)))
        else:
            return {"status": "error", "message": "未提供音频文件"}

        if image_file:
            await image_file.seek(0)
            files.append(("image_files", (image_file.filename, await image_file.read(), image_file.content_type)))

        data = {"session_id": session_id}
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(f"{AI_MODULE_BASE_URL}/chat_with_audio", files=files, data=data)
                result = resp.json()
                if result.get("status") == "success":
                    audio_url = result.get("reply_audio_url")
                    if audio_url and not audio_url.startswith("http"):
                        result["reply_audio_url"] = f"{AI_MODULE_BASE_URL}/{audio_url.lstrip('/')}"
                return result
            except Exception as e:
                return {"status": "error", "message": str(e)}

# 🔴 注意看！名字改成了 endpoints.py 里调用的名字，参数也改成了接收字典！
    @staticmethod
    async def get_final_report_json(payload: dict):
        # 从字典里把真正的 session_id 抠出来
        session_id = payload.get("session_id") 
        
        # 必须把 timeout 调大，因为大模型生成图表需要时间
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                # 呼叫底层的 Python AI 引擎
                response = await client.post(f"{AI_MODULE_BASE_URL}/report", json={"session_id": session_id})
                result = response.json()
                
                if result.get("status") != "success":
                    return result

                # 完美解决 "暂无建议" 的单复数 Bug
                content_items = []
                for turn in result.get("interview_history") or []:
                    eval_data = turn.get("evaluation") or {}
                    content_items.append({
    "type": "content_item",
    "item": {
        "question": turn.get("question", ""),
        "userAnswer": turn.get("user_answer", ""),
        "analysis": eval_data.get("analysis", "系统暂未生成详细分析"),
        "feedback": eval_data.get("suggestion", eval_data.get("suggestions", "暂无建议")),
        
        # 🌟 核心修复：把分数和学习资源原封不动地发给前端！
        "score": eval_data.get("scores", {}).get("accuracy", 0),
        "job_id": result.get("job_id"),
        "learning_resource": turn.get("learning_resource", {})
    }

})
                report_markdown = result.get("report_markdown", "")
                extracted_score = 0.0

                if report_markdown:
                    import re
                    # 使用正则匹配形如 "Resume Fit 分数：90" 的文本
                    match = re.search(r'Resume Fit 分数[：:]\s*(\d+(\.\d+)?)', report_markdown)
                    if match:
                        extracted_score = float(match.group(1))

                # 2. 把雷达数据 dict 转成前端雷达图需要的格式
                radar_data = result.get("radar_data", {})
                dim_labels = [
                    ("resume_fit", "简历匹配"),
                    ("accuracy", "技术准确"),
                    ("depth", "知识深度"),
                    ("logic", "逻辑思维"),
                    ("communication", "沟通表达"),
                    ("non_verbal", "非语言"),
                ]
                radar_packet = {
                    "type": "radar",
                    "data": [{"label": label, "value": int(radar_data.get(key, 0))} for key, label in dim_labels]
                }

                # 3. 计算平均分
                scores_list = [d["value"] for d in radar_packet["data"] if d["value"] > 0]
                raw_avg = round(sum(scores_list) / len(scores_list)) if scores_list else 0

                # 4. 构建总览数据包
                history = result.get("interview_history") or []
                total_questions = len([t for t in history if t.get("question")])
                summary_packet = {
                    "type": "summary",
                    "totalQuestions": total_questions,
                    "averageScore": raw_avg,
                    "matchScore": extracted_score,
                }

                # 5. 推断难度（从历史记录中分析）
                difficulty = "Medium"
                if history:
                    hard_count = sum(1 for t in history if t.get("difficulty") == "hard")
                    total = len(history)
                    if hard_count > total * 0.5:
                        difficulty = "Hard"
                    elif hard_count == 0:
                        difficulty = "Easy"

                # 把底层生成的新数据，打包透传给前端
                final_response = {
                    "status": "success",
                    "job_id": result.get("job_id"),
                    "match_score": extracted_score,
                    "average_score": raw_avg,
                    "difficulty": difficulty,
                    "summary_packet": summary_packet,
                    "radar_packet": radar_packet,
                    "content_items": content_items,
                    "report_markdown": result.get("report_markdown", ""),
                    "voice_data": result.get("voice_data", []),
                    "video_data": result.get("video_data", []),
                    "tips_data": result.get("tips_data", [])
                }
                
                return final_response

            except httpx.TimeoutException:
                # 捕获超时异常，给前端说人话
                return {"status": "error", "message": "AI 正在深度分析您的全模态表现，耗时较长，请稍后刷新查看。"}
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                return {"status": "error", "message": f"报告组装异常: {str(e)}"}

    @staticmethod
    async def call_ai_generate_plan(payload: dict):
        # 记得把 timeout 设置长一点，因为大模型生成几百字需要时间
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                # 转发给 ai_module 的 /generate_plan 接口
                response = await client.post(f"{AI_MODULE_BASE_URL}/generate_plan", json=payload)
                return response.json()
            except Exception as e:
                return {"status": "error", "message": f"AI生成计划服务异常: {str(e)}"}