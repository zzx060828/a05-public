import requests
import os
import json

# ==========================================
# 🎯 准备配置
# ==========================================
audio_path = "test.wav"   # 你的测试录音（循环使用）
image_path = "test_1.jpg" # 你的测试照片（循环使用）

if not os.path.exists(audio_path) or not os.path.exists(image_path):
    print("❌ 请确保 test.wav 和 test_1.jpg 在当前目录下！")
    exit()

BASE_URL = "http://127.0.0.1:8000"

# ==========================================
# 🚀 第一幕：敲门开局 (/start)
# ==========================================
print("\n" + "="*50)
print("🎬 面试模拟器启动中...")
print("="*50)

start_res = requests.post(f"{BASE_URL}/start", json={
    "session_id": "123",  # 让后端帮你生成一个全局唯一的会话ID
    "target_role": "Java后端开发工程师",
    "mode": "exam"  # 可以改成 coach 试试不同语气
})

if start_res.status_code != 200:
    print("❌ 启动失败:", start_res.text)
    exit()

session_id = start_res.json().get("session_id")
print(f"✅ 成功连接！会话 ID: {session_id}\n")
print(f"🤖【面试官开场】: {start_res.json().get('reply_text')}")

# ==========================================
# ⚔️ 第二幕：多轮高压交锋 (/chat_with_audio)
# ==========================================
turn = 1
while True:
    print("\n" + "-"*50)
    user_input = input(f"👉 [第 {turn} 轮] 按回车键发送你的音视频文件进行回答 (输入 'q' 提前交卷): ")
    
    if user_input.lower() == 'q':
        print("\n🏃 候选人请求提前结束面试...")
        break
        
    print("⏳ 正在上传多模态数据，请等待考官思考...")
    
    with open(audio_path, "rb") as audio_f, open(image_path, "rb") as img_f:
        files = [
            ("audio_file", (audio_path, audio_f, "audio/wav")),
            ("image_files", (image_path, img_f, "image/jpeg")) 
        ]
        
        chat_res = requests.post(
            f"{BASE_URL}/chat_with_audio", 
            data={"session_id": session_id}, 
            files=files
        )
        
        if chat_res.status_code == 200:
            res_data = chat_res.json()
            print("\n" + "✨"*25)
            # 实时打印出 AI 的内心戏和分数，满足你的监控欲
            print(f"🧠 [AI 内心OS]: {res_data.get('thought_process')}")
            print(f"📊 [实时打分]: {res_data.get('scores')}")
            print(f"🗣️ [面试官回复]: {res_data.get('reply_text')}")
            print("✨"*25)
            
            # 如果后端返回了结束的标识（比如没话说了，或者走完了流程），也可以在这里打断
            if "面试流程已结束" in res_data.get('reply_text', ''):
                print("\n🏁 考官宣布面试正式结束。")
                break
        else:
            print("❌ 对话接口报错:", chat_res.text)
            break
            
    turn += 1

# ==========================================
# 📜 第三幕：生成终极复盘报告 (/report)
# ==========================================
print("\n" + "="*50)
print("📊 正在生成多维度面试体检报告，请稍候...")
print("="*50)

report_res = requests.post(f"{BASE_URL}/report", json={"session_id": session_id})

if report_res.status_code == 200:
    report_data = report_res.json()
    print("\n✅ 报告生成成功！\n")
    
    print("🌟【五维能力雷达平均分】🌟")
    print(json.dumps(report_data.get("radar_data"), indent=4, ensure_ascii=False))
    
    print("\n📝【综合评估小作文】📝")
    print(report_data.get("report_markdown"))
    
    # history 太长了，这里就不全部 print 了，前端知道怎么画就行
    print(f"\n📦 (已成功提取 {len(report_data.get('interview_history', []))} 轮逐句复盘历史数据)")
else:
    print("❌ 报告生成失败:", report_res.text)

print("\n🎉 全链路测试完美通关！")