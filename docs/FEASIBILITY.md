# Feasibility gates (no premature success claims)

| Gate | Evidence needed | Current status |
| --- | --- | --- |
| A. GitHub lab scaffold | Workflow, pinned .uproject, source-only repo | Configured; GitHub Actions #1 succeeded |
| B. Hosted runner sizing | Successful Ubuntu and Windows probes with report artifacts | Confirmed: Ubuntu 85.8 GiB and Windows 147.0 GiB free at probe time |
| C. Free engine provisioning | Official Epic GHCR image pulled on hosted Ubuntu (credentialed) or installed on separate authorized runner | **Blocked: registry denied (runs #5–6); Epic organization entitlement / token scope needs verification** |
| D. Automated APK | A successful UE BuildCookRun job and downloadable APK artifact | **Not established** |
| E. Android compatibility | Install and launch on the Moto G Play 2026 | **Not established** |
| F. Hover-racer suitability | Drivable craft, track, FPS measurements vs Godot | **Not established** |

Official Epic UE 5.8 container route: [EPIC_CONTAINER.md](EPIC_CONTAINER.md). This avoids an immediate self-hosted runner but requires Epic-entitled GitHub container access. The 5.8.0 development image is large and may still exceed available runner resources after Android tooling and cook output.

## Decision rule

GitHub-hosted runners are currently 16 GiB RAM / 14 GB SSD (public 4-core configurations). An Epic-licensed UE install and build output may exceed this disk. The probe only **measures** this, not bypasses it.

**Do not** report success based on green preflight status. Green preflight means test harness and reporting worked; it is not an Unreal compile or Android package.

When gate C can be satisfied on no-cost infrastructure, run the optional manual packaging workflow. Once D/E/F pass, decide whether an Unreal migration is worthwhile. Until then SceneForge Godot stays authoritative.

## Failure criteria

- Engine download requires credentials and cannot fit within public runner resources.
- UE packaging repeatedly fails due to storage, memory, SDK/NDK mismatch, or run limits.
- Android launch works but device performance is markedly below existing Godot baseline (~60 FPS on Crimson Serpent).

Any unsuccessful branch remains an experiment; do not merge or migrate the Godot game.

## Live GHCR access tests — November 6, 2026 (America/Detroit)

- [Run 42321414655](https://github.com/tpylman90-ctrl/SceneForge-UE5-Lab/actions/runs/42321414655): Docker GHCR login succeeded using the stored secret; UE 5.8 digest manifest request returned `denied`.
- [Run 42321489184](https://github.com/tpylman90-ctrl/SceneForge-UE5-Lab/actions/runs/42321489184): repeat using the plain official `dev-slim-5.8.0` tag; login succeeded; manifest still returned `denied`.

No Epic engine downloaded or APK produced. Most likely next checks: confirm Epic Games GitHub organization invitation was **accepted**, the token belongs to that linked GitHub account, and it has `read:packages`. Successful Docker registry login alone does not prove Epic package authorization.

## Update — authenticated engine download completed successfully

[GitHub Actions run 42321825428](https://github.com/tpylman90-ctrl/SceneForge-UE5-Lab/actions/runs/42321825428) completed successfully: official Epic UE 5.8 `dev-slim` container digest `sha256:daac02628ea880513e18ccd1364b1cac949d40609b24c040d73872d8214a0c46` was retrieved, and `RunUAT.sh` and UE build version 5.8 were verified. Unpacked image 57,423,881,405 bytes (57.4 decimal GB). GitHub Ubuntu runner had **32 GiB free after extraction**, measured via `df -h`. No APK was created in that run. An Android SDK + packaging attempt is the next gate; 4-core hosted runner may still run out of RAM, time, or disk.
