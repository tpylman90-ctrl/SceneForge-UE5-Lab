#!/usr/bin/env python3
"""Fail Android packaging early when Unreal's own Android automation is absent."""
import json
import sys
from pathlib import Path

def main():
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf8"))
    if not data.get("android_automation_assembly", False):
        print("::error::UE installed build lacks Android.Automation.dll. "
              "The official dev-slim Linux image is not yet proven Android-packageable; "
              "installing Android SDK/NDK alone cannot repair missing UE platform support.")
        return 6
    print("Android automation assembly found; additional platform support "
          "and packaging still require verification.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
