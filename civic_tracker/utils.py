import frappe


@frappe.whitelist()
def get_wards_for_select():
    """Return wards for use in select fields."""
    wards = frappe.get_all("Municipal Ward", fields=["name", "ward_name"], order_by="ward_name")
    return [{"value": w.name, "label": w.ward_name} for w in wards]
