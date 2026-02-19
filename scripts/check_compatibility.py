from __future__ import annotations

import json
from pathlib import Path

from notebooklm_mcp import NotebookLMMCPServer


def main() -> None:
    server = NotebookLMMCPServer()
    report = server.compatibility_report()

    out_path = Path("artifacts") / "compatibility-report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Compatibilidad: {'OK' if report['compatible'] else 'FAIL'}")
    print(f"Checks OK: {report['summary']}")
    print(f"Reporte exportado en: {out_path}")


if __name__ == "__main__":
    main()
