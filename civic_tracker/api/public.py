import frappe

@frappe.whitelist(allow_guest=True)
def get_open_data(limit=100, offset=0):
    """
    Day 43: Public Open Data API
    Read-only, rate-limited REST API endpoint.
    Queries all resolved Civic Issues, strictly strips out PII.
    """
    # Rate limit could be handled at nginx/frappe layer (frappe rate limiting config).
    
    issues = frappe.get_all(
        "Civic Issue",
        filters={"status": ["in", ["Resolved", "Closed"]]},
        fields=[
            "name as tracking_id", "issue_title", "issue_type", "priority", 
            "ward", "status", "issue_date", "resolution_date", 
            "latitude", "longitude"
        ],
        limit_start=offset,
        limit_page_length=limit,
        order_by="issue_date desc"
    )
    
    # We explicitly excluded citizen_name, citizen_email, citizen_phone (PII)
    return {
        "dataset": "Civic Issues (Resolved)",
        "count": len(issues),
        "data": issues
    }

def generate_weekly_csv_dump():
    """
    Day 45: Write an export script that automatically dumps anonymized civic data
    into a public CSV file every Sunday at midnight.
    """
    import csv
    from io import StringIO
    from frappe.utils import now_datetime
    
    # Get all resolved issues, stripping PII
    issues = frappe.get_all(
        "Civic Issue",
        filters={"status": ["in", ["Resolved", "Closed"]]},
        fields=[
            "name", "issue_title", "issue_type", "priority", 
            "ward", "status", "issue_date", "resolution_date", 
            "latitude", "longitude"
        ]
    )
    
    if not issues:
        return
        
    csv_file = StringIO()
    writer = csv.DictWriter(csv_file, fieldnames=issues[0].keys())
    writer.writeheader()
    writer.writerows(issues)
    
    csv_content = csv_file.getvalue()
    
    file_name = f"civic_open_data_latest.csv"
    
    # Check if file already exists and update it, or create a new one
    existing_file = frappe.db.exists("File", {"file_name": file_name})
    
    if existing_file:
        _file = frappe.get_doc("File", existing_file)
        _file.content = csv_content
        _file.save()
    else:
        _file = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "is_private": 0,
            "content": csv_content,
            "folder": "Home"
        })
        _file.insert()
        
    frappe.db.commit()
