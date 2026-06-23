import frappe
from frappe.utils import now_datetime, add_to_date, get_url, cint


def check_overdue_issues():
    """
    Daily scheduled job to check all open issues.
    If current time exceeds the Escalation Time, change status to 'Overdue'
    and send escalation notifications.
    """
    now = now_datetime()

    # Find all open/assigned/in-progress issues that are past their escalation time
    issues = frappe.get_all(
        "Civic Issue",
        filters={
            "status": ["in", ["Open", "Assigned", "In Progress"]],
            "escalation_time": ["<", now],
            "docstatus": 1,
        },
        fields=["name", "issue_type", "ward", "assigned_contractor", "tracking_id",
                "issue_title", "escalation_time", "citizen_email", "citizen_name"],
    )

    for issue in issues:
        try:
            escalate_issue(issue)
        except Exception as e:
            frappe.log_error(
                f"Error escalating issue {issue.name}: {str(e)}",
                "Civic Tracker SLA Escalation",
            )


def escalate_issue(issue):
    """Escalate a single overdue issue."""
    now = now_datetime()

    # Update status to Overdue
    frappe.db.set_value("Civic Issue", issue.name, "status", "Overdue")

    # Get SLA configuration for this issue type
    sla = frappe.db.get_value(
        "Issue SLA",
        {"issue_type": issue.issue_type, "is_active": 1},
        ["sla_hours", "ward_commissioner_email", "district_magistrate_email"],
        as_dict=True,
    )

    if not sla:
        return

    # Determine escalation level based on time past due
    hours_overdue = (now - issue.escalation_time).total_seconds() / 3600

    escalation_level = 1
    escalate_to_email = sla.ward_commissioner_email
    escalation_type = "SLA Breach"

    if hours_overdue > 24 and sla.district_magistrate_email:
        escalation_level = 2
        escalate_to_email = sla.district_magistrate_email
        escalation_type = "Ward Commissioner"

    if hours_overdue > 48 and sla.district_magistrate_email:
        escalation_level = 3
        escalate_to_email = sla.district_magistrate_email
        escalation_type = "District Magistrate"

    # Log escalation
    escalation_log = frappe.get_doc({
        "doctype": "Issue Escalation Log",
        "parent": issue.name,
        "parenttype": "Civic Issue",
        "parentfield": "escalation_log",
        "escalation_level": escalation_level,
        "escalated_to": escalate_to_email or "System Admin",
        "escalation_type": escalation_type,
        "escalation_date": now,
        "notification_sent": 0,
    })

    # Send escalation email
    if escalate_to_email:
        tracking_url = get_url(f"/track-issue/{issue.tracking_id}")
        frappe.sendmail(
            recipients=[escalate_to_email],
            subject=f"[ESCALATION] Civic Issue Overdue: {issue.tracking_id}",
            message=f"""
            <h2>Civic Issue Escalation Alert</h2>
            <p><strong>Issue:</strong> {issue.issue_title}</p>
            <p><strong>Tracking ID:</strong> <a href="{tracking_url}">{issue.tracking_id}</a></p>
            <p><strong>Type:</strong> {issue.issue_type}</p>
            <p><strong>Ward:</strong> {issue.ward}</p>
            <p><strong>Assigned Contractor:</strong> {issue.assigned_contractor or 'Not Assigned'}</p>
            <p><strong>Escalation Level:</strong> {escalation_level} - {escalation_type}</p>
            <p><strong>Hours Overdue:</strong> {hours_overdue:.1f}</p>
            <p>This issue has exceeded its SLA deadline and requires immediate attention.</p>
            """,
        )
        escalation_log.notification_sent = 1

    # Save the escalation log entry
    frappe.get_doc({
        "doctype": "Civic Issue",
        "name": issue.name,
    }).run_method("add_escalation_log", escalation_log)

    frappe.db.commit()


def on_civic_issue_update(doc, method):
    """Hook: called when a Civic Issue is updated."""
    # Auto-assign contractor if not assigned
    if doc.status == "Open" and not doc.assigned_contractor:
        auto_assign_contractor(doc)


def auto_assign_contractor(issue):
    """
    Automatically assign a contractor based on ward and issue type.
    Looks for active contractors assigned to the ward who handle this service type.
    """
    contractors = frappe.db.sql(
        """
        SELECT DISTINCT cc.name, cc.contractor_name
        FROM `tabCivic Contractor` cc
        INNER JOIN `tabContractor Ward Assignment` cwa ON cwa.parent = cc.name
        INNER JOIN `tabContractor Service Type` cst ON cst.parent = cc.name
        WHERE cc.status = 'Active'
        AND cwa.ward = %s
        AND cst.service_type = %s
        ORDER BY cc.name
        LIMIT 1
        """,
        (issue.ward, issue.issue_type),
        as_dict=True,
    )

    if contractors:
        frappe.db.set_value(
            "Civic Issue", issue.name, "assigned_contractor", contractors[0].name
        )
        frappe.db.set_value("Civic Issue", issue.name, "status", "Assigned")
        frappe.db.commit()
