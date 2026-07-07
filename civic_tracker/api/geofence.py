import frappe
from geopy.distance import geodesic

def validate_resolution_location(doc, method=None):
    """ Day 8: Geofence Validation (on_update) """
    if doc.status == "Resolved" and doc.latitude and doc.actual_resolution_lat_lng:
        issue_coords = (doc.latitude, doc.longitude)
        resolution_coords = tuple(map(float, doc.actual_resolution_lat_lng.split(',')))
        distance = geodesic(issue_coords, resolution_coords).meters
        
        if distance > 50:
            frappe.throw("Resolution photo must be taken within 50m of the issue.")
