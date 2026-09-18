from pathlib import Path

me_file = Path("src/data/me.txt")
if not me_file.exists():
    me_file = Path("src/data/me.example.txt")

me_txt = me_file.read_text(encoding="utf-8")
prompt = Path("src/prompt.py").read_text(encoding="utf-8").format(me_txt=me_txt)

EXAMPLES = [
    ["What are your core skills and tech stack?", None],
    ["Walk me through your professional background.", None],
    ["What is the best way to contact you?", None],
    ["Can you save my email or phone number so we can connect?", None]
]