import frappe
import unittest


class TestIssueSLA(unittest.TestCase):
    def test_sla_creation(self):
        sla = frappe.get_doc({
            "doctype": "Issue SLA",
            "sla_name": "Test Road SLA",
            "issue_type": "Road",
            "sla_hours": 48,
            "escalation_hours": 72,
            "is_active": 1,
        })
        sla.insert(ignore_permissions=True)

        self.assertEqual(sla.sla_hours, 48)
        self.assertEqual(sla.escalation_hours, 72)

        # Cleanup
        frappe.delete_doc("Issue SLA", sla.name, force=1)
        frappe.db.commit()

    def test_escalation_must_be_greater_than_sla(self):
        sla = frappe.get_doc({
            "doctype": "Issue SLA",
            "sla_name": "Test Invalid SLA",
            "issue_type": "Sanitation",
            "sla_hours": 72,
            "escalation_hours": 24,
            "is_active": 1,
        })
        with self.assertRaises(frappe.exceptions.ValidationError):
            sla.insert()

    def tearDown(self):
        frappe.db.sql("DELETE FROM `tabIssue SLA` WHERE sla_name LIKE 'Test%'")
        frappe.db.commit()
