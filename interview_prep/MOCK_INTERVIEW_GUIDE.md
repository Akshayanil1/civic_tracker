# Mock Technical Interview Guide

Use this guide to practice explaining the deep technical decisions of your architecture aloud. Focus on clear pronunciation, pacing, and avoiding filler words (um, like).

## Question 1: "Why did you choose the Frappe Framework instead of building a backend from scratch with Django/Express?"

**Key Talking Points:**
- **Time-to-Value:** Mention that Frappe provides built-in RBAC (Role-Based Access Control), an excellent ORM, and automated REST API generation.
- **Background Jobs:** Highlight Frappe's native integration with Redis Queue for handling the asynchronous SLA penalty calculations.
- **Multi-Tenancy:** Discuss how Frappe's `bench` utility allows for true multi-tenant scaling (one codebase, multiple isolated MariaDB databases), which was crucial for a state-wide GovTech platform.

## Question 2: "Explain how you handled the AI integration. Why put it in the `before_insert` hook?"

**Key Talking Points:**
- **Database Integrity:** Explain that putting the AI Vision validation in the `before_insert` document lifecycle prevents spam from ever hitting the database or triggering downstream assignment rules.
- **Synchronous vs. Asynchronous:** Acknowledge the trade-off. Mention that while calling an external API synchronously during database insertion adds latency, it was necessary for immediate validation and spam rejection. For heavier tasks, you would move it to a background worker.

## Question 3: "How does the offline-first mobile app work?"

**Key Talking Points:**
- **Local Storage:** Explain the use of `AsyncStorage` (or SQLite) in React Native.
- **Queueing Strategy:** Describe how, when a field worker hits "Resolve" without an internet connection, the payload (issue ID, notes, base64 image) is serialized into a local queue array.
- **Network Listener:** Mention the use of `NetInfo` to listen for network state changes. Once a connection is detected, a background sync manager iterates over the queue and executes the REST POST requests, updating the local state upon success.

## Question 4: "How did you ensure the system could handle a massive spike in traffic, like during a monsoon?"

**Key Talking Points:**
- **Locust Load Testing:** Mention writing Python scripts in Locust to simulate 10,000 concurrent citizens submitting JSON payloads.
- **Nginx Security:** Explain that you configured Nginx with strict `limit_req_zone` rules (10 requests/second per IP) to prevent DDoS attacks, alongside essential headers like CSP, X-XSS-Protection, and Strict-Transport-Security.
