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
]

# Scheduled Jobs
scheduler_events = {
    "daily": [
        "civic_tracker.api.sla.check_overdue_issues",
    ],
}

# Document Events
doc_events = {
    "Civic Issue": {
        "on_update": "civic_tracker.api.sla.on_civic_issue_update",
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
