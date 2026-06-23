# Civic Tracker

Municipal SLA & Grievance Routing Engine — An open-source civic administration system built on Frappe framework.

## Overview

Civic Tracker enables citizens to report municipal issues (potholes, garbage, water leaks, broken street lights) through a public web portal. Issues are automatically routed to the correct municipal ward, assigned to active contractors, and escalated via background jobs if Service Level Agreements (SLAs) are breached.

## Features

### Phase 1: Core Administrative Architecture
- **Municipal Ward** — Divide the city into wards with commissioner contact details
- **Civic Contractor** — Track contractor details, active contracts, and assigned wards
- **Civic Issue** — Full issue lifecycle with type, geo-coordinates, ward link, status, and image evidence
- **Auto-Assignment** — Frappe Assignment Rules automatically route issues to the right contractor

### Phase 2: Citizen Web Portal
- **Public Web Form** — Citizens submit issues without logging into the ERP backend
- **Geolocation** — Browser Geolocation API auto-populates latitude/longitude from mobile
- **Tracking System** — Unique Tracking IDs let citizens check issue status on the portal

### Phase 3: SLA Automation & Escalations
- **Issue SLA** — Define time limits per issue type (e.g., "Potholes must be fixed in 48 hours")
- **Daily Scheduled Job** — Background job checks open issues; marks overdue if escalation time exceeded
- **Automated Alerts** — Email notifications to Ward Commissioner/District Magistrate on SLA breach

### Phase 4: Executive Dashboards
- **Number Cards** — Total Open Issues, In Progress, Overdue, Resolved
- **Charts** — Issues by Type, Issues by Ward, Issues by Status
- **Executive Workspace** — Centralized dashboard for the Municipal Commissioner

## Installation

### Prerequisites
- Python 3.10+
- MariaDB 10.6+ or MySQL 8.0+
- Redis
- Node.js 16+ and npm

### Quick Setup with Frappe Bench

```bash
# Clone into your bench's apps directory
cd ~/frappe-bench/apps
git clone https://github.com/your-org/civic_tracker.git

# Install the app
bench --site your-site.local install-app civic_tracker

# Run migrations
bench --site your-site.local migrate

# Build assets
bench build

# Restart
bench restart
```

### Deploy via Frappe Cloud (Recommended for Municipalities)

1. Sign up at [Frappe Cloud](https://frappecloud.com)
2. Create a new site
3. Install the `civic_tracker` app from the app marketplace
4. Configure your Municipal Wards and Contractors
5. Share the public portal URL with citizens

### Deploy on a VPS

```bash
# Install bench
pip3 install frappe-bench

# Initialize a new bench
bench init frappe-bench
cd frappe-bench

# Get the app
bench get-app civic_tracker https://github.com/your-org/civic_tracker.git

# Create site
bench new-site civic.example.com
bench --site civic.example.com install-app civic_tracker
bench --site civic.example.com set-config -g serving_site_name civic.example.com

# Setup production
sudo bench setup production [user]
```

## Configuration

### 1. Create Municipal Wards
Go to **Civic Tracker > Municipal Ward** and create entries for each ward in your city.

### 2. Register Contractors
Go to **Civic Tracker > Civic Contractor** and add active contractors with their assigned wards and service types.

### 3. Define SLAs
Go to **Civic Tracker > Issue SLA** and configure time limits:
- **SLA Time** — Maximum hours to resolve the issue
- **Escalation Time** — Hours after which the issue is escalated
- **Escalation Recipients** — Ward Commissioner and District Magistrate emails

### 4. Enable Public Portal
The public forms are available at:
- **Report Issue:** `https://your-site/report-issue`
- **Track Issue:** `https://your-site/track-issue/{tracking-id}`

## Architecture

```
civic_tracker/
├── civic_tracker/
│   ├── api/
│   │   ├── sla.py          # SLA checking & escalation logic
│   │   ├── issue.py        # Issue submission & tracking API
│   │   └── dashboard.py    # Dashboard statistics API
│   ├── municipal_ward/     # Municipal Ward doctype
│   ├── civic_contractor/   # Civic Contractor doctype
│   ├── civic_issue/        # Civic Issue doctype
│   ├── issue_sla/          # Issue SLA doctype
│   ├── civic_tracker/
│   │   └── setup/          # Workspaces & number cards
│   ├── templates/
│   │   └── pages/
│   │       ├── report-issue.html  # Public issue submission form
│   │       └── track-issue.html   # Public issue tracking page
│   └── public/             # Static assets (JS, CSS, images)
├── hooks.py                # Frappe hooks & scheduler events
├── setup.py                # Package setup
├── pyproject.toml          # Build configuration
└── LICENSE                 # MIT License
```

## Doctypes

| Doctype | Purpose |
|---------|---------|
| `Municipal Ward` | City ward divisions with commissioner contacts |
| `Civic Contractor` | Contractor details, contracts, assigned wards |
| `Civic Issue` | Citizen-reported issues with full lifecycle |
| `Issue SLA` | Time limit definitions per issue type |
| `Contractor Ward Assignment` | Child table linking contractors to wards |
| `Contractor Service Type` | Child table for contractor service capabilities |
| `Issue Escalation Log` | Child table tracking escalation history |

## Scheduled Jobs

| Schedule | Function | Purpose |
|----------|----------|---------|
| Daily | `civic_tracker.api.sla.check_overdue_issues` | Mark overdue issues & send escalations |

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `civic_tracker.api.issue.submit_civic_issue` | Whitelisted | Submit issue from public portal |
| `civic_tracker.api.issue.get_issue_by_tracking_id` | Whitelisted | Track issue by ID |
| `civic_tracker.api.dashboard.get_dashboard_stats` | Whitelisted | Dashboard statistics |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on the [Frappe Framework](https://frappe.io/framework)
- Designed for civic accountability in Indian municipalities
- Inspired by the need for transparent, trackable citizen grievance systems
