import json
from pathlib import Path


def load_json(path: Path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def save_uploaded_file(uploaded_file, directory: Path) -> Path:
    directory.mkdir(exist_ok=True)
    safe_name = Path(uploaded_file.name).name
    target = directory / safe_name
    target.write_bytes(uploaded_file.getbuffer())
    return target
