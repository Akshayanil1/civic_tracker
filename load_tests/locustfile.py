from locust import HttpUser, task, between
import random
import json

class CivicCitizenUser(HttpUser):
    """
    Day 58: Enterprise Load Testing (Monsoon Crisis Simulation)
    Simulates thousands of concurrent citizens reporting flooded streets and potholes.
    Run this with: `locust -f locustfile.py --host=https://your-frappe-instance.local`
    """
    wait_time = between(1, 5)
    
    @task(3)
    def report_issue(self):
        issue_types = ["Road", "Water", "Sanitation", "Electricity", "Drainage", "Garbage"]
        priorities = ["High", "Critical", "Medium"]
        
        payload = {
            "issue_title": "Severe flooding and pothole after monsoon",
            "issue_type": random.choice(issue_types),
            "priority": random.choice(priorities),
            "description": "The entire street is flooded and there is a massive pothole causing accidents. Please help immediately!",
            "ward": "Ward 4",
            "latitude": 13.0827 + random.uniform(-0.01, 0.01),
            "longitude": 80.2707 + random.uniform(-0.01, 0.01),
            "citizen_name": "Test User",
            "citizen_phone": "9999999999",
            "source_channel": "Web Portal"
        }
        
        # Simulating hitting the native Frappe REST API to create a document
        # Or you can hit the custom webhook endpoint
        self.client.post("/api/resource/Civic Issue", json=payload, headers={
            # In a real test, you'd use a token or test against a public webhook that allows guest reporting
            "Content-Type": "application/json"
        })

    @task(1)
    def check_open_data(self):
        """Simulate data scientists fetching the open data dashboard during the crisis."""
        self.client.get("/api/method/civic_tracker.api.public.get_open_data?limit=100")
