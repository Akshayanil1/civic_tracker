import frappe
from frappe.model.document import Document

class CitizenVote(Document):
    def after_insert(self):
        # Update total votes in proposal
        proposal = frappe.get_doc("Civic Proposal", self.proposal)
        proposal.total_votes = frappe.db.count("Citizen Vote", {"proposal": self.proposal})
        proposal.save(ignore_permissions=True)
