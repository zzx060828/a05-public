import asyncio
import edge_tts
async def list_voices():
    """列出所有可用的语音"""
    print("正在获取可用的语音列表...")
    print("=" * 60)

    voices = await edge_tts.list_voices()

    # 按语言分组显示
    voices_by_language = {}
    for voice in voices:
        lang = voice["Locale"]
        if lang not in voices_by_language:
            voices_by_language[lang] = []
        voices_by_language[lang].append(voice)

    # 显示前几种语言的语音
    for i, (lang, voice_list) in enumerate(voices_by_language.items()):
        if i >= 10:  # 只显示前10种语言
            break
        print(f"\n语言: {lang}")
        for voice in voice_list[:3]:  # 每种语言显示前3个
            gender = "woman" if voice["Gender"] == "Female" else "man"
            local_name = voice['LocalName'] if 'LocalName' in voice else 'N/A'
            print(f" {gender} {voice['ShortName']} - {local_name}")

    print(f"\n总共支持 {len(voices)} 种语音，{len(voices_by_language)} 种语言")
    return voices


# 运行
asyncio.run(list_voices())