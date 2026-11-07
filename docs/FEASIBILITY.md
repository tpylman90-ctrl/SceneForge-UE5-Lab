# Feasibility gates (no premature success claims)

| Gate | Evidence needed | Current status |
| --- | --- | --- |
| A. GitHub lab scaffold | Workflow, pinned .uproject, source-only repo | Configured, awaiting CI |
| B. Hosted runner sizing | Successful Ubuntu and Windows probes with report artifacts | Awaiting CI |
| C. Free engine provisioning | UE 5.8 legally installed on a runner; enough disk/RAM for cook | **Not established** |
| D. Automated APK | A successful UE BuildCookRun job and downloadable APK artifact | **Not established** |
| E. Android compatibility | Install and launch on the Moto G Play 2026 | **Not established** |
| F. Hover-racer suitability | Drivable craft, track, FPS measurements vs Godot | **Not established** |

## Decision rule

GitHub-hosted runners are currently 16 GiB RAM / 14 GB SSD (public 4-core configurations). An Epic-licensed UE install and build output may exceed this disk. The probe only **measures** this, not bypasses it.

**Do not** report success based on green preflight status. Green preflight means test harness and reporting worked; it is not an Unreal compile or Android package.

When gate C can be satisfied on no-cost infrastructure, run the optional manual packaging workflow. Once D/E/F pass, decide whether an Unreal migration is worthwhile. Until then SceneForge Godot stays authoritative.

## Failure criteria

- Engine download requires credentials and cannot fit within public runner resources.
- UE packaging repeatedly fails due to storage, memory, SDK/NDK mismatch, or run limits.
- Android launch works but device performance is markedly below existing Godot baseline (~60 FPS on Crimson Serpent).

Any unsuccessful branch remains an experiment; do not merge or migrate the Godot game.
