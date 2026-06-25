import frappe
from frappe.utils import now_datetime


@frappe.whitelist(allow_guest=True)
def get_issues_geojson(status=None, ward=None, issue_type=None):
    """Return all Civic Issues with coordinates as a GeoJSON FeatureCollection.
    Used by the Leaflet.js city map for real-time visualization.

    Args:
        status: Filter by status (optional)
        ward: Filter by ward (optional)
        issue_type: Filter by issue type (optional)

    Returns:
        GeoJSON FeatureCollection with color-coded markers.
    """
    filters = {}

    if status:
        filters["status"] = status
    if ward:
        filters["ward"] = ward
    if issue_type:
        filters["issue_type"] = issue_type

    # Only fetch issues that have coordinates
    issues = frappe.db.sql(
        """
        SELECT
            ci.name,
            ci.tracking_id,
            ci.issue_title,
            ci.issue_type,
            ci.status,
            ci.priority,
            ci.latitude,
            ci.longitude,
            ci.ward,
            ci.assigned_contractor,
            ci.issue_date,
            ci.due_date,
            ci.resolution_date,
            ci.citizen_name,
            mw.ward_name
        FROM `tabCivic Issue` ci
        LEFT JOIN `tabMunicipal Ward` mw ON mw.name = ci.ward
        WHERE ci.latitude IS NOT NULL
        AND ci.longitude IS NOT NULL
        AND ci.latitude != 0
        AND ci.longitude != 0
        {status_filter}
        {ward_filter}
        {type_filter}
        ORDER BY ci.issue_date DESC
        """.format(
            status_filter=f"AND ci.status = %(status)s" if status else "",
            ward_filter=f"AND ci.ward = %(ward)s" if ward else "",
            type_filter=f"AND ci.issue_type = %(issue_type)s" if issue_type else "",
        ),
        filters,
        as_dict=True,
    )

    features = []
    for issue in issues:
        # Determine marker color based on status
        marker_color = get_marker_color(issue.status)

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(issue.longitude), float(issue.latitude)],
            },
            "properties": {
                "id": issue.name,
                "tracking_id": issue.tracking_id,
                "title": issue.issue_title,
                "issue_type": issue.issue_type,
                "status": issue.status,
                "priority": issue.priority,
                "ward": issue.ward_name or issue.ward,
                "contractor": issue.assigned_contractor or "Unassigned",
                "reported_date": str(issue.issue_date) if issue.issue_date else None,
                "due_date": str(issue.due_date) if issue.due_date else None,
                "resolution_date": str(issue.resolution_date) if issue.resolution_date else None,
                "marker_color": marker_color,
                "icon": get_issue_icon(issue.issue_type),
            },
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "total_count": len(features),
            "generated_at": str(now_datetime()),
            "filters_applied": {
                "status": status,
                "ward": ward,
                "issue_type": issue_type,
            },
        },
    }


@frappe.whitelist(allow_guest=True)
def get_ward_boundaries():
    """Return ward information for map overlays."""
    wards = frappe.get_all(
        "Municipal Ward",
        fields=["name", "ward_name", "ward_code", "area_name",
                "commissioner_name", "population"],
    )
    return wards


@frappe.whitelist(allow_guest=True)
def get_map_statistics():
    """Return summary statistics for the map dashboard."""
    stats = frappe.db.sql(
        """
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_count,
            SUM(CASE WHEN status = 'Overdue' THEN 1 ELSE 0 END) as overdue_count,
            SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) as resolved_count,
            SUM(CASE WHEN status IN ('Assigned', 'In Progress') THEN 1 ELSE 0 END) as active_count,
            SUM(CASE WHEN latitude IS NOT NULL AND latitude != 0 THEN 1 ELSE 0 END) as geolocated_count
        FROM `tabCivic Issue`
        """,
        as_dict=True,
    )
    return stats[0] if stats else {}


def get_marker_color(status):
    """Return hex color for map marker based on issue status."""
    colors = {
        "Open": "#FFC107",       # Yellow/Amber
        "Assigned": "#17A2B8",   # Teal
        "In Progress": "#2490EF", # Blue
        "Overdue": "#DC3545",    # Red
        "Resolved": "#28A745",   # Green
        "Closed": "#6C757D",     # Gray
        "Reopened": "#FD7E14",   # Orange
    }
    return colors.get(status, "#6C757D")


def get_issue_icon(issue_type):
    """Return an icon identifier for the issue type."""
    icons = {
        "Road": "road",
        "Water": "tint",
        "Sanitation": "broom",
        "Electricity": "bolt",
        "Garbage": "trash",
        "Drainage": "water",
        "Street Light": "lightbulb",
        "Other": "exclamation-circle",
    }
    return icons.get(issue_type, "map-marker")
