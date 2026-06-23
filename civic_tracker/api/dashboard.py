import frappe


@frappe.whitelist()
def get_dashboard_stats():
    """Get statistics for the executive dashboard."""
    stats = {}

    # Total issues by status
    status_data = frappe.db.sql(
        """
        SELECT status, COUNT(*) as count
        FROM `tabCivic Issue`
        WHERE docstatus = 1
        GROUP BY status
        """,
        as_dict=True,
    )
    stats["by_status"] = status_data

    # Issues by type
    type_data = frappe.db.sql(
        """
        SELECT issue_type, COUNT(*) as count
        FROM `tabCivic Issue`
        WHERE docstatus = 1
        GROUP BY issue_type
        """,
        as_dict=True,
    )
    stats["by_type"] = type_data

    # Issues by ward
    ward_data = frappe.db.sql(
        """
        SELECT ward, COUNT(*) as count
        FROM `tabCivic Issue`
        WHERE docstatus = 1
        GROUP BY ward
        ORDER BY count DESC
        LIMIT 20
        """,
        as_dict=True,
    )
    stats["by_ward"] = ward_data

    # Issues by contractor
    contractor_data = frappe.db.sql(
        """
        SELECT assigned_contractor, COUNT(*) as count
        FROM `tabCivic Issue`
        WHERE docstatus = 1 AND assigned_contractor IS NOT NULL
        GROUP BY assigned_contractor
        ORDER BY count DESC
        LIMIT 20
        """,
        as_dict=True,
    )
    stats["by_contractor"] = contractor_data

    # Summary counts
    stats["total_open"] = frappe.db.count("Civic Issue", {"status": "Open", "docstatus": 1})
    stats["total_assigned"] = frappe.db.count("Civic Issue", {"status": "Assigned", "docstatus": 1})
    stats["total_in_progress"] = frappe.db.count("Civic Issue", {"status": "In Progress", "docstatus": 1})
    stats["total_overdue"] = frappe.db.count("Civic Issue", {"status": "Overdue", "docstatus": 1})
    stats["total_resolved"] = frappe.db.count("Civic Issue", {"status": "Resolved", "docstatus": 1})
    stats["total_closed"] = frappe.db.count("Civic Issue", {"status": "Closed", "docstatus": 1})
    stats["total_issues"] = stats["total_open"] + stats["total_assigned"] + stats["total_in_progress"] + stats["total_overdue"] + stats["total_resolved"] + stats["total_closed"]

    return stats
