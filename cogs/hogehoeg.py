import re

def clean_text(text):
    text = re.sub(r'\|\|.+?\|\|', 'ネタバレ', text)
    text = re.sub(r'`[^\n\r\f\v`]+?`|```[\s\S]+?```', 'コード省略', text)
    text = re.sub(r'^(-#\ )?(#{1,3}\ )?;[\s\S]*|//.*?(\n|$)|/\*[\s\S]*?\*/', '\n', text).strip()
    text = text.replace('IA姉', 'いあねえ')
    text = text.replace('ia姉', 'いあねえ')
    text = text.replace("IA", "いあ")
    text = text.replace('`ia', 'いあ')
    return text
