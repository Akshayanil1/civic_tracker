import frappe
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from frappe.utils import getdate

def generate_trend_report():
    """Scheduled job to run monthly and group historical issues."""
    today = getdate()
    # Let's analyze previous month
    target_date = today - relativedelta(months=1)
    
    issues = frappe.db.sql("""
        SELECT issue_type, ward, COUNT(name) as count
        FROM `tabCivic Issue`
        WHERE MONTH(issue_date) = %s AND YEAR(issue_date) = %s
        GROUP BY issue_type, ward
    """, (target_date.month, target_date.year), as_dict=True)
    
    # Process into JSON
    analysis = {}
    for row in issues:
        if row.ward not in analysis:
            analysis[row.ward] = {}
        analysis[row.ward][row.issue_type] = row.count
        
    report = frappe.get_doc({
        "doctype": "Civic Trend Report",
        "month": target_date.strftime("%B"),
        "year": target_date.year,
        "analysis_data": json.dumps(analysis, indent=2)
    })
    report.insert(ignore_permissions=True)

def pre_monsoon_forecasting():
    """Background job that analyzes data from previous year's monsoon (June-Sept)
    and flags high-risk wards for pothole/drainage checks.
    Runs roughly 30 days before expected rainfall (e.g. May 1st).
    """
    today = getdate()
    
    # E.g., if today is May, analyze last year's June-Sept
    last_year = today.year - 1
    
    # We want to find Wards with high number of Road and Drainage issues last monsoon
    high_risk_issues = frappe.db.sql("""
        SELECT ward, issue_type, COUNT(name) as count
        FROM `tabCivic Issue`
        WHERE issue_type IN ('Road', 'Drainage')
        AND MONTH(issue_date) IN (6, 7, 8, 9)
        AND YEAR(issue_date) = %s
        GROUP BY ward, issue_type
        HAVING count > 10
    """, (last_year,), as_dict=True)
    
    risk_wards = set([row.ward for row in high_risk_issues if row.ward])
    
    for ward in risk_wards:
        # Check if we already created a pre-monsoon issue this year for this ward
        existing = frappe.db.exists("Civic Issue", {
            "issue_title": ["like", "%Pre-Monsoon%"],
            "ward": ward,
            "issue_type": "Other"
        })
        if not existing:
            issue = frappe.get_doc({
                "doctype": "Civic Issue",
                "issue_title": f"Pre-Monsoon Pothole/Drainage Check for {ward}",
                "issue_type": "Other",
                "priority": "High",
                "ward": ward,
                "description": f"Automated predictive task: This ward had a high volume of Road/Drainage issues during last year's monsoon. Please conduct preventative checks.",
                "source_channel": "Web Portal",
                "citizen_name": "Predictive AI Engine"
            })
            issue.insert(ignore_permissions=True)
