#!/usr/bin/env python3
"""Inspect licensed Unreal engine presence without copying proprietary components."""
import json
import os
from pathlib import Path

def inspect(root):
    engine = Path(root) / "Engine"
    auto = engine / "Binaries/DotNET/AutomationTool/AutomationScripts/Platforms/Android/Android.Automation.dll"
    # Check paths that commonly contain precompiled Android engine runtime libs/receipts.
    runtime_directories = [
        engine / "Binaries/Android",
        engine / "Intermediate/Build/Android",
        engine / "Plugins/Runtime/Android",
    ]
    has_auto = auto.is_file()
    available_paths = [p for p in runtime_directories if p.exists()]
    # Installed Android target support cannot be inferred solely from the SDK.
    # Absence of the automation assembly is a decisive staging blocker.
    verdict = ("ANDROID_AUTOMATION_MISSING" if not has_auto
               else "ANDROID_AUTOMATION_PRESENT_RUNTIME_UNVERIFIED")
    return {
        "engine_root_readable": engine.is_dir(),
        "android_automation_assembly": has_auto,
        "android_runtime_artifacts": bool(available_paths),
        "android_runtime_path_count": len(available_paths),
        "assessment": verdict,
        "explanation": ("This is an inspection, not a packaging success. SDK installation "
                        "cannot add Unreal platform components omitted from an installed build."),
    }

if __name__ == "__main__":
    print(json.dumps(inspect(os.environ.get("UE_ROOT", "/home/ue4/UnrealEngine")), indent=2))
