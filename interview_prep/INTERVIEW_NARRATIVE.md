# 2-Minute Interview Narrative (Elevator Pitch)

*Use this framework when asked: "Tell me about a complex project you worked on," or "Describe a problem you solved using technology."*

### The Hook (0:00 - 0:15)
"One of the most complex projects I’ve engineered is Civic Tracker, an open-source, multi-tenant GovTech ERP. I built it to solve a systemic problem in Indian municipalities: the lack of strict Service Level Agreement (SLA) accountability when contractors fail to fix civic hazards like potholes or flooded streets."

### The Technical Complexity (0:15 - 1:00)
"The core challenge was orchestrating a massive, multi-modal ingestion pipeline while preventing the system from being overwhelmed by spam. I utilized the Frappe Framework as a Headless ERP to manage the relational data. To handle ingestion, I integrated web forms, a Meta WhatsApp bot, and even automated IoT sensor webhooks. 

To filter the noise, I hooked an AI layer directly into the database’s pre-insert lifecycle. It uses Vision AI to reject invalid photos and Natural Language Processing to analyze sentiment, calculating an 'Urgency Score' that can dynamically bypass standard routing for extreme crises."

### The Impact / Scale (1:00 - 1:45)
"However, the real engineering feat was the financial enforcement engine. I utilized asynchronous Redis background jobs to constantly monitor SLA deadlines across isolated, multi-tenant databases. If a contractor breaches their deadline, the system automatically triggers a financial penalty and generates a Razorpay UPI link for instant clearance, logging the transaction via webhooks. I also built a React Native offline-first mobile app with local SQLite syncing for field workers without 4G."

### The Conclusion (1:45 - 2:00)
"Ultimately, I load-tested the Nginx layer with 10,000 concurrent requests to ensure it survives a 'monsoon crisis.' Building this system taught me how to scale distributed architecture, securely manage multi-tenant environments, and pragmatically apply machine learning to solve critical public sector issues."
