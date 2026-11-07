#!/usr/bin/env python3
"""Package a smoke-test Unreal project using a separately provisioned UE 5.8 runner."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from runner_probe import ENGINE_V, find_engine

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "SceneForgeUE5Lab.uproject"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--archive-dir", default=str(ROOT / "dist"))
    p.add_argument("--dry-run", action="store_true",
                   help="validate paths and print command without executing it")
    args = p.parse_args()
    project = json.loads(PROJECT.read_text(encoding="utf-8"))
    if project.get("EngineAssociation") != ".".join(map(str, ENGINE_V)):
        raise SystemExit("Project engine does not match pinned CI engine version.")
    engine, uat = find_engine()
    if not uat:
        raise SystemExit("UE 5.8 RunUAT not found. Set UE_ROOT to a legitimately "
                         "installed Unreal Engine 5.8 directory on the runner.")
    version_file = engine / "Engine" / "Build" / "Build.version"
    if not version_file.is_file():
        raise SystemExit("Unreal Engine/Build/Build.version not found.")
    info = json.loads(version_file.read_text(encoding="utf-8"))
    if (info.get("MajorVersion"), info.get("MinorVersion")) != ENGINE_V:
        raise SystemExit(f"Unexpected installed Unreal version: {info.get('MajorVersion')}."
                         f"{info.get('MinorVersion')} (need 5.8)")
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if not sdk or not Path(sdk).is_dir():
        raise SystemExit("ANDROID_HOME must point to a configured Android SDK.")
    if not os.environ.get("JAVA_HOME"):
        raise SystemExit("JAVA_HOME must point to OpenJDK 21.")
    ndk = os.environ.get("NDKROOT") or os.environ.get("ANDROID_NDK_ROOT")
    if not ndk:
        guess = Path(sdk) / "ndk" / "27.2.12479018"
        if guess.is_dir():
            ndk = str(guess)
            os.environ["NDKROOT"] = ndk
    if not ndk or not Path(ndk).is_dir():
        raise SystemExit("UE 5.8 requires Android NDK r27c. Configure NDKROOT.")
    archive = Path(args.archive_dir).resolve()
    archive.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(uat), "BuildCookRun", f"-project={PROJECT}", "-noP4",
        "-platform=Android", "-clientconfig=Development",
        "-cookflavor=ASTC", "-build", "-cook", "-allmaps", "-stage",
        "-pak", "-package", "-archive", f"-archivedirectory={archive}",
        "-unattended", "-utf8output"
    ]
    print("Using licensed local UE 5.8 installation; no engine download or credentials.")
    print("Packaging command:", subprocess.list2cmdline(cmd))
    if not args.dry_run:
        subprocess.run(cmd, check=True, cwd=ROOT)
        apks = list(archive.rglob("*.apk"))
        if not apks:
            raise SystemExit("Unreal packaging returned without an Android .apk. "
                             "Mark this run failed; inspect UAT logs.")
        print("APK artifacts:", [str(p.relative_to(ROOT)) for p in apks])
    return 0


if __name__ == "__main__":
    sys.exit(main())
