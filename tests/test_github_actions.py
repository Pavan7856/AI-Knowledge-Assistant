import unittest
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
WORKFLOW_FILE = BASE_DIR / ".github" / "workflows" / "ci-cd.yml"

class TestGitHubActionsWorkflow(unittest.TestCase):
    """
    Automated validation suite for Phase 6 CI/CD Pipeline:
    1. Workflow file existence and YAML syntax
    2. Branch triggers (main, master)
    3. CI Testing Stage configuration
    4. Container Build Stage configuration
    5. Kubernetes Dry-Run Validation Stage configuration
    """

    def test_01_workflow_file_exists_and_parses(self):
        self.assertTrue(WORKFLOW_FILE.exists(), "ci-cd.yml must exist in .github/workflows/")
        with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
            workflow = yaml.safe_load(f)

        self.assertIn("name", workflow)
        self.assertTrue("on" in workflow or True in workflow, "Workflow must define triggers")
        self.assertIn("jobs", workflow)
        print("\n[CI/CD Test 1/5] ci-cd.yml syntax and structure verified.")

    def test_02_triggers_and_branches(self):
        with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
            workflow = yaml.safe_load(f)

        triggers = workflow.get("on") or workflow.get(True, {})
        self.assertTrue("push" in triggers or "pull_request" in triggers)
        push_branches = triggers.get("push", {}).get("branches", [])
        self.assertTrue("main" in push_branches or "master" in push_branches)
        print("[CI/CD Test 2/5] Git triggers (push, pull_request) verified.")

    def test_03_test_stage_configuration(self):
        with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
            workflow = yaml.safe_load(f)

        jobs = workflow.get("jobs", {})
        self.assertIn("unit-and-integration-tests", jobs)
        test_job = jobs["unit-and-integration-tests"]
        self.assertEqual(test_job["runs-on"], "ubuntu-latest")

        # Find the test execution step
        steps = test_job.get("steps", [])
        run_commands = [s.get("run", "") for s in steps]
        has_test_cmd = any("unittest discover" in cmd for cmd in run_commands)
        self.assertTrue(has_test_cmd, "Test stage must execute unittest discovery")
        print("[CI/CD Test 3/5] CI unit-and-integration-tests stage verified.")

    def test_04_docker_build_stage(self):
        with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
            workflow = yaml.safe_load(f)

        jobs = workflow.get("jobs", {})
        self.assertIn("docker-build-validation", jobs)
        docker_job = jobs["docker-build-validation"]
        self.assertEqual(docker_job["needs"], "unit-and-integration-tests")

        # Verify steps build backend and frontend
        steps = docker_job.get("steps", [])
        with_blocks = [s.get("with", {}) for s in steps]
        files = [w.get("file", "") for w in with_blocks]
        self.assertTrue(any("Dockerfile.backend" in f for f in files))
        self.assertTrue(any("Dockerfile.frontend" in f for f in files))
        print("[CI/CD Test 4/5] Container build and verification stage verified.")

    def test_05_kubernetes_validation_stage(self):
        with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
            workflow = yaml.safe_load(f)

        jobs = workflow.get("jobs", {})
        self.assertIn("k8s-manifest-validation", jobs)
        k8s_job = jobs["k8s-manifest-validation"]
        self.assertEqual(k8s_job["needs"], "unit-and-integration-tests")

        steps = k8s_job.get("steps", [])
        run_commands = [s.get("run", "") for s in steps]
        has_k8s_validate = any("kubectl apply --dry-run=client -k k8s/" in cmd for cmd in run_commands)
        self.assertTrue(has_k8s_validate, "K8s stage must run dry-run validation on k8s/ bundle")
        print("[CI/CD Test 5/5] Kubernetes schema dry-run validation stage verified.")

if __name__ == "__main__":
    unittest.main()
