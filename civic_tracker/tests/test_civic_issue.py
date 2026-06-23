import frappe
import unittest


class TestCivicIssue(unittest.TestCase):
    def setUp(self):
        # Ensure test ward exists
        if not frappe.db.exists("Municipal Ward", "Test Ward 01"):
            ward = frappe.get_doc({
                "doctype": "Municipal Ward",
                "ward_name": "Test Ward 01",
                "ward_code": "TW01",
            })
            ward.insert(ignore_permissions=True)

    def test_issue_creation(self):
        issue = frappe.get_doc({
            "doctype": "Civic Issue",
            "issue_title": "Test Pothole Issue",
            "issue_type": "Road",
            "description": "Large poothole on main road near junction",
            "ward": "Test Ward 01",
            "priority": "High",
            "citizen_name": "Test Citizen",
            "citizen_email": "citizen@test.com",
        })
        issue.insert(ignore_permissions=True)

        self.assertTrue(issue.tracking_id.startswith("CT-"))
        self.assertEqual(issue.status, "Open")
        self.assertIsNotNone(issue.due_date)
        self.assertIsNotNone(issue.escalation_time)

        # Cleanup
        frappe.delete_doc("Civic Issue", issue.name, force=1)
        frappe.db.commit()

    def test_tracking_id_format(self):
        issue = frappe.get_doc({
            "doctype": "Civic Issue",
            "issue_title": "Tracking ID Test",
            "issue_type": "Water",
            "description": "Testing tracking ID generation",
            "ward": "Test Ward 01",
        })
        issue.insert(ignore_permissions=True)

        import re
        self.assertRegex(issue.tracking_id, r"^CT-\d{2}-[A-Z0-9]{6}$")

        # Cleanup
        frappe.delete_doc("Civic Issue", issue.name, force=1)
        frappe.db.commit()

    def tearDown(self):
        frappe.db.sql("DELETE FROM `tabCivic Issue` WHERE issue_title LIKE 'Test%'")
        frappe.db.sql("DELETE FROM `tabCivic Issue` WHERE issue_title = 'Tracking ID Test'")
        frappe.db.commit()
