from __future__ import annotations

import json
from pathlib import Path

from notebooklm_mcp import NotebookLMMCPServer


def main() -> None:
    server = NotebookLMMCPServer()
    descriptor = server.descriptor()

    out_path = Path("artifacts") / "mcp-descriptor.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(descriptor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Descriptor exportado en: {out_path}")


if __name__ == "__main__":
    main()
