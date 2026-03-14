from locust import HttpUser, task, between

class AdventureBookingUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def view_health(self):
        self.client.get("/health", name="Health Check")

    @task(2)
    def view_adventures(self):
        self.client.get("/api/adventures/?limit=10", name="List Adventures")

    @task(1)
    def view_docs(self):
        self.client.get("/docs", name="Swagger API Docs")
