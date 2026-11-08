# SceneForge UE5.8: staged BuildGraph and UET

## Integrated workflow

- [.github/workflows/ue-buildgraph-staged.yml](../.github/workflows/ue-buildgraph-staged.yml) is a new **manual only** GitHub Action, isolated from ongoing full-source hosted runner attempts.
- For graph listing it uses the MIT-licensed [heucuva/unreal-buildgraph-action](https://github.com/heucuva/unreal-buildgraph-action) pinned to commit cb990a03268dc20817c2b5b396a4f553eebd6228.
- For compilation, scripts/ci/staged_buildgraph.ps1 calls Epic's BuildGraph privately using -Export, -SingleNode, -SharedStorageDir, -WriteToSharedStorage, and -Resume. This retains private logs rather than printing them into a public GitHub Actions run.

## Required before executing the new workflow

This workflow needs a *trusted, persistent Windows self-hosted runner* labeled [self-hosted, Windows, X64, ue5-android] with an **authorized Unreal Engine 5.8 source checkout**, completed Setup.bat, Visual Studio build tools, and Android JDK/SDK/NDK. There is **no confirmed such runner yet**. GitHub-hosted ephemeral runners discard source/intermediates between jobs; they cannot complete this multi-run strategy without a separate secure private build-product store.

Prepare a private Windows volume with restrictive permissions, never public GitHub artifacts/cache. Set GitHub Actions **repository variables** SCENEFORGE_UE58_ROOT (local source checkout) and SCENEFORGE_UE58_PRIVATE_STORAGE (persistent PRIVATE shared directory). These are paths, NOT access tokens. Do not run a public PR on a trusted self-hosted build runner.

## Stages

1. **list**: community Action lists BuildGraph nodes (public CI logs may show BuildGraph node names; it never uploads source).
2. **export**: exports a private graph JSON and matching source/config fingerprint. Use a fresh private store per engine revision.
3. **node**: execute one node from the graph via -SingleNode, in dependency order. Build outputs persist privately for subsequent runs.
4. **resume**: on the same persistent checkout, attempt to continue remaining work with -Resume. It is not a cross-host scheduler.

Only one build stage runs at a time, protected by GitHub concurrency. For a multi-machine farm, an additional scheduler must read the private exported JSON graph and assign dependency-ready nodes to eligible machines; the graph/action alone do not do that.

There are disk and per-stage time safeguards. Raw Unreal source, binaries, intermediates, graphs and logs must never be published to this public repository or GitHub Actions artifacts/caches.

## UET for Android packaging

Redpoint Games' MIT-licensed [UET](https://github.com/RedpointGames/uet) supports project builds for Android once the engine is usable:

    uet build --platform Android

We have **not installed or executed UET** in CI; this is the intended project-packaging handoff after an Android-capable engine compiles. The lab's SceneForgeUE5Lab.uproject remains a minimal test shell. A completed engine build is not yet an APK.

The existing monolithic UE5.8 Windows+Android source compilation workflow remains unchanged and in progress at the time of this integration.
