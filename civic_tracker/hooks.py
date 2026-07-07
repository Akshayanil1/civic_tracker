# hooks.py for Civic Tracker

app_name = "civic_tracker"
app_title = "Civic Tracker"
app_publisher = "Akshay Anilkumar"
app_description = "Civic Tracker GovTech ERP"
app_email = "akshayy.anill@gmail.com"
app_license = "mit"

doc_events = {
    "Civic Issue": {
        "before_insert": [
            "civic_tracker.api.ai.validate_civic_issue_image"
        ],
        "after_insert": [
            "civic_tracker.api.clustering.cluster_duplicates"
        ],
        "on_update": [
            "civic_tracker.api.geofence.validate_resolution_location",
            "civic_tracker.api.accounting.generate_journal_entry"
        ]
    }
}

scheduler_events = {
    "daily": [
        "civic_tracker.api.sla_engine.check_overdue_issues",
        "civic_tracker.api.sla_engine.check_unpaid_penalties"
    ],
    "weekly": [
        "civic_tracker.api.dispatch.dispatch_monday_pdfs",
        "civic_tracker.api.reporting.generate_weekly_csv_dump"
    ]
}
