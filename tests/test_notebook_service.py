import json
import subprocess
import sys
from pathlib import Path

import unittest

from notebooklm_mcp import NotebookLMMCPServer, NotebookService, SchemaValidationError


class NotebookServiceTest(unittest.TestCase):
    def test_create_and_history(self) -> None:
        service = NotebookService()
        notebook = service.create_notebook(
            title="Proyecto IA",
            description="Investigación de agentes",
            tags=["ia", "mcp"],
            template_id="investigacion_academica",
            actor="tester",
        )

        self.assertEqual(notebook["title"], "Proyecto IA")
        self.assertEqual(len(notebook["sections"]), 4)

        history = service.notebook_history(notebook["id"])
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["action"], "notebook.create")

    def test_merge_cleanup_and_search(self) -> None:
        service = NotebookService()
        n1 = service.create_notebook(title="A", description="uno", tags=["x"])
        n2 = service.create_notebook(title="B", description="dos", tags=["x", "y"])

        service.apply_template(n1["id"], "analisis_producto")
        merged = service.merge_notebooks([n1["id"], n2["id"]], "Fusion")

        self.assertEqual(merged["title"], "Fusion")
        self.assertEqual(set(merged["tags"]), {"x", "y"})

        cleaned = service.cleanup_notebook(merged["id"])
        lowered = [s.lower() for s in cleaned["sections"]]
        self.assertEqual(len(lowered), len(set(lowered)))

        found = service.search_notebooks("fusion")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["id"], merged["id"])


