import frappe
from frappe.utils import nowdate, getdate

def check_overdue_issues():
    """ Day 10: SLA Engine (Daily Scheduler) """
    # Get all Open/In Progress issues that missed SLA
    overdue_issues = frappe.get_all("Civic Issue", filters={
        "status": ["in", ["Open", "Assigned", "In Progress"]],
        "sla_deadline": ["<", nowdate()]
    }, fields=["name", "assigned_contractor", "issue_type"])
    
    for issue in overdue_issues:
        frappe.db.set_value("Civic Issue", issue.name, "status", "Overdue")
        
        # Generate Contractor Penalty
        penalty = frappe.get_doc({
            "doctype": "Contractor Penalty",
            "contractor": issue.assigned_contractor,
            "issue": issue.name,
            "penalty_amount": 500, # Fixed penalty for demonstration
            "status": "Unpaid"
        })
        penalty.insert(ignore_permissions=True)

def check_unpaid_penalties():
    """ Day 10: Check Unpaid Penalties """
    # Logic to trigger reminders or deduct from ERPNext
    pass
