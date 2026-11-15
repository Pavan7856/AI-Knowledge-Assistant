import unittest
from pathlib import Path
import json
import yaml
from fastapi.testclient import TestClient

from backend.main import app

BASE_DIR = Path(__file__).resolve().parent.parent
MONITORING_DIR = BASE_DIR / "monitoring"

class TestPhase5Monitoring(unittest.TestCase):
    """
    Automated test suite for Phase 5 Monitoring and Observability:
    1. FastAPI /metrics endpoint outputs standard Prometheus metrics
    2. Prometheus scraping configuration syntax and jobs
    3. Loki centralized log configuration
    4. Grafana Alloy log shipper configuration
    5. Grafana datasources provisioning (Prometheus & Loki)
    6. Grafana JSON Dashboard schema & panels
    7. Docker Compose monitoring services stack
    """

    def test_01_metrics_endpoint_output(self):
        client = TestClient(app)
        response = client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        content = response.text

        # Verify key Prometheus metrics
        self.assertIn("chromadb_chunks_total", content)
        self.assertIn("http_requests_total", content)
        self.assertIn("documents_ingested_total", content)
        self.assertIn("rag_queries_total", content)
        print("\n[Monitoring Test 1/7] FastAPI /metrics Prometheus output verified.")

    def test_02_prometheus_config(self):
        prom_file = MONITORING_DIR / "prometheus" / "prometheus.yml"
        self.assertTrue(prom_file.exists())
        with open(prom_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertIn("scrape_configs", data)
        job_names = [j["job_name"] for j in data["scrape_configs"]]
        self.assertIn("backend-api", job_names)
        self.assertIn("prometheus", job_names)
        print("[Monitoring Test 2/7] prometheus.yml scrape jobs verified.")

    def test_03_loki_config(self):
        loki_file = MONITORING_DIR / "loki" / "loki-config.yml"
        self.assertTrue(loki_file.exists())
        with open(loki_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertEqual(data["server"]["http_listen_port"], 3100)
        self.assertIn("schema_config", data)
        print("[Monitoring Test 3/7] loki-config.yml configuration verified.")

    def test_04_alloy_config(self):
        alloy_file = MONITORING_DIR / "alloy" / "config.alloy"
        self.assertTrue(alloy_file.exists())
        content = alloy_file.read_text(encoding="utf-8")

        self.assertIn("loki.write", content)
        self.assertIn("http://loki:3100/loki/api/v1/push", content)
        print("[Monitoring Test 4/7] config.alloy pipeline verified.")

    def test_05_grafana_datasources(self):
        ds_file = MONITORING_DIR / "grafana" / "provisioning" / "datasources" / "datasources.yml"
        self.assertTrue(ds_file.exists())
        with open(ds_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        ds_names = [d["name"] for d in data.get("datasources", [])]
        self.assertIn("Prometheus", ds_names)
        self.assertIn("Loki", ds_names)
        print("[Monitoring Test 5/7] Grafana datasources provisioning verified.")

    def test_06_grafana_dashboard_json(self):
        dash_file = MONITORING_DIR / "grafana" / "dashboards" / "assistant_dashboard.json"
        self.assertTrue(dash_file.exists())
        with open(dash_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["uid"], "ai-assistant-overview")
        panel_titles = [p.get("title", "") for p in data.get("panels", [])]
        self.assertIn("Active ChromaDB Chunks", panel_titles)
        self.assertIn("HTTP Request Rate (RPS)", panel_titles)
        self.assertIn("P95 API Request Latency", panel_titles)
        self.assertIn("Live Application Logs", panel_titles)
        print("[Monitoring Test 6/7] Grafana assistant_dashboard.json panels validated.")

    def test_07_monitoring_docker_compose(self):
        compose_file = MONITORING_DIR / "docker-compose.monitoring.yml"
        self.assertTrue(compose_file.exists())
        with open(compose_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertIn("services", data)
        services = data["services"]
        self.assertIn("prometheus", services)
        self.assertIn("loki", services)
        self.assertIn("alloy", services)
        self.assertIn("grafana", services)
        print("[Monitoring Test 7/7] docker-compose.monitoring.yml 4-service stack validated.")

if __name__ == "__main__":
    unittest.main()

