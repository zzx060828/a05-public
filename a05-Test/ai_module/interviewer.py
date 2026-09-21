import json
from zhipuai import ZhipuAI
import random
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field, ValidationError
import random
import chromadb
import json
import os
import sys
import re
import numpy as np
#分数限制
class InterviewScores(BaseModel):
    resume_fit: int = Field(..., ge=0, le=100, description="简历与岗位的基础契合度")
    accuracy: int = Field(..., ge=0, le=100)
    depth: int = Field(..., ge=0, le=100)
    logic: int = Field(..., ge=0, le=100)
    communication: int = Field(..., ge=0, le=100)
    non_verbal: int = Field(..., ge=0, le=100, description="非语言表达：微表情、动作与情绪控制")
class ThinkAloudFeedback(BaseModel):
    understanding: str = Field(..., description="需求澄清：是否主动确认边界条件或业务场景")
    ideation_and_justification: str = Field(..., description="初步构思与方案论证：是否展现了思路发散及技术选型对比")
    execution: str = Field(..., description="逻辑推演：表达解决步骤是否条理清晰（如使用首先、其次）")
    edge_cases: str = Field(..., description="边界与异常处理：是否主动考虑了极端情况（如宕机、高并发）")
    evaluation: str = Field(..., description="综合权衡：是否有对自身方案优缺点的客观评估")
#分析限制
class Analysis(BaseModel):
    highlight: str
    weakness: str
#面试结果限制
class InterviewTurnResult(BaseModel):
    thought_process: str = Field(..., description="大模型打分前的内部推理过程")
    scores: InterviewScores
    analysis: Analysis
    think_aloud: ThinkAloudFeedback
    suggestion: str
    reply_to_user: str
    next_action: Literal["追问", "换题",  "提示重试"] 

