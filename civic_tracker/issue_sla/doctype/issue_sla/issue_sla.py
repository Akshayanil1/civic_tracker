import frappe
from frappe.model.document import Document


class IssueSLA(Document):
    def validate(self):
        self.validate_hours()

    def validate_hours(self):
        if self.sla_hours and self.escalation_hours:
            if self.escalation_hours <= self.sla_hours:
                frappe.throw(
                    "Escalation Time must be greater than SLA Time. "
                    "Escalation happens after the SLA deadline."
                )
