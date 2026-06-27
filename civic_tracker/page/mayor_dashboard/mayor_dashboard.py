import frappe
from frappe.utils import getdate

@frappe.whitelist()
def get_dashboard_data():
    # Provide mock data for predictive charts for now or aggregate real data
    # Real data aggregation:
    today = getdate()
    last_year = today.year - 1
    
    # Seasonal Data (e.g., Road vs Drainage for last year)
    seasonal = frappe.db.sql("""
        SELECT MONTH(issue_date) as month, issue_type, COUNT(name) as count
        FROM `tabCivic Issue`
        WHERE issue_type IN ('Road', 'Drainage')
        AND YEAR(issue_date) = %s
        GROUP BY month, issue_type
    """, (last_year,), as_dict=True)
    
    # Format for Frappe Charts
    labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    road_data = [0] * 12
    drainage_data = [0] * 12
    
    for row in seasonal:
        m = int(row.month) - 1
        if row.issue_type == "Road":
            road_data[m] = row.count
        else:
            drainage_data[m] = row.count
            
    seasonal_chart = {
        "labels": labels,
        "datasets": [
            {"name": "Road Issues", "values": road_data},
            {"name": "Drainage Issues", "values": drainage_data}
        ]
    }
    
    # High Risk Wards
    ward_counts = frappe.db.sql("""
        SELECT ward, COUNT(name) as count
        FROM `tabCivic Issue`
        WHERE issue_type IN ('Road', 'Drainage')
        AND MONTH(issue_date) IN (6, 7, 8, 9)
        AND YEAR(issue_date) = %s
        GROUP BY ward
        ORDER BY count DESC
        LIMIT 5
    """, (last_year,), as_dict=True)
    
    ward_chart = {
        "labels": [w.ward for w in ward_counts],
        "datasets": [
            {"name": "Issues during Monsoon", "values": [w.count for w in ward_counts]}
        ]
    }
    
    # Return fake data if db is empty for visualization
    if not ward_counts:
        seasonal_chart = {
            "labels": ["Jun", "Jul", "Aug", "Sep"],
            "datasets": [
                {"name": "Road", "values": [50, 120, 150, 80]},
                {"name": "Drainage", "values": [60, 200, 180, 90]}
            ]
        }
        ward_chart = {
            "labels": ["Ward 1", "Ward 2", "Ward 3", "Ward 4"],
            "datasets": [
                {"name": "Risk Score", "values": [85, 60, 45, 90]}
            ]
        }
    
    return {
        "seasonal_data": seasonal_chart,
        "ward_data": ward_chart
    }
