from pathlib import Path


def get_background(topic: str) -> str:
    """Retrieves verified background facts, experience, writing, and stack details about Vasanth.

    Args:
        topic: The topic to look up (e.g. 'experience', 'skills', 'projects', 'writing', 'rates', 'substack')
    """

    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    ME_FILE = PROJECT_ROOT / "data" / "me.txt"

    if not ME_FILE.exists():
        return "No background file found."

    return ME_FILE.read_text(encoding="utf-8")
