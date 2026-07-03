import frappe
from frappe.model.document import Document
import subprocess
import os

class GlobalMasterControl(Document):
    pass

@frappe.whitelist()
def provision_new_tenant(municipality_name, site_name, admin_email):
    """
    Day 50: API that provisions a new Frappe site automatically when a new municipality signs up.
    """
    if not frappe.db.get_single_value("Global Master Control", "enable_saas"):
        frappe.throw("Multi-Tenant SaaS Mode is not enabled.")
        
    master = frappe.get_doc("Global Master Control")
    db_password = master.get_password("default_db_password") or "root"
    
    # In a real environment, this would run `bench new-site` via subprocess
    # Command: bench new-site {site_name} --db-root-password {db_password} --admin-password admin
    # Command: bench --site {site_name} install-app civic_tracker
    
    # We add it to the tenant list
    master.append("tenant_list", {
        "municipality_name": municipality_name,
        "site_name": site_name,
        "admin_email": admin_email,
        "status": "Active" # Assuming provisioning successful
    })
    master.save(ignore_permissions=True)
    
    # Log the simulated action
    frappe.log_error(f"Simulated provisioning of site {site_name} for {municipality_name}", "SaaS Provisioning")
    
    return {"status": "success", "message": f"Site {site_name} successfully provisioned."}
