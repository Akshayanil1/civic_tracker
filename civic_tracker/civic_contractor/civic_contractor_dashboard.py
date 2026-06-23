from frappe import _


def get_data():
    return {
        "fieldname": "assigned_contractor",
        "label": _("Contractor"),
        "non_standard_filter_conversion": {"assigned_contractor": "assigned_contractor"},
    }
