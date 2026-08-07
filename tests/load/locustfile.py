"""
Locust Performance & Concurrency Load Benchmark Suite for LawyerGrid.
Simulates concurrent user load against marketplace search, health checks, and stats.
"""
from locust import HttpUser, task, between

class MarketplaceUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def search_lawyers(self):
        self.client.get("/api/v1/lawyers?practice=property")

    @task(2)
    def fetch_public_stats(self):
        self.client.get("/api/v1/public/stats")

    @task(1)
    def check_health(self):
        self.client.get("/api/v1/health")

    @task(1)
    def fetch_metrics(self):
        self.client.get("/metrics")
