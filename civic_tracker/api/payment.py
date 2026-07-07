import frappe

@frappe.whitelist(allow_guest=True)
def razorpay_webhook():
    """ Day 11: Payment Gateway Webhook """
    data = frappe.request.get_json()
    if data.get("event") == "payment.captured":
        penalty = frappe.get_doc("Contractor Penalty", data["payload"]["payment"]["entity"]["notes"]["penalty_id"])
        penalty.status = "Paid"
        penalty.save(ignore_permissions=True)
    return "OK"
