frappe.ui.form.on("Issue SLA", {
    refresh: function (frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("View Issues of this Type"), function () {
                frappe.set_route("List", "Civic Issue", {
                    issue_type: frm.doc.issue_type,
                });
            }, __("Actions"));
        }
    },
});
