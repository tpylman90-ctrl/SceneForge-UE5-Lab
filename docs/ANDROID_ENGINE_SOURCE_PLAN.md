# UE5 Android-capable engine acquisition

## Established failure

The official Epic `ghcr.io/epicgames/unreal-engine:dev-slim-5.8.0` image is a Linux Installed Build, not a verified Android Installed Build. Our [Android build test](https://github.com/tpylman90-ctrl/SceneForge-UE5-Lab/actions/runs/42325569107) completed the cook with zero content errors but could not stage: `GetBuildPlatform: No BuildPlatform found for Android`.

Our [component inspection](https://github.com/tpylman90-ctrl/SceneForge-UE5-Lab/actions/runs/42327957593) reported no `Android.Automation.dll` and no checked Android runtime directory in this container. That is a blocker for this engine installation, *not* evidence that Unreal cannot target Android.

## Candidate: Epic source → Android-enabled Installed Build

Epic's [installed-build documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/installed-build-reference-guide-for-unreal-engine) supports an Android build via the BuildGraph switch `-set:WithAndroid=true`. That **configures** target-platform inclusion; it does not add Android to an already compiled container.

Proposed gated plan:

1. Check whether the existing Epic-linked GitHub Actions token can access `EpicGames/UnrealEngine` using only an API status request. Never log the token or private repository data. A green diagnostic workflow means **the check ran**, not that source access passed.
2. Only after access is confirmed, assess whether GitHub's standard public runner (4 cores, 16 GB RAM, limited storage despite our larger measured free-root-space) can accommodate a trimmed UE 5.8 source checkout, dependencies and platform binaries. Stop before a large download unless capacity is grounded.
3. If feasible, compile an Android-capable installed build with explicit `WithAndroid=true`, avoiding unrelated platforms and debug symbols. **Do not upload or commit Epic source/engine binaries to the public repository.** Store output only in license-compliant protected locations, or rebuild in the job.
4. Verify `Android.Automation.dll` **and** target runtime/receipts before cooking; then run `BuildCookRun`, upload only our resulting APK and nonproprietary diagnostic reports.
5. Install the APK on the Android review phone and measure frame rate before considering any migration.

## Other possible path

Epic's Linux [precompiled installed build](https://dev.epicgames.com/documentation/unreal-engine/linux-development-quickstart-for-unreal-engine) might have different platform components, but its actual content and unattended download availability are unverified. Do not assume it includes Android.

The [official development container overview](https://dev.epicgames.com/documentation/unreal-engine/overview-of-containers-in-unreal-engine) describes the full `dev` image as a Linux Installed Build with symbols and templates; there is **no evidence** that switching to the much larger `dev` image includes Android support. Do not incur that download without evidence.

## Limits / security

- Android SDK/NDK are installed successfully in prior runs; reinstalling them will not restore missing Unreal Android platform modules.
- GitHub app permissions and a GitHub PAT are separate; a token with package access may lack private source-repository permission.
- Public GitHub Actions runs are free, but they are not persistent. Do not upload proprietary engine files, credentials or private Unreal code as artifacts.
- Keep the production Godot SceneForge repo untouched. Do not claim an APK until the packaging artifact exists.
