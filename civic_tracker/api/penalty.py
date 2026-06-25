import frappe
from frappe.utils import now_datetime, flt, getdate, add_months


@frappe.whitelist()
def create_contractor_penalty(issue_name):
    """Create a Contractor Penalty record for an overdue Civic Issue.
    Called automatically when an issue is closed after its escalation time.
    """
    issue = frappe.get_doc("Civic Issue", issue_name)

    if not issue.assigned_contractor:
        return None

    if not issue.escalation_time:
        return None

    resolution_time = issue.resolution_date or now_datetime()
    escalation_time = issue.escalation_time

    # Calculate hours overdue
    time_diff = (resolution_time - escalation_time).total_seconds()
    if time_diff <= 0:
        return None  # Not overdue

    hours_overdue = time_diff / 3600
    days_overdue = hours_overdue / 24

    # Check if penalty already exists for this issue
    existing = frappe.db.exists(
        "Contractor Penalty",
        {"civic_issue": issue_name, "status": ["not in", ["Waived"]]},
    )
    if existing:
        return existing

    # Default penalty rate: \u20b9500 per day
    penalty_rate = flt(
        frappe.db.get_single_value("Civic Tracker Settings", "default_penalty_rate")
        or 500
    )

    penalty = frappe.get_doc({
        "doctype": "Contractor Penalty",
        "penalty_title": f"SLA Breach: {issue.issue_title[:60]}",
        "contractor": issue.assigned_contractor,
        "civic_issue": issue.name,
        "sla_deadline": escalation_time,
        "resolution_date": resolution_time,
        "hours_overdue": round(hours_overdue, 1),
        "days_overdue": round(days_overdue, 1),
        "penalty_rate_per_day": penalty_rate,
        "penalty_amount": round(days_overdue * penalty_rate, 2),
        "ward": issue.ward,
        "issue_type": issue.issue_type,
        "penalty_date": getdate(),
        "status": "Pending",
        "reason": (
            f"Contractor failed to resolve '{issue.issue_title}' within the SLA deadline. "
            f"Issue was {round(hours_overdue, 1)} hours overdue "
            f"({round(days_overdue, 1)} days)."
        ),
    })
    penalty.insert(ignore_permissions=True)
    frappe.db.commit()

    return penalty.name


def auto_generate_penalty_on_close(doc, method):
    """Hook: Auto-generate penalty when a Civic Issue is closed/resolved after SLA breach.
    Attached to Civic Issue on_update doc_event.
    """
    if doc.status not in ("Resolved", "Closed"):
        return

    if not doc.escalation_time or not doc.assigned_contractor:
        return

    resolution_time = doc.resolution_date or now_datetime()

    # Only generate penalty if resolved after escalation time
    if resolution_time > doc.escalation_time:
        try:
            penalty_name = create_contractor_penalty(doc.name)
            if penalty_name:
                frappe.msgprint(
                    f"\u26a0\ufe0f Contractor Penalty <b>{penalty_name}</b> generated for SLA breach.",
                    alert=True,
                    indicator="orange",
                )
        except Exception as e:
            frappe.log_error(
                f"Auto penalty generation failed for {doc.name}: {str(e)}",
                "Contractor Penalty Auto-Generation",
            )


