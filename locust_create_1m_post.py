from locust import HttpUser, task, between
import random
import os
import logging

class OptimizedPostUser(HttpUser):
    wait_time = between(0.05, 0.2)  # Random wait 50-200ms to avoid rate limiting
    host = "http://localhost:3001"

    def on_start(self):
        self.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNtaG40NHR2bDAwMDBmdXA5amF4cHVrY3IiLCJpYXQiOjE3NjI0MTQ1ODIsImV4cCI6MTc2MjQzMjU4Mn0.2V8_xf7Qv8Zoc0bRnN3FBaLYju7-0Rp81gBztE1l0UU"
        # Pre-load file content to memory
        with open("dummy.JPG", "rb") as f:
            self.file_content = f.read()

    @task
    def create_post_fast(self):
        content = f"Test post {random.randint(1, 1000000)}"

        files = {
            'content': (None, content),
            'files': ('test.png', self.file_content, 'image/png')
        }

        with self.client.post(
            '/api/v1/post/create',
            headers={'Authorization': f'Bearer {self.token}'},
            files=files,
            name="Create Post Fast",
            catch_response=True
        ) as response:
            if response.status_code == 200 or response.status_code == 201:
                response.success()
            else:
                logging.error(f"Request failed: Status {response.status_code}, Response: {response.text[:200]}")
                response.failure(f"Status {response.status_code}: {response.text[:100]}")