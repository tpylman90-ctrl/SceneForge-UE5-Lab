# GitHub-only UE5 feasibility: official Epic development container

This is the **preferred no-PC candidate**. Epic officially publishes licensed Unreal Engine development images to GitHub Container Registry. A container pull is a legal alternative to downloading and compiling Unreal Engine from source, **when performed by an authorized Epic licensee**.

References:
- [Epic official Containers Quick Start](https://dev.epicgames.com/documentation/unreal-engine/quick-start-guide-for-using-container-images-in-unreal-engine)
- [Epic's GitHub access instructions](https://www.unrealengine.com/ue-on-github)
- [UE 5.8 Android SDK requirements](https://dev.epicgames.com/documentation/unreal-engine/android-development-requirements-for-unreal-engine)

## Required one-time account setup

1. Create/sign into an Epic Games account, accept the Unreal Engine agreement, and link the **GitHub account with access to the lab** to Epic, including acceptance of the invitation to Epic's GitHub organization.
2. From that licensed GitHub account, create a limited GitHub personal access token with **read:packages** access as Epic specifies. Do **not** post or send that token in chat.
3. Go to this lab's **Settings → Secrets and variables → Actions → New repository secret**, and add it as `EPIC_GHCR_TOKEN`. The workflow uses it only as a masked CI secret for `docker login`.
4. Run **Actions → Official Epic container feasibility (manual)**, first with stage `manifest`. If it passes, choose `pull`; only after a successful pull try `android`.

No credential, Epic source, or engine binary is stored in this public repository or uploaded as an artifact.

## Pinned image

`ghcr.io/epicgames/unreal-engine:dev-slim-5.8.0@sha256:daac02628ea880513e18ccd1364b1cac949d40609b24c040d73872d8214a0c46`

This pinned tag/digest has been reported by third-party developers; **the lab has not authenticated to the registry or confirmed it via a successful pull**. If Epic removes this digest, investigate a newer authorized official UE5.8 image rather than silently using unknown binaries.

## What the stages prove

- `manifest`: authenticated registry access to the pinned official UE image; little download and no build.
- `pull`: disk and network capacity to obtain the real installed UE engine image and locate RunUAT. A successful pull **is not an APK**.
- `android`: install/verify Java 21, API 35, Build-tools 35.0.1 and NDK r27c on the hosted runner; mount them into the official image; run UAT to cook/package an ASTC Development APK from the minimal project; upload APK only if produced.

**Caveats:** Epic's development image is large (some reported 5.8 slim images are tens of gigabytes unpacked). GitHub-hosted runner free space is not guaranteed across machines, and the engine's Android build requirements inside the Linux container have not been verified. The workflow is deliberately a test and can fail at any stage. We do not claim a functioning APK pipeline until the Android stage completes and the APK installs on the phone.

## Secrets safety

Never put the `EPIC_GHCR_TOKEN` into repository files, issues, workflow inputs, screenshots, or logs. The workflow is manual-only, on trusted code from the repository; do not expand it to run untrusted pull requests. GitHub Actions logs are visible publicly on public repositories.

If the official container path fails, the pre-existing manual-only `android-package.yml` provides a provisioned-runner fallback. See [ANDROID_RUNNER.md](ANDROID_RUNNER.md).
