import frappe
import json
import requests
from frappe.utils import get_url

def get_ai_settings():
    return frappe.get_doc("Civic Tracker AI Settings")

def validate_image_with_ai(image_url):
    """
    Day 38: AI Image Validation
    Sends the image URL to the Vision API with the prompt:
    "Does this image contain a civic infrastructure issue like a pothole, garbage, or broken pipe? Return YES or NO."
    """
    settings = get_ai_settings()
    if not settings.enable_ai_triage or not settings.api_key:
        return True # Default to valid if AI is disabled

    prompt = "Does this image contain a civic infrastructure issue like a pothole, garbage, or broken pipe? Return YES or NO."
    full_url = get_url(image_url) if image_url.startswith("/") else image_url
    
    # Mocking actual API calls based on provider
    if settings.ai_provider == "OpenAI":
        # Mocking OpenAI Vision API call
        # Actual implementation would be:
        # headers = {"Authorization": f"Bearer {settings.get_password('api_key')}"}
        # payload = { "model": "gpt-4-vision-preview", "messages": [ ... ] }
        # r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        # response_text = r.json().get("choices")[0].get("message").get("content")
        response_text = "YES" # Mocked for testing
    else:
        # Mocking Gemini Vision API call
        response_text = "YES" # Mocked for testing
        
    return "NO" not in response_text.upper()

def analyze_issue_text(description):
    """
    Day 40 & 41: NLP-Based Automated Triaging & Sentiment Analysis
    Analyzes citizen's text description using an LLM.
    Returns categorized issue_type and urgency_score.
    """
    settings = get_ai_settings()
    if not settings.enable_ai_triage or not settings.api_key:
        return None, None # Fallback

    prompt = f"""
    Analyze the following civic issue description: "{description}"
    1. Categorize it into one of these: Road, Water, Sanitation, Electricity, Garbage, Drainage, Street Light, Other.
    2. Rate the citizen's frustration/urgency level from 1 to 10 based on the text.
    Return JSON format exactly like this: {{"category": "Water", "urgency_score": 8}}
    """
    
    # Mocking actual API call
    # response_text = call_llm(prompt, settings)
    
    # Simple keyword-based mock for testing purposes
    category = "Other"
    urgency_score = 5
    
    text = description.lower()
    if "tap is dry" in text or "water" in text:
        category = "Water"
    elif "pothole" in text or "road" in text:
        category = "Road"
    elif "garbage" in text or "trash" in text:
        category = "Garbage"
        
    if "emergency" in text or "help immediately" in text or "dying" in text or "urgent" in text:
        urgency_score = 9
    elif "angry" in text or "frustrated" in text or "terrible" in text:
        urgency_score = 7
        
    return category, urgency_score

def dynamic_assignment_routing(issue_doc):
    """
    Day 42: Dynamic assignment rule
    If categorized as 'Water' AND Urgency Score > 8, bypass standard routing and immediately SMS the Ward Commissioner.
    """
    settings = get_ai_settings()
    if not settings.enable_ai_triage:
        return
        
    threshold = settings.emergency_urgency_threshold or 8
    
    if issue_doc.issue_type == "Water" and issue_doc.urgency_score > threshold:
        # Emergency! SMS Ward Commissioner
        ward_doc = frappe.get_doc("Municipal Ward", issue_doc.ward)
        commissioner_name = ward_doc.commissioner_name or "Commissioner"
        # Simulate SMS
        frappe.log_error(
            f"EMERGENCY SMS to {commissioner_name} for Ward {issue_doc.ward}: Water issue '{issue_doc.issue_title}' needs immediate intervention!",
            "Dynamic Assignment Bypass"
        )
        # We can also create a ToDo or assign to a specific high-priority user
        issue_doc.priority = "Critical"
