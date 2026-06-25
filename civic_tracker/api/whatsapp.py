"""
WhatsApp Bot Integration for Civic Tracker.

Implements Meta Cloud API webhook receiver for incoming WhatsApp messages,
message parsing to create Civic Issues, and outbound status notifications.

Configuration (in site_config.json):
    whatsapp_verify_token: Webhook verification token
    whatsapp_access_token: Meta Cloud API access token
    whatsapp_phone_number_id: WhatsApp Business phone number ID
    whatsapp_app_secret: Meta App secret for signature verification
"""

import frappe
import json
import hmac
import hashlib
from frappe.utils import now_datetime, get_url


WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"


def get_whatsapp_settings():
    """Retrieve WhatsApp configuration from site config."""
    return {
        "verify_token": frappe.conf.get("whatsapp_verify_token", "civic_tracker_webhook_verify"),
        "access_token": frappe.conf.get("whatsapp_access_token", ""),
        "phone_number_id": frappe.conf.get("whatsapp_phone_number_id", ""),
        "app_secret": frappe.conf.get("whatsapp_app_secret", ""),
    }


def verify_webhook_signature(payload_body, signature):
    """Verify the X-Hub-Signature-256 header from Meta."""
    settings = get_whatsapp_settings()
    app_secret = settings.get("app_secret")
    if not app_secret:
        return True  # Skip verification if secret not configured

    expected_signature = hmac.new(
        app_secret.encode("utf-8"),
        payload_body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(f"sha256={expected_signature}", signature or "")


@frappe.whitelist(allow_guest=True)
def webhook_verify():
    """WhatsApp webhook verification endpoint (GET).

    Meta sends a GET request with hub.mode, hub.verify_token, and hub.challenge
    to verify the webhook URL during setup.
    """
    mode = frappe.form_dict.get("hub.mode")
    token = frappe.form_dict.get("hub.verify_token")
    challenge = frappe.form_dict.get("hub.challenge")

    settings = get_whatsapp_settings()

    if mode == "subscribe" and token == settings["verify_token"]:
        frappe.response["type"] = "text"
        frappe.response["text"] = challenge
        return challenge

    frappe.throw("Webhook verification failed", frappe.AuthenticationError)


@frappe.whitelist(allow_guest=True)
def webhook_receive():
    """WhatsApp webhook receiver endpoint (POST).

    Receives incoming WhatsApp messages from Meta Cloud API,
    parses them, and creates Civic Issues in Frappe.
    """
    try:
        signature = frappe.request.headers.get("X-Hub-Signature-256", "")
        payload_body = frappe.request.get_data(as_text=True)

        if not verify_webhook_signature(payload_body, signature):
            frappe.throw("Invalid webhook signature", frappe.AuthenticationError)

        payload = json.loads(payload_body)
        process_webhook_payload(payload)

        return {"status": "ok"}

    except Exception as e:
        frappe.log_error(
            f"WhatsApp Webhook Error: {str(e)}",
            "WhatsApp Integration",
        )
        return {"status": "error", "message": str(e)}


def process_webhook_payload(payload):
    """Process the incoming WhatsApp webhook payload."""
    if not payload.get("entry"):
        return

    for entry in payload["entry"]:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            contacts = value.get("contacts", [])

            for message in messages:
                contact = next(
                    (c for c in contacts if c["wa_id"] == message["from"]),
                    {},
                )
                process_incoming_message(message, contact)


def process_incoming_message(message, contact):
    """Parse a single WhatsApp message and create a Civic Issue."""
    phone_number = message.get("from", "")
    message_type = message.get("type", "")
    citizen_name = contact.get("profile", {}).get("name", "WhatsApp User")

    description = ""
    image_url = None

    if message_type == "text":
        description = message.get("text", {}).get("body", "")
    elif message_type == "image":
        image_data = message.get("image", {})
        description = image_data.get("caption", "Issue reported via WhatsApp (image attached)")
        image_url = download_whatsapp_media(image_data.get("id"))
    elif message_type == "location":
        location = message.get("location", {})
        description = (
            f"Location-based issue report. "
            f"Lat: {location.get('latitude')}, Lon: {location.get('longitude')}. "
            f"Address: {location.get('name', 'N/A')}"
        )
    else:
        send_whatsapp_reply(
            phone_number,
            "\U0001f3db\ufe0f *Civic Tracker*\n\n"
            "Please send a *text description* of the issue, "
            "or share a *photo* with a caption describing the problem.\n\n"
            "You can also share your *location* to help us find the issue.",
        )
        return

    if not description or len(description.strip()) < 5:
        send_whatsapp_reply(
            phone_number,
            "\U0001f3db\ufe0f *Civic Tracker*\n\n"
            "Please provide a more detailed description of the civic issue "
            "(at least a few words).\n\n"
            "Example: _Large pothole on MG Road near the bus stop_",
        )
        return

    parsed = parse_issue_from_text(description)

    try:
        issue = frappe.get_doc({
            "doctype": "Civic Issue",
            "issue_title": parsed["title"],
            "issue_type": parsed["issue_type"],
            "description": description,
            "priority": parsed["priority"],
            "citizen_name": citizen_name,
            "citizen_phone": format_phone_number(phone_number),
            "status": "Open",
            "ward": get_default_ward(),
            "source_channel": "WhatsApp",
        })

        if image_url:
            issue.issue_image = image_url

        if message_type == "location":
            location = message.get("location", {})
            issue.latitude = location.get("latitude")
            issue.longitude = location.get("longitude")

        issue.insert(ignore_permissions=True)
        frappe.db.commit()

        portal_url = get_url(f"/track-issue/{issue.tracking_id}")
        send_whatsapp_reply(
            phone_number,
            f"\u2705 *Issue Registered Successfully!*\n\n"
            f"\U0001f4cb *Tracking ID:* `{issue.tracking_id}`\n"
            f"\U0001f4dd *Issue:* {issue.issue_title}\n"
            f"\U0001f4cc *Type:* {issue.issue_type}\n"
            f"\u23f0 *Status:* Open\n\n"
            f"\U0001f517 Track online: {portal_url}\n\n"
            f"_You will receive updates on this number as your issue progresses._",
        )

    except Exception as e:
        frappe.log_error(
            f"Failed to create issue from WhatsApp: {str(e)}",
            "WhatsApp Integration - Error",
        )
        send_whatsapp_reply(
            phone_number,
            "\u274c *Sorry, we couldn't register your issue.*\n\n"
            "Please try again or visit our web portal to report the issue.\n"
            f"\U0001f517 {get_url('/report-issue')}",
        )


def parse_issue_from_text(text):
    """Extract issue type, title, and priority from free-text message."""
    text_lower = text.lower()

    type_keywords = {
        "Road": ["road", "pothole", "crack", "asphalt", "footpath", "pavement", "highway", "bridge"],
        "Water": ["water", "leak", "pipe", "tap", "supply", "flooding", "borewell", "tank"],
        "Sanitation": ["sanitation", "toilet", "sewage", "drain", "hygiene", "clean"],
        "Electricity": ["electricity", "power", "cable", "transformer", "pole", "wire", "outage", "blackout"],
        "Garbage": ["garbage", "waste", "trash", "dustbin", "dump", "litter", "rubbish"],
        "Drainage": ["drainage", "gutter", "manhole", "sewer", "clog", "overflow", "waterlog"],
        "Street Light": ["light", "lamp", "bulb", "street light", "streetlight", "dark"],
    }

    issue_type = "Other"
    for itype, keywords in type_keywords.items():
        if any(kw in text_lower for kw in keywords):
            issue_type = itype
            break

    priority = "Medium"
    high_priority_words = ["urgent", "emergency", "dangerous", "critical", "immediate", "serious", "severe"]
    low_priority_words = ["minor", "small", "slight", "little"]

    if any(word in text_lower for word in high_priority_words):
        priority = "High"
    elif any(word in text_lower for word in low_priority_words):
        priority = "Low"

    title = text.split(".")[0].split("\n")[0][:80].strip()
    if len(title) < 5:
        title = f"{issue_type} issue reported via WhatsApp"

    return {
        "title": title,
        "issue_type": issue_type,
        "priority": priority,
    }


def format_phone_number(wa_id):
    """Format WhatsApp ID to a displayable phone number."""
    if wa_id and not wa_id.startswith("+"):
        return f"+{wa_id}"
    return wa_id


def get_default_ward():
    """Return the first available ward as default for WhatsApp issues."""
    ward = frappe.db.get_value("Municipal Ward", {}, "name", order_by="name asc")
    return ward or None


def download_whatsapp_media(media_id):
    """Download media from WhatsApp Cloud API and save as Frappe file."""
    if not media_id:
        return None

    settings = get_whatsapp_settings()
    access_token = settings.get("access_token")
    if not access_token:
        return None

    try:
        import requests

        # Step 1: Get media URL
        media_url_response = requests.get(
            f"{WHATSAPP_API_URL}/{media_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30,
        )
        media_url_response.raise_for_status()
        media_url = media_url_response.json().get("url")

        if not media_url:
            return None

        # Step 2: Download the actual file
        file_response = requests.get(
            media_url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=60,
        )
        file_response.raise_for_status()

        # Step 3: Save as Frappe file
        content_type = file_response.headers.get("Content-Type", "image/jpeg")
        extension = content_type.split("/")[-1].split(";")[0]
        filename = f"whatsapp_{media_id}.{extension}"

        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "content": file_response.content,
            "is_private": 0,
        })
        file_doc.save(ignore_permissions=True)
        return file_doc.file_url

    except Exception as e:
        frappe.log_error(
            f"Failed to download WhatsApp media {media_id}: {str(e)}",
            "WhatsApp Media Download",
        )
        return None


