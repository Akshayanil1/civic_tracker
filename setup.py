import frappe


def create_modules():
    """Create the Civic Tracker module if it doesn't exist."""
    if not frappe.db.exists("Module Def", "Civic Tracker"):
        frappe.get_doc(
            {
                "doctype": "Module Def",
                "module_name": "Civic Tracker",
                "app_name": "civic_tracker",
                "label": "Civic Tracker",
            }
        ).insert(ignore_permissions=True)
