import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))
import runner_probe  # noqa: E402


class LabContractTests(unittest.TestCase):
    def test_project_shell_is_unreal_58(self):
        project = json.loads((ROOT / "SceneForgeUE5Lab.uproject").read_text())
        self.assertEqual(project["EngineAssociation"], "5.8")
        self.assertEqual(project["FileVersion"], 3)

    def test_android_baseline(self):
        ini = (ROOT / "Config" / "DefaultEngine.ini").read_text()
        for line in ["PackageName=com.sceneforge.ue5lab", "TargetSDKVersion=35",
                     "bBuildForArm64=True", "r.MobileHDR=False"]:
            self.assertIn(line, ini)

    def test_probe_has_immutable_expected_version(self):
        self.assertEqual(runner_probe.ENGINE_V, (5, 8))

    def test_no_unreal_binaries_in_repo(self):
        for path in ("Engine", "Binaries", "Intermediate", "Saved"):
            self.assertFalse((ROOT / path).exists(), path)

    def test_workflows_present(self):
        for path in (".github/workflows/preflight.yml",
                     ".github/workflows/android-package.yml"):
            self.assertTrue((ROOT / path).is_file(), path)

    def test_container_packaging_uses_epic_default_user(self):
        # The official engine directory is inaccessible to the GitHub runner
        # identity when forced into the container with docker --user.
        workflow = (ROOT / ".github/workflows/hosted-container.yml").read_text()
        self.assertIn('image_uid=$(docker run --rm --entrypoint /usr/bin/id', workflow)
        self.assertIn('sudo chown -R "$image_uid:$image_gid" "$GITHUB_WORKSPACE"', workflow)
        self.assertNotIn('--user "$(id -u):$(id -g)"', workflow)
        self.assertIn('Restore host ownership for artifact uploader', workflow)


if __name__ == "__main__":
    unittest.main()
