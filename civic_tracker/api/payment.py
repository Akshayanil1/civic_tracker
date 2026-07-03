import frappe
from frappe.utils import get_url

# To use this in production, install razorpay via `pip install razorpay`
# import razorpay

@frappe.whitelist()
def generate_payment_link(penalty_name):
    """
    Day 56: Generate automated payment links.
    When a penalty is finalized, SMS/WhatsApp the contractor a secure payment link.
    """
    penalty = frappe.get_doc("Contractor Penalty", penalty_name)
    
    if penalty.status not in ["Approved", "Pending"]:
        frappe.throw("Payment link can only be generated for Approved or Pending penalties.")
        
    # In a real implementation:
    # client = razorpay.Client(auth=(frappe.conf.razorpay_key, frappe.conf.razorpay_secret))
    # payment_link = client.payment_link.create({
    #     "amount": int(penalty.penalty_amount * 100),
    #     "currency": "INR",
    #     "description": f"Penalty for SLA Breach - {penalty.civic_issue}",
    #     "reference_id": penalty.name,
    #     "notify": {"sms": True, "email": True}
    # })
    # penalty.payment_link = payment_link['short_url']
    
    # Mocking for demonstration
    mock_payment_id = f"plink_{penalty.name.replace('-', '')}"
    penalty.payment_link = f"https://rzp.io/i/{mock_payment_id}"
    penalty.save(ignore_permissions=True)
    
    # Simulate sending SMS / WhatsApp
    contractor = frappe.get_doc("Civic Contractor", penalty.contractor)
    frappe.log_error(
        f"Simulated SMS to {contractor.contractor_name}: Please pay your penalty of Rs. {penalty.penalty_amount}. Link: {penalty.payment_link}",
        "Payment Link Generated"
    )
    
    return penalty.payment_link

@frappe.whitelist(allow_guest=True)
def razorpay_webhook():
    """
    Day 57: Webhook listener for Payment Gateway.
    When payment succeeds, auto update status to 'Paid' and log transaction.
    """
    # Verify signature in production
    data = frappe.request.get_json()
    
    if data and data.get("event") == "payment_link.paid":
        payload = data.get("payload", {}).get("payment_link", {}).get("entity", {})
        reference_id = payload.get("reference_id")
        transaction_id = data.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
        
        if reference_id:
            try:
                penalty = frappe.get_doc("Contractor Penalty", reference_id)
                penalty.status = "Paid"
                penalty.transaction_id = transaction_id
                penalty.save(ignore_permissions=True)
                
                frappe.db.commit()
                
                # If ERPNext is installed, we can create a Payment Entry
                if "erpnext" in frappe.get_installed_apps():
                    create_payment_entry(penalty)
                    
            except frappe.DoesNotExistError:
                pass
                
    return "OK"

def create_payment_entry(penalty):
    # Dummy function to show integration with ERPNext
    frappe.log_error(f"Created ERPNext Payment Entry for {penalty.name}", "Payment Integration")