def send_whatsapp_reply(to_phone, message_text):
    """Send a WhatsApp text reply via Meta Cloud API."""
    settings = get_whatsapp_settings()
    access_token = settings.get("access_token")
    phone_number_id = settings.get("phone_number_id")

    if not access_token or not phone_number_id:
        frappe.log_error(
            f"WhatsApp not configured. Cannot send to {to_phone}: {message_text}",
            "WhatsApp Outbound",
        )
        return False

    try:
        import requests

        response = requests.post(
            f"{WHATSAPP_API_URL}/{phone_number_id}/messages",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "text",
                "text": {"body": message_text},
            },
            timeout=30,
        )
        response.raise_for_status()
        return True

    except Exception as e:
        frappe.log_error(
            f"WhatsApp send error to {to_phone}: {str(e)}",
            "WhatsApp Outbound Error",
        )
        return False


def send_status_update_whatsapp(doc, method):
    """Send a WhatsApp status update when a Civic Issue status changes.

    Called from the doc_events hook on Civic Issue.
    """
    try:
        if not doc.citizen_phone:
            return

        phone = doc.citizen_phone
        wa_phone = phone.lstrip("+")

        status_emoji = {
            "Open": "\U0001f7e1",
            "Assigned": "\U0001f535",
            "In Progress": "\U0001f527",
            "Resolved": "\u2705",
            "Closed": "\u2714\ufe0f",
            "Overdue": "\U0001f534",
            "Reopened": "\U0001f504",
        }

        emoji = status_emoji.get(doc.status, "\U0001f4cb")
        portal_url = get_url(f"/track-issue/{doc.tracking_id}")

        message = (
            f"{emoji} *Civic Issue Update*\n\n"
            f"\U0001f4cb *Tracking ID:* `{doc.tracking_id}`\n"
            f"\U0001f4dd *Issue:* {doc.issue_title}\n"
            f"\U0001f4ca *Status:* {doc.status}\n"
        )

        if doc.status == "Assigned" and doc.assigned_contractor:
            contractor_name = frappe.db.get_value(
                "Civic Contractor", doc.assigned_contractor, "contractor_name"
            )
            message += f"\U0001f477 *Assigned To:* {contractor_name}\n"

        if doc.status == "Resolved" and doc.resolution_notes:
            message += f"\U0001f4dd *Resolution:* {doc.resolution_notes}\n"

        message += f"\n\U0001f517 Track online: {portal_url}"

        send_whatsapp_reply(wa_phone, message)

    except Exception as e:
        frappe.log_error(
            f"WhatsApp status update error for {doc.name}: {str(e)}",
            "WhatsApp Status Update",
        )
