import unittest
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent

class TestDockerConfiguration(unittest.TestCase):
    """
    Test suite for Phase 3 Docker and Containerization validation:
    1. Dockerfile.backend structure and directives
    2. Dockerfile.frontend structure and directives
    3. docker-compose.yml YAML syntax, services, ports, and volumes
    4. .dockerignore exclusion list
    """

    def test_dockerfile_backend(self):
        backend_dockerfile = BASE_DIR / "Dockerfile.backend"
        self.assertTrue(backend_dockerfile.exists(), "Dockerfile.backend must exist")
        content = backend_dockerfile.read_text(encoding="utf-8")

        self.assertIn("FROM python:3.11-slim", content)
        self.assertIn("EXPOSE 8000", content)
        self.assertIn("HEALTHCHECK", content)
        self.assertIn("uvicorn", content)
        self.assertIn("/app/data/uploads", content)
        self.assertIn("/app/chroma_db", content)
        print("\n[Docker Test 1/4] Dockerfile.backend directives validated successfully.")

    def test_dockerfile_frontend(self):
        frontend_dockerfile = BASE_DIR / "Dockerfile.frontend"
        self.assertTrue(frontend_dockerfile.exists(), "Dockerfile.frontend must exist")
        content = frontend_dockerfile.read_text(encoding="utf-8")

        self.assertIn("FROM python:3.11-slim", content)
        self.assertIn("EXPOSE 8501", content)
        self.assertIn("HEALTHCHECK", content)
        self.assertIn("streamlit", content)
        print("[Docker Test 2/4] Dockerfile.frontend directives validated successfully.")

    def test_docker_compose_syntax(self):
        compose_file = BASE_DIR / "docker-compose.yml"
        self.assertTrue(compose_file.exists(), "docker-compose.yml must exist")
        
        with open(compose_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertIn("services", data)
        self.assertIn("backend", data["services"])
        self.assertIn("frontend", data["services"])

        # Check port mappings
        self.assertIn("8000:8000", data["services"]["backend"]["ports"])
        self.assertIn("8501:8501", data["services"]["frontend"]["ports"])

        # Check volumes
        self.assertIn("volumes", data)
        self.assertIn("pdf_data", data["volumes"])
        self.assertIn("chroma_data", data["volumes"])

        # Check dependency
        self.assertIn("backend", data["services"]["frontend"]["depends_on"])
        print("[Docker Test 3/4] docker-compose.yml services, ports, and volumes validated.")

    def test_dockerignore(self):
        dockerignore = BASE_DIR / ".dockerignore"
        self.assertTrue(dockerignore.exists(), ".dockerignore must exist")
        content = dockerignore.read_text(encoding="utf-8")

        self.assertIn(".venv", content)
        self.assertIn(".git", content)
        self.assertIn("__pycache__", content)
        print("[Docker Test 4/4] .dockerignore rules verified.")

if __name__ == "__main__":
    unittest.main()

