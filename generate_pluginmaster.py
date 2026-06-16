#!/usr/bin/env python3
"""Scan plugins/*/*.json and generate pluginmaster.json.

Each plugin manifest only carries basic metadata; this script augments every
entry with the computed download links (pointing at this repo's GitHub Release
assets, tagged <InternalName>-v<AssemblyVersion>), the LastUpdate timestamp
(taken from the manifest file's last git commit) and default flags, then writes
the aggregated pluginmaster.json.
"""
import json
import subprocess
import glob
from pathlib import Path

META_REPO = "denghaoxuan991876906/DalamudPlugins"


def last_commit_ts(path: str) -> int:
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--pretty=%ct", "--", path], text=True
        ).strip()
        return int(out) if out else 0
    except Exception:
        return 0


def main() -> None:
    output = []
    for jf in sorted(glob.glob("plugins/*/*.json")):
        data = json.loads(Path(jf).read_text(encoding="utf-8"))
        internal = data["InternalName"]
        version = data["AssemblyVersion"]
        tag = f"{internal}-v{version}"
        url = f"https://github.com/{META_REPO}/releases/download/{tag}/latest.zip"
        # Respect a hand-set DownloadLinkInstall (e.g. a plugin that hosts its
        # own release on its public repo); otherwise default to this repo.
        data.setdefault("DownloadLinkInstall", url)
        data.setdefault("DownloadLinkUpdate", url)
        data["LastUpdate"] = last_commit_ts(jf)
        data.setdefault("IsHide", "False")
        data.setdefault("IsTestingExclusive", "False")
        output.append(data)
        print(f"  - {internal} v{version} -> {tag}")

    Path("pluginmaster.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Generated pluginmaster.json with {len(output)} plugins")


if __name__ == "__main__":
    main()