class MCPServerTest(unittest.TestCase):
    def test_registry_and_tool_calls(self) -> None:
        server = NotebookLMMCPServer()
        tools = server.list_tools()
        names = {tool["name"] for tool in tools}
        self.assertIn("notebook.create", names)
        self.assertIn("notebook.history", names)
        self.assertIn("analysis.find_contradictions", names)
        self.assertIn("analysis.suggest_questions", names)
        self.assertIn("analysis.tone", names)
        self.assertIn("research.web_search_with_citations", names)
        self.assertIn("research.translate_source", names)
        self.assertIn("material.generate_audiovisual_pack", names)
        self.assertIn("material.preview", names)
        self.assertIn("material.generate_mindmap", names)
        self.assertIn("material.export_summary", names)
        self.assertIn("study.generate_quiz", names)
        self.assertIn("study.interactive_mindmap", names)

        created = server.call_tool(
            "notebook.create",
            {
                "title": "Cuaderno desde tool",
                "template_id": "investigacion_academica",
            },
        )
        history = server.call_tool("notebook.history", {"notebook_id": created["id"]})
        questions = server.call_tool(
            "analysis.suggest_questions",
            {"notebook_id": created["id"], "limit": 3},
        )
        tone = server.call_tool("analysis.tone", {"notebook_id": created["id"]})

        self.assertEqual(created["title"], "Cuaderno desde tool")
        self.assertEqual(len(history), 1)
        self.assertEqual(len(questions["questions"]), 3)
        self.assertIn(tone["primary_tone"], {"neutral", "promocional", "critico"})

    def test_find_contradictions(self) -> None:
        server = NotebookLMMCPServer()
        created = server.call_tool(
            "notebook.create",
            {
                "title": "Conflictos",
                "description": "Prueba de contradicción",
            },
        )

        notebook = server.service.repo.get(created["id"])
        notebook.sections = [
            "El modelo responde con exactitud",
            "El modelo no responde con exactitud",
            "Metodología",
        ]
        server.service.repo.update(notebook)

        result = server.call_tool("analysis.find_contradictions", {"notebook_id": created["id"]})
        self.assertGreaterEqual(len(result["contradictions"]), 1)
        self.assertIn("hipótesis", result["missing_information"])

    def test_research_tools(self) -> None:
        server = NotebookLMMCPServer()

        results = server.call_tool(
            "research.web_search_with_citations",
            {"query": "MCP notebook research", "limit": 2, "language": "es"},
        )
        self.assertLessEqual(results["total"], 2)
        self.assertGreaterEqual(results["total"], 1)
        self.assertIn("url", results["results"][0])

        translation = server.call_tool(
            "research.translate_source",
            {
                "text": "Este cuaderno de investigación usa fuentes y preguntas",
                "target_language": "en",
                "source_language": "es",
            },
        )
        self.assertEqual(translation["target_language"], "en")
        self.assertIn("notebook", translation["translated_text"].lower())

    def test_input_validation_errors(self) -> None:
        server = NotebookLMMCPServer()

        with self.assertRaises(KeyError):
            server.call_tool("unknown.tool", {})

        with self.assertRaises(SchemaValidationError):
            server.call_tool("notebook.create", {"description": "sin título"})

        with self.assertRaises(SchemaValidationError):
            server.call_tool("research.web_search_with_citations", {"query": "mcp", "limit": "dos"})

        with self.assertRaises(SchemaValidationError):
            server.call_tool(
                "notebook.merge",
                {"source_ids": ["a"], "destination_title": "fusion"},
            )

    def test_resources_listing_and_read(self) -> None:
        server = NotebookLMMCPServer()
        created = server.call_tool(
            "notebook.create",
            {"title": "Recurso Notebook", "template_id": "analisis_producto"},
        )

        resources = server.list_resources()
        uris = {item["uri"] for item in resources}
        self.assertIn("mcp://server/info", uris)
        self.assertIn("mcp://templates/notebook", uris)
        self.assertIn(f"mcp://notebooks/{created['id']}/summary", uris)

        server_info = server.read_resource("mcp://server/info")
        self.assertEqual(server_info["contents"]["name"], "notebooklm-mcp-server")

        templates = server.read_resource("mcp://templates/notebook")
        self.assertIn("investigacion_academica", templates["contents"])

        notebook_summary = server.read_resource(f"mcp://notebooks/{created['id']}/summary")
        self.assertEqual(notebook_summary["contents"]["id"], created["id"])

    def test_prompts_listing_and_get(self) -> None:
        server = NotebookLMMCPServer()
        created = server.call_tool(
            "notebook.create",
            {"title": "Prompt Notebook", "template_id": "investigacion_academica"},
        )

        prompts = server.list_prompts()
        names = {item["name"] for item in prompts}
        self.assertIn("research_brief", names)
        self.assertIn("study_plan", names)

        brief = server.get_prompt("research_brief", {"notebook_id": created["id"]})
        self.assertEqual(brief["name"], "research_brief")
        self.assertEqual(brief["messages"][0]["role"], "system")

        plan = server.get_prompt("study_plan", {"notebook_id": created["id"], "days": 5})
        self.assertEqual(plan["name"], "study_plan")
        self.assertIn("5 días", plan["messages"][1]["content"])

    def test_descriptor_and_export_script(self) -> None:
        server = NotebookLMMCPServer()
        descriptor = server.descriptor()

        self.assertIn("server", descriptor)
        self.assertIn("capabilities", descriptor)
        self.assertIn("tools", descriptor)
        self.assertIn("resources", descriptor)
        self.assertIn("prompts", descriptor)
        self.assertEqual(descriptor["server"]["name"], "notebooklm-mcp-server")
        self.assertGreaterEqual(descriptor["capabilities"]["tools"]["count"], 1)
        self.assertTrue(descriptor["capabilities"]["resources"]["supported"])
        self.assertTrue(descriptor["capabilities"]["prompts"]["supported"])

        cmd = [sys.executable, "scripts/export_descriptor.py"]
        completed = subprocess.run(
            cmd,
            cwd=Path(__file__).resolve().parents[1],
            env={"PYTHONPATH": "src"},
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Descriptor exportado", completed.stdout)

        descriptor_path = Path(__file__).resolve().parents[1] / "artifacts" / "mcp-descriptor.json"
        self.assertTrue(descriptor_path.exists())
        loaded = json.loads(descriptor_path.read_text(encoding="utf-8"))
        self.assertEqual(loaded["server"]["name"], "notebooklm-mcp-server")

    def test_material_and_study_tools(self) -> None:
        server = NotebookLMMCPServer()
        created = server.call_tool(
            "notebook.create",
            {
                "title": "Material de Estudio",
                "template_id": "investigacion_academica",
            },
        )

        pack = server.call_tool(
            "material.generate_audiovisual_pack",
            {"notebook_id": created["id"], "style": "soft"},
        )
        preview = server.call_tool("material.preview", {"notebook_id": created["id"]})
        mindmap = server.call_tool("material.generate_mindmap", {"notebook_id": created["id"]})
        exported = server.call_tool(
            "material.export_summary",
            {"notebook_id": created["id"], "format": "md"},
        )
        quiz = server.call_tool(
            "study.generate_quiz",
            {"notebook_id": created["id"], "difficulty": "media", "limit": 3},
        )
        interactive = server.call_tool("study.interactive_mindmap", {"notebook_id": created["id"]})

        self.assertGreaterEqual(pack["total_scenes"], 1)
        self.assertGreaterEqual(len(preview["blocks"]), 1)
        self.assertGreaterEqual(len(mindmap["nodes"]), 1)
        self.assertIn("# Material de Estudio", exported["content"])
        self.assertEqual(quiz["total"], 3)
        self.assertGreaterEqual(len(interactive["nodes"]), 1)


if __name__ == "__main__":
    unittest.main()
