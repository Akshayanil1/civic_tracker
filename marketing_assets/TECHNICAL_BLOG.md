# How I Built an AI-Powered Smart City ERP in 60 Days

*(To be published on Hashnode, Dev.to, and Medium)*

## The Problem
Infrastructure management in rapidly growing cities often lacks strict accountability. A citizen reports a pothole, but without a binding Service Level Agreement (SLA) tied to financial consequences, the issue languishes. 

I decided to solve this by building **Civic SLA Engine**, an open-source GovTech ERP.

## The Stack
I needed a robust ORM, Role-Based Access Control, and background job scheduling out of the box. I chose the **Frappe Framework** (Python/MariaDB) and treated it as a Headless ERP.

## Core Features & Architecture

### 1. Multi-Modal Ingestion
The system accepts issues via a Next.js web portal, a Meta WhatsApp Bot, and direct IoT webhooks (for smart sensors). 

### 2. The AI Triage Layer
To prevent spam, I hooked an OpenAI/Gemini Vision API into Frappe's `before_insert` document lifecycle.
```python
def before_insert(self):
    if self.issue_image:
        is_valid = validate_image_with_ai(self.issue_image)
        if not is_valid:
            self.status = "Spam"
```
Simultaneously, NLP categorizes the issue and scores the user's sentiment (1-10) to dynamically bypass routing and alert officials during emergencies.

### 3. Hitting the Bottom Line (Automated Penalties)
Using Redis-backed crons, the system checks open tickets. If a contractor breaches their SLA deadline, the system automatically generates a penalty and deducts it from their ERPNext invoice. Razorpay integration allows them to clear these dues instantly via UPI.

## Scaling to SaaS
I scaled this into a multi-tenant architecture, allowing a central master server to automatically provision isolated databases for new municipalities, and built a React Native offline-first mobile app for field contractors to sync resolution photos without internet.

## Conclusion
Tech can drive civic accountability. Check out the full source code and documentation on [GitHub](https://github.com/Akshayanil1/civic_tracker).
