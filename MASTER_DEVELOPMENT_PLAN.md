# SYSTEM INSTRUCTIONS: CIVIC TRACKER - MASTER DEVELOPMENT PLAN

## 1. Project Vision
**Civic Tracker** aims to be the definitive open-source, headless ERP platform for enforcing Service Level Agreements (SLAs) for municipal contractors. By combining AI triage, IoT webhooks, geospatial validation, and automated financial penalties, this project provides a scalable blueprint for Smart City governance.

## 2. Phased Development Roadmap

### Phase 1: Core Foundation & Data Modeling
- **Environment Setup:** Initialize Frappe Framework (Python/MariaDB) and configure Multi-Tenant architecture.
- **Doctype Creation:** Build core doctypes including `Civic Issue`, `Civic Contractor`, `Municipal Ward`, `Issue SLA`, and `Standard Repair Cost`.
- **Assignment Logic:** Implement Frappe Assignment Rules to automatically map issues to contractors based on Ward and Issue Type.
- **Background Job Queue:** Set up Redis and Frappe scheduler events (`hooks.py`) for automated task management.

### Phase 2: Multichannel Ingestion & IoT Automation
- **WhatsApp Integration:** Develop Meta Webhook handlers (`api/whatsapp.py`) for omnichannel issue reporting via conversational SMS.
- **M2M Endpoints:** Create robust API endpoints (`api/iot.py`) to accept automated JSON payloads from IoT devices like smart bins and flood sensors.
- **RESTful API:** Build Open Data APIs (`api/public.py`, `api/geojson.py`) for public transparency, leaflet.js maps, and third-party dashboards.

### Phase 3: AI-Powered Triage & Spam Prevention (Version 4.0)
- **Vision AI Validation:** Integrate OpenAI/Gemini Vision API (`api/ai.py`) in `before_insert` hooks to reject non-civic image uploads and prevent spam.
- **NLP Sentiment Analysis:** Implement LLM-based parsing of issue descriptions to assign departments and compute an `Urgency Score` (1-10).
- **Spatial Clustering:** Develop background tasks (`api/clustering.py`) to auto-merge duplicate issues reported within a 100m radius.

### Phase 4: SLA Enforcement & Financial Penalties
- **Automated Monitoring:** Implement daily scheduled jobs (`check_overdue_issues`) to monitor SLA deadlines.
- **Penalty Generation:** Automatically generate `Contractor Penalty` records for breached SLAs.
- **FinTech Integration:** Integrate Razorpay SDK (`api/payment.py`) to generate secure UPI payment links and handle webhook updates for instant penalty clearance.
- **ERP Integration:** Build `api/accounting.py` to auto-generate ERPNext Journal Entries and Purchase Invoices for vendor deductions.

### Phase 5: Field Operations & Geofencing (Mobile First - Version 5.0)
- **Mobile App Development:** Build an offline-first React Native app (`mobile_app/`) for field workers.
- **Offline Sync:** Implement `AsyncStorage` caching (`sync.js`) and robust push logic to Frappe APIs when internet is restored.
- **Geofence Validation:** Utilize `geopy` (`api/geofence.py`) on `on_update` hooks to ensure "Actual Resolution" photos are taken within 50 meters of the original issue coordinates.

### Phase 6: Reporting & Civic Transparency
- **Automated Reporting:** Schedule `dispatch_monday_pdfs` (`api/dispatch.py`) to generate and email PDF summary reports to Ward Commissioners weekly.
- **Public Dashboards:** Expose Ward Leaderboards and a Participatory Budgeting module to allow citizens to vote on infrastructure proposals.
- **Predictive Analytics:** Implement `generate_trend_report` and `pre_monsoon_forecasting` to identify recurring failure points.

## 3. Technology Stack & Deployment
- **Backend Core:** Frappe, Python 3.10+, MariaDB, Redis
- **Integrations:** Meta Cloud API, OpenAI/Gemini, Razorpay, ERPNext
- **Frontend / Mobile:** React Native, Vanilla JS, Leaflet.js
- **Testing & Security:** Locust for Load Testing, Nginx (Rate limiting & CSP)
- **CI/CD:** GitHub Actions (Automated testing with Frappe Docker containers)

## 4. Key Success Metrics
1. **SLA Compliance Rate:** Achieve >90% on-time resolution for critical issues.
2. **AI Triage Accuracy:** Reduce manual triage time by 80% with Vision/NLP automation.
3. **Citizen Engagement:** Increase monthly active users reporting via WhatsApp by 50% year-over-year.
4. **Financial Accountability:** 100% automated collection or deduction of SLA penalties.
