from frappe import _


def get_data():
    return {
        "fieldname": "issue_type",
        "label": _("Issue Type"),
        "non_standard_filter_conversion": {"issue_type": "issue_type"},
    }
