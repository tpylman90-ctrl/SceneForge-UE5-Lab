# Provisioning guide for an eventual Android packaging runner

**Nothing in this repository installs Unreal or grants Epic license access.** Unreal Engine source and Linux installed builds require authorized Epic account access. Do not place engine files, Epic tokens, or session cookies in this public repository.

## Pinned stack

- UE **5.8** installed build from Epic, verified via `Engine/Build/Build.version`
- Android SDK Platform **35**, Build-tools **35.0.1**
- Android NDK **r27c** (`27.2.12479018`)
- OpenJDK **21**
- Python 3.9+ for the CI scripts
- x64 Windows or Linux with enough storage for the installed UE engine, Android toolchain, intermediate cook output and artifacts; treat 50 GB+ free as an initial planning allowance rather than a measured requirement

References: [UE 5.8 Android requirements](https://dev.epicgames.com/documentation/unreal-engine/android-development-requirements-for-unreal-engine), [Epic Linux engine installation](https://dev.epicgames.com/documentation/unreal-engine/linux-development-quickstart-for-unreal-engine).

## Runner environment

1. Install UE 5.8 via an authorized Epic method.
2. Configure Android SDK/NDK/JDK per Epic's instructions.
3. Set machine environment `UE_ROOT` to the UE installed-build directory and `ANDROID_HOME`, `NDKROOT`, `JAVA_HOME` to the correct paths. On Linux, ensure `RunUAT.sh` is executable.
4. Register an appropriate GitHub Actions **self-hosted** runner with label `ue5-android` in addition to the OS label.
5. In GitHub Actions, select **Unreal Android APK (provisioned runner only)** → Run workflow → `linux` or `windows`.

**Security warning:** A self-hosted runner executing code from a public repository has significant remote-code-execution and credential-exposure risk. GitHub strongly discourages self-hosted runners for public repos. Prefer a dedicated isolated build host, no personal files, restricted network/permissions, disposable runner, and manual trusted-branch dispatch only. Never use a personal workstation with secrets for untrusted contributions. If we choose self-hosting, first reassess whether a private repository is safer.

This workflow is intentionally `workflow_dispatch`-only and does not execute on pull requests. That is a partial guard, **not** complete isolation.

## What the command does

`python scripts/ci/package_android.py` calls UE 5.8's `RunUAT BuildCookRun` for Development / Android / ASTC and checks that an APK exists under `dist/`. It requires the engine and tools already present. The first build uses the engine's Entry map to avoid adding unverifiable pre-generated binary game assets.

A runner report is uploaded even if package generation fails. A real APK artifact is published only if produced. The initial install must be tested on-device before any claims about graphics or FPS.

## GitHub-hosted runner limitation

The default 14 GB SSD is not assumed sufficient for UE + SDK + cook. The GitHub-hosted preflight purposefully does **not** attempt to download proprietary engine files or pretend Unreal is preinstalled. Results will establish available headroom and SDK availability, not working UE packaging.