@frappe.whitelist()
def create_invoice_deduction(penalty_name):
    """Link penalty deduction to a Purchase Invoice (ERPNext integration).
    Checks for unpaid penalties and deducts from the contractor's monthly payout.
    """
    penalty = frappe.get_doc("Contractor Penalty", penalty_name)

    if penalty.status != "Approved":
        frappe.throw("Only approved penalties can be deducted from invoices.")

    if penalty.purchase_invoice:
        frappe.throw(f"Penalty already linked to invoice {penalty.purchase_invoice}")

    # Check if Purchase Invoice doctype exists (ERPNext integration)
    if not frappe.db.exists("DocType", "Purchase Invoice"):
        frappe.throw(
            "ERPNext is not installed. Purchase Invoice doctype not found. "
            "Please install ERPNext for invoice deduction functionality."
        )

    # Find the contractor's supplier record
    contractor = frappe.get_doc("Civic Contractor", penalty.contractor)
    supplier_name = contractor.company_name or contractor.contractor_name

    # Look for existing draft Purchase Invoice for this contractor
    existing_invoice = frappe.db.get_value(
        "Purchase Invoice",
        {
            "supplier_name": supplier_name,
            "docstatus": 0,  # Draft
        },
        "name",
    )

    if existing_invoice:
        # Add deduction item to existing invoice
        pi = frappe.get_doc("Purchase Invoice", existing_invoice)
        pi.append("items", {
            "item_name": f"SLA Penalty Deduction - {penalty.name}",
            "description": penalty.reason,
            "qty": 1,
            "rate": -flt(penalty.penalty_amount),  # Negative for deduction
            "uom": "Nos",
        })
        pi.save(ignore_permissions=True)
        invoice_name = pi.name
    else:
        # Create new deduction note
        invoice_name = f"Deduction pending for {supplier_name}"
        frappe.msgprint(
            f"No draft Purchase Invoice found for {supplier_name}. "
            f"Penalty of \u20b9{penalty.penalty_amount} recorded for future deduction.",
            indicator="yellow",
        )

    # Update penalty record
    penalty.db_set("status", "Deducted")
    penalty.db_set("purchase_invoice", existing_invoice or None)
    frappe.db.commit()

    return invoice_name


@frappe.whitelist()
def get_contractor_penalty_summary(contractor=None):
    """Get summary of penalties for a contractor or all contractors."""
    filters = {}
    if contractor:
        filters["contractor"] = contractor

    penalties = frappe.db.sql(
        """
        SELECT
            contractor,
            COUNT(*) as total_penalties,
            SUM(CASE WHEN status = 'Pending' THEN penalty_amount ELSE 0 END) as pending_amount,
            SUM(CASE WHEN status = 'Approved' THEN penalty_amount ELSE 0 END) as approved_amount,
            SUM(CASE WHEN status = 'Deducted' THEN penalty_amount ELSE 0 END) as deducted_amount,
            SUM(CASE WHEN status = 'Waived' THEN penalty_amount ELSE 0 END) as waived_amount,
            SUM(penalty_amount) as total_amount,
            AVG(days_overdue) as avg_days_overdue
        FROM `tabContractor Penalty`
        {where_clause}
        GROUP BY contractor
        ORDER BY total_amount DESC
        """.format(
            where_clause=f"WHERE contractor = %(contractor)s" if contractor else ""
        ),
        filters,
        as_dict=True,
    )

    return penalties


def check_unpaid_penalties():
    """Scheduled job: Check for unpaid penalties and send reminders.
    Runs daily to flag contractors with accumulated unpaid penalties.
    """
    pending_penalties = frappe.db.sql(
        """
        SELECT contractor, COUNT(*) as count,
               SUM(penalty_amount) as total_pending
        FROM `tabContractor Penalty`
        WHERE status IN ('Pending', 'Approved')
        GROUP BY contractor
        HAVING total_pending > 0
        """,
        as_dict=True,
    )

    for record in pending_penalties:
        contractor_doc = frappe.get_doc("Civic Contractor", record.contractor)
        if contractor_doc.email:
            frappe.sendmail(
                recipients=[contractor_doc.email],
                subject=f"Pending SLA Penalties - \u20b9{record.total_pending:,.2f}",
                message=f\"\"\"
                <h3>Pending SLA Penalty Notice</h3>
                <p>Dear {contractor_doc.contractor_name},</p>
                <p>You have <strong>{record.count}</strong> pending SLA penalty(ies)
                totaling <strong>\u20b9{record.total_pending:,.2f}</strong>.</p>
                <p>These amounts will be deducted from your next municipal payout
                unless resolved or disputed.</p>
                <p>Please contact the Municipal Administration for details.</p>
                \"\"\",
            )
