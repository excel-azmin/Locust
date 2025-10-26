from locust import HttpUser, task, between
import json
import csv
import os
from datetime import datetime

class TrainingAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize request counter
        self.request_counter = 0
        # Create CSV file and write header if it doesn't exist
        self.csv_file = "training_api_responses.csv"
        self._init_csv_file()
    
    def _init_csv_file(self):
        """Initialize CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'counter', 
                    'timestamp', 
                    'status_code', 
                    'response_time_ms',
                    'total_trainings',
                    'page',
                    'limit',
                    'has_next_page',
                    'training_titles'
                ])
    
    def _save_to_csv(self, response, response_data):
        """Save response data to CSV"""
        self.request_counter += 1
        
        # Extract data from response
        training_data = response_data.get('response', {})
        trainings = training_data.get('training', [])
        pagination = training_data.get('pagination', {})
        
        # Prepare CSV row
        training_titles = [t.get('title', '') for t in trainings]
        training_titles_str = ' | '.join(training_titles)
        
        csv_row = [
            self.request_counter,
            datetime.now().isoformat(),
            response.status_code,
            response.elapsed.total_seconds() * 1000,  # Convert to milliseconds
            len(trainings),
            pagination.get('page', ''),
            pagination.get('limit', ''),
            pagination.get('hasNext', ''),
            training_titles_str
        ]
        
        # Write to CSV
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(csv_row)
        
        # print(f"✅ Request #{self.request_counter} saved to CSV")
    
    def on_start(self):
        # Disable SSL verification
        self.client.verify = False
        print(f"🚀 Starting performance test - CSV will be saved to: {self.csv_file}")
    
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
                try:
                    response_data = response.json()
                    
                    # Save to CSV
                    self._save_to_csv(response, response_data)
                    
                    # Print summary to console
                    training_count = len(response_data.get('response', {}).get('training', []))
                    # print(f"📊 Request #{self.request_counter}: {training_count} trainings found")
                    
                    response.success()
                    
                except json.JSONDecodeError as e:
                    response.failure(f"JSON decode error: {e}")
            elif response.status_code == 0:
                response.failure("Connection failed - SSL or network issue")
            else:
                response.failure(f"HTTP {response.status_code}")