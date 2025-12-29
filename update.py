#!/usr/bin/env python3
import subprocess
import json
import sys
from pathlib import Path
from collections import OrderedDict


def main():
    filename = "superhtml.json"
    outs = {}
    if len(sys.argv) < 2:
        raise ValueError("No version provided")
    version = sys.argv[1]
    version_triple = version[1:].split(".")
    print(version_triple)
    data = {}
    if (Path.cwd() / filename).exists():
        with open(filename, "r") as f:
            data = json.load(f)
            if version in data:
                print(f"Version {version} already exists")
                exit()

    systems = {
        "x86_64-linux-musl": "x86_64-linux",
        "aarch64-linux": "aarch64-linux",
        "x86_64-macos": "x86_64-darwin",
        "aarch64-macos": "aarch64-darwin",
    }
    item = {}
    for system in systems:
        url = ""
        # Older versions used tar.gz
        if int(version_triple[0]) <= 0 and int(version_triple[1]) <= 5:
            url = f"https://github.com/kristoff-it/superhtml/releases/download/{version}/{system}.tar.gz"
        else:
            if "linux" in system:
                url = f"https://github.com/kristoff-it/superhtml/releases/download/{version}/{system}.tar.xz"
            if "macos" in system:
                url = f"https://github.com/kristoff-it/superhtml/releases/download/{version}/{system}.zip"
        prefetch_hash_output = subprocess.run(
            ["nix-prefetch-url", f"{url}"], capture_output=True
        )
        if prefetch_hash_output.returncode == 0:
            prefetch_hash = prefetch_hash_output.stdout.decode("utf-8").strip("\n")
            print(f"Hash {prefetch_hash} for system {system}")
            res = {}
            res["hash"] = prefetch_hash
            res["version"] = version
            res["url"] = url
            res["downloaded-system"] = system
            item[systems[system]] = res
        else:
            print(f"Warning: Could not fetch hash for system {system}, skipping")
    outs[version] = item

    with open(filename, "w") as f:
        if data != {}:
            data.update(outs)
            ordered_data = OrderedDict(sorted(data.items(), reverse=True))
            json.dump(ordered_data, f, indent=2)
        else:
            json.dump(outs, f, indent=2)


if __name__ == "__main__":
    main()
