// Civic Tracker - Desk Customizations
frappe.provide('civic_tracker');

$(document).ready(function () {
    // Add civic tracker branding
    if (frappe.get_route()[0] === 'civic-dashboard') {
        loadCivicDashboard();
    }
});

function loadCivicDashboard() {
    frappe.call({
        method: 'civic_tracker.api.dashboard.get_dashboard_stats',
        callback: function (r) {
            if (r.message) {
                renderDashboardStats(r.message);
            }
        }
    });
}

function renderDashboardStats(data) {
    const container = $('<div class="civic-dashboard-stats"></div>');
    // Stats will be rendered by the dashboard page
}
