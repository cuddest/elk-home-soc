#!/usr/bin/env python3
import argparse
import random
import time
import requests


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://127.0.0.1:8080")
    p.add_argument("--count", type=int, default=30)
    args = p.parse_args()

    endpoints = ["/health", "/products", "/cart", "/checkout", "/slow"]
    for _ in range(args.count):
        endpoint = random.choice(endpoints)
        if endpoint == "/checkout":
            r = requests.post(args.url + endpoint, timeout=3)
        else:
            r = requests.get(args.url + endpoint, timeout=3)
        print(f"{r.status_code:3} {endpoint}")
        time.sleep(random.uniform(0.1, 0.5))


if __name__ == "__main__":
    main()
