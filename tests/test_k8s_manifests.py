import unittest
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
K8S_DIR = BASE_DIR / "k8s"

class TestKubernetesManifests(unittest.TestCase):
    """
    Automated validation suite for Phase 4 Kubernetes Manifests:
    - Syntax & Schema Validation (YAML)
    - Resource Specifications (Deployments, Services, ConfigMaps, Secrets, PVCs)
    - Health Probes (Liveness & Readiness)
    - High-Availability Replica Configurations
    """

    def test_01_configmap_structure(self):
        file_path = K8S_DIR / "configmap.yaml"
        self.assertTrue(file_path.exists())
        with open(file_path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)

        self.assertEqual(doc["kind"], "ConfigMap")
        self.assertEqual(doc["metadata"]["name"], "assistant-config")
        self.assertIn("API_PORT", doc["data"])
        self.assertIn("BACKEND_URL", doc["data"])
        print("\n[K8s Test 1/7] configmap.yaml validated.")

    def test_02_secrets_structure(self):
        file_path = K8S_DIR / "secrets.yaml"
        self.assertTrue(file_path.exists())
        with open(file_path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)

        self.assertEqual(doc["kind"], "Secret")
        self.assertEqual(doc["metadata"]["name"], "assistant-secrets")
        self.assertIn("GEMINI_API_KEY", doc.get("stringData", {}))
        print("[K8s Test 2/7] secrets.yaml validated.")

    def test_03_pvc_storage_claims(self):
        file_path = K8S_DIR / "pvc.yaml"
        self.assertTrue(file_path.exists())
        with open(file_path, "r", encoding="utf-8") as f:
            docs = list(yaml.safe_load_all(f))

        self.assertEqual(len(docs), 2, "Expected 2 PVC definitions (uploads & chroma)")
        names = [d["metadata"]["name"] for d in docs]
        self.assertIn("pdf-storage-pvc", names)
        self.assertIn("chroma-storage-pvc", names)
        print("[K8s Test 3/7] pvc.yaml persistent storage claims validated.")

    def test_04_backend_deployment_and_probes(self):
        file_path = K8S_DIR / "backend-deployment.yaml"
        self.assertTrue(file_path.exists())
        with open(file_path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)

        self.assertEqual(doc["kind"], "Deployment")
        self.assertEqual(doc["spec"]["replicas"], 2, "High Availability requires at least 2 replicas")

        container = doc["spec"]["template"]["spec"]["containers"][0]
        self.assertEqual(container["ports"][0]["containerPort"], 8000)

        # Verify Probes
        self.assertIn("livenessProbe", container)
        self.assertEqual(container["livenessProbe"]["httpGet"]["path"], "/health")
        self.assertIn("readinessProbe", container)
        self.assertEqual(container["readinessProbe"]["httpGet"]["path"], "/health")

        # Verify Volume Mounts
        mount_paths = [m["mountPath"] for m in container["volumeMounts"]]
        self.assertIn("/app/data/uploads", mount_paths)
        self.assertIn("/app/chroma_db", mount_paths)
        print("[K8s Test 4/7] backend-deployment.yaml replicas, probes & volumes validated.")

    def test_05_backend_service(self):
        file_path = K8S_DIR / "backend-service.yaml"
        self.assertTrue(file_path.exists())
        with open(file_path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)

        self.assertEqual(doc["kind"], "Service")
        self.assertEqual(doc["spec"]["type"], "ClusterIP")
        self.assertEqual(doc["spec"]["ports"][0]["port"], 8000)
        print("[K8s Test 5/7] backend-service.yaml ClusterIP routing validated.")

    def test_06_frontend_deployment_and_service(self):
        dep_path = K8S_DIR / "frontend-deployment.yaml"
        svc_path = K8S_DIR / "frontend-service.yaml"
        self.assertTrue(dep_path.exists())
        self.assertTrue(svc_path.exists())

        with open(dep_path, "r", encoding="utf-8") as f:
            dep_doc = yaml.safe_load(f)
        with open(svc_path, "r", encoding="utf-8") as f:
            svc_doc = yaml.safe_load(f)

        # Check frontend deployment
        self.assertEqual(dep_doc["spec"]["replicas"], 2)
        container = dep_doc["spec"]["template"]["spec"]["containers"][0]
        self.assertEqual(container["ports"][0]["containerPort"], 8501)
        self.assertEqual(container["livenessProbe"]["httpGet"]["path"], "/_stcore/health")

        # Check frontend service
        self.assertEqual(svc_doc["spec"]["type"], "NodePort")
        self.assertEqual(svc_doc["spec"]["ports"][0]["nodePort"], 30501)
        print("[K8s Test 6/7] frontend-deployment and NodePort service validated.")

    def test_07_kustomization(self):
        file_path = K8S_DIR / "kustomization.yaml"
        self.assertTrue(file_path.exists())
        with open(file_path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)

        self.assertIn("resources", doc)
        self.assertEqual(len(doc["resources"]), 7)
        print("[K8s Test 7/7] kustomization.yaml 1-click bundle validated.")

if __name__ == "__main__":
    unittest.main()

