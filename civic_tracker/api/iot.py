import frappe

@frappe.whitelist(allow_guest=True)
def receive_sensor_data():
    """ Day 6: IoT M2M Endpoints """
    api_key = frappe.request.headers.get("X-API-Key")
    if api_key != "secret_iot_key":
        frappe.throw("Invalid API Key", frappe.PermissionError)
        
    data = frappe.request.get_json()
    doc = frappe.get_doc({
        "doctype": "Civic Issue",
        "issue_type": "Flood",
        "description": f"Auto-reported by sensor {data.get('sensor_id')}",
        "latitude": data.get("lat"),
        "longitude": data.get("lng")
    })
    doc.insert(ignore_permissions=True)
    return {"status": "success", "issue": doc.name}
