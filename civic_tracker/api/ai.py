import frappe
from frappe import _

@frappe.whitelist()
def validate_civic_issue_image(doc, method=None):
    """
    Day 4: AI Triage.
    Wired into before_insert of Civic Issue to prevent spam.
    Uses Vision API to validate the image, and NLP to generate urgency_score.
    """
    if not doc.image:
        return
    
    # Mocking Vision AI validation
    # If it was a selfie, we would raise frappe.ValidationError("Image rejected: Not a civic issue.")
    
    # Mocking NLP Sentiment
    doc.urgency_score = 8 # High urgency example
    doc.department = "Public Works"
