import os
import json

doctypes = [
    # Day 1
    "Civic Issue",
    "Civic Contractor",
    # Day 2
    "Municipal Ward",
    "Issue SLA",
    "Contractor Penalty",
    "Standard Repair Cost",
    # Day 3
    "Global Master Control",
    "Municipal Tenant"
]

base_dir = "/root/civic_tracker/civic_tracker/civic_tracker/doctype"

for dt in doctypes:
    dt_name = dt.lower().replace(" ", "_")
    dt_dir = os.path.join(base_dir, dt_name)
    os.makedirs(dt_dir, exist_ok=True)
    
    # JSON schema
    schema = {
        "name": dt,
        "module": "Civic Tracker",
        "custom": 0,
        "fields": [{"fieldname": "title", "fieldtype": "Data", "label": "Title"}],
        "permissions": [{"role": "System Manager", "read": 1, "write": 1}]
    }
    with open(os.path.join(dt_dir, f"{dt_name}.json"), "w") as f:
        json.dump(schema, f, indent=4)
        
    # Python file
    class_name = "".join(x.title() for x in dt.split(" "))
    with open(os.path.join(dt_dir, f"{dt_name}.py"), "w") as f:
        f.write(f'''from frappe.model.document import Document

class {class_name}(Document):
    pass
''')

    # Init file
    with open(os.path.join(dt_dir, "__init__.py"), "w") as f:
        f.write("")

print("Schemas generated.")
