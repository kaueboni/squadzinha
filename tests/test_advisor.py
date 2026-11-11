"""Advisor do Claude Code (params.advisor). Só biblioteca padrão: python -m unittest discover -s tests"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def run_install(proj, *args):
    out = subprocess.run([sys.executable, str(INSTALL), "--project", str(proj), *args],
                         capture_output=True, text=True, encoding="utf-8")
    return out.returncode, json.loads(out.stdout)


class Advisor(unittest.TestCase):
    def setUp(self):
        base = tempfile.mkdtemp(prefix="squad advisor ")
        self.addCleanup(shutil.rmtree, base, ignore_errors=True)
        self.proj = Path(base) / "projeto"
        (self.proj / "tests").mkdir(parents=True)
        (self.proj / "pyproject.toml").write_text('[project]\nname="x"\ndependencies=["pytest"]\n', encoding="utf-8")
        git(self.proj, "init", "-q")

    def config(self, target=None):
        args = ["--init-config"] + (["--target", target] if target else [])
        code, out = run_install(self.proj, *args)
        self.assertEqual(code, 0, out)
        meta = ".github" if target == "copilot" else ".claude"
        return self.proj / meta / "minimal-squad.json"

    def set_advisor(self, cfg_path, value):
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        cfg.setdefault("params", {})["advisor"] = value
        cfg_path.write_text(json.dumps(cfg), encoding="utf-8")

    def read(self, rel):
        return (self.proj / rel).read_text(encoding="utf-8")

    def test_padrao_liga_opus_no_settings_e_nos_textos(self):
        cfg = json.loads(self.config().read_text(encoding="utf-8"))
        self.assertEqual(cfg["params"]["advisor"], "opus")
        code, out = run_install(self.proj, "--steps", "agents,commands,settings,claude-md")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(self.read(".claude/settings.json"))["advisorModel"], "opus")
        build = self.read(".claude/commands/build.md")
        self.assertIn("consulte o\n   advisor (opus)", build)
        self.assertIn("o advisor NÃO decide estes", build)
        self.assertIn("8. **Ao final:**", build)
        self.assertIn("Advisor (opus)", self.read(".claude/agents/developer.md"))
        self.assertIn("Advisor (opus)", self.read(".claude/agents/tech-lead.md"))
        self.assertNotIn("advisor", self.read(".claude/agents/auditor.md").lower())
        self.assertIn("Advisor (opus)", self.read("CLAUDE.md"))

    def test_vazio_desliga_e_mantem_texto_original(self):
        self.set_advisor(self.config(), "")
        code, out = run_install(self.proj, "--steps", "agents,commands,settings")
        self.assertEqual(code, 0, out)
        self.assertNotIn("advisorModel", json.loads(self.read(".claude/settings.json")))
        build = self.read(".claude/commands/build.md")
        self.assertNotIn("advisor", build.lower())
        self.assertIn("6. **Pare e pergunte** quando: a spec for ambígua", build)
        self.assertIn("7. **Ao final:**", build)

    def test_nao_sobrescreve_advisor_do_usuario(self):
        self.config()
        settings = self.proj / ".claude" / "settings.json"
        settings.write_text(json.dumps({"advisorModel": "fable"}), encoding="utf-8")
        code, out = run_install(self.proj, "--steps", "settings")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(settings.read_text(encoding="utf-8"))["advisorModel"], "fable")
        self.assertTrue(any("advisorModel" in w for w in out["warnings"]), out["warnings"])

    def test_copilot_ignora_advisor(self):
        self.config("copilot")
        code, out = run_install(self.proj, "--steps", "all")
        self.assertEqual(code, 0, out)
        for path in (self.proj / ".github").rglob("*.md"):
            if "skills" in path.parts or "references" in path.parts:
                continue
            self.assertNotIn("advisor", path.read_text(encoding="utf-8").lower(), path)


class ContractTesterRemovido(unittest.TestCase):
    """Projetos instalados com a 0.2.0 tinham .claude/agents/contract-tester.md."""

    def setUp(self):
        base = tempfile.mkdtemp(prefix="squad retired ")
        self.addCleanup(shutil.rmtree, base, ignore_errors=True)
        self.proj = Path(base) / "projeto"
        (self.proj / "tests").mkdir(parents=True)
        git(self.proj, "init", "-q")
        code, out = run_install(self.proj, "--init-config")
        self.assertEqual(code, 0, out)
        self.agent = self.proj / ".claude" / "agents" / "contract-tester.md"
        self.agent.parent.mkdir(parents=True, exist_ok=True)
        self.agent.write_text("---\nname: contract-tester\n---\nantigo\n", encoding="utf-8")

    def lock(self, content):
        sys.path.insert(0, str(ROOT / "scripts"))
        from common import sha256_text
        lock = self.proj / ".claude" / "minimal-squad.lock.json"
        lock.write_text(json.dumps({"files": {".claude/agents/contract-tester.md": sha256_text(content)}}),
                        encoding="utf-8")

    def test_remove_se_nao_foi_editado(self):
        self.lock(self.agent.read_text(encoding="utf-8"))
        code, out = run_install(self.proj, "--steps", "agents")
        self.assertEqual(code, 0, out)
        self.assertFalse(self.agent.exists())
        self.assertTrue(any("contract-tester" in r for r in out.get("removed", [])), out)
        self.assertFalse((self.proj / ".claude" / "agents" / "developer.md").read_text(
            encoding="utf-8").count("tests/contract"))

    def test_mantem_se_foi_editado(self):
        self.lock("outro conteúdo")
        code, out = run_install(self.proj, "--steps", "agents")
        self.assertEqual(code, 0, out)
        self.assertTrue(self.agent.exists())
        self.assertTrue(any("contract-tester" in w for w in out["warnings"]), out["warnings"])

    def test_instalacao_nova_nao_menciona(self):
        self.agent.unlink()
        code, out = run_install(self.proj, "--steps", "agents,layout")
        self.assertEqual(code, 0, out)
        self.assertFalse(any("contract-tester" in s for s in out["skipped"]), out["skipped"])
        self.assertFalse((self.proj / "tests" / "contract").exists())
        self.assertEqual(len(list((self.proj / ".claude" / "agents").glob("*.md"))), 5)


if __name__ == "__main__":
    unittest.main()
