import frappe
import unittest
from frappe.utils import now_datetime, add_days
from civic_tracker.api.penalty import create_contractor_penalty

class TestCivicIssue(unittest.TestCase):
    def setUp(self):
        # Create a test Ward
        if not frappe.db.exists("Municipal Ward", "Test Ward"):
            frappe.get_doc({
                "doctype": "Municipal Ward",
                "ward_name": "Test Ward",
                "ward_code": "TW-01"
            }).insert()
            
        # Create a test Contractor
        if not frappe.db.exists("Civic Contractor", "Test Contractor"):
            frappe.get_doc({
                "doctype": "Civic Contractor",
                "contractor_name": "Test Contractor"
            }).insert()
            
        # Create a test SLA Policy
        if not frappe.db.exists("SLA Policy", "Test Policy"):
            frappe.get_doc({
                "doctype": "SLA Policy",
                "policy_name": "Test Policy",
                "issue_type": "Road",
                "priority": "High",
                "resolution_time_hours": 24
            }).insert()

    def test_sla_penalty_generation(self):
        # Create issue
        issue = frappe.get_doc({
            "doctype": "Civic Issue",
            "issue_title": "Test Pothole",
            "issue_type": "Road",
            "priority": "High",
            "ward": "Test Ward",
            "description": "Test",
            "citizen_name": "Test User",
            "assigned_contractor": "Test Contractor"
        })
        issue.insert()
        
        # Simulate SLA assignment (mocking hook if necessary)
        issue.escalation_time = add_days(now_datetime(), -2) # 2 days ago
        issue.save()
        
        # Manually trigger penalty creation (mocking SLA breach closure)
        issue.status = "Resolved"
        issue.resolution_date = now_datetime()
        issue.save()
        
        penalty_name = create_contractor_penalty(issue.name)
        
        self.assertTrue(penalty_name is not None)
        
        penalty = frappe.get_doc("Contractor Penalty", penalty_name)
        self.assertEqual(penalty.contractor, "Test Contractor")
        self.assertTrue(penalty.penalty_amount > 0)
        self.assertEqual(penalty.status, "Pending")
