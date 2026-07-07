import frappe

def get_tenant_permission_query_conditions(user):
    """
    Day 3: Multi-Tenancy Foundations - Base query logic for strict database isolation.
    Returns SQL conditions to append to list queries so users only see data for their tenant.
    """
    if not user:
        user = frappe.session.user
        
    if "System Manager" in frappe.get_roles(user):
        return "" # System managers see everything globally
        
    # Find the tenant associated with the current user
    # For example, we might have a User-Tenant mapping doctype or custom field on User.
    # We will assume User has a custom field `municipal_tenant`.
    tenant = frappe.db.get_value("User", user, "municipal_tenant")
    
    if not tenant:
        # If user has no tenant, they see nothing
        return "1=0"
        
    return f"`tab{frappe.qb.engine.get_query_builder().table.name}`.tenant = '{frappe.db.escape(tenant)}'"

def has_tenant_permission(doc, user, ptype="read"):
    """
    Day 3: Multi-Tenancy Foundations - Row level isolation.
    Ensures a user cannot directly access a document belonging to another tenant.
    """
    if "System Manager" in frappe.get_roles(user):
        return True
        
    user_tenant = frappe.db.get_value("User", user, "municipal_tenant")
    
    if not user_tenant or doc.tenant != user_tenant:
        return False
        
    return True
