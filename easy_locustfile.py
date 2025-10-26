from locust import HttpUser, task, between
import json
import os

class TrainingAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Disable SSL verification
        self.client.verify = False
    
    @task(1)
    def get_training_list(self):
        """Test the training list API endpoint"""
        params = {
            'page': 1,
            'limit': 6,
            'fromDate': '2025-10-26',
            'toDate': '2026-02-26',
            'dateField': 'startDateTime',
            'select': '_id,title,startDateTime,endDateTime,trainerName,trainerDesignation,trainingVenue,lastRegistrationDateTime'
        }
        
        with self.client.get(
            "/api/v1/training/list-for-user",
            params=params,
            name="GetTrainingList",
            catch_response=True
        ) as response:
            
            if response.status_code == 200:
                response.success()
                print("Response JSON:", json.dumps(response.json(), indent=2))
            elif response.status_code == 0:
                response.failure("Connection failed - SSL or network issue")
            else:
                response.failure(f"HTTP {response.status_code}")