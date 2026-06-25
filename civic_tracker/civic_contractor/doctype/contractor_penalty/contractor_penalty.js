frappe.ui.form.on("Contractor Penalty", {
    refresh: function (frm) {
        if (!frm.is_new() && frm.doc.status === "Draft") {
            frm.add_custom_button(__("Approve Penalty"), function () {
                frappe.call({
                    method: "frappe.client.set_value",
                    args: {
                        doctype: "Contractor Penalty",
                        name: frm.doc.name,
                        fieldname: {
                            status: "Approved",
                            approved_by: frappe.session.user,
                        },
                    },
                    callback: function () {
                        frm.reload_doc();
                        frappe.show_alert(__("Penalty approved."));
                    },
                });
            }, __("Actions"));
        }

        if (!frm.is_new() && frm.doc.status === "Approved") {
            frm.add_custom_button(__("Create Purchase Invoice Deduction"), function () {
                frappe.call({
                    method: "civic_tracker.api.penalty.create_invoice_deduction",
                    args: { penalty_name: frm.doc.name },
                    callback: function (r) {
                        if (r.message) {
                            frm.reload_doc();
                            frappe.show_alert(__("Invoice deduction created: " + r.message));
                        }
                    },
                });
            }, __("Actions"));

            frm.add_custom_button(__("Waive Penalty"), function () {
                frappe.prompt(
                    {
                        label: __("Reason for Waiver"),
                        fieldname: "reason",
                        fieldtype: "Small Text",
                        reqd: 1,
                    },
                    function (values) {
                        frappe.call({
                            method: "frappe.client.set_value",
                            args: {
                                doctype: "Contractor Penalty",
                                name: frm.doc.name,
                                fieldname: {
                                    status: "Waived",
                                    reason: values.reason,
                                },
                            },
                            callback: function () {
                                frm.reload_doc();
                                frappe.show_alert(__("Penalty waived."));
                            },
                        });
                    },
                    __("Waive Penalty")
                );
            }, __("Actions"));
        }
    },

    civic_issue: function (frm) {
        if (frm.doc.civic_issue) {
            frappe.call({
                method: "frappe.client.get",
                args: { doctype: "Civic Issue", name: frm.doc.civic_issue },
                callback: function (r) {
                    if (r.message) {
                        var issue = r.message;
                        frm.set_value("sla_deadline", issue.escalation_time);
                        frm.set_value("resolution_date", issue.resolution_date || frappe.datetime.now_datetime());
                        frm.set_value("ward", issue.ward);
                        frm.set_value("issue_type", issue.issue_type);
                        frm.set_value("contractor", issue.assigned_contractor);

                        // Calculate overdue
                        if (issue.escalation_time) {
                            var esc = moment(issue.escalation_time);
                            var res = moment(issue.resolution_date || frappe.datetime.now_datetime());
                            var hours_diff = res.diff(esc, "hours", true);
                            if (hours_diff > 0) {
                                frm.set_value("hours_overdue", hours_diff.toFixed(1));
                                frm.set_value("days_overdue", (hours_diff / 24).toFixed(1));
                            }
                        }
                    }
                },
            });
        }
    },
});
