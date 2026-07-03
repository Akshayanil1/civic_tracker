# Civic SLA Engine - Technical Portfolio

**Name:** Developer  
**GitHub:** github.com/Akshayanil1/civic_tracker  
**Tech Stack:** Python, Frappe Framework, React Native, Redis, MariaDB, OpenAI API, Nginx  

## 1. Project Overview
Civic Tracker is an enterprise-scale, open-source GovTech SaaS designed to enforce Service Level Agreements (SLAs) for municipal contractors. It transitions bureaucratic grievance redressal into an automated, financially accountable ecosystem.

## 2. System Architecture
- **Headless ERP Core:** Built on the Frappe framework, managing complex relational data (Wards, Contractors, SLAs) with native Role-Based Access Control.
- **Multi-Tenant SaaS:** Configured for state-wide deployment. A Global Master Control server programmatically provisions isolated databases for individual municipalities sharing a single codebase.
- **Offline-First Mobile App:** Developed a React Native field worker application utilizing `AsyncStorage`. Contractors can close issues in remote areas, with a background sync manager executing the REST API payloads once connectivity is restored.

## 3. Artificial Intelligence Integration
To ensure data integrity and triage emergencies:
- **Spam Prevention (Vision AI):** A pre-insert database hook intercepts image payloads. If the Vision API determines the image does not depict civic infrastructure, the submission is rejected.
- **Dynamic Routing (NLP):** Natural Language Processing categorizes the issue text and generates a 1-10 Sentiment Urgency Score, triggering immediate SMS bypass routing for extreme crises.

## 4. Performance & Load Testing
- **Concurrency Resilience:** Load-tested using Locust, successfully simulating 10,000 concurrent "monsoon crisis" reports without dropping database transactions.
- **Security Hardening:** Secured the Frappe monolith with Nginx-level strict Rate Limiting (10 req/s per IP), XSS filters, and CSP headers to mitigate DDoS attacks against the public APIs.

## 5. Financial & Open Data Modules
- **Automated Deductions:** Redis cron jobs evaluate SLA breaches nightly, automatically generating financial penalties tied directly to contractor ERPNext Purchase Invoices.
- **FinTech Integration:** Integrates Razorpay Python SDK to generate instant UPI payment links for penalty clearance via webhook listeners.
- **Civic Transparency:** Exposes a PII-scrubbed Open Data REST API and auto-generates weekly CSV dumps for researchers and data scientists.
