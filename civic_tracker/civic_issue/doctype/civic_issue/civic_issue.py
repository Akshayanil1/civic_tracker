import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date, get_url
from civic_tracker.api.ai import validate_image_with_ai, analyze_issue_text, dynamic_assignment_routing


class CivicIssue(Document):
    def before_insert(self):
        self.generate_tracking_id()
        
        # Phase 14: NLP Categorization and Sentiment
        if self.description:
            category, urgency = analyze_issue_text(self.description)
            if category:
                self.issue_type = category
            if urgency:
                self.urgency_score = urgency
                
        # Phase 13: Image Validation
        if self.issue_image:
            is_valid = validate_image_with_ai(self.issue_image)
            if not is_valid:
                self.status = "Spam"
                # Rejecting submission effectively if we don't want it open
                
        # Phase 14: Dynamic Assignment for Critical Issues
        dynamic_assignment_routing(self)
        
        self.set_escalation_time()

    def validate(self):
        self.validate_assignment()

    def on_update(self):
        self.send_tracking_email()

    def generate_tracking_id(self):
        """Generate a unique tracking ID for citizen reference."""
        import random
        import string

        prefix = "CT"
        year = now_datetime().strftime("%y")
        random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.tracking_id = f"{prefix}-{year}-{random_part}"

    def set_escalation_time(self):
        """Set escalation time based on SLA defined for the issue type."""
        sla = frappe.db.get_value(
            "Issue SLA",
            {"issue_type": self.issue_type, "is_active": 1},
            ["sla_hours", "escalation_hours"],
        )
        if sla:
            sla_hours, escalation_hours = sla
            self.due_date = add_to_date(self.issue_date, hours=int(sla_hours or 48))
            self.escalation_time = add_to_date(
                self.issue_date, hours=int(escalation_hours or 72)
            )
        else:
            self.due_date = add_to_date(self.issue_date, hours=48)
            self.escalation_time = add_to_date(self.issue_date, hours=72)

    def validate_assignment(self):
        """Validate contractor assignment rules."""
        if self.assigned_contractor and self.ward:
            contractor = frappe.get_doc("Civic Contractor", self.assigned_contractor)
            assigned_wards = [d.ward for d in contractor.assigned_ward]
            if assigned_wards and self.ward not in assigned_wards:
                frappe.msgprint(
                    f"Warning: Contractor {self.assigned_contractor} is not formally assigned to Ward {self.ward}.",
                    alert=True,
                )

    def send_tracking_email(self):
        """Send tracking ID to citizen if email is provided."""
        if self.citizen_email and not self.is_anonymous:
            tracking_url = get_url(f"/track-issue/{self.tracking_id}")
            frappe.sendmail(
                recipients=[self.citizen_email],
                subject=f"Civic Issue Reported - {self.tracking_id}",
                message=f"""
                <p>Dear {self.citizen_name or 'Citizen'},</p>
                <p>Thank you for reporting a civic issue. Your grievance has been registered.</p>
                <p><strong>Tracking ID:</strong> {self.tracking_id}</p>
                <p><strong>Issue Type:</strong> {self.issue_type}</p>
                <p><strong>Ward:</strong> {self.ward}</p>
                <p><strong>Status:</strong> {self.status}</p>
                <p>You can track your issue at: <a href="{tracking_url}">{tracking_url}</a></p>
                <p>Thank you for helping improve our city.</p>
                """,
            )

    def resolve_issue(self, notes=""):
        """Mark issue as resolved."""
        self.status = "Resolved"
        self.resolution_date = now_datetime()
        self.resolution_notes = notes
        self.save(ignore_permissions=True)

    def reopen_issue(self, reason=""):
        """Reopen a resolved issue."""
        self.status = "Reopened"
        self.resolution_date = None
        self.resolution_notes = ""
        self.save(ignore_permissions=True)
