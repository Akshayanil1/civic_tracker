import frappe
from frappe.model.document import Document


class CivicContractor(Document):
    def validate(self):
        self.validate_dates()
        self.validate_active_contract()

    def validate_dates(self):
        if self.contract_start_date and self.contract_end_date:
            if self.contract_end_date < self.contract_start_date:
                frappe.throw("Contract End Date cannot be before Contract Start Date.")

    def validate_active_contract(self):
        if self.status == "Active" and self.contract_end_date:
            from frappe.utils import getdate

            if getdate(self.contract_end_date) < getdate():
                frappe.msgprint(
                    "Warning: Contract has expired but status is still Active.",
                    alert=True,
                )
