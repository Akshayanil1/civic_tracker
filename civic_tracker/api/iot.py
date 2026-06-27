import frappe
import json
from frappe.utils import now_datetime

@frappe.whitelist(allow_guest=True, methods=["POST"])
def sensor_webhook():
    """
    High-throughput webhook for IoT sensors.
    Payload format: {"mac_address": "XX:XX:XX...", "capacity": 95, ...}
    """
    try:
        # For a high throughput endpoint, we might do rate limiting here,
        # but Frappe has built-in rate limiting config we can use in production.
        payload = frappe.request.get_data(as_text=True)
        data = json.loads(payload)
        mac_address = data.get("mac_address")
        
        if not mac_address:
            frappe.throw("MAC Address is required", frappe.ValidationError)
            
        if not frappe.db.exists("IoT Device", mac_address):
            frappe.throw(f"IoT Device {mac_address} not found", frappe.DoesNotExistError)
            
        # Update last ping and payload
        frappe.db.set_value("IoT Device", mac_address, {
            "last_ping": now_datetime(),
            "last_payload": json.dumps(data, indent=2)
        })
        
        device = frappe.get_doc("IoT Device", mac_address)
        
        # Trigger logic for Smart Bin
        if device.device_type == "Smart Bin" and "capacity" in data:
            capacity = float(data.get("capacity", 0))
            if capacity > 90.0:
                create_smart_bin_issue(device, capacity)
                
        # Trigger logic for Flood Sensor
        if device.device_type == "Flood Sensor" and "water_level_cm" in data:
            level = float(data.get("water_level_cm", 0))
            if level > 50.0:
                create_flood_issue(device, level)

        frappe.db.commit()
        return {"status": "success", "message": "Payload processed"}
        
    except Exception as e:
        frappe.log_error(f"IoT Webhook Error: {str(e)}", "IoT Ingestion Error")
        return {"status": "error", "message": str(e)}

def create_smart_bin_issue(device, capacity):
    """Automatically create an issue for a full smart bin."""
    # Check if an open issue already exists for this bin to avoid duplicates
    existing_issue = frappe.db.exists("Civic Issue", {
        "issue_type": "Garbage",
        "ward": device.ward,
        "status": ["in", ["Open", "Assigned", "In Progress"]],
        "description": ["like", f"%{device.mac_address}%"]
    })
    
    if existing_issue:
        return
        
    issue = frappe.get_doc({
        "doctype": "Civic Issue",
        "issue_title": f"Smart Bin Full ({capacity}%) at {device.location_details or device.ward}",
        "issue_type": "Garbage",
        "priority": "High",
        "ward": device.ward,
        "description": f"Automated alert from IoT Device {device.mac_address}. Bin capacity has reached {capacity}%. Please clear immediately.",
        "latitude": device.latitude,
        "longitude": device.longitude,
        "source_channel": "Web Portal", # Or 'IoT Sensor' if added to options
        "citizen_name": "IoT Automation",
    })
    issue.insert(ignore_permissions=True)

def create_flood_issue(device, level):
    # Check for existing open issue
    existing_issue = frappe.db.exists("Civic Issue", {
        "issue_type": "Drainage",
        "ward": device.ward,
        "status": ["in", ["Open", "Assigned", "In Progress"]],
        "description": ["like", f"%{device.mac_address}%"]
    })
    
    if existing_issue:
        return
        
    issue = frappe.get_doc({
        "doctype": "Civic Issue",
        "issue_title": f"Flood Warning (Level: {level}cm) at {device.location_details or device.ward}",
        "issue_type": "Drainage",
        "priority": "Critical",
        "ward": device.ward,
        "description": f"Automated alert from Flood Sensor {device.mac_address}. Water level is {level}cm.",
        "latitude": device.latitude,
        "longitude": device.longitude,
        "source_channel": "Web Portal",
        "citizen_name": "IoT Automation",
    })
    issue.insert(ignore_permissions=True)
