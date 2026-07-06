# Civic Tracker Live Webinar: Run of Show & Script

**Title:** Building an AI-Driven Smart City ERP in Python & Frappe  
**Platform:** YouTube Live / LinkedIn Live  
**Target Duration:** 45 Minutes  

## Pre-Stream Checklist
- [ ] Share the YouTube link on LinkedIn, Twitter, and Dev.to.
- [ ] Ensure Frappe Bench is running locally (`bench start`).
- [ ] Have the GitHub repository open in a browser tab.
- [ ] Have Postman/Insomnia open to demonstrate the Open Data API.

---

## 1. The Introduction (0:00 - 5:00)
**Goal:** Hook the audience and establish technical authority.
**Script Idea:** 
> "Hello everyone, and welcome! I’m [Your Name], and today I’m going to show you how I built an enterprise-scale, open-source GovTech platform called Civic Tracker. We’re going to dive deep into the Frappe framework, look at how to hook an AI Vision model directly into a database lifecycle, and explore how to handle multi-tenant architecture."

## 2. Architecture Overview (5:00 - 15:00)
**Goal:** Clearly explain the system design (excellent practice for IELTS speaking).
**Action:** Share your screen and display the Mermaid diagram or Excalidraw architecture.
**Talking Points:**
- The problem with traditional civic reporting (lack of SLAs).
- How the Headless ERP solves this by decoupling the Next.js frontend from the MariaDB backend.
- The multi-modal ingestion pipeline (Web, WhatsApp, IoT).

## 3. Live Code Walkthrough: AI Triage (15:00 - 25:00)
**Goal:** Show them the code.
**Action:** Open VS Code. Navigate to `civic_tracker/api/ai.py` and `civic_issue.py`.
**Talking Points:**
- Walk through the `before_insert` document hook.
- Explain how the payload is paused, sent to the OpenAI Vision API, and validated before being committed to the database.
- Highlight the NLP sentiment analysis function that calculates the `Urgency Score`.

## 4. Live Code Walkthrough: Asynchronous Penalties (25:00 - 35:00)
**Goal:** Demonstrate knowledge of background processing and cron jobs.
**Action:** Open `hooks.py` and `penalty.py`.
**Talking Points:**
- Show the Redis-backed `scheduler_events`.
- Explain the logic: "If the issue is past the SLA deadline, generate a Contractor Penalty."
- Discuss the FinTech integration (Razorpay) for instant clearance.

## 5. Q&A and Call to Action (35:00 - 45:00)
**Goal:** Build community and drive GitHub stars.
**Script Idea:**
> "That wraps up the core architecture of Civic Tracker. I’d love to answer any questions in the chat. Also, if you’re a junior developer looking for open-source experience, head over to the GitHub repo—I’ve tagged several 'Good First Issues' that you can tackle today. Please drop a star on the repo if you found this valuable!"
