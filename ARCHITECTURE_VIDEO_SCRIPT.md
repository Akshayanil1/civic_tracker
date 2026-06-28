# Architecture Breakdown Video Script (3 minutes)

**Title**: Civic Tracker - Architecture & AI Integration Showcase
**Speaker**: Developer (You)
**Target Audience**: Master's Admission Committee / Tech Recruiters

---

### [0:00 - 0:30] Introduction & Problem Statement
*(Visual: Screen share of the citizen portal and a congested Indian city street showing potholes/garbage)*

**Speaker:** 
"Hello! Welcome to my technical breakdown of Civic Tracker, a headless ERP platform I built to solve a massive problem in Indian municipalities: civic grievance accountability. 
The core challenge was that citizens report issues like potholes or overflowing garbage, but there was no systemic Service Level Agreement (SLA) to hold contractors financially accountable for delays. I wanted to build an automated, transparent engine to solve this."

### [0:30 - 1:15] Core Architecture (The Headless ERP)
*(Visual: Diagram showing WhatsApp & Web Portal -> Frappe Framework -> MariaDB -> Contractor Portals)*

**Speaker:** 
"At its core, Civic Tracker is built on the Frappe framework. 
When a citizen reports an issue—either via our custom Web Portal or our Meta Cloud API WhatsApp bot—the payload hits our high-throughput REST endpoints. 
Frappe acts as the orchestration layer. It automatically maps the geo-coordinates to a Municipal Ward and uses Frappe's Assignment Rules to route the ticket to the correct Civic Contractor.
Most importantly, it calculates a strict SLA deadline based on the issue type."

### [1:15 - 2:00] AI Triage & Spam Prevention
*(Visual: Code snippet of `before_insert` hook in `civic_issue.py` calling the Vision API and LLM)*

**Speaker:** 
"To prevent spam and prioritize emergencies, I integrated an AI layer in the document lifecycle. 
During the `before_insert` hook, the system sends any uploaded photo to a Vision API (like Gemini). If the AI determines the image doesn't contain civic infrastructure—like someone uploading a selfie—it automatically flags it as Spam and rejects the workflow.
Simultaneously, an LLM analyzes the citizen's text description to auto-categorize the issue and calculate an 'Urgency Score' using sentiment analysis. If a water crisis scores above an 8, the system bypasses standard routing and immediately SMS alerts the Ward Commissioner."

### [2:00 - 2:30] Financial Penalties & IoT
*(Visual: ERPNext Purchase Invoice deduction screen & IoT Webhook endpoint)*

**Speaker:**
"If a contractor breaches their SLA, background cron jobs managed by Redis Queue automatically generate a financial penalty and link it as a deduction to their ERPNext Purchase Invoice. 
In Version 3.0, we even bypassed human reporting entirely. I built rate-limited IoT endpoints that accept JSON payloads from Smart Garbage Bins, auto-generating high-priority issues when capacity exceeds 90%."

### [2:30 - 3:00] Open Data & Conclusion
*(Visual: Developer Portal screen showing the Open Data API and weekly CSV dumps)*

**Speaker:**
"Finally, for ultimate transparency, I built a public Open Data API and a Developer Portal. It strips out all Personally Identifiable Information and serves the resolved datasets to researchers and journalists, complete with weekly automated CSV dumps. 
By combining headless ERP logic, AI triage, and Open Data, Civic Tracker proves how modern tech can enforce real-world accountability. Thanks for watching!"
