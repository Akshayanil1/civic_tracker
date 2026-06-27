import frappe
from frappe.utils import now_datetime

@frappe.whitelist(allow_guest=True)
def get_ward_proposals(ward=None):
    """Fetch proposals open for voting."""
    filters = {"status": "Open for Voting"}
    if ward:
        filters["ward"] = ward
        
    proposals = frappe.get_all(
        "Civic Proposal",
        filters=filters,
        fields=["name", "title", "description", "estimated_budget", "ward", "total_votes"],
        order_by="total_votes desc"
    )
    return proposals

@frappe.whitelist()
def cast_vote(proposal_name, ward):
    """Cast a vote. Requires authenticated user."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You must be logged in to vote.")
        
    # Check if already voted for this proposal
    existing_vote = frappe.db.exists("Citizen Vote", {
        "proposal": proposal_name,
        "citizen_email": user
    })
    
    if existing_vote:
        frappe.throw("You have already voted for this proposal.")
        
    vote = frappe.get_doc({
        "doctype": "Citizen Vote",
        "proposal": proposal_name,
        "citizen_email": user,
        "ward": ward,
        "vote_timestamp": now_datetime()
    })
    vote.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "success", "message": "Vote cast successfully!"}
