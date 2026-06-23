from frappe import _
from frappe.desk.form.load import getdoctype


def get_data():
    return {
        "fieldname": "ward",
        "label": _("Ward"),
        "get_route_options_for_list_view": lambda doc: {"ward": doc.ward},
    }