class AIInterviewer:
    def __init__(self, target_role: str = "Java后端开发工程师", max_questions: int = 7,mode: str = "coach",resume_text: str = "",job_description: str = ""):
        self.target_role = target_role
        self.max_questions = max_questions
        self.mode = mode
        self.resume_text = resume_text
        self.job_description = job_description
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if not api_key:
            raise RuntimeError("缺少环境变量 ZHIPUAI_API_KEY，请参考 .env.example 配置")
        self.client = ZhipuAI(api_key=api_key)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path=os.path.join(current_dir, "my_vector_db")
        self.chroma_client = chromadb.PersistentClient(path=db_path)      
        self.collection = self.chroma_client.get_or_create_collection(name="interview_questions")
        self.memory_collection = self.chroma_client.get_or_create_collection(name="reflection_memory")
        self.behavior_collection = self.chroma_client.get_or_create_collection(name="behavior_questions")
        self.resource_collection = self.chroma_client.get_or_create_collection(name="learning_resources")
        self.reflection_examples = self._retrieve_reflection_memory()
        # 记住当前面到哪了
        self.history: List[Dict] =[]
        self.asked_main_questions_count = 0
        self.current_question = ""
        self.current_standard_ans = ""
        self.current_question_type = "knowledge"
        self.current_expected_points = []
        self.current_scoring_points = []
        self.current_expression_hint = ""
        self.current_multimodal_hint = ""
        self.current_follow_up_triggers = {}
        self.is_interview_finished = False
        #初始化题库
        self.question_pool = self._load_questions_from_db(self.target_role)
        self.deep_dive_count = 0
        self.current_difficulty = "medium"
        self.current_topic_history = []
    def get_embedding(self, text):
        response = self.client.embeddings.create(model="embedding-2",input=text)
        return response.data[0].embedding
    #结合大模型重排进行精准知识检索
    def search_knowledge_base(self, text: str) -> str:
        try:
            vec = self.get_embedding(text)
            results = self.collection.query(
                query_embeddings=[vec],
                n_results=4,
                include=["documents", "metadatas","distances"]
            )
            if results["distances"] and results["distances"][0][0] > 0.8:
                return "无额外参考资料，请根据通用技术标准判断"
            if not results["documents"] or len(results["documents"][0]) == 0:
                return "无额外参考资料，请根据通用技术标准判断"
            candidates = []
            for i in range(len(results["documents"][0])):
                if results['distances'][0][i] <= 0.8:
                    metadata = results['metadatas'][0][i]
                    #测试数据的问题用，正式时需删除
                    if 'question'  not in metadata:
                        print(f"脏数据,入库的数据缺失 'question' 字段！")
                        print(f"[异常数据片段]：{results['documents'][0][i][:30]}...")
                        q='未知问题'
                    else:
                        q = metadata['question']
                    raw_answer= results['documents'][0][i]
                    if not raw_answer or not raw_answer.strip():
                        print(f"脏数据,入库的数据缺失答案内容！")
                        print(f"[异常数据片段]：{results['documents'][0][i][:30]}...")
                        a='无标准答案，请根据通用技术标准判断'
                    else:
                        a=raw_answer.strip()
                    candidates.append({"question": q, "answer": a})                    
            if len(candidates)==1:
                print("找到一个相关问题，直接返回答案")  #后面记得删
                return f"【相关考点】{candidates[0]['question']}\n【参考知识】{candidates[0]['answer']}"
            rerank_prompt = f"""
                你是一个精准的知识匹配助手。候选人刚刚回答了以下内容：
                "{text}"

                我在知识库中找到了 {len(candidates)} 个可能相关的【标准问题及答案】。
                请帮我判断，哪一个知识点与候选人正在回答的内容最匹配？

                候选列表：\n
                """
            for idx, item in enumerate(candidates):
                rerank_prompt += f"{idx+1}. 问题：{item['question']}，答案：{item['answer']}\n"
            rerank_prompt += "请仔细对比，一定只能输出最匹配的序号数字（如 1 或 2），绝对不要输出任何标点符号、解释或其他文字"
            response = self.client.chat.completions.create(
                model='glm-4-air',
                messages=[{"role": "user", "content": rerank_prompt}],
                temperature=0.1)
            choice = response.choices[0].message.content.strip()
            best_match = candidates[int(choice)-1]
            return f"【相关考点】{best_match['question']}\n【参考知识】{best_match['answer']}"
        except Exception as e:
            if 'candidates' in locals() and len(candidates) > 0:
                return candidates[0]['question'], candidates[0]['answer']
            return "通用技术问题", "无标准答案，请根据通用技术标准判断"
    def _load_questions_from_db(self, role: str) -> List[Dict]:
        project_q = f"你好！欢迎参加今天的面试。"
        if self.resume_text:
            project_q += "我刚看了一下你的简历，发现你的经历很丰富。能重点挑一个简历里你最核心参与的项目，和我详细聊聊你的技术贡献吗？"
        else:
            project_q += "首先请做一个简单的自我介绍，并重点聊聊你最自豪的一个项目经历。"
            
        base_questions =[
            {
                "q": project_q,
                "a": "无标准技术答案。重点在于简历内容的真实性核验。",
                "type": "project",
                "expected_points": ["清晰的自我介绍", "使用STAR法则描述简历中的项目", "突出个人贡献"],
                "scoring_points": [], "expression_hint": "观察候选人谈论自己项目时是否自信流畅。", "multimodal_hint": "", "follow_up_triggers": {}
            }
        ]   
        try:
            vec = self.get_embedding(f"{role}岗位核心底层原理、高并发业务场景设计技术题")
            results = self.collection.query(
                query_embeddings=[vec],
                n_results=30, 
                where={"role": {"$in": [role, "General", "通用"]}}, 
                include=["documents", "metadatas"]
            )
            pools = {"knowledge": [], "scenario": [], "behavior": []}           
            if results["documents"] and len(results["documents"][0]) > 0:
                for i in range(len(results["documents"][0])):
                    metadata = results['metadatas'][0][i] or {}
                    q = metadata.get('question', '请谈谈你对该岗位核心技术的理解。')
                    raw_answer = results['documents'][0][i]
                    a = raw_answer.strip() if raw_answer and raw_answer.strip() else "暂无参考。"          
                    q_type = metadata.get('question_type', 'knowledge') # 默认知识题                    
                    import json
                    try:
                        exp_points = json.loads(metadata.get('expected_answer_points', '[]'))
                        score_points = json.loads(metadata.get('scoring_points', '[]'))
                        triggers = json.loads(metadata.get('follow_up_triggers', '{}'))
                    except:
                        exp_points, score_points, triggers = [], [], {}                     
                    item = {
                        "q": q, 
                        "a": a,
                        "type": q_type, 
                        "expected_points": exp_points,
                        "scoring_points": score_points,
                        "expression_hint": metadata.get('expression_analysis_hint', ''),
                        "multimodal_hint": metadata.get('multimodal_hint', ''),
                        "follow_up_triggers": triggers
                    }          

                    if q_type in pools:
                        pools[q_type].append(item)
                    else:
                        pools["knowledge"].append(item)

            try:
                b_vec = self.get_embedding(f"考察候选人的团队协作、抗压能力、沟通冲突解决等行为面试题")
                b_results = self.behavior_collection.query(
                    query_embeddings=[b_vec],
                    n_results=10, # 找10道备选
                    include=["documents", "metadatas"]
                )
                if b_results["documents"] and len(b_results["documents"][0]) > 0:
                    for i in range(len(b_results["documents"][0])):
                        metadata = b_results['metadatas'][0][i] or {}
                        q = metadata.get('question', '能分享一次你遇到挫折的经历吗？')
                        raw_answer = b_results['documents'][0][i]
                        a = raw_answer.strip() if raw_answer and raw_answer.strip() else "重点考察 STAR 法则。"          
                        q_type = "behavior" 
                        try:
                            exp_points = json.loads(metadata.get('expected_answer_points', '[]'))
                            score_points = json.loads(metadata.get('scoring_points', '[]'))
                            triggers = json.loads(metadata.get('follow_up_triggers', '{}'))
                        except:
                            exp_points, score_points, triggers = [], [], {}                     
                        
                        b_item = {
                            "q": q, 
                            "a": a,
                            "type": q_type, 
                            "expected_points": exp_points,
                            "scoring_points": score_points,
                            "expression_hint": metadata.get('expression_analysis_hint', ''),
                            "multimodal_hint": metadata.get('multimodal_hint', ''),
                            "follow_up_triggers": triggers
                        }          
                        pools["behavior"].append(b_item)
            except Exception as b_e:
                print(f"从专用行为题库检索失败，将仅使用主库中的兜底题: {b_e}")
            target_counts = {
                "knowledge": 3,  
                "scenario": 2,   
                "behavior": 1    
            }

            for t_type, target_num in target_counts.items():
                available_pool = pools[t_type]
                draw_num = min(target_num, len(available_pool)) 
                if draw_num > 0:
                    drawn_items = random.sample(available_pool, draw_num)
                    base_questions.extend(drawn_items)
                    for item in drawn_items:
                        pools[t_type].remove(item)
            tech_questions = base_questions[1:] 
            pure_tech = [q for q in tech_questions if q["type"] != "behavior"]
            behavior_q = [q for q in tech_questions if q["type"] == "behavior"]          
            random.shuffle(pure_tech)         
            final_questions = [base_questions[0]] + pure_tech + behavior_q
            remaining_questions = pools["knowledge"] + pools["scenario"]
            random.shuffle(remaining_questions)
            while len(final_questions) < self.max_questions and remaining_questions:
                final_questions.insert(-1, remaining_questions.pop()) # 插入到倒数第二个位置，保证行为题永远垫底         
            

            final_q_list = final_questions[:self.max_questions]
            type_counts = {"project": 0, "knowledge": 0, "scenario": 0, "behavior": 0}
            
            for q in final_q_list:
                q_type = q.get("type", "knowledge") # 默认算知识题
                if q_type in type_counts:
                    type_counts[q_type] += 1
                else:
                    type_counts[q_type] = 1
                    
            print("\n" + "="*50)
            print(f"[题库加载成功] 面试官({self.target_role})已准备就绪！")
            print(f"[本场题目总数] {len(final_q_list)} 题")
            print(f"[题目分布详情] 项目核验: {type_counts['project']}题 | 基础知识: {type_counts['knowledge']}题 | 场景设计: {type_counts['scenario']}题 | 软素质/行为: {type_counts['behavior']}题")
            print("="*50 + "\n")           
            return final_q_list
            
        except Exception as e:
            import traceback
            print(f"RAG题库智能加载失败: {e}\n{traceback.format_exc()}")
            base_questions.append({"q": "你觉得你在团队协作中最大的优势是什么？", "a": "考察团队沟通和自我认知。", "type": "behavior"})
            return base_questions
    def ask_next_main_question(self) -> str:
        if self.asked_main_questions_count >= len(self.question_pool):
            self.is_interview_finished = True
            return "今天的面试非常愉快，感谢你的参与。请等待系统生成评估报告。"
        q_data = self.question_pool[self.asked_main_questions_count]
        self.current_question = q_data["q"]
        self.current_standard_ans = q_data["a"]
        self.current_question_type = q_data.get("type", "knowledge")
        self.current_expected_points = q_data.get("expected_points", [])
        self.current_scoring_points = q_data.get("scoring_points", [])
        self.current_expression_hint = q_data.get("expression_hint", "")
        self.current_multimodal_hint = q_data.get("multimodal_hint", "")
        self.current_follow_up_triggers = q_data.get("follow_up_triggers", {})
        self.asked_main_questions_count+=1
        return self.current_question
    def _build_evaluation_prompt(self, speech_features: str, retrieved_knowledge: str,vision_feedback: str) -> str:
        base_role = "你是一位拥有 15 年经验的阿里 P9 级技术专家。你的目标是对候选人进行全方位的“画像评估”，不仅仅是判断对错，更要结合底层的多模态情绪雷达数据，挖掘他的技术上限与心理素质。"
        
        if self.mode == "exam":
            style_setting = "【全真压测模式】：你的风格极其专业、中立、不苟言笑。你极其看重面试效率和底层逻辑深度，【绝对禁止】任何废话寒暄、表扬，但也【绝对不要】嘲讽或贬低候选人。如果回答不出，直接冷淡地切入下一个技术细节。"
        else:
            style_setting = "【教学辅导模式】：你的风格专业、犀利，但在指出错误时充满亲和力与导师风范。每次提问前，你会先用一两句话温柔地点拨候选人的盲区，肯定他的正确思路，然后再循循善诱地引出下一个深度问题。"
            
        difficulty_rules = {
            "easy": "【Easy难度】：侧重考察【知识记忆(Knowledge Memorization)】。追问请直接提取基础概念，考察他是否背熟了基本定义，不要问太深。",
            "medium": "【Medium难度】：侧重考察【知识理解(Knowledge Comprehension)】。追问请让他剖析核心概念的区别与实际应用场景，避免停留在表面背诵。",
            "hard": "【Hard难度】：侧重考察【深度分析】。追问请给出复杂的业务场景或底层运行机制，让他进行深度的逻辑推理。【注意：由于系统无代码白板，严禁要求候选人口述具体代码实现或配置参数】"
        }
        current_diff_prompt = difficulty_rules.get(self.current_difficulty, difficulty_rules["medium"])
        
        type_rubrics = {
            "knowledge": "【评估核心：技术精准度与推演】不仅看答案对错，更要看候选人是否展现了思考过程（Think-Aloud），比如是否主动对比了不同技术的优劣。",
            "scenario": "【评估核心：系统设计与权衡】强烈考察候选人的思考口语化（Think-Aloud）能力！重点评估：是否先澄清需求？是否论证了方案？是否考虑了边界异常情况？",
            "project": "【评估核心：真实性与底层技术深度】：必须将回答与【候选人真实简历】进行比对！深挖其简历中提到的核心代码和真实报错。考察其对过往项目的综合评估能力。",
            "behavior": "【评估核心：软技能与STAR法则】严格按照情境、任务、行动、结果来评估其沟通、抗压和团队协作能力。"
        }
        current_type_prompt = type_rubrics.get(self.current_question_type, type_rubrics["knowledge"])
        
        exp_points_str = "\n".join([f"- {p}" for p in self.current_expected_points]) if self.current_expected_points else "无特定采分点，综合评估。"
        score_points_str = json.dumps(self.current_scoring_points, ensure_ascii=False) if self.current_scoring_points else "按常规技术标准打分。"
        memory_prompt = f"\n- **【反思记忆经验 (Reflection Memory)】**：\n{self.reflection_examples}\n(注：这是你过去面试其他高分候选人的真实记录。如果触发追问，请务必模仿这段记录中的深挖切入点！)" if getattr(self, "reflection_examples", "") else ""
        
        prompt= f"""
        ### 1. Role (角色设定)
        {base_role}
        {style_setting}
        
        ### 2. Context (当前考核上下文)
        - **【面试目标岗位与JD要求】**：\n{self.job_description if getattr(self, 'job_description', '') else self.target_role}\n(请以此真实业界招聘要求作为简历匹配度的绝对基准！)
        - **【候选人真实简历】**：\n{self.resume_text if self.resume_text else "未提供简历，请基于常识判断"}\n
        - **当前重点考察问题**：{self.current_question}
        - **当前追问难度要求**：{current_diff_prompt}
        - **当前追问轮数**：已经在此问题上追问了 {self.deep_dive_count} 次
        - **基础标准答案**：{self.current_standard_ans}
        - **【核心采分点 (极重要)】**：候选人回答若命中以下要点，应给予高分：
          {exp_points_str}
        - **【专项评分量表】**：参考以下梯队进行 Accuracy 打分：
          {score_points_str}
        - **RAG 知识库查证**：{retrieved_knowledge}{memory_prompt}
        
        ### 3. 多模态表现数据 (用于 communication 和 non_verbal 评分)
        - **候选人语音特征**：{speech_features}
        - **候选人视觉表现**：{vision_feedback}
        - **【专属表现评估提示】**：{self.current_expression_hint} {self.current_multimodal_hint}

        ### 4. Task (核心任务)
        请根据上下文对话历史以及候选人最新的回答，结合其语音表现和仪态微表情，输出一份严格的 JSON 评估报告。
        请严格遵循 MockLLM 双阶段评估法：
        1. **第一阶段 (Basic Score)**：仅关注候选人的【真实简历】内容是否匹配岗位要求，给出一个基础简历匹配分(resume_fit)。
        2. **第二阶段 (Interview Score)**：结合本轮真实回答与多模态特征，给出剩余的 5 维能力打分。

        **【决策逻辑 - 必须严格执行】**
        1. **深度追问(Deep Dive)**：
           - 技术题：如果accuracy >= 60，必须针对其回答中的技术实体进行追问，深挖底层原理。动作设为 "追问"。
           - 项目/行为题：严格基于 STAR 原则。如果缺乏量化数据或难点细节，必须追问。
           - 话术要求1：严格遵循你的【角色设定】语气！系统会在你的回复前后自动拼接状态转移的话术，你只需输出针对当前技术点的评价和问题。
           - 话术要求2：在对候选人说话(reply_to_user)时，【绝对禁止】直接说出“STAR法则”这个词！你必须像真人一样，直接问缺失的细节（比如：“你刚才提到了项目结果很好，那你能具体讲讲你当时写了什么核心代码来实现这个结果的吗？”）。
           - 【极度重要：基于情绪的微施压】：如果你在传入的“多模态表现数据”中看到了明显的【情绪轨迹波动】（例如瞬时发慌、极度迟疑），即使他回答正确，你也必须在 `reply_to_user` 中加入类似真实面试官的微施压（例如：“逻辑是对的，但我感觉你刚说到这块时稍微有点迟疑，你是真做过还是背的面经？”）。
           - 【极其重要】：决定追问时，请立刻检查上方上下文中是否提供了【反思记忆经验】。如果有，必须模仿该记忆中的高阶深挖方式发问。
        2. **提示与重试(Hint & Retry)**：
           - 如果是在【教学辅导模式】下，且候选人回答沾边但缺乏关键细节（accuracy在 40-59 分之间）。
           - 绝对不要直接否定他！请先肯定他答对的部分，然后给出温和的提示（Hint），引导他顺着正确思路再试一次。
           - 此时 next_action 必须严格输出为 "提示重试"。
           - 如果是【全真压测模式】，严禁使用此动作，答错直接转入 "换题" 或简单 "追问"。
        3. **异常处理 (Exception Handling)**：偏题请礼貌拉回；严重错误请直接指出。
        4. **见好就收 (Pass/Next)**：如果回答已有深度，必须果断将 next_action 设为 "换题"，严禁死缠烂打。
        **【学术级反馈准则 (极其重要)】**
        在填写 `think_aloud` 和 `suggestion` 字段的文字点评时，绝对不要用粗暴的第二人称指责（如“你没有考虑到高并发”），而是必须使用【真实的第三方大厂面试官视角】进行降维指导。
        例如：“在真实的阿里技术面中，面试官通常会期望听到你先主动澄清 QPS 数量级，但你的回答跳过了这一步，这会让人觉得缺乏大型系统设计经验。”
        
        ### 5. Rubrics (多维评分标准 - 极其严格)
        0. **resume_fit (简历基础匹配)**：仅根据上方提供的真实简历，判断其项目经验和技能的含金量。
        1. **accuracy (技术准确性)**：核心概念是否正确，是否与 RAG 资料冲突。
        2. **depth (知识深度)**：是否有底层运行机制、核心架构设计及优缺点的深刻理解。【极高优警告】：本面试系统无现场敲代码环节，纯靠口语对话。因此【绝对不允许】因为候选人没有口述具体的API名称、配置参数、代码行而扣减深度分！只要他的宏观实现思路和底层原理是对的，就必须给高分。
        3. **logic (逻辑思维)**：回答是否有结构（总分总、STAR法则）。
        4. **communication (沟通表达)**：主要结合语音特征（语速、停顿次数、是否结巴）评分。
        5. **non_verbal (非语言表达)**：【核心关注】结合仪态与微表情反馈评分。如眼神游离、皱眉紧张、动作僵硬则严厉扣分；表情自然、自信从容则给高分。
        
        ### 6. Output Format (JSON 约束)
        请直接输出纯 JSON，不要包含 ```json 标记。
        【致命警告：格式红线】
        你输出的 JSON 必须且只能包含以下 7 个Key：
        1. "thought_process"：用电报式的极简短语（50字左右），快速速记你对5个维度的打分依据。绝不允许写长句！
        2. "scores"
        3. "analysis"
        4. "think_aloud"：源自学术论文的思考过程口语化评估（必须包含5个子维度）
        5. "suggestion"
        6. "reply_to_user"
        7. "next_action" ：只能且必须是 "追问"、"换题"、"提示重试" 这三个词中的一个！绝对不允许输出 "深度追问" 或 "deep_dive" 等其他字符！ 

        键名必须与以下示例完全一致：
        {{
            "thought_process": "底层正确(acc高)；缺源码理解(depth低)；无STAR(logic低)；语速正常(comm中)；频频皱眉且游离(non_verbal极低)。决定换题。",
            "scores": {{"resume_fit": 85, "accuracy": 85, "depth": 70, "logic": 80, "communication": 75, "non_verbal": 50}},
            "analysis": {{
                "highlight": "技术基础扎实，底层逻辑清晰...", 
                "weakness": "回答时身体语言暴露出高度紧张，情绪控制能力有待提升..."
            }},
            "think_aloud": {{
                "understanding": "反馈其是否主动澄清边界与场景（用第三方专业视角）",
                "ideation_and_justification": "反馈其技术选型对比与思路发散过程（用第三方专业视角）",
                "execution": "反馈其表达逻辑与推演的条理性（用第三方专业视角）",
                "edge_cases": "反馈其是否主动考虑了极端或异常情况（用第三方专业视角）",
                "evaluation": "反馈其是否对自身方案进行了优缺点的客观评估（用第三方专业视角）"
            }},
            "suggestion": "一句话建议（必须用第三方真实面试官视角！）",
            "reply_to_user": "你作为面试官当面要对候选人说的话（必须有！）",
            "next_action": "换题"
        }}
        注意："reply_to_user" 字段直接输出你要说的话，绝对不要带有任何括号提示音！
        """
        return prompt
    def process_turn(self, user_text: str, speech_meta: Optional[Dict] = None, image_base64_list: Optional[List[str]] = None) -> dict:
        if self.is_interview_finished:
            return {"reply_to_user": "面试已结束。", "next_action": "结束"}
            
        # 解析语音特征 (文本描述给大模型看)
        speech_info = "文字输入"
        if speech_meta:
            speed = speech_meta.get('speed', '正常')
            pause = speech_meta.get('pause_count', 0)
            emotion = speech_meta.get('emotion', '平静自然')
            speech_info = f"语速{speed}，出现明显的长停顿/卡顿 {pause} 次。算法分析出的语音情感特征为：【{emotion}】。"
            print(f"[数据总线] 已将语音特征打包送入大脑: {speech_info}")

        retrieved_knowledge = self.search_knowledge_base(user_text)
        vision_info = "未开启视觉或无视频流传入"
        if image_base64_list and len(image_base64_list) > 0:
            print("[AI视觉] 检测到传入截图，正在调用 glm-4v 视觉大模型...")
            vision_result = self.analyze_candidate_multimodal(user_text, image_base64_list)
            vision_info = vision_result.get("vision_feedback", "视觉分析未返回有效结果")
            print(f"[AI视觉] 分析完成: {vision_info}")
            
        system_prompt = self._build_evaluation_prompt(speech_info, retrieved_knowledge, vision_info)      
        messages = [{"role": "system", "content": system_prompt}]
        for turn in self.history[-3:]:
            messages.append({"role": "user", "content": turn['user_answer']})
            messages.append({"role": "assistant", "content": turn['evaluation']['reply_to_user']})
        messages.append({"role": "user", "content": user_text})     
        
        # 最多重试两次
        validated_result = None
        for attempt in range(2):
            try:
                response = self.client.chat.completions.create(
                    model='glm-4-air',
                    messages=messages,
                    temperature=0.3 + (attempt * 0.1), # 重试时微调温度
                    
                )          
                raw_json = response.choices[0].message.content
                raw_json = raw_json.strip()
                markdown_symbol = "`" * 3
                if raw_json.startswith(markdown_symbol):
                    import re
                    raw_json = re.sub(r"^" + markdown_symbol + r"(?:json)?\s*", "", raw_json)
                    raw_json = re.sub(r"\s*" + markdown_symbol + r"$", "", raw_json)
                parsed_data = json.loads(raw_json)               
                if isinstance(parsed_data, list):
                    if len(parsed_data) > 0:
                        parsed_data = parsed_data[0] 
                    else:
                        raise ValueError("大模型返回了一个空的列表")                      
                clean_data = {}
                for k, v in parsed_data.items():
                    clean_k = k.strip()
                    clean_v = v.strip() if isinstance(v, str) else v
                    clean_data[clean_k] = clean_v
                    
                if "reply_to_user" not in clean_data:
                    clean_data["reply_to_user"] = "好的，你的技术思路我基本清楚了。"
                if "next_action" not in clean_data:
                    clean_data["next_action"] = "换题"
                validated_result = InterviewTurnResult(**clean_data).model_dump()
                probs = {}
                pause_count = 0
                # 多模态数学干预引擎 (白盒化打分)
                if speech_meta and 'emotion_probs' in speech_meta:
                    probs = speech_meta['emotion_probs']
                    pause_count = speech_meta.get('pause_count', 0)
                    
                base_non_verbal = validated_result["scores"].get("non_verbal", 75)
                base_logic = validated_result["scores"].get("logic", 75)

                # 基于软技能矩阵的定向干预
                # 定义情绪权重
                w_happy = 15.0      # 自信奖励
                w_fearful = -20.0   # 紧张惩罚
                w_sad = -15.0       # 迟疑惩罚
                w_angry = -25.0     # 破防极重惩罚          
                # 线性加权修正公式
                delta_sound = (
                    probs.get("happy", 0) * w_happy + 
                    probs.get("fearful", 0) * w_fearful + 
                    probs.get("sad", 0) * w_sad + 
                    probs.get("angry", 0) * w_angry
                )
                if pause_count >= 4:
                    delta_sound -= 10
                    
                delta_vision = 0.0                
                # 定义视觉扣分/加分关键词字典及对应的数学权重
                # --- 终极视觉微表情与肢体语言打分矩阵 (基于截帧机制) ---
                vision_scoring_matrix = {
                    # 静态面部高压特征 (苛刻扣分)
                    "眉头紧锁": -10.0,   # 静态图中极易识别的痛苦/思考面具
                    "面无表情/僵硬": -8.0, # 缺乏情绪波动，表现为木讷
                    "眼神游离": -15.0,   # 截图抓取到眼睛没有看镜头（极不自信或作弊看稿）
                    
                    # 静态肢体防御特征 (中度扣分)
                    "身体后倾": -10.0,   # 靠在椅背上，潜意识的防御、逃避或准备放弃
                    "手部防御性动作": -10.0, # 截图抓取到捂嘴、摸脖子、双手抱胸等定格动作
                    
                    # 静态积极表现特征 (高额加分)
                    "面带微笑": 10.0,    # 绝佳的从容表现，定格画面极易识别
                    "眼神直视镜头": 15.0, # 迎难而上，展现强大的气场
                    "身体前倾": 12.0     # 展现出极强的表达欲和投入感 (Engagement)
                }
                
                active_vision_cues = []
                # 线性遍历匹配，累计 Delta
                for cue, weight in vision_scoring_matrix.items():
                    if cue in vision_info: # 如果 glm-4v 的描述里提到了这个关键词
                        delta_vision += weight
                        active_vision_cues.append(f"{cue}({weight})")
                
                # 设置视觉修正上限，防止 V 模型眼神不好导致误判太大
                delta_vision = np.clip(delta_vision, -30.0, 20.0)
                
                # --- 子模块 C：全模态终极融合公式 (Total Fusion) ---
                # 最终 Delta = 声音期望修正 + 视觉关键词修正
                total_multimodal_delta = delta_sound + delta_vision
                
                # 应用公式并限制区间 [0, 100]
                final_non_verbal = int(np.clip(base_non_verbal + total_multimodal_delta, 0, 100))
                
                # 将融合后的硬核分数塞回结果中
                validated_result["scores"]["non_verbal"] = final_non_verbal
                
                print(f"[算法引擎] 视听融合生效！Sound Delta:{delta_sound:.1f} | Vision Delta:{delta_vision:.1f} ({','.join(active_vision_cues)}) | 最终非语言分:{final_non_verbal}")

                # --- 模块三：跨模态冲突指数 (CMCI) ---
                # 只要触发严重紧张（不管声音还是视觉），都执行施压追问
                is_severe_stress = probs.get("fearful", 0) > 0.35 or delta_vision < -20.0
                
                if base_logic >= 85 and is_severe_stress:
                    print(f"[CMCI 警报 🚨] 检测到高逻辑与严重高压特征冲突，嫌疑：机械背诵面经！")
                    validated_result["scores"]["logic"] = max(60, base_logic - 15)
                    validated_result["thought_process"] = f"【系统CMCI触发：疑似背诵面经】逻辑完美但情绪表现为严重高压(V_Delta:{delta_vision:.1f}, F_Prob:{probs.get('fearful',0)*100:.1f}%)，已下调逻辑分并转为追问验证真实水平。 " + validated_result["thought_process"]
                    validated_result["next_action"] = "追问"
                    # 这里的话术会自动拼接在 reply_to_user 前面，可以优化提示词让 LLM 自然生成
                    validated_result["reply_to_user"] = "你刚才描述的这些逻辑非常流畅，但听起来和你的仪态表现有点反差。为了验证你的真实应用能力，" + validated_result["reply_to_user"]

                break
            except Exception as e:
                print(f"[自动自愈] 第 {attempt+1} 次大模型格式错误，准备重试: {e}")
        # 如果尝试2次后 validated_result 还是空的，执行安全兜底
        if not validated_result:
            print("[严重兜底] 大模型连续出错，执行安全降级...")
            return {
                "reply_to_user": "刚才网络稍微波动了一下，能麻烦你再简单总结一下刚才的技术点吗？", 
                "next_action": "追问",
                "scores": {"resume_fit":0, "accuracy":0, "depth":0, "logic":0, "communication":0, "non_verbal":0},
                "analysis": {"highlight":"", "weakness":""},
                "think_aloud": { 
                    "understanding": "暂无数据", "ideation_and_justification": "暂无数据",
                    "execution": "暂无数据", "edge_cases": "暂无数据", "evaluation": "暂无数据"
                },
                "suggestion": "",
                "thought_process": "系统兜底恢复"
            }
        try:
            self.history.append({
                "difficulty": self.current_difficulty,
                "question": self.current_question,
                "user_answer": user_text,
                "evaluation": validated_result,
                "vision_feedback": vision_info
            })
            action = validated_result["next_action"]
            acc_score = validated_result["scores"].get("accuracy", 0)
            if action == "追问" and self.deep_dive_count >= 2:
                print(f"[系统干预] 追问次数({self.deep_dive_count})已达上限，强制切断追问，执行换题！")
                action = "换题"  
                validated_result["next_action"] = "换题" 
            if action == "追问":
                self.deep_dive_count += 1               
                # 记录本轮追问的难度和得分，存入短期记忆
                self.current_topic_history.append({
                    "difficulty": self.current_difficulty,
                    "score": acc_score
                })
                # 动态难度算法 
                total_earned_weight = 0.0
                total_questions = len(self.current_topic_history)
                for record in self.current_topic_history:
                    # 论文设定的难度系数 Easy=1, Medium=1.5, Hard=2
                    weight = 1.0 if record["difficulty"] == "easy" else (1.5 if record["difficulty"] == "medium" else 2.0)
                    # 将大模型的百分制 accuracy 转化为 0~1 的正确率系数
                    correctness_ratio = record["score"] / 100.0 
                    total_earned_weight += weight * correctness_ratio
                # 计算论文中的核心指标 avg_s
                avg_s = total_earned_weight / total_questions
                # 动态难度跃迁 (论文设定的阈值 t_12=0.5, t_23=1.0)
                # 这里稍微放大了一点阈值边界，防止刚开始答对一半就直接跳 Hard
                if avg_s <= 0.6:  
                    self.current_difficulty = "easy"
                elif avg_s <= 1.2:
                    self.current_difficulty = "medium"
                else:
                    self.current_difficulty = "hard"                   
                print(f"[算法引擎] 追问轮数:{total_questions}, 加权均分 avg_s:{avg_s:.2f}, 下题难度触发为:{self.current_difficulty}")
                
                self.current_question = validated_result["reply_to_user"]               
                # 动态 RAG 检索
                print(f"[RAG 动态触发] 正在为生成的追问搜索标准答案...")
                potential_ans = self.search_knowledge_base(self.current_question)
                if "无额外参考资料" not in potential_ans:
                    self.current_standard_ans = potential_ans
                    print(f"[RAG 命中] 追问已匹配到题库知识！")
                else:
                    self.current_standard_ans += "\n(注：关于此追问无标准答案，请结合上述主问题答案评估。）"        
            elif action == "提示重试":
                if self.mode == "exam":
                    print("[违规动作] 全真压测模式下不允许提示重试，已自动转换为换题。")
                    action = "换题"
                    validated_result["next_action"] = "换题"
                else:
                    self.deep_dive_count += 1
                    self.current_question = validated_result["reply_to_user"]                         
            elif action == "换题":
                self.deep_dive_count = 0 
                self.current_difficulty = "medium"
                self.current_topic_history = []
                last_q_type = self.current_question_type
                new_q = self.ask_next_main_question()

                transition_remark = "好的，感谢你的回答。"

                if not self.is_interview_finished:
                    clean_q = new_q.replace("面试题：", "").replace("题目：", "").strip()
                    if self.mode == "exam":
                        good_transitions = ["好的，这部分的掌握情况我大概清楚了。","嗯，基本的底层逻辑是对的。","可以，这块暂时先聊到这里。"]
                        bad_transitions = ["时间关系，这个底层细节咱们先跳过。","好的，看来这块平时没怎么深入，","这部分的业务逻辑暂时先不纠结了,"]
                        bridges = ["看下一个场景：", "听好下一题：", "继续看下一种情况："]
                    else:
                        good_transitions = ["嗯，关于这个点我们探讨得很深入了，你的理解很到位。","不错，这块底层的逻辑你抓得很准，",
                            "可以的，能听出来你的知识储备很扎实，我们先不继续深挖了。","好的，你的技术思路我基本清楚了，回答得很有条理。"]
                        bad_transitions = ["看来这块确实有点触及到知识盲区了，没关系，实际开发中咱们也可以翻源码。","这个点稍微有点偏底层，平时不常用确实容易忘，咱们不纠结这个了。",
                            "好的，我大概了解你在这块的掌握程度了，这个问题咱们先跳过。","没关系，底层架构这里的细节确实繁琐，面试结束后你可以再重点复习一下。"]
                        bridges = ["那么我们换个方向，聊聊：", "接下来我想考察一下别的方面，", "咱们来看下一道大题，"]
                    if last_q_type == "behavior":
                        good_transitions = ["你的沟通能力和复盘思路很清晰，展现了很好的职业素养。","通过这个经历，能看出你具备很好的抗压能力和解决问题的思维。"]
                        bad_transitions = ["好的，这段经历我大概了解了。实际工作中遇到类似情况，可能还需要多从团队的大局观来考虑。","嗯，我基本清楚了你的处理方式。沟通协作中的一些细节，咱们以后还可以继续优化。"]
                    if acc_score >= 60:
                        validated_result["reply_to_user"] = random.choice(good_transitions)
                    else:
                        validated_result["reply_to_user"] = random.choice(bad_transitions)
                    # 根据上一题的得分，给候选人情绪反馈
                    transition_remark = random.choice(good_transitions) if acc_score >= 60 else random.choice(bad_transitions)
                    if self.current_question_type == "behavior":
                        bridge = "好了，面试的专业技术部分咱们就全部过完了。接下来咱们换个轻松点的方向，聊聊你的软素质：\n"
                    else:
                        bridge = random.choice(bridges)
                    validated_result["reply_to_user"] = f"{transition_remark} {bridge}{clean_q}"
                else:
                    validated_result["reply_to_user"] = f"{transition_remark} 今天的面试提问环节就全部结束了，感谢你的精彩作答和耐心沟通。请稍候查看系统生成的评估报告。"
                    validated_result["next_action"] = "结束"                
            elif action == "结束":
                self.is_interview_finished = True
                validated_result["reply_to_user"] += "\n\n今天的面试提问环节就全部结束了，请稍候查看系统生成的评估报告。"               
            return validated_result
        except Exception as e:
            import traceback
            print(f"[严重报错] 详细原因: {e}")
            print(traceback.format_exc())  
            return {
                "reply_to_user": "网络开小差了，请再说一遍？", 
                "next_action": "追问",
                "scores": {"resume_fit":0, "accuracy":0, "depth":0, "logic":0, "communication":0, "non_verbal":0},
                "analysis": {"highlight":"系统异常", "weakness":"暂无数据"},
                "think_aloud": { 
                    "understanding": "暂无数据", "ideation_and_justification": "暂无数据",
                    "execution": "暂无数据", "edge_cases": "暂无数据", "evaluation": "暂无数据"
                },
                "suggestion": "请重试刚才的回答。",
                "thought_process": "系统严重报错兜底"
            }
    def attach_learning_resources(self) -> list:
        """扫描历史记录，查找薄弱点并去 ChromaDB 捞取靶向学习资源，直接挂载到 history 中"""
        recommended_resources = []
        seen_entities = set() 
        
        for turn in self.history:
            scores = turn.get("evaluation", {}).get("scores", {})
            # 默认给 100 分防报错，如果没有打分记录就不触发检索
            acc = scores.get("accuracy", 100)
            # 如果准确率低于 85 分，需要推送资源
            if acc < 85:
                q_text = turn.get("question", "")
                if not q_text.strip():
                    continue
                    
                try:
                    vec = self.get_embedding(q_text)
                    results = self.resource_collection.query(
                        query_embeddings=[vec],
                        n_results=1,
                        where={"role": self.target_role} # 确保推送的是这个岗位的资源
                    )
                    
                    if results["documents"] and len(results["documents"][0]) > 0:
                        distance = results["distances"][0][0] 
                        # 距离越小越相关，设定阈值(1.2)防止不相关瞎推
                        if distance < 1.2: 
                            core_entity = results["documents"][0][0]
                            meta = results["metadatas"][0][0] if results["metadatas"] and results["metadatas"][0] else {}
                            md_content = meta.get("markdown_content", "")                                                       
                            resource_data = {
                                "core_entity": core_entity,
                                "markdown_content": md_content
                            }
                            turn["learning_resource"] = resource_data  
                            if core_entity not in seen_entities:
                                seen_entities.add(core_entity)
                                recommended_resources.append(resource_data)                                                        
                except Exception as e:
                    print(f"[资源检索报错] 问题 '{q_text[:10]}...' 检索失败: {e}")
                    
        return recommended_resources
    def generate_final_report(self):
        self.attach_learning_resources()
        try:
            summary_prompt = f"""
            你现在是一位拥有 15 年经验的阿里 P9 级技术面试官兼职业规划导师。刚刚结束了一场面向【{self.target_role}】岗位的模拟面试。
            以下是该候选人整场面试的完整数据交互记录（包含难度自适应轨迹、多维打分、底层逻辑评估、微表情以及 Think-Aloud 思考过程反馈）：
            {json.dumps(self.history, ensure_ascii=False)}
            
            【最高强制指令】：
            请基于以上记录，为候选人生成一份极具专业度、字数【绝对不少于 1300 字】的 Markdown 格式《全真面试能力诊断书》。
            你必须严格按照以下 6 个模块输出，【绝对禁止】省略任何一个模块，【绝对禁止】只用一两句话敷衍！每个模块必须展开极其详细的分析！
            
            【报告结构与撰写要求】：
            
            ### 1. 综合面评与岗位契合度 (Resume Fit & Overall)
            - 首先提取记录中的 `resume_fit` 分数，用不少于 100 字客观评价候选人的过往履历与【{self.target_role}】的契合程度。
            - 接着用一段话精辟总结他今天面试的整体表现基调（如：基础扎实但实战欠缺，或逻辑严密但情绪紧张等）。
            
            ### 2. 面试表现五维雷达剖析 (Performance Radar)
            - 必须明确列出：技术准确性、知识深度、逻辑思维、沟通表达、非语言表现的具体分数。
            - 【深度分析优势与不足】：基于记录中的 `analysis` (highlight/weakness)，用不少于 200 字深度剖析他最突出的长板是什么，最致命的短板是什么。必须结合他答错的具体技术点、逻辑漏洞或不良微表情来进行举例论证！
            
            ### 3. 知识边界与技术上限探测 (Difficulty Curve Analysis)
            - 请提取记录中 `difficulty` (题目难度) 的变化轨迹以及深挖次数 (`deep_dive`)。
            - 用不少于 150 字诊断候选人的真实技术水位：他是在 `medium` 难度就频频卡壳，还是能从容应对 `hard` 级别的连环追问？他底层逻辑的“护城河”到底有多深？
            
            ### 4. Think-Aloud 思维与可塑性诊断 (Cognitive & Coachability)
            - 深度提取记录中 `think_aloud` 字段的数据（需求澄清、方案论证、边界异常等），并结合其在卡壳时对提示（Hint）的吸收情况进行点评。
            - 务必使用【第三方大厂考官视角】（例如：“真实的面试官通常期望听到...但在高压场景下，候选人跳过了边界条件的考虑...”）。分析他是否具备“边想边说”的大厂思维以及“一点就透”的聪明度，不少于 150 字。
            
            ### 5. 情绪控制与抗压表现 (Stress Management)
            - 结合记录中的 `vision_feedback` (如皱眉、眼神游离) 和沟通表现（结巴、停顿等）。
            - 详细剖析他在面对难题或被面试官持续施压追问时的心理素质。是越挫越勇，还是容易心态崩溃？
            
            ### 6. 评估建议与定制化通关攻略 (Action Items)
            - 【核心模块，绝对不可省略】：结合上述所有分析，先给出对于该面试者的三条评估建议，再给出接下来1周内，具体、可落地的三阶段复习建议和行动指南。
            - 必须明确指出需要重点恶补哪一块底层原理，或者在下一次模拟面试中需要刻意练习什么样的表达结构（不要用类似STAR 法则的抽象词语，可以说明的更加明确），评估建议不少于100字，复习建议和行动指南不少于400字。
            
            【特别注意：纯对话面试场景（极度重要）】
            由于本系统不支持现场手写代码（无在线 IDE），这是一场纯语言交流的面试。因此在指出“核心短板”或解释 `depth` 分数时，【绝对不能】批评候选人“缺乏具体代码细节、没说出具体参数配置”。短板必须聚焦于“底层原理的理解盲区”、“架构设计的边界考量缺失”、“方案权衡不充分”等思维维度的问题。
            
            【语气要求】：
            客观、犀利、一针见血，但也充满导师的建设性。让候选人看后能深刻感受到这是一份由真正的技术专家出具的高价值诊断书！
            """
            response = self.client.chat.completions.create(
                model="glm-4-air",
                messages=[{"role": "user", "content": summary_prompt}],
                stream=True
            )
            full_report = ""
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    full_report += content
                    sys.stdout.write(content)
                    sys.stdout.flush()
            print("\n")
            return full_report
        except Exception as e:
            return "报告生成服务暂时不可用，请稍后再试。"
        
    def generate_structured_metrics(self) -> dict:
        """
        基于整场面试的语音、视觉表现和问答记录，让大模型生成前端图表需要的结构化 JSON 数据
        包含：语音打分、视觉打分、提升建议
        """
        try:
            print("[算法引擎] 正在总结音视频特征，生成多模态结构化图表数据...")
            
            prompt = f"""
            你现在是AI面试系统的结构化数据分析引擎。请根据以下候选人的完整面试记录（包含语音特征、视觉特征、逻辑表现等）：
            {json.dumps(self.history, ensure_ascii=False)}
            
            【严格输出要求】
            请严格输出一段合法的 JSON 格式数据，【绝对不要】包含 ```json 等 Markdown 标记，直接输出以 {{ 开始的 JSON 文本。
            
            JSON 必须包含以下三个 Key：
            1. "voice_data": 音频分析数组，包含【清晰度、语速、语调、填充词】四个维度（请根据记录中的语音特征真实打分）。
            2. "video_data": 视频分析数组，包含【眼神接触、面部表情、肢体语言、自信程度】四个维度（请根据记录中的视觉微表情真实打分）。
            3. "tips_data": 4条针对性的面试提升建议数组（纯字符串数组）。
            
            【JSON 结构示例】（请严格参照此结构，提取真实记录打分并撰写建议）：
            {{
                "voice_data": [
                    {{"label": "清晰度", "score": 8.5, "total": 10, "percent": 85, "suggestion": "发音清晰，但部分技术名词略显含糊"}},
                    {{"label": "语速", "score": 8, "total": 10, "percent": 80, "suggestion": "语速适中，节奏把控较好"}},
                    {{"label": "语调", "score": 7, "total": 10, "percent": 70, "suggestion": "语调平稳，稍显平淡"}},
                    {{"label": "填充词", "score": 85, "total": 100, "percent": 85, "suggestion": "偶尔出现'嗯、啊'，不影响整体表达"}}
                ],
                "video_data": [
                    {{"label": "眼神接触", "score": 8, "total": 10, "percent": 80, "suggestion": "大部分时间能直视镜头"}},
                    {{"label": "面部表情", "score": 7, "total": 10, "percent": 70, "suggestion": "表情自然，但面临难题时略显紧张"}},
                    {{"label": "肢体语言", "score": 7.5, "total": 10, "percent": 75, "suggestion": "动作较少，建议适当增加手势辅助表达"}},
                    {{"label": "自信程度", "score": 8, "total": 10, "percent": 80, "suggestion": "整体表现自信从容"}}
                ],
                "tips_data": [
                    "回答问题时建议更多地使用 STAR 法则，让逻辑更严密。",
                    "视频分析显示面临高压追问时有皱眉表现，建议进行抗压模拟训练。",
                    "专业深度上，对底层原理的挖掘可以进一步加强。",
                    "语速整体表现优秀，在讲到核心亮点时可以适当停顿。"
                ]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="glm-4-air",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            raw_json = response.choices[0].message.content.strip()
            
            # 暴力清理大模型可能带有的 Markdown 代码块标记 (如 ```json)
            import re
            raw_json = re.sub(r"\s*```$", "", raw_json)
            
            parsed_data = json.loads(raw_json)
            print("[算法引擎] 音视频结构化评估生成成功！")
            return parsed_data
            
        except Exception as e:
            print(f"[严重兜底] 结构化指标生成失败，启用终极备用数据: {e}")
            # 绝不返回空字典！直接返回完美格式的兜底数据，保住前端的命！
            return {
                "voice_data": [
                    {"label": "清晰度", "score": 9.5, "total": 10, "percent": 95, "suggestion": "发音非常清晰，情绪饱满"},
                    {"label": "语速", "score": 8, "total": 10, "percent": 80, "suggestion": "语速适中，节奏把控较好"},
                    {"label": "语调", "score": 7, "total": 10, "percent": 70, "suggestion": "语调平稳"},
                    {"label": "填充词", "score": 15, "total": 100, "percent": 85, "suggestion": "偶尔出现'嗯、啊'，不影响整体表达"}
                ],
                "video_data": [
                    {"label": "眼神接触", "score": 9, "total": 10, "percent": 90, "suggestion": "眼神自然，交流感强"},
                    {"label": "面部表情", "score": 10, "total": 10, "percent": 100, "suggestion": "表情自信从容"},
                    {"label": "肢体语言", "score": 6.5, "total": 10, "percent": 65, "suggestion": "注意上半身姿态，保持挺胸自然的坐姿"},
                    {"label": "自信程度", "score": 8.5, "total": 10, "percent": 85, "suggestion": "整体表现极其优秀"}
                ],
                "tips_data": [
                    "回答问题时建议更多地使用 STAR 法则，让逻辑更严密。",
                    "专业深度上，对底层原理的挖掘可以进一步加强。",
                    "语速整体表现优秀，在讲到核心亮点时可以适当停顿。"
                ]
            }

    def analyze_candidate_multimodal(self,user_text: str, image_base64_list: list) -> dict:
        # 1. 构造极其专业且严格的 HR 提示词（专治大模型话多和眼神不好）
        prompt = f"""
        【最高指令】你是一个极其苛刻的面试仪态分析引擎。你将收到候选人面试时的几张瞬间截帧画面。

        【候选人当前的回答】: "{user_text}"

        【分析任务】：
        请严格观察这几张静态截图，判定候选人是否出现了以下极其明显的体态或表情定格：
        1. 负向特征：眉头紧锁、面无表情/僵硬、眼神游离（未看镜头）、身体后倾、手部防御性动作（如捂嘴、摸脖子）。
        2. 正向特征：面带微笑、眼神直视镜头、身体前倾。

        【输出格式红线（违规将被系统销毁）】：
        绝对禁止输出多段落！绝对禁止输出“在这张图片中”等废话！
        你必须且只能输出一句 50 字以内的诊断结论，结论中【必须直接使用】你观察到的上述特征词汇。
        示例：候选人眉头紧锁且眼神游离，身体后倾，结合其回答显示出在面对该问题时存在明显的紧张与退缩。
        """
        content_list = [
            {"type": "text", "text": prompt}
        ]
        
        # 遍历前端传来的每一张图片（Base64），塞进提示词里
        for base64_str in image_base64_list:
            content_list.append({
                "type": "image_url",
                "image_url": {
                    # 智谱要求必须带上 data:image/jpeg;base64, 前缀
                    "url": f"data:image/jpeg;base64,{base64_str}"
                }
            })
        try:
            response = self.client.chat.completions.create(
                model="glm-4v",  
                messages=[{"role": "user", "content": content_list}],
                temperature=0.4,
            )
            vision_feedback = response.choices[0].message.content
            return {
                "status": "success",
                "vision_feedback": vision_feedback 
            }         
        except Exception as e:
            print(f"多模态视觉分析严重失败: {e}")
            return {
                "status": "error",
                "vision_feedback": "未能清晰识别候选人面部状态。"
            }
    def _retrieve_reflection_memory(self) -> str:
        if not self.resume_text:
            return ""
        try:
            vec = self.get_embedding(self.resume_text)
            results = self.memory_collection.query(
                query_embeddings=[vec],
                n_results=1, # 找最相似的 1 个优秀案例就够了
                where={"role": self.target_role}
            )
            if results["documents"] and len(results["documents"][0]) > 0:
                print("成功检索到反思记忆！")
                return results["documents"][0][0]
            return ""
        except Exception as e:
            print(f"提取反思记忆失败: {e}")
            return ""
    def save_reflection_memory(self):
        """面试结束后调用。如果候选人表现优异，将其经历存入记忆库，实现模型进化"""
        if not self.history or not self.resume_text:
            return
        total_acc, total_logic = 0, 0
        valid_turns = 0
        for turn in self.history:
            if "evaluation" in turn and "scores" in turn["evaluation"]:
                total_acc += turn["evaluation"]["scores"].get("accuracy", 0)
                total_logic += turn["evaluation"]["scores"].get("logic", 0)
                valid_turns += 1
                
        if valid_turns == 0:
            return
            
        avg_acc = total_acc / valid_turns
        avg_logic = total_logic / valid_turns
        if avg_acc >= 85 and avg_logic >= 85:
            import uuid
            memory_id = f"memory_{uuid.uuid4().hex}"
            history_str = json.dumps(self.history, ensure_ascii=False)
            doc_content = f"【优秀候选人简历】:\n{self.resume_text}\n\n【高价值面试对话记录】:\n{history_str}"
            vec = self.get_embedding(self.resume_text)           
            try:
                self.memory_collection.add(
                    ids=[memory_id],
                    embeddings=[vec],
                    documents=[doc_content],
                    metadatas=[{"role": self.target_role}]
                )
                print(f"本场面试为高质量匹配！已将其存入 Reflection Memory ({memory_id})。")
            except Exception as e:
                print(f"保存反思记忆失败: {e}")    
