# 文件路径：backend/app/data_initializer.py
import json
import os
from .database import SessionLocal, QuestionBank  # 👈 引入同级目录下的数据库工具


def auto_import_json():
    db = SessionLocal()
    try:
        # 1. 安全检查：如果数据库里已经有数据了，直接跳过
        existing_count = db.query(QuestionBank).count()

        # 💡 【核心改进】：如果你发现行为题数量不对（比如少于 10 条），强制清空表重新导！
        # 这样你就不用每次去 Navicat 手动清空表了
        if 0 < existing_count < 10:
            print("⚠️ [题库初始化] 检测到数据库中数据不完整，正在强制清空并重新导入...")
            db.query(QuestionBank).delete()
            db.commit()
            existing_count = 0

        if existing_count > 0:
            print(f"ℹ️ [题库初始化] 数据库中已存在 {existing_count} 条数据，跳过自动导入。")
            return

        print("🚀 [题库初始化] 检测到题库为空，开始自动初始化数据...")

        # 2. 获取当前文件的绝对路径，精准推导最外层 project_root
        current_file_path = os.path.abspath(__file__)
        core_dir = os.path.dirname(current_file_path)
        app_dir = os.path.dirname(core_dir)
        backend_dir = os.path.dirname(app_dir)
        project_root = os.path.dirname(backend_dir)

        ai_module_dir = os.path.join(project_root, 'ai_module')

        all_json_path = os.path.join(ai_module_dir, 'all.json')
        behavior_json_path = os.path.join(ai_module_dir, 'behavior_questions.json')

        # 3. 读取 JSON 文件
        with open(all_json_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        with open(behavior_json_path, 'r', encoding='utf-8') as f:
            behavior_data = json.load(f)

        questions_to_insert = []

        # 辅助判断函数（保持你原有的逻辑）
        def get_role_prefix(role_str):
            if "Java" in role_str: return "java"
            if "Python" in role_str: return "python"
            if "前端" in role_str or "Web" in role_str: return "frontend"
            return "common"

        # 4. 组装 all.json
        for item in all_data:
            role = item.get("role", "")
            q_type = item.get("question_type", "")
            q_id = item.get("id", "")
            prefix = get_role_prefix(role)

            if "Turn3" in q_id:
                tab_type = "project"
            elif q_type == "scenario":
                tab_type = "scenario"
            else:
                tab_type = "knowledge"

            questions_to_insert.append(QuestionBank(
                category=f"{prefix}_{tab_type}",
                core_entity=item.get("core_entity", ""),
                question=item.get("question", "").strip(),
                answer=item.get("answer", "").strip(),
                difficulty=item.get("difficulty", "Medium"),
                expected_answer_points=item.get("expected_answer_points", []),
                scoring_points=item.get("scoring_points", [])
            ))

        # 5. 组装 behavior_questions.json (通用行为题)
        for item in behavior_data:
            questions_to_insert.append(QuestionBank(
                category="common_behavior",
                core_entity=item.get("core_entity", ""),
                question=item.get("question", "").strip(),
                answer=item.get("answer", "").strip(),
                difficulty=item.get("difficulty", "Medium"),
                expected_answer_points=item.get("expected_answer_points", []),
                scoring_points=item.get("scoring_points", [])
            ))

        # 🔴 【核心改动 1】：把这两行移到 for 循环的外面！
        # 等几百条数据全部 append 到 questions_to_insert 列表中之后，一次性写入
        db.add_all(questions_to_insert)
        db.commit()

        print(f"🎉 [题库初始化] 成功初始化导入 {len(questions_to_insert)} 条题库数据！")

    except Exception as e:
        db.rollback()
        print(f"❌ [题库初始化] 导入失败，原因: {e}")
    finally:
        db.close()


        