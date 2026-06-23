frappe.ui.form.on("Municipal Ward", {
    refresh: function (frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("View Issues"), function () {
                frappe.set_route("List", "Civic Issue", {
                    ward: frm.doc.name,
                });
            }, __("Actions"));
        }
    },
});
