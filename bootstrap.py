#!/usr/bin/env python
import shutil
from pathlib import Path

ROOT = Path(__file__).parent


def main():
    created = []
    for example in sorted(ROOT.glob("PLUGINS/*/CONFIG.example.py")):
        target = example.with_name("CONFIG.py")
        if target.exists():
            continue
        shutil.copyfile(example, target)
        created.append(str(target.relative_to(ROOT)))
    for name in created:
        print(f"created {name}")
    if not created:
        print("all CONFIG.py files already present")
    missing_models = [
        d for d in ("bm25", "bge-reranker-v2-m3")
        if not any((ROOT / "Docker" / "Huggingface" / d).glob("*[!.gitkeep]*"))
    ]
    if missing_models:
        print("NOTE: local embedding models missing: " + ", ".join(missing_models))
        print("run: python PLUGINS/Huggingface/download_model.py")


if __name__ == "__main__":
    main()
