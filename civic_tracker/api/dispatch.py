import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import now_datetime

def generate_ward_summary_pdf(ward_name):
    """
    Day 10: Build a custom HTML/Jinja Print Format for the Municipal Ward.
    """
    ward = frappe.get_doc("Municipal Ward", ward_name)
    
    # Gather data
    open_issues = frappe.db.count("Civic Issue", {"ward": ward_name, "status": "Open"})
    sla_breaches = frappe.db.count("Contractor Penalty", {"ward": ward_name, "status": ["in", ["Approved", "Pending", "Deducted"]]})
    
    # Calculate funds deducted
    penalties = frappe.get_all("Contractor Penalty", {"ward": ward_name, "status": "Deducted"}, ["penalty_amount"])
    funds_deducted = sum(p.penalty_amount for p in penalties if p.penalty_amount)
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ text-align: center; background-color: #0056b3; color: white; padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
            th {{ background-color: #f4f4f4; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Monday Morning Ward Summary</h2>
            <h3>Ward: {ward.ward_name} ({ward.ward_code})</h3>
            <p>Generated on: {now_datetime().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <table>
            <tr>
                <th>Metric</th>
                <th>Count / Value</th>
            </tr>
            <tr>
                <td>Total Open Issues</td>
                <td>{open_issues}</td>
            </tr>
            <tr>
                <td>Contractor SLA Breaches</td>
                <td>{sla_breaches}</td>
            </tr>
            <tr>
                <td>Funds Deducted (Penalties)</td>
                <td>Rs. {funds_deducted}</td>
            </tr>
        </table>
        
        <p style="margin-top: 50px;">Please review the above metrics for the weekly district magistrate briefing.</p>
    </body>
    </html>
    """
    
    return get_pdf(html)

@frappe.whitelist()
def dispatch_monday_pdfs():
    """
    Day 11 & 12: Generate PDFs and email to Ward Commissioners.
    Runs every Monday at 6:00 AM via hooks.py
    """
    wards = frappe.get_all("Municipal Ward", filters={"commissioner_email": ["is", "set"]}, fields=["name", "commissioner_email", "ward_name"])
    
    for ward in wards:
        try:
            pdf_data = generate_ward_summary_pdf(ward.name)
            
            # Attach and send email
            attachments = [{
                "fname": f"Ward_Summary_{ward.ward_name.replace(' ', '_')}.pdf",
                "fcontent": pdf_data
            }]
            
            frappe.sendmail(
                recipients=[ward.commissioner_email],
                subject=f"Weekly Summary Report - {ward.ward_name}",
                message="<p>Dear Commissioner,</p><p>Please find attached your automated Monday morning summary report.</p>",
                attachments=attachments
            )
            
            frappe.log_error(f"Dispatched weekly PDF to {ward.commissioner_email}", "PDF Dispatcher")
        except Exception as e:
            frappe.log_error(f"Failed to dispatch PDF for {ward.ward_name}: {str(e)}", "PDF Dispatcher Error")
            
    return {"status": "success", "dispatched_count": len(wards)}
