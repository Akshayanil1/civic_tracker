import frappe

def generate_journal_entry(doc, method=None):
    """ Day 9: Automated Journal Entries upon ticket closure """
    if doc.status == "Closed":
        repair_cost = frappe.get_value("Standard Repair Cost", doc.issue_type, "rate")
        # Logic to generate ERPNext Journal Entry debiting Ward, crediting Contractor
        pass
