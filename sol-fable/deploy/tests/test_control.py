import importlib.util
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("control", ROOT / "control.py")
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)


class ControlTests(unittest.TestCase):
    def test_init_is_private_and_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / "state"
            control.initialize(state)
            original = (state / "credentials.env").read_bytes()
            values = control.read_env(state)
            self.assertNotEqual(values["POSTGRES_PASSWORD"], values["RABBITMQ_PASSWORD"])
            control.initialize(state)
            self.assertEqual(original, (state / "credentials.env").read_bytes())
            self.assertEqual(stat.S_IMODE(state.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE((state / "credentials.env").stat().st_mode), 0o600)

    def test_foreign_config_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp)
            secret = state / "credentials.env"
            secret.write_text("OPENAI_API_KEY=do-not-send\n")
            secret.chmod(0o600)
            with self.assertRaises(ValueError):
                control.initialize(state)
            self.assertEqual(secret.read_text(), "OPENAI_API_KEY=do-not-send\n")

    def test_symlink_config_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / "state"
            state.mkdir(mode=0o700)
            target = Path(temp) / "target"
            target.write_text("keep")
            (state / "credentials.env").symlink_to(target)
            with self.assertRaises(ValueError):
                control.initialize(state)
            self.assertEqual(target.read_text(), "keep")

    def test_wide_permissions_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "state"
            p.mkdir()
            p.chmod(0o755)
            with self.assertRaises(ValueError):
                control.initialize(p)

    def test_foreign_environment_does_not_reach_compose(self):
        incoming = {"PATH": "/bin", "HOME": "/home/test", "DOCKER_HOST": "unix:///tmp/test.sock",
                    "OPENAI_API_KEY": "private", "OLLAMA_BASE_URL": "http://private",
                    "COMPOSE_FILE": "hostile.yaml", "COMPOSE_PROJECT_NAME": "other",
                    "POSTGRES_PASSWORD": "wrong", "FIRECRAWL_API_KEY": "private"}
        clean = control.clean_environment({"POSTGRES_PASSWORD": "a" * 64,
                                           "RABBITMQ_PASSWORD": "b" * 64}, incoming)
        self.assertEqual(clean["POSTGRES_PASSWORD"], "a" * 64)
        self.assertEqual(clean["DOCKER_HOST"], incoming["DOCKER_HOST"])
        for forbidden in ["OPENAI_API_KEY", "OLLAMA_BASE_URL", "COMPOSE_FILE", "COMPOSE_PROJECT_NAME", "FIRECRAWL_API_KEY"]:
            self.assertNotIn(forbidden, clean)
        self.assertEqual(clean["COMPOSE_DISABLE_ENV_FILE"], "1")

    def test_missing_docker_fails_without_action(self):
        with patch.object(control.shutil, "which", return_value=None):
            with self.assertRaisesRegex(ValueError, "no stack started"):
                control.compose_command()

    def test_source_paths_resolve_to_real_upstream(self):
        self.assertTrue((control.SOURCE / "LICENSE").is_file())
        control.inspect_source()

    def test_modified_source_does_not_prevent_stop_or_status(self):
        with tempfile.TemporaryDirectory() as temp:
            control.initialize(temp)
            with patch.object(control, 'inspect_source', side_effect=ValueError('modified')) as inspect:
                with patch.object(control, 'compose_command', return_value=['docker', 'compose']):
                    with patch.object(control.subprocess, 'run') as run:
                        run.return_value.returncode = 0
                        self.assertEqual(control.execute('stop', temp), 0)
                        self.assertEqual(control.execute('status', temp), 0)
                inspect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
