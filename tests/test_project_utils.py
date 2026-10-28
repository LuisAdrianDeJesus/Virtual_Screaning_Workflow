import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import main as orchestrator
from project_utils import load_project


REPO = Path(__file__).resolve().parents[1]


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def project(self, name):
        directory = self.root / name
        directory.mkdir()
        (directory / "project_config.json").write_text(json.dumps({
            "project_name": name, "project_path": r"C:\old\computer\project"
        }))
        return directory

    def test_explicit_project_wins_when_multiple_projects_exist(self):
        self.project("example")
        chosen = self.project("chosen")
        config = load_project("chosen", cwd=self.root)
        self.assertEqual(Path(config["project_path"]), chosen)

    def test_ambiguous_discovery_requires_selection(self):
        self.project("alpha")
        self.project("beta")
        with self.assertRaisesRegex(ValueError, "--project"):
            load_project(cwd=self.root)

    def test_config_location_overrides_obsolete_absolute_path(self):
        project = self.project("copied")
        config = load_project(project / "project_config.json")
        self.assertEqual(Path(config["project_path"]), project)

    def test_discovery_inside_project(self):
        project = self.project("inside")
        self.assertEqual(load_project(cwd=project)["project_path"], str(project))

    def test_single_child_discovery(self):
        project = self.project("only")
        self.assertEqual(load_project(cwd=self.root)["project_path"], str(project))

    def test_missing_project_never_falls_back_to_another_project(self):
        self.project("other")
        with self.assertRaises(FileNotFoundError):
            load_project("missing", cwd=self.root)

    def test_empty_explicit_path_rejected(self):
        with self.assertRaises(ValueError):
            load_project("", cwd=self.root)

    def test_invalid_config_rejected(self):
        project = self.project("invalid")
        for invalid in ([], {"project_name": ""}, {"project_name": 12}):
            with self.subTest(config=invalid):
                (project / "project_config.json").write_text(json.dumps(invalid))
                with self.assertRaises(ValueError):
                    load_project(project)

    def test_setup_creates_portable_project_and_refuses_overwrite(self):
        target = self.root / "project with spaces"
        command = [sys.executable, str(REPO / "setup.py"), "--project", str(target)]
        completed = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        config_file = target / "project_config.json"
        original = config_file.read_bytes()
        self.assertEqual(json.loads(original)["project_path"], ".")
        self.assertTrue((target / "environment.yml").is_file())
        completed = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(config_file.read_bytes(), original)

    def test_orchestrator_passes_the_same_project_to_every_child(self):
        project = self.project("chosen")
        (project / "environment.yml").write_text("name: vina_pipeline\n")
        calls = []
        with (
            patch.object(sys, "argv", ["main.py", "--project", str(project)]),
            patch.object(orchestrator.shutil, "which", return_value="/fake/conda"),
            patch.object(orchestrator, "check_env_exists", return_value=True),
            patch.object(orchestrator, "run_step", side_effect=lambda title, cmd: calls.append(cmd)),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            orchestrator.main()
        self.assertEqual(len(calls), 4)
        for command in calls:
            self.assertEqual(command[-2:], ["--project", str(project)])
            self.assertTrue(Path(command[-3]).is_absolute())


if __name__ == "__main__":
    unittest.main()
