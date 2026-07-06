# IELTS Speaking Part 2 & 3 - Cue Card Script

**Cue Card Prompt:**
Describe a complex project you successfully developed.
You should say:
- What the project was
- Why you decided to develop it
- What difficulties you faced
- And explain how you overcame those difficulties to complete it successfully.

### Practice Script for Recording (Target: 2 Minutes Continuous Speech)

"I'd like to talk about a highly complex software architecture project I independently engineered recently, called the Civic SLA Engine. Essentially, it is an open-source, headless ERP platform designed to automate municipal grievance tracking in India. 

I decided to develop this platform because I noticed a systemic lack of accountability in urban infrastructure management. Citizens would report hazards, like potholes or broken pipes, but without strict Service Level Agreements—or SLAs—tied to financial consequences, contractors often ignored them. I wanted to build a system that algorithmically enforced these deadlines.

The primary difficulty I faced during development was scaling the ingestion pipeline without overwhelming the database with spam. Because the system was omnichannel—accepting data from web portals, a Meta WhatsApp bot, and IoT sensors—the volume of data was immense. 

To overcome this, I integrated a sophisticated artificial intelligence layer using Vision APIs and Natural Language Processing. Instead of allowing direct database insertion, the AI acts as a triage mechanism. It analyzes uploaded images to reject non-civic photos and calculates sentiment scores to instantly route high-urgency crises. Furthermore, to manage the heavy SLA penalty calculations, I implemented an asynchronous processing architecture utilizing Redis background queues. This ensured the main server thread remained unblocked, even under heavy load. 

Ultimately, successfully deploying this multi-tenant SaaS taught me invaluable lessons in distributed systems and technical leadership, and I'm incredibly proud of the open-source community it has begun to foster."
