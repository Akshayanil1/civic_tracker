frappe.pages['mayor-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Mayor\'s Smart City Predictive Dashboard',
        single_column: true
    });

    $(wrapper).bind('show', function() {
        render_dashboard(page);
    });
};

function render_dashboard(page) {
    page.main.empty();
    $(`<div class="row">
        <div class="col-md-6">
            <div id="chart-seasonal" class="card" style="padding: 15px; margin-bottom: 20px;"></div>
        </div>
        <div class="col-md-6">
            <div id="chart-ward" class="card" style="padding: 15px; margin-bottom: 20px;"></div>
        </div>
    </div>`).appendTo(page.main);

    // Call an API to get chart data
    frappe.call({
        method: "civic_tracker.civic_tracker.page.mayor_dashboard.mayor_dashboard.get_dashboard_data",
        callback: function(r) {
            if (r.message) {
                new frappe.Chart("#chart-seasonal", {
                    data: r.message.seasonal_data,
                    title: "Seasonal Trend (Road & Drainage vs Months)",
                    type: 'bar',
                    colors: ['#7cd6fd', '#743ee2']
                });
                
                new frappe.Chart("#chart-ward", {
                    data: r.message.ward_data,
                    title: "High Risk Wards for Upcoming Monsoon",
                    type: 'percentage',
                    colors: ['#ffa3ef', '#light-blue']
                });
            }
        }
    });
}
