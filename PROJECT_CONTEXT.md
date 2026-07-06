# Civic Tracker: Project Context & Architecture

**Project Goal:** A headless ERP built on the Frappe framework designed to enforce Service Level Agreements (SLAs) for municipal contractors via AI triage, IoT webhooks, geospatial validation, and automated financial penalties.

## 1. Tech Stack
- **Backend/ORM:** Frappe Framework (Python)
- **Database:** MariaDB
- **Background Jobs:** Redis Queue (via Frappe `enqueue` and `scheduler_events`)
- **Mobile App:** React Native (Offline-first with `AsyncStorage`)
- **Integrations:** Meta WhatsApp Cloud API, OpenAI/Gemini Vision AI, Razorpay Python SDK, ERPNext (Journal Entries/Purchase Invoices)
- **Web Frontend:** Next.js (conceptual), Jinja Templates, Vanilla JS, Leaflet.js
- **Load Testing & Security:** Locust (Python), Nginx (Rate limiting & CSP)

## 2. Core Doctypes & Data Models
- **`Civic Issue`:** The central state machine tracking citizen grievances.
  - *Key Fields:* `issue_type`, `priority`, `status` (Open, Assigned, In Progress, Resolved, Closed, Overdue, Reopened, Spam, Merged), `ward`, `assigned_contractor`, `latitude`, `longitude`, `actual_resolution_lat_lng`, `urgency_score`, `master_issue`.
  - *Hooks (`before_insert`):* Vision AI spam check, NLP sentiment analysis & dynamic routing.
  - *Hooks (`after_insert`):* Spatial duplicate clustering.
  - *Hooks (`on_update`):* SLA monitoring, Geofence validation (checks if resolution photo is within 50m of original coords), WhatsApp status updates, Journal Entry generation.
- **`Civic Contractor`:** Manages municipal vendors and their assigned wards.
- **`Municipal Ward`:** Represents the geographic boundary. Mapped to ERPNext `cost_center` and Ward Commissioner details for automated PDF dispatch.
- **`Contractor Penalty`:** Auto-generated when a contractor misses an SLA. Linked to Razorpay for UPI payments and ERPNext for invoice deductions.
- **`Issue SLA`:** Defines the timeline (e.g., Water = 24hrs, Road = 72hrs).
- **`Global Master Control` & `Municipal Tenant`:** Enables true multi-tenant SaaS provisioning, isolating state-wide municipal databases.
- **`Standard Repair Cost`:** Maps issue types to standard flat rates (e.g., Pothole = ₹1500) for automated journal entries.

## 3. Key APIs & Integrations (`civic_tracker/api/`)
- **`ai.py`:** Handles Vision API requests to validate issue photos (rejects selfies/non-civic images) and NLP to generate `urgency_score`.
- **`whatsapp.py`:** Meta Webhook handlers (`webhook_verify`, `webhook_receive`) for omnichannel issue ingestion via SMS.
- **`iot.py`:** M2M endpoints for smart sensors (e.g., flood sensors, smart bins) to automatically generate `Civic Issues`.
- **`clustering.py`:** Contains `cluster_duplicates`, invoked via background jobs to auto-merge identical issues submitted within a 100m radius.
- **`geofence.py` / `civic_issue.py`:** Uses `geopy.distance` to validate that a contractor's "Actual Resolution" coordinates are within 50m of the reported issue.
- **`payment.py`:** Razorpay integration generating secure payment links for SLA penalties and listening to webhooks (`razorpay_webhook`) to mark them as "Paid".
- **`accounting.py`:** Generates ERPNext Journal Entries (debiting ward Cost Center, crediting Contractor) when a Ward Commissioner closes a ticket.
- **`dispatch.py`:** Uses Frappe's `get_pdf()` to generate automated Monday Morning summary reports for Ward Commissioners.
- **`public.py` & `geojson.py`:** Rate-limited Open Data APIs scrubbing PII, exposing data for Leaflet.js maps and academic researchers.

## 4. Background Jobs (`hooks.py`)
- **Daily:** `check_overdue_issues` (flags missed SLAs), `check_unpaid_penalties`.
- **Weekly:** `generate_weekly_csv_dump` (Open Data), `dispatch_monday_pdfs` (Emails PDFs to commissioners every Monday at 6 AM).
- **Monthly:** `generate_trend_report`, `pre_monsoon_forecasting`.
- **Event-Driven (`on_update` / `after_insert`):** WhatsApp notifications, AI validations, Spatial Clustering, Geofencing, Auto-Journal Entries.

## 5. Mobile App (`mobile_app/`)
- Built in React Native.
- **Offline Sync (`sync.js`):** Field workers can resolve issues without 4G. Payloads are serialized to `AsyncStorage` and pushed to Frappe via REST API (`api.js`) once `NetInfo` detects connectivity.

## 6. How to Instruct an AI Agent
If you spawn a new AI agent to work on this repository, provide them with this document and tell them:
> *"You are working on the Civic Tracker GovTech ERP. Read `PROJECT_CONTEXT.md` to understand the architecture. We use Frappe as a Headless ERP, Redis for background jobs, and Python for custom API logic. Ensure all new features integrate seamlessly with our existing Multi-Tenant structure, AI triage hooks, and automated SLA mechanisms."*
