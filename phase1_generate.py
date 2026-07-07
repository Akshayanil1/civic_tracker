import os
import json

base_dir = "/root/civic_tracker/civic_tracker/civic_tracker/doctype"

def write_doctype(name, fields, settings=None):
    dt_name = name.lower().replace(" ", "_")
    dt_dir = os.path.join(base_dir, dt_name)
    os.makedirs(dt_dir, exist_ok=True)
    
    schema = {
        "name": name,
        "module": "Civic Tracker",
        "custom": 0,
        "fields": fields,
        "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}],
        "naming_rule": "Expression",
        "autoname": f"format:{{{{tenant}}}}-{name.split()[0].upper()}-.####" if name != "Municipal Tenant" else "format:TENANT-.####"
    }
    
    if settings:
        schema.update(settings)
        
    with open(os.path.join(dt_dir, f"{dt_name}.json"), "w") as f:
        json.dump(schema, f, indent=4)
        
    class_name = "".join(x.title() for x in name.split(" "))
    with open(os.path.join(dt_dir, f"{dt_name}.py"), "w") as f:
        f.write(f'''from frappe.model.document import Document

class {class_name}(Document):
    pass
''')

# 1. Civic Issue
civic_issue_fields = [
    {"fieldname": "title", "fieldtype": "Data", "label": "Title", "reqd": 1},
    {"fieldname": "tenant", "fieldtype": "Link", "options": "Municipal Tenant", "label": "Tenant", "reqd": 1},
    {"fieldname": "issue_type", "fieldtype": "Select", "label": "Issue Type", "options": "Pothole\nWater Leak\nStreetlight\nGarbage\nFlood"},
    {"fieldname": "description", "fieldtype": "Text Editor", "label": "Description"},
    {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Open\nAssigned\nIn Progress\nResolved\nClosed\nOverdue\nReopened\nSpam\nMerged", "default": "Open"},
    {"fieldname": "priority", "fieldtype": "Select", "label": "Priority", "options": "Low\nMedium\nHigh\nCritical"},
    {"fieldname": "urgency_score", "fieldtype": "Int", "label": "Urgency Score"},
    {"fieldname": "ward", "fieldtype": "Link", "options": "Municipal Ward", "label": "Ward"},
    {"fieldname": "assigned_contractor", "fieldtype": "Link", "options": "Civic Contractor", "label": "Assigned Contractor"},
    {"fieldname": "latitude", "fieldtype": "Float", "label": "Latitude"},
    {"fieldname": "longitude", "fieldtype": "Float", "label": "Longitude"},
    {"fieldname": "actual_resolution_lat_lng", "fieldtype": "Data", "label": "Actual Resolution Lat/Lng"},
    {"fieldname": "master_issue", "fieldtype": "Link", "options": "Civic Issue", "label": "Master Issue"},
    {"fieldname": "image", "fieldtype": "Attach Image", "label": "Issue Image"},
    {"fieldname": "sla_deadline", "fieldtype": "Datetime", "label": "SLA Deadline"}
]
write_doctype("Civic Issue", civic_issue_fields)

# 2. Civic Contractor
contractor_fields = [
    {"fieldname": "contractor_name", "fieldtype": "Data", "label": "Contractor Name", "reqd": 1},
    {"fieldname": "tenant", "fieldtype": "Link", "options": "Municipal Tenant", "label": "Tenant", "reqd": 1},
    {"fieldname": "phone", "fieldtype": "Data", "label": "Phone Number"},
    {"fieldname": "email", "fieldtype": "Data", "label": "Email Address"},
    {"fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "label": "ERPNext Supplier"},
    {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Active\nSuspended", "default": "Active"}
]
write_doctype("Civic Contractor", contractor_fields)

# 3. Municipal Ward
ward_fields = [
    {"fieldname": "ward_name", "fieldtype": "Data", "label": "Ward Name", "reqd": 1},
    {"fieldname": "tenant", "fieldtype": "Link", "options": "Municipal Tenant", "label": "Tenant", "reqd": 1},
    {"fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "label": "ERPNext Cost Center"},
    {"fieldname": "ward_commissioner", "fieldtype": "Link", "options": "User", "label": "Ward Commissioner"}
]
write_doctype("Municipal Ward", ward_fields)

# 4. Contractor Penalty
penalty_fields = [
    {"fieldname": "contractor", "fieldtype": "Link", "options": "Civic Contractor", "label": "Contractor", "reqd": 1},
    {"fieldname": "tenant", "fieldtype": "Link", "options": "Municipal Tenant", "label": "Tenant", "reqd": 1},
    {"fieldname": "issue", "fieldtype": "Link", "options": "Civic Issue", "label": "Civic Issue"},
    {"fieldname": "penalty_amount", "fieldtype": "Currency", "label": "Penalty Amount", "reqd": 1},
    {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Unpaid\nPaid\nDeducted", "default": "Unpaid"}
]
write_doctype("Contractor Penalty", penalty_fields)

# 5. Issue SLA
sla_fields = [
    {"fieldname": "issue_type", "fieldtype": "Select", "label": "Issue Type", "options": "Pothole\nWater Leak\nStreetlight\nGarbage\nFlood", "reqd": 1, "unique": 1},
    {"fieldname": "tenant", "fieldtype": "Link", "options": "Municipal Tenant", "label": "Tenant", "reqd": 1},
    {"fieldname": "resolution_time_hours", "fieldtype": "Int", "label": "Resolution Time (Hours)", "reqd": 1}
]
write_doctype("Issue SLA", sla_fields)

# 6. Standard Repair Cost
cost_fields = [
    {"fieldname": "issue_type", "fieldtype": "Select", "label": "Issue Type", "options": "Pothole\nWater Leak\nStreetlight\nGarbage\nFlood", "reqd": 1, "unique": 1},
    {"fieldname": "tenant", "fieldtype": "Link", "options": "Municipal Tenant", "label": "Tenant", "reqd": 1},
    {"fieldname": "rate", "fieldtype": "Currency", "label": "Standard Rate", "reqd": 1}
]
write_doctype("Standard Repair Cost", cost_fields)

# 7. Municipal Tenant
tenant_fields = [
    {"fieldname": "tenant_name", "fieldtype": "Data", "label": "Tenant Name", "reqd": 1},
    {"fieldname": "domain", "fieldtype": "Data", "label": "Domain", "unique": 1},
    {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Active\nInactive", "default": "Active"}
]
write_doctype("Municipal Tenant", tenant_fields)

# 8. Global Master Control
master_control_fields = [
    {"fieldname": "enable_global_analytics", "fieldtype": "Check", "label": "Enable Global Analytics"},
    {"fieldname": "default_tenant", "fieldtype": "Link", "options": "Municipal Tenant", "label": "Default Tenant"}
]
write_doctype("Global Master Control", master_control_fields, {"issingle": 1})

print("Phase 1 detailed schemas generated.")
