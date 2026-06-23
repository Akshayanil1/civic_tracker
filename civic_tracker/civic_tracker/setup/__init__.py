import frappe
from frappe.utils import nowdate


def execute():
    """Create default dashboard Number Cards and Charts for Civic Tracker."""
    _create_number_cards()
    _create_dashboards()


def _create_number_cards():
    """Create number cards for the dashboard."""
    cards = [
        {
            "name": "Total Open Issues",
            "label": "Total Open Issues",
            "document_type": "Civic Issue",
            "filters_json": '{"status":"Open"}',
            "color": "#ff5858",
            "icon": "fa fa-exclamation-circle",
        },
        {
            "name": "Issues In Progress",
            "label": "Issues In Progress",
            "document_type": "Civic Issue",
            "filters_json": '{"status":"In Progress"}',
            "color": "#2490ef",
            "icon": "fa fa-spinner",
        },
        {
            "name": "Overdue Issues",
            "label": "Overdue Issues",
            "document_type": "Civic Issue",
            "filters_json": '{"status":"Overdue"}',
            "color": "#ff8c00",
            "icon": "fa fa-warning",
        },
        {
            "name": "Resolved Issues",
            "label": "Resolved Issues",
            "document_type": "Civic Issue",
            "filters_json": '{"status":"Resolved"}',
            "color": "#5e64ff",
            "icon": "fa fa-check-circle",
        },
    ]

    for card_data in cards:
        if not frappe.db.exists("Number Card", card_data["name"]):
            card = frappe.get_doc({
                "doctype": "Number Card",
                "label": card_data["name"],
                "document_type": card_data["document_type"],
                "filters_json": card_data["filters_json"],
                "color": card_data.get("color"),
                "icon": card_data.get("icon"),
            })
            card.insert(ignore_permissions=True)


def _create_dashboards():
    """Create dashboard charts."""
    charts = [
        {
            "name": "Issues by Type",
            "chart_name": "Issues by Type",
            "chart_type": "Donut",
            "document_type": "Civic Issue",
            "group_by_field": "issue_type",
        },
        {
            "name": "Issues by Ward",
            "chart_name": "Issues by Ward",
            "chart_type": "Bar",
            "document_type": "Civic Issue",
            "group_by_field": "ward",
        },
        {
            "name": "Issues by Status",
            "chart_name": "Issues by Status",
            "chart_type": "Donut",
            "document_type": "Civic Issue",
            "group_by_field": "status",
        },
    ]

    for chart_data in charts:
        if not frappe.db.exists("Dashboard Chart", chart_data["name"]):
            chart = frappe.get_doc({
                "doctype": "Dashboard Chart",
                "chart_name": chart_data["chart_name"],
                "chart_type": chart_data["chart_type"],
                "document_type": chart_data["document_type"],
                "group_by_field": chart_data["group_by_field"],
                "is_public": 1,
            })
            chart.insert(ignore_permissions=True)
