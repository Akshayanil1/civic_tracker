app_name = "civic_tracker"
app_title = "Civic Tracker"
app_publisher = "Civic Tracker Contributors"
app_description = "Municipal SLA & Grievance Routing Engine for Citizen Issue Tracking"
app_email = "civictracker@example.com"
app_license = "mit"

app_logo_url = "/assets/civic_tracker/images/civic_logo.svg"
splash_image = "/assets/civic_tracker/images/civic_logo.svg"

add_to_apps_screen = [
    {
        "name": "civic_tracker",
        "logo": "/assets/civic_tracker/images/civic_logo.svg",
        "title": "Civic Tracker",
        "route": "/app/civic-issue",
        "type": "link",
    },
]

# Website route rules for public portal
website_route_rules = [
    {"from_route": "/report-issue", "to_route": "report-issue"},
    {"from_route": "/track-issue/<path:tracking_id>", "to_route": "track-issue"},
    {"from_route": "/api/method/civic_tracker.api.whatsapp.webhook_verify", "to_route": "api/method/civic_tracker.api.whatsapp.webhook_verify"},
    {"from_route": "/api/method/civic_tracker.api.whatsapp.webhook_receive", "to_route": "api/method/civic_tracker.api.whatsapp.webhook_receive"},
    {"from_route": "/city-map", "to_route": "city-map"},
    {"from_route": "/ward-leaderboard", "to_route": "ward-leaderboard"},
    {"from_route": "/proposals", "to_route": "proposals"},
    {"from_route": "/api/method/civic_tracker.api.iot.sensor_webhook", "to_route": "api/method/civic_tracker.api.iot.sensor_webhook"},
]

# Scheduled Jobs
scheduler_events = {
    "daily": [
        "civic_tracker.api.sla.check_overdue_issues",
        "civic_tracker.api.penalty.check_unpaid_penalties",
    ],
    "monthly": [
        "civic_tracker.api.predictive.generate_trend_report",
        "civic_tracker.api.predictive.pre_monsoon_forecasting",
    ],
}

# Document Events
doc_events = {
    "Civic Issue": {
        "on_update": [
            "civic_tracker.api.sla.on_civic_issue_update",
            "civic_tracker.api.penalty.auto_generate_penalty_on_close"
        ],
        "on_change": "civic_tracker.api.whatsapp.send_status_update_whatsapp",
    },
}

# Installation hooks
after_install = "civic_tracker.setup.create_modules"

# Jinja methods
jinja = {
    "methods": [
        "civic_tracker.utils.get_wards_for_select",
    ]
}

# Fixtures
fixtures = ["Workspace"]
