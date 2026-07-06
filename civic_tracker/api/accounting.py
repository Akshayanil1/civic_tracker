import frappe

def generate_journal_entry_on_close(doc, method):
    """
    Day 9: Automated Ward Budget Accounting
    When a Ward Commissioner approves a 'Resolved' ticket (changing status to 'Closed'),
    generate a draft Journal Entry crediting the Contractor and debiting the Ward's Cost Center.
    """
    # Check if status is transitioning to 'Closed'
    if doc.status != "Closed":
        return
        
    # Prevent duplicate entries if reopened and closed again
    if frappe.db.exists("Journal Entry", {"remark": f"Auto-generated for {doc.name}"}):
        return
        
    if not doc.assigned_contractor or not doc.ward:
        return
        
    ward = frappe.get_doc("Municipal Ward", doc.ward)
    if not ward.cost_center:
        frappe.log_error(f"Cannot generate Journal Entry: Ward {doc.ward} has no Cost Center mapped.", "Budget Accounting")
        return
        
    # Get standard cost
    standard_cost_doc = frappe.db.get_value("Standard Repair Cost", {"issue_type": doc.issue_type}, "standard_cost")
    if not standard_cost_doc:
        frappe.log_error(f"Cannot generate Journal Entry: No Standard Repair Cost defined for {doc.issue_type}.", "Budget Accounting")
        return
        
    cost = standard_cost_doc
    
    # In a full ERPNext installation, we would create a Journal Entry.
    # Since we might be in a Frappe-only environment for this module, we simulate/try it.
    if "erpnext" in frappe.get_installed_apps():
        try:
            je = frappe.new_doc("Journal Entry")
            je.voucher_type = "Journal Entry"
            je.company = "Municipal Corporation" # Ideally fetched from settings
            je.remark = f"Auto-generated for {doc.name}"
            
            # Debit the Ward's Cost Center (Expense)
            je.append("accounts", {
                "account": "Maintenance Expenses - MC",
                "cost_center": ward.cost_center,
                "debit_in_account_currency": cost,
                "credit_in_account_currency": 0
            })
            
            # Credit the Contractor (Payable)
            # Assuming Contractor is mapped to a Supplier account
            je.append("accounts", {
                "account": "Creditors - MC",
                "party_type": "Supplier",
                # "party": doc.assigned_contractor, # Usually linked to a supplier
                "debit_in_account_currency": 0,
                "credit_in_account_currency": cost
            })
            
            je.insert(ignore_permissions=True)
            frappe.log_error(f"Draft Journal Entry {je.name} created for {doc.name}", "Budget Accounting Success")
            
        except Exception as e:
            frappe.log_error(f"Failed to create Journal Entry: {str(e)}", "Budget Accounting Error")
    else:
        # Mock for non-ERPNext environments
        frappe.log_error(f"Simulated Journal Entry: Debited {ward.cost_center}, Credited {doc.assigned_contractor} for Rs. {cost}", "Budget Accounting Mock")
