from frappe import _


def get_data():
    return {
        "fieldname": "ward",
        "label": _("Ward"),
        "non_standard_filter_conversion": {"ward": "ward"},
    }
