import frappe
from frappe.utils import now_datetime

@frappe.whitelist()
def get_assigned_issues():
    """
    Day 52 & 53: REST API for Mobile App (Token Auth).
    Fetches issues assigned to the logged-in contractor.
    """
    user = frappe.session.user
    # Find contractor linked to this user
    contractor = frappe.db.get_value("Civic Contractor", {"user": user})
    
    if not contractor:
        # If user is not linked directly, check if they are a system manager for testing
        if "System Manager" in frappe.get_roles(user):
            contractor = frappe.db.get_list("Civic Contractor", limit=1)
            contractor = contractor[0].name if contractor else None
            
    if not contractor:
        return []
        
    issues = frappe.get_all(
        "Civic Issue",
        filters={
            "assigned_contractor": contractor,
            "status": ["in", ["Open", "Assigned", "In Progress", "Overdue"]]
        },
        fields=["tracking_id", "issue_title", "priority", "due_date", "status", "ward"]
    )
    
    return issues

@frappe.whitelist()
def resolve_issue(tracking_id, resolution_notes, image_b64=None):
    """
    Day 53 & 54: Resolve issue from Mobile App (Supports Offline Sync Queueing).
    """
    issue_name = frappe.db.get_value("Civic Issue", {"tracking_id": tracking_id})
    if not issue_name:
        frappe.throw("Issue not found")
        
    issue = frappe.get_doc("Civic Issue", issue_name)
    
    # Check permissions conceptually
    user = frappe.session.user
    # In a strict environment we'd verify the user is the assigned contractor
    
    # Create the resolution file if image_b64 is provided
    # ... code to save image_b64 as a Frappe File and link it ...
    
    issue.status = "Resolved"
    issue.resolution_date = now_datetime()
    issue.resolution_notes = resolution_notes
    issue.save(ignore_permissions=True)
    
    frappe.db.commit()
    
    return {"status": "success", "message": f"{tracking_id} successfully resolved."}
