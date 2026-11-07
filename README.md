# SceneForge UE5 Lab

A **standalone, no-cost feasibility experiment** to see whether SceneForge's GitHub → Android APK → phone feedback loop can be reproduced with Unreal Engine 5.

**Production SceneForge remains on Godot and is not modified by this lab.**

## Current state

- `preflight.yml`: **active** on every push or manual dispatch. Checks repo integrity and examines free GitHub-hosted Linux/Windows runner resources and installed Android/Unreal tools; uploads a probe report. **This does NOT build an APK.**
- `hosted-container.yml`: **engine pull + Android cooking confirmed; Android staging blocked by platform registration in run #7**. The workflow now performs a fast component audit after the engine download on a trusted main-branch push, avoiding repeated expensive cooking. Android packaging is explicit/manual. Test of the official Epic UE 5.8 development container on an ordinary free GitHub runner. Requires an Epic-entitled GitHub account and a read-only GHCR token stored as a GitHub Actions secret. Test modes: manifest, pull, Android packaging. **Not tested without the credential.**
- `android-package.yml`: **prepared, not yet validated**. Manually callable only on an appropriately configured self-hosted runner with a licensed local Unreal Engine 5.8 installation and Android toolchain. It will remain queued if no eligible runner is online.
- `SceneForgeUE5Lab.uproject`: minimal content-free UE 5.8 Android project shell for a packaging smoke test. It uses the engine's Entry map; **no hovercraft, track, or imported game assets yet**.

## Where to look

- [GitHub Actions](https://github.com/tpylman90-ctrl/SceneForge-UE5-Lab/actions) — see **Hosted runner feasibility probe** first.
- [Feasibility gates](docs/FEASIBILITY.md) — how we decide go/no-go.
- [Official Epic container experiment](docs/EPIC_CONTAINER.md) — the GitHub-only candidate.
- [Android runner setup](docs/ANDROID_RUNNER.md) — tooling and security for a provisioned runner.
- [Epic Android requirements](https://dev.epicgames.com/documentation/unreal-engine/android-development-requirements-for-unreal-engine) and [Linux engine setup](https://dev.epicgames.com/documentation/unreal-engine/linux-development-quickstart-for-unreal-engine).

## Ground rules

1. Free tools and services only. No paid Unreal cloud builders, unauthorized engine binary redistribution, or embedded Epic credentials.
2. Keep UE engine binaries, SDKs, signing keys, packaged APKs, and generated/cache files **out of the Git repository**.
3. The project is public. Do **not** submit a PAT, Epic login, keystore, or signing passwords in a file, workflow input, or log.
4. An actual APK must be attached to a **successful packaging run**, installed on the Android phone, and measured before claiming the Godot pipeline has been reproduced.
5. This first milestone is a headless infrastructure test, not a graphics comparison.

## Optional local check

```sh
python3 -m unittest discover -s scripts/ci/tests -v
python3 scripts/ci/runner_probe.py --report-dir reports
```

The lab is intentionally modest: we prove build infrastructure first and add the Shrike/Kestrel/Crimson Serpent tests only after a real Android APK is reproducible.
