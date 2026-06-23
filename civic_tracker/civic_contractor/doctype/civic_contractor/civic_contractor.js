frappe.ui.form.on("Civic Contractor", {
    refresh: function (frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("View Assigned Issues"), function () {
                frappe.set_route("List", "Civic Issue", {
                    assigned_contractor: frm.doc.name,
                });
            }, __("Actions"));
        }
    },
});
