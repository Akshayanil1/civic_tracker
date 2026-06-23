frappe.ui.form.on("Civic Issue", {
    refresh: function (frm) {
        if (!frm.is_new()) {
            // Show tracking ID prominently
            if (frm.doc.tracking_id) {
                frm.dashboard.add_comment(
                    __("Tracking ID: {0}", [frm.doc.tracking_id]),
                    "blue",
                    true
                );
            }

            // Action buttons based on status
            if (frm.doc.status === "Open" || frm.doc.status === "Reopened") {
                frm.add_custom_button(__("Assign Contractor"), function () {
                    frappe.prompt(
                        {
                            label: __("Select Contractor"),
                            fieldname: "contractor",
                            fieldtype: "Link",
                            options: "Civic Contractor",
                            reqd: 1,
                        },
                        function (values) {
                            frappe.call({
                                method: "frappe.client.set_value",
                                args: {
                                    doctype: "Civic Issue",
                                    name: frm.doc.name,
                                    fieldname: {
                                        assigned_contractor: values.contractor,
                                        status: "Assigned",
                                    },
                                },
                                callback: function () {
                                    frm.reload_doc();
                                    frappe.show_alert(__("Issue assigned successfully!"));
                                },
                            });
                        },
                        __("Assign to Contractor")
                    );
                }, __("Actions"));
            }

            if (frm.doc.status !== "Resolved" && frm.doc.status !== "Closed") {
                frm.add_custom_button(__("Mark Resolved"), function () {
                    frappe.prompt(
                        {
                            label: __("Resolution Notes"),
                            fieldname: "notes",
                            fieldtype: "Small Text",
                            reqd: 1,
                        },
                        function (values) {
                            frappe.call({
                                method: "frappe.client.set_value",
                                args: {
                                    doctype: "Civic Issue",
                                    name: frm.doc.name,
                                    fieldname: {
                                        status: "Resolved",
                                        resolution_date: frappe.datetime.now_datetime(),
                                        resolution_notes: values.notes,
                                    },
                                },
                                callback: function () {
                                    frm.reload_doc();
                                    frappe.show_alert(__("Issue marked as resolved!"));
                                },
                            });
                        },
                        __("Resolution Notes")
                    );
                }, __("Actions"));
            }

            if (frm.doc.status === "Resolved") {
                frm.add_custom_button(__("Close Issue"), function () {
                    frappe.call({
                        method: "frappe.client.set_value",
                        args: {
                            doctype: "Civic Issue",
                            name: frm.doc.name,
                            fieldname: "status",
                            value: "Closed",
                        },
                        callback: function () {
                            frm.reload_doc();
                            frappe.show_alert(__("Issue closed."));
                        },
                    });
                }, __("Actions"));
            }

            // Show map if coordinates exist
            if (frm.doc.latitude && frm.doc.longitude) {
                frm.add_custom_button(__("View on Map"), function () {
                    window.open(
                        `https://maps.google.com/?q=${frm.doc.latitude},${frm.doc.longitude}`,
                        "_blank"
                    );
                }, __("Actions"));
            }
        }
    },
});
