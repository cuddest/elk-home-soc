#!/usr/bin/env python3
from pathlib import Path
import argparse
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SSH = ROOT / "generators" / "ssh" / "generate_ssh_logs.sh"
WIN = ROOT / "generators" / "windows" / "generate_windows_events.py"


def run_ssh(count: int, source_ip: str, mode: str):
    env = dict(__import__("os").environ)
    env.update({"SOURCE_IP": source_ip, "MODE": mode})
    subprocess.run(["bash", str(SSH), str(count)], check=True, env=env)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ssh-count", type=int, default=8)
    p.add_argument("--windows-count", type=int, default=8)
    p.add_argument("--source-ip", default="185.234.72.45")
    args = p.parse_args()

    run_ssh(args.ssh_count, args.source_ip, "failure")
    run_ssh(1, args.source_ip, "success")
    subprocess.run([
        "python3", str(WIN), "--count", str(args.windows_count),
        "--mode", "failure", "--source-ip", args.source_ip,
    ], check=True)
    subprocess.run([
        "python3", str(WIN), "--count", "1", "--mode", "success",
        "--source-ip", args.source_ip,
    ], check=True)
    print("Generated SSH failures -> SSH success and Windows 4625 -> 4624 sequences.")


if __name__ == "__main__":
    main()
