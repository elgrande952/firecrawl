#!/usr/bin/env python3
"""Manage the isolated Firecrawl stack; Python standard library only."""
import argparse
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent.parent
PIN = "7666c1f9ae8720a6bba271e0f60b6a217f8a5210"
PROJECT = "firecrawl-sol-fable"
REQUIRED_KEYS = {"POSTGRES_PASSWORD", "RABBITMQ_PASSWORD"}
BUILD_PATHS = ["apps/api", "apps/playwright-service-ts", "apps/nuq-postgres"]


def private_state(path):
    """Never replace an existing configuration or follow a symbolic link."""
    path = Path(path)
    if path.is_symlink():
        raise ValueError("State directory must not be a symbolic link")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    mode = path.stat().st_mode
    if not stat.S_ISDIR(mode) or stat.S_IMODE(mode) & 0o077:
        raise ValueError("State directory must be private (mode 0700)")
    return path


def read_env(state):
    p = Path(state) / "credentials.env"
    if p.is_symlink() or not p.is_file():
        raise ValueError("Run init first; credentials.env must be a regular file")
    if stat.S_IMODE(p.stat().st_mode) & 0o077:
        raise ValueError("credentials.env must be private (mode 0600)")
    values = {}
    for line in p.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep or key in values or key not in REQUIRED_KEYS:
            raise ValueError("Unexpected or duplicate setting in credentials.env")
        if not re.fullmatch(r"[a-f0-9]{64}", value):
            raise ValueError("Credentials must use 64 hexadecimal characters")
        values[key] = value
    if set(values) != REQUIRED_KEYS:
        raise ValueError("Incomplete credentials.env; existing file preserved")
    return values


def initialize(state):
    state = private_state(state)
    path = state / "credentials.env"
    if path.exists() or path.is_symlink():
        read_env(state)
        return "Existing configuration preserved"
    content = "# Sol-Fable dedicated stack; do not publish\n" + "".join(
        f"{key}={secrets.token_hex(32)}\n" for key in sorted(REQUIRED_KEYS)
    )
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return "Private configuration created"


def clean_environment(values, environ=None):
    source = os.environ if environ is None else environ
    # Keep Docker transport/configuration, never application/provider variables.
    allowed = {"PATH", "HOME", "USER", "DOCKER_HOST", "DOCKER_CONTEXT",
               "DOCKER_CONFIG", "DOCKER_CERT_PATH", "DOCKER_TLS_VERIFY",
               "SSH_AUTH_SOCK", "XDG_RUNTIME_DIR", "LANG", "LC_ALL"}
    env = {k: v for k, v in source.items() if k in allowed}
    env.update(values)
    env["COMPOSE_DISABLE_ENV_FILE"] = "1"
    return env


def inspect_source():
    if not shutil.which("git"):
        raise ValueError("Git is required to verify the pinned source")
    check = subprocess.run(["git", "diff", "--quiet", PIN, "--", *BUILD_PATHS],
                           cwd=SOURCE, capture_output=True)
    if check.returncode:
        raise ValueError("Source differs from the pinned release or Git revision is unavailable")
    for path in BUILD_PATHS:
        if not (SOURCE / path / "Dockerfile").is_file():
            raise ValueError("Required upstream Dockerfile missing")


def compose_command():
    docker = shutil.which("docker")
    if not docker:
        raise ValueError("Docker Engine/Compose are unavailable; no stack started")
    check = subprocess.run([docker, "compose", "version", "--short"],
                           capture_output=True, timeout=15)
    if check.returncode:
        raise ValueError("Docker Compose plugin is unavailable; no stack started")
    return [docker, "compose"]


def execute(action, state):
    state = private_state(state)
    values = read_env(state)
    if action in {'up', 'config'}:
        inspect_source()
    prefix = compose_command()
    cmd = prefix + ["--project-name", PROJECT, "--project-directory", str(ROOT),
                    "--env-file", str(state / "credentials.env"), "-f", str(ROOT / "compose.yaml")]
    actions = {"config": ["config", "--quiet"],
               "up": ["up", "--build", "--detach", "--wait", "--wait-timeout", "300"],
               "status": ["ps", "--all"], "stop": ["stop", "--timeout", "60"]}
    # Quiet config preflight fails before creating containers and never prints secrets.
    env = clean_environment(values)
    result = subprocess.run(cmd + ["config", "--quiet"], env=env, capture_output=True)
    if result.returncode:
        raise ValueError("Compose configuration rejected; credentials withheld from output")
    if action == "config":
        print("Compose configuration valid; no container started")
        return 0
    result = subprocess.run(cmd + actions[action], env=env)
    return result.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", choices=["init", "config", "up", "status", "stop"])
    parser.add_argument("--state-dir", type=Path, default=ROOT / ".state")
    parser.add_argument("--check", action="store_true", help="Read-only prerequisites check")
    args = parser.parse_args(argv)
    try:
        if args.check:
            inspect_source()
            compose_command()
            print("Pinned source and Compose executable available; daemon and runtime not tested")
            return 0
        if not args.action:
            parser.error("Choose an action or --check")
        if args.action == "init":
            print(initialize(args.state_dir))
            return 0
        return execute(args.action, args.state_dir)
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
