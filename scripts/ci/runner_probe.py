#!/usr/bin/env python3
"""Non-invasive GitHub runner capacity/provisioning report, no credentials logged."""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
ENGINE_V = (5, 8)
NDK_R27C = "27.2.12479018"


def find_engine():
    roots = [os.environ.get(n, "") for n in ("UE_ROOT", "UE_ENGINE_ROOT", "UE_INSTALL_DIR")]
    roots += ["/opt/unreal", "/opt/UnrealEngine", "/usr/local/UnrealEngine",
              "C:/Program Files/Epic Games/UE_5.8"]
    for raw in roots:
        if not raw:
            continue
        root = Path(raw).expanduser()
        uat = root / "Engine" / "Build" / "BatchFiles" / (
            "RunUAT.bat" if os.name == "nt" else "RunUAT.sh"
        )
        if uat.is_file():
            return root, uat
    return None, None


def sdk_state():
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    root = Path(sdk) if sdk else None
    ndk_env = os.environ.get("NDKROOT") or os.environ.get("ANDROID_NDK_ROOT")
    ndk = Path(ndk_env) if ndk_env else (root / "ndk" / NDK_R27C if root else None)
    return {
        "sdk_configured": bool(root and root.is_dir()),
        "android_35_present": bool(root and (root / "platforms" / "android-35").is_dir()),
        "build_tools_35_present": bool(root and (root / "build-tools" / "35.0.1").is_dir()),
        "ndk_r27c_present": bool(ndk and ndk.is_dir() and (NDK_R27C in str(ndk) or
                              (ndk / "source.properties").is_file())),
    }


def java_state():
    executable = shutil.which("java")
    if not executable:
        return {"installed": False, "java_21": False}
    try:
        r = subprocess.run([executable, "-version"], capture_output=True, text=True,
                           timeout=8, check=False)
        banner = (r.stderr or r.stdout).splitlines()[0][:110]
    except (OSError, subprocess.TimeoutExpired, IndexError):
        banner = ""
    return {"installed": True, "java_21": ('"21.' in banner or '"21"' in banner),
            "version": banner}


def make_report():
    disk = shutil.disk_usage(Path.cwd().anchor)
    root, uat = find_engine()
    ue_version_match = False
    version = None
    if root is not None:
        vfile = root / "Engine" / "Build" / "Build.version"
        if vfile.is_file():
            try:
                v = json.loads(vfile.read_text(encoding="utf-8"))
                version = f'{v.get("MajorVersion")}.{v.get("MinorVersion")}'
                ue_version_match = (v.get("MajorVersion"), v.get("MinorVersion")) == ENGINE_V
            except (OSError, ValueError):
                pass
    sdk = sdk_state()
    java = java_state()
    min_tools = bool(uat and ue_version_match and all(sdk.values()) and java["java_21"])
    return {
        "runner": platform.platform(),
        "github_runner_name": os.environ.get("RUNNER_OS", "local"),
        "cpu_count": os.cpu_count(),
        "disk_total_gib": round(disk.total / 2**30, 2),
        "disk_free_gib": round(disk.free / 2**30, 2),
        "ue_5_8_automation_tool_present": bool(uat),
        "ue_version": version,
        "ue_5_8_version_verified": ue_version_match,
        "android_toolchain": sdk,
        "java": java,
        "status": "READY_TO_ATTEMPT_PACKAGING" if min_tools else "NOT_PROVISIONED_FOR_UE_PACKAGING",
        "note": ("Readiness only checks tool discovery; actual feasibility requires "
                 "a successful cook/package and phone installation.")
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--report-dir", default="reports")
    args = p.parse_args()
    report = make_report()
    out = ROOT / args.report_dir
    out.mkdir(parents=True, exist_ok=True)
    name = (os.environ.get("RUNNER_OS", platform.system())).lower()
    json_path = out / f"runner-{name}.json"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        f"### SceneForge UE5 hosted runner probe — {name}",
        f"- Status: **{report['status']}**",
        f"- CPU count: {report['cpu_count']}",
        f"- Total/free disk: {report['disk_total_gib']} / {report['disk_free_gib']} GiB",
        f"- UE 5.8 RunUAT present: {report['ue_5_8_automation_tool_present']}",
        f"- UE version verified: {report['ue_5_8_version_verified']}",
        f"- Android API 35 present: {report['android_toolchain']['android_35_present']}",
        f"- NDK r27c detected: {report['android_toolchain']['ndk_r27c_present']}",
        f"- Java 21 detected: {report['java']['java_21']}",
        "",
        report["note"],
    ]
    summary = "\n".join(lines) + "\n"
    (out / f"summary-{name}.md").write_text(summary, encoding="utf-8")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fp:
            fp.write(summary)
    print(summary)
    print(f"Saved: {json_path}")
    # Absence of proprietary UE is an expected *result*, not a CI failure.
    return 0


if __name__ == "__main__":
    sys.exit(main())
