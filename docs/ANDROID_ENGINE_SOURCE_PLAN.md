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

## Verified source entitlement check — November 6–7, 2026

[Source access probe](https://github.com/tpylman90-ctrl/SceneForge-UE5-Lab/actions/runs/42329959235) completed successfully as an HTTP-status diagnostic, but access to `EpicGames/UnrealEngine` returned **404** using our existing `EPIC_GHCR_TOKEN`. This token's successful package-registry access does **not** imply private-repository access.

The probe uses a **separate** fine-grained secret named `EPIC_SOURCE_TOKEN`, with an optional temporary classic PAT secret `EPIC_SOURCE_CLASSIC_TOKEN`. It never falls back to the package-registry token. The workflow checks the fine-grained token first; if that token is pending approval, it tests the classic token. It reports which one worked but never prints token values or repository contents.

To enable further work, verify that your signed-in GitHub account can visit `https://github.com/EpicGames/UnrealEngine`. If it can, create a GitHub personal access token that can **read that repository's contents**, ideally scoped specifically to that repository if GitHub/Epic permits. Some configurations may require a classic PAT's broad `repo` scope, which can access other private repos: understand that risk and use a short expiry. Store the token **only** as the Actions repository secret `EPIC_SOURCE_TOKEN`; never paste it into an issue, log, chat, or project code. The source-access check does not clone, download, or publish Epic code. No token alone guarantees compilation within free runner limits.

Do **not** replace the existing working `EPIC_GHCR_TOKEN`: it continues to authorize Epic's container downloads.

## Temporary classic PAT trial while fine-grained Epic access is pending

Create a **classic** personal access token in GitHub's [Tokens (classic)](https://github.com/settings/tokens/new) page with a 7-day expiration and the `repo` scope, the only classic scope covering private repository reads. This scope is **broad**, potentially reading and writing every accessible private repository; GitHub does not offer a read-only classic `repo` scope. Use only a short-lived token; do not add additional scopes. Epic may independently prohibit classic PAT access. The token may need SSO authorization if the organization requires it.

Save the token as `EPIC_SOURCE_CLASSIC_TOKEN` in the **SceneForge-UE5-Lab** GitHub Actions secrets. Keep the fine-grained `EPIC_SOURCE_TOKEN` pending and stored separately; keep the working `EPIC_GHCR_TOKEN` unchanged. Re-run `epic-source-access.yml` manually or push a trusted change to the workflow file.

The GitHub workflow always tests the fine-grained token *first* and uses the temporary classic token only while the fine-grained token cannot access the source. Once the fine-grained token returns HTTP 200, **revoke the classic token and delete the `EPIC_SOURCE_CLASSIC_TOKEN` repo secret**. Never paste tokens in chat, issues, screenshots or repository files.

An HTTP 200 confirms *source access only*. GitHub runner feasibility and Android-enabled UE engine compilation are separate, unverified gates.
