from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ME_FILE = PROJECT_ROOT / "data" / "me.txt"

if not ME_FILE.exists():
    ME_FILE = Path("data/me.example.txt")

me_txt = ME_FILE.read_text(encoding="utf-8")
prompt = Path("src/prompt.py").read_text(encoding="utf-8").format(me_txt=me_txt)

EXAMPLES = [
    ["What are your core skills and tech stack?", None],
    ["Walk me through your professional background.", None],
    ["What is the best way to contact you?", None],
    ["Can you save my email or phone number so we can connect?", None],
]
