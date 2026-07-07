import frappe

def dispatch_monday_pdfs():
    """ Day 12: Automated PDF Dispatch (Weekly Job) """
    commissioners = frappe.get_all("Ward Commissioner", fields=["email", "ward"])
    for comm in commissioners:
        # Use frappe.get_print() to generate report and frappe.sendmail()
        pass
