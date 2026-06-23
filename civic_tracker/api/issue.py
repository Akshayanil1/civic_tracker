import frappe
from frappe.utils import cint


@frappe.whitelist()
def get_issue_by_tracking_id(tracking_id):
    """API to fetch issue details by tracking ID for citizen portal."""
    if not tracking_id:
        frappe.throw("Tracking ID is required.")

    issue = frappe.db.get_value(
        "Civic Issue",
        {"tracking_id": tracking_id},
        [
            "name", "issue_title", "tracking_id", "issue_type", "status",
            "priority", "issue_date", "due_date", "resolution_date",
            "resolution_notes", "ward", "assigned_contractor",
            "description", "citizen_name", "citizen_email",
        ],
        as_dict=True,
    )

    if not issue:
        frappe.throw("No issue found with this Tracking ID.")

    # Get ward details
    if issue.ward:
        ward_info = frappe.db.get_value(
            "Municipal Ward", issue.ward,
            ["ward_name", "commissioner_name"],
            as_dict=True,
        )
        issue.ward_name = ward_info.ward_name if ward_info else issue.ward

    # Get contractor details
    if issue.assigned_contractor:
        contractor_info = frappe.db.get_value(
            "Civic Contractor", issue.assigned_contractor,
            ["contractor_name", "company_name"],
            as_dict=True,
        )
        issue.contractor_name = contractor_info.contractor_name if contractor_info else ""
        issue.contractor_company = contractor_info.company_name if contractor_info else ""

    # Build status timeline
    issue.status_history = get_status_history(issue.name)

    return issue


def get_status_history(issue_name):
    """Get status change history for an issue."""
    return []


@frappe.whitelist()
def submit_civic_issue(
    issue_title, issue_type, description, ward,
    citizen_name=None, citizen_email=None, citizen_phone=None,
    latitude=None, longitude=None, address_text=None,
    issue_image=None, priority="Medium", is_anonymous=0,
):
    """Public API to submit a new civic issue from the web portal."""
    issue = frappe.get_doc({
        "doctype": "Civic Issue",
        "issue_title": issue_title,
        "issue_type": issue_type,
        "description": description,
        "ward": ward,
        "citizen_name": citizen_name,
        "citizen_email": citizen_email,
        "citizen_phone": citizen_phone,
        "latitude": latitude,
        "longitude": longitude,
        "address_text": address_text,
        "issue_image": issue_image,
        "priority": priority,
        "is_anonymous": cint(is_anonymous),
        "status": "Open",
    })
    issue.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "name": issue.name,
        "tracking_id": issue.tracking_id,
        "status": issue.status,
        "message": "Issue reported successfully!",
    }
