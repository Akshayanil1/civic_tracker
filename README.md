# Civic Tracker: A Case Study in Civic SLA Accountability

**Using Headless ERPs and AI to Enforce Civic SLA Accountability in Indian Municipalities.**

---

## 1. Abstract

Urban infrastructure management in densely populated municipalities often suffers from a lack of accountability, opaque grievance redressal mechanisms, and delayed vendor responses. **Civic Tracker** is an open-source, headless ERP platform engineered to bridge the gap between citizen reporting and contractor execution. By leveraging the Frappe Framework, AI-driven triage, IoT ingestion, and automated financial penalties, this project demonstrates a highly scalable blueprint for Smart City governance.

---

## 2. The Problem Statement

In many municipal corporations:
1. **Citizens** lack a transparent, omnichannel method to report infrastructural decay (e.g., potholes, broken pipes).
2. **Administrators** struggle to categorize and route thousands of daily complaints to the correct localized contractor.
3. **Contractors** operate without strictly enforced Service Level Agreements (SLAs), leading to prolonged hazards.
4. There is no automated penalty mechanism tying a contractor's payout to their SLA compliance.

---

## 3. The Civic Tracker Solution

Civic Tracker addresses these bottlenecks through a four-tiered architecture:

### 3.1. Omnichannel Ingestion & IoT Automation
Citizens can report issues via a responsive Web Portal or a Meta Cloud API-integrated WhatsApp Bot. Additionally, Machine-to-Machine (M2M) endpoints allow "Smart Garbage Bins" and flood sensors to bypass human reporting entirely, pushing high-throughput JSON payloads to generate priority tickets automatically.

### 3.2. AI-Powered Triage & Spam Prevention (Version 4.0)
To prevent the system from being overwhelmed by spam, a multi-modal AI layer intercepts incoming payloads via Frappe's `before_insert` document hooks:
- **Vision AI Validation:** Image evidence is routed to a Vision API (OpenAI/Gemini). If the image lacks civic infrastructure context (e.g., selfies, random objects), the payload is rejected and marked as "Spam".
- **NLP Sentiment & Categorization:** An LLM analyzes the text descriptions to automatically map the grievance to departments (e.g., "Water", "Sanitation") and computes a 1-10 `Urgency Score` using sentiment analysis.

### 3.3. SLA Enforcement & Financial Penalties
Once mapped to a Municipal Ward, Frappe's Assignment Rules automatically route the issue to the active Civic Contractor. The system computes a strict SLA deadline. 
If the SLA is breached, Redis-backed scheduled jobs automatically generate a **Contractor Penalty** record. If integrated with ERPNext, this penalty is directly inserted as a deduction item in the contractor's monthly Purchase Invoice, hitting their bottom line.

### 3.4. Civic Transparency & Open Data
Accountability is a two-way street. The platform provides:
- **Ward Leaderboards:** A competitive ranking of municipal wards based on SLA compliance and resolution speed.
- **Participatory Budgeting:** A module where citizens can securely vote on upcoming infrastructure proposals.
- **Open Data API:** A rate-limited, anonymized REST API and weekly CSV dumps for researchers, journalists, and data scientists to build independent dashboards.

---

## 4. Technical Architecture

### Core Stack
- **Framework:** Frappe (Python/MariaDB)
- **Frontend:** Jinja Templates, Vanilla JS, Bootstrap, Leaflet.js (GIS Mapping)
- **AI Integration:** Python `requests` wrapped around Vision APIs and LLMs
- **CI/CD:** GitHub Actions (Automated testing with Frappe Docker containers)

### Document Lifecycle Diagram
```text
[ Citizen / WhatsApp / IoT Sensor ] 
         │ (POST JSON)
         ▼
[ Frappe API Routing ] 
         │
         ▼
[ AI Triage Hook ] ────(NO)────> [ Rejected / Marked Spam ]
         │ (YES)
         ▼
[ Civic Issue Created ]
         │ (Assign Ward & Contractor)
         ▼
[ SLA Timer Starts ] 
         │
    (SLA Breached) ────────────> [ Penalty Deduction (ERPNext) ]
         │
    (Resolved) ────────────────> [ Open Data API / Public Leaderboard ]
```

---

## 5. Key Modules Breakdown

| Module | Description |
|--------|-------------|
| **Civic Issue Engine** | The core headless ticket system with geo-coordinates, automated tracking IDs, and state transitions. |
| **Contractor & Penalty** | Manages vendors, active ward contracts, and automated financial deductions for SLA breaches. |
| **WhatsApp Bot** | Meta webhook integration for end-to-end ticketing via conversational SMS. |
| **Geospatial Analytics** | Live Leaflet.js maps and predictive Mayor Dashboards for preventative monsoon maintenance. |
| **Participatory Budgeting** | `Civic Proposal` and `Citizen Vote` doctypes to crowd-source capital expenditure priorities. |
| **Open Data Portal** | PII-scrubbed API endpoints and weekly CSV dumps for researchers. |

---

## 6. Installation & Deployment

### Prerequisites
- Python 3.10+
- MariaDB 10.6+ / Redis
- Node.js 18+

### Setup via Frappe Bench
```bash
bench get-app civic_tracker https://github.com/your-org/civic_tracker.git
bench --site your-site.local install-app civic_tracker
bench --site your-site.local migrate
```

---

## 7. Conclusion

By combining the robustness of Headless ERP workflows with modern Vision/NLP AI and public Open Data APIs, **Civic Tracker** provides a highly scalable, financially accountable engine for municipal governance. 

*This project was built as a capstone demonstration of advanced backend engineering, AI systems integration, and open-source civic tech development.*
