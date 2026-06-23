import frappe
import unittest
from frappe.utils import now_datetime


class TestMunicipalWard(unittest.TestCase):
    def setUp(self):
        if not frappe.db.exists("Municipal Ward", "Test Ward 01"):
            ward = frappe.get_doc({
                "doctype": "Municipal Ward",
                "ward_name": "Test Ward 01",
                "ward_code": "TW01",
                "commissioner_name": "Test Commissioner",
                "commissioner_email": "test@example.com",
                "state": "Test State",
            })
            ward.insert(ignore_permissions=True)

    def test_ward_creation(self):
        ward = frappe.get_doc("Municipal Ward", "Test Ward 01")
        self.assertEqual(ward.ward_name, "Test Ward 01")
        self.assertEqual(ward.ward_code, "TW01")

    def tearDown(self):
        frappe.db.sql("DELETE FROM `tabMunicipal Ward` WHERE name = 'Test Ward 01'")
        frappe.db.commit()
