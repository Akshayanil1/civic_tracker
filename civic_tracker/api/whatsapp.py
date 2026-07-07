import frappe

@frappe.whitelist(allow_guest=True)
def webhook_verify():
    """ Day 5: WhatsApp Ingestion Verification """
    request = frappe.request
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == "secret_token":
        return request.args.get("hub.challenge")
    return "Invalid verification token"

@frappe.whitelist(allow_guest=True)
def webhook_receive():
    """ Day 5: WhatsApp Ingestion Receiver """
    data = frappe.request.get_json()
    # Logic to parse whatsapp media/text and create a Civic Issue payload
    # doc = frappe.get_doc({"doctype": "Civic Issue", "description": data.get("text")})
    # doc.insert(ignore_permissions=True)
    return "Success"
