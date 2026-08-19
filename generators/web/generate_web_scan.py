#!/usr/bin/env python3
import argparse
import time
import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8080")
    parser.add_argument("--count", type=int, default=15)
    parser.add_argument("--delay", type=float, default=0.05)
    args = parser.parse_args()

    paths = [
        "/admin", "/wp-admin", "/.env", "/phpmyadmin", "/server-status",
        "/does-not-exist", "/backup", "/config", "/api/unknown", "/secret",
    ]
    headers = {"User-Agent": "LabScanner/1.0"}
    for i in range(args.count):
        path = paths[i % len(paths)]
        r = requests.get(args.url + path, headers=headers, timeout=3)
        print(f"{r.status_code:3} GET {path}")
        time.sleep(args.delay)


if __name__ == "__main__":
    main()
