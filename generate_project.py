import os
import json

base_dir = "/root/civic_tracker/civic_tracker/api"
os.makedirs(base_dir, exist_ok=True)

# 1. ai.py
with open(os.path.join(base_dir, "ai.py"), "w") as f:
    f.write('''import frappe
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
''')

# 2. whatsapp.py
with open(os.path.join(base_dir, "whatsapp.py"), "w") as f:
    f.write('''import frappe

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
''')

# 3. iot.py
with open(os.path.join(base_dir, "iot.py"), "w") as f:
    f.write('''import frappe

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
''')

# 4. clustering.py
with open(os.path.join(base_dir, "clustering.py"), "w") as f:
    f.write('''import frappe

def cluster_duplicates(doc, method=None):
    """ Day 7: Spatial Clustering (after_insert) """
    # Enqueue background job to find nearby issues
    frappe.enqueue("civic_tracker.api.clustering.find_and_merge", doc=doc)

def find_and_merge(doc):
    """ Find issues within 100m and merge """
    # Mocking geospatial clustering logic
    pass
''')

# 5. geofence.py
with open(os.path.join(base_dir, "geofence.py"), "w") as f:
    f.write('''import frappe
from geopy.distance import geodesic

def validate_resolution_location(doc, method=None):
    """ Day 8: Geofence Validation (on_update) """
    if doc.status == "Resolved" and doc.latitude and doc.actual_resolution_lat_lng:
        issue_coords = (doc.latitude, doc.longitude)
        resolution_coords = tuple(map(float, doc.actual_resolution_lat_lng.split(',')))
        distance = geodesic(issue_coords, resolution_coords).meters
        
        if distance > 50:
            frappe.throw("Resolution photo must be taken within 50m of the issue.")
''')

# 6. accounting.py
with open(os.path.join(base_dir, "accounting.py"), "w") as f:
    f.write('''import frappe

def generate_journal_entry(doc, method=None):
    """ Day 9: Automated Journal Entries upon ticket closure """
    if doc.status == "Closed":
        repair_cost = frappe.get_value("Standard Repair Cost", doc.issue_type, "rate")
        # Logic to generate ERPNext Journal Entry debiting Ward, crediting Contractor
        pass
''')

# 7. payment.py
with open(os.path.join(base_dir, "payment.py"), "w") as f:
    f.write('''import frappe

@frappe.whitelist(allow_guest=True)
def razorpay_webhook():
    """ Day 11: Payment Gateway Webhook """
    data = frappe.request.get_json()
    if data.get("event") == "payment.captured":
        penalty = frappe.get_doc("Contractor Penalty", data["payload"]["payment"]["entity"]["notes"]["penalty_id"])
        penalty.status = "Paid"
        penalty.save(ignore_permissions=True)
    return "OK"
''')

# 8. dispatch.py
with open(os.path.join(base_dir, "dispatch.py"), "w") as f:
    f.write('''import frappe

def dispatch_monday_pdfs():
    """ Day 12: Automated PDF Dispatch (Weekly Job) """
    commissioners = frappe.get_all("Ward Commissioner", fields=["email", "ward"])
    for comm in commissioners:
        # Use frappe.get_print() to generate report and frappe.sendmail()
        pass
''')

# 9. public.py
with open(os.path.join(base_dir, "public.py"), "w") as f:
    f.write('''import frappe

@frappe.whitelist(allow_guest=True)
def get_geojson_issues():
    """ Day 13: Open Data APIs """
    issues = frappe.get_all("Civic Issue", fields=["name", "latitude", "longitude", "issue_type"])
    features = []
    for issue in issues:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [issue.longitude, issue.latitude]},
            "properties": {"id": issue.name, "type": issue.issue_type}
        })
    return {"type": "FeatureCollection", "features": features}
''')

# 10. sync.py
with open(os.path.join(base_dir, "sync.py"), "w") as f:
    f.write('''import frappe

@frappe.whitelist()
def bulk_sync_issues(payload):
    """ Day 14: Mobile Sync API """
    import json
    data = json.loads(payload)
    for issue_data in data:
        # Logic to update issues that were resolved offline
        pass
    return {"status": "success"}
''')

print("Generated all API modules.")
