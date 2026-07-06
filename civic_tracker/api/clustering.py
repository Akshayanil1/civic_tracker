import frappe
try:
    from geopy.distance import geodesic
except ImportError:
    pass

@frappe.whitelist()
def cluster_duplicates(issue_name):
    """
    Day 4, 5, 6: Spatial Duplicate Clustering (Automated Triage)
    Called as a background job after a new Civic Issue is inserted.
    """
    new_issue = frappe.get_doc("Civic Issue", issue_name)
    
    if not (new_issue.latitude and new_issue.longitude):
        return
        
    # We want to find open issues of the same type within 100 meters.
    # Without PostGIS, we fetch potential candidates in the same ward and filter in Python.
    candidates = frappe.get_all(
        "Civic Issue",
        filters={
            "name": ["!=", issue_name],
            "status": "Open",
            "issue_type": new_issue.issue_type,
            "ward": new_issue.ward,
            "master_issue": ["is", "not set"] # Don't merge into already merged issues
        },
        fields=["name", "latitude", "longitude"]
    )
    
    new_point = (new_issue.latitude, new_issue.longitude)
    
    master_issue_name = None
    
    for candidate in candidates:
        if candidate.latitude and candidate.longitude:
            candidate_point = (candidate.latitude, candidate.longitude)
            try:
                dist = geodesic(new_point, candidate_point).meters
                if dist <= 100:
                    master_issue_name = candidate.name
                    break
            except Exception:
                pass
                
    if master_issue_name:
        # Day 6: Change status to Merged, link to master ticket
        new_issue.status = "Merged"
        new_issue.master_issue = master_issue_name
        new_issue.save(ignore_permissions=True)
        frappe.db.commit()
        
        # Conceptually append citizen's email to a "Notify on Resolution" list of the master ticket.
        # In this implementation, we just log it.
        frappe.log_error(f"Merged {issue_name} into {master_issue_name} (Distance <= 100m)", "Spatial Clustering")
