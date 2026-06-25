import frappe
from frappe.model.document import Document
from frappe.utils import flt, now_datetime, getdate


class ContractorPenalty(Document):
    def validate(self):
        self.calculate_penalty()
        self.set_issue_details()

    def calculate_penalty(self):
        """Calculate penalty amount based on days overdue and rate per day."""
        if self.days_overdue and self.penalty_rate_per_day:
            amount = flt(self.days_overdue) * flt(self.penalty_rate_per_day)
            # Apply cap if set
            if self.max_penalty_cap and amount > flt(self.max_penalty_cap):
                amount = flt(self.max_penalty_cap)
            self.penalty_amount = amount

    def set_issue_details(self):
        """Auto-populate fields from the linked Civic Issue."""
        if self.civic_issue:
            issue = frappe.get_doc("Civic Issue", self.civic_issue)
            self.ward = issue.ward
            self.issue_type = issue.issue_type
            if not self.sla_deadline:
                self.sla_deadline = issue.escalation_time
            if not self.resolution_date:
                self.resolution_date = issue.resolution_date or now_datetime()

    def on_update(self):
        if self.status == "Approved" and not self.approved_by:
            self.db_set("approved_by", frappe.session.user)
