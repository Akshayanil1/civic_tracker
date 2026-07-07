import frappe

@frappe.whitelist(allow_guest=True)
def get_geojson_issues():
    """ Day 13: Open Data APIs """
    issues = frappe.get_all("Civic Issue", fields=["name", "latitude", "longitude", "issue_type"])
    features = []
    for issue in issues:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [issue.longitude, issue.latitude]},
            "properties": {"id": issue.name, "type": issue.issue_type}
        })
    return {"type": "FeatureCollection", "features": features}
