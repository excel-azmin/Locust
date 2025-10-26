from locust import HttpUser, task, between, TaskSet
import csv
import random
from datetime import datetime

class RegistrationTasks(TaskSet):
    
    def on_start(self):
        self.client.verify = False
        self.request_counter = 0
        
        # Initialize training_ids with names for better debugging
        self.training_ids = {
            "68fdbd54adeaed890251a76e": "Main Training",
            "68f890dd844d9ad7d2f39925": "Node.js Training 11", 
            "68f890d3844d9ad7d2f39922": "Node.js Training 10",
            "68f890ca844d9ad7d2f3991f": "Node.js Training 09",
            "68f890c0844d9ad7d2f3991c": "Node.js Training 08",
            "68f88a48cbb8b656f316020b": "Node.js Training 04"
        }
        self._load_user_data()
    
    def _load_user_data(self):
        """Load user data and assign to this user"""
        try:
            with open('registration.csv', 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                all_users = list(reader)
            
            # Skip header row if it exists
            if all_users and len(all_users[0]) == 4 and all_users[0][0] == 'email':
                all_users = all_users[1:]  # Remove header row
            
            if all_users and len(all_users[0]) >= 4:
                user_data = random.choice(all_users)
                self.user_email = user_data[0].strip()
                self.user_company = user_data[1].strip()
                self.user_name = user_data[2].strip()
                self.user_phone = user_data[3].strip()
                
                print(f"👤 User assigned: {self.user_email}")
            else:
                print("❌ No valid users found in CSV file")
                self.user_email = None
                
        except FileNotFoundError:
            print("❌ registration.csv file not found!")
            self.user_email = None
        except Exception as e:
            print(f"❌ Error loading user data: {e}")
            self.user_email = None
    
    @task(3)
    def register_main_training(self):
        """Register for main training (most frequent)"""
        self._register_for_training("68fdbd54adeaed890251a76e", "MainTraining")
    
    @task(2)
    def register_alternative_training(self):
        """Register for alternative trainings"""
        # Exclude the main training ID from alternatives
        alternative_ids = list(self.training_ids.keys())[1:]
        training_id = random.choice(alternative_ids)
        training_name = self.training_ids[training_id]
        self._register_for_training(training_id, f"AltTraining-{training_name}")
    
    @task(1)
    def register_random_training(self):
        """Register for any random training"""
        training_id = random.choice(list(self.training_ids.keys()))
        training_name = self.training_ids[training_id]
        self._register_for_training(training_id, f"RandomTraining-{training_name}")
    
    def _register_for_training(self, training_id, name_prefix):
        """Helper method to register for a specific training"""
        if not hasattr(self, 'user_email') or not self.user_email:
            print("⚠️ No user data available for registration")
            return
        
        self.request_counter += 1
        training_name = self.training_ids.get(training_id, "Unknown Training")
        
        registration_data = {
            "fullName": self.user_name,
            "email": f"test{self.request_counter}_{self.user_email}",  # Make email unique
            "contactNumber": self.user_phone,
            "companyName": self.user_company,
            "designation": "Software Engineer",
            "lastEducation": "BSc in Computer Science",
            "training": training_id
        }
        
        print(f"📤 [{self.request_counter}] Registering {registration_data['email']} for {training_name}")
        
        with self.client.post(
            "/api/v1/training-registration",
            json=registration_data,
            name=name_prefix,
            catch_response=True,
            timeout=30
        ) as response:
            
            if response.status_code == 201:
                try:
                    response_data = response.json()
                    if response_data.get('statusCode') == 201:
                        reg_id = response_data.get('response', {}).get('_id', 'Unknown')
                        print(f"✅ [{self.request_counter}] SUCCESS: {registration_data['email']} -> {training_name} (ID: {reg_id})")
                        response.success()
                    else:
                        error_msg = response_data.get('message', 'Registration failed')
                        print(f"❌ [{self.request_counter}] API ERROR: {registration_data['email']} -> {training_name}: {error_msg}")
                        response.failure(f"API Error: {error_msg}")
                        
                except Exception as e:
                    print(f"❌ [{self.request_counter}] JSON ERROR: {registration_data['email']} -> {training_name}: {str(e)}")
                    print(f"   Response text: {response.text[:200]}...")
                    response.failure("Invalid JSON response")
                    
            elif response.status_code == 400:
                error_msg = "Bad Request - Possibly duplicate email or invalid data"
                print(f"❌ [{self.request_counter}] 400 ERROR: {registration_data['email']} -> {training_name}: {error_msg}")
                response.failure(error_msg)
                
            elif response.status_code == 409:
                error_msg = "Conflict - User already registered for this training"
                print(f"❌ [{self.request_counter}] 409 ERROR: {registration_data['email']} -> {training_name}: {error_msg}")
                response.failure(error_msg)
                
            elif response.status_code == 422:
                error_msg = "Validation Error - Check request data"
                print(f"❌ [{self.request_counter}] 422 ERROR: {registration_data['email']} -> {training_name}: {error_msg}")
                response.failure(error_msg)
                
            else:
                print(f"❌ [{self.request_counter}] HTTP {response.status_code}: {registration_data['email']} -> {training_name}")
                print(f"   Response: {response.text[:200]}...")
                response.failure(f"HTTP {response.status_code}")

class TrainingRegistrationUser(HttpUser):
    tasks = [RegistrationTasks]
    wait_time = between(2, 5)  # Increased wait time to avoid rate limiting