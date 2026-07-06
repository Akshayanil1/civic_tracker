import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date, get_url
from civic_tracker.api.ai import validate_image_with_ai, analyze_issue_text, dynamic_assignment_routing

try:
    from geopy.distance import geodesic
except ImportError:
    pass


class CivicIssue(Document):
    def before_insert(self):
        self.generate_tracking_id()
        
        # Phase 14: NLP Categorization and Sentiment
        if self.description:
            category, urgency = analyze_issue_text(self.description)
            if category:
                self.issue_type = category
            if urgency:
                self.urgency_score = urgency
                
        # Phase 13: Image Validation
        if self.issue_image:
            is_valid = validate_image_with_ai(self.issue_image)
            if not is_valid:
                self.status = "Spam"
                # Rejecting submission effectively if we don't want it open
                
        # Phase 14: Dynamic Assignment for Critical Issues
        dynamic_assignment_routing(self)
        
        self.set_escalation_time()

    def after_insert(self):
        # Phase 26, Day 4: Spatial Duplicate Clustering (enqueue job)
        frappe.enqueue("civic_tracker.api.clustering.cluster_duplicates", queue="short", issue_name=self.name)

    def validate(self):
        self.validate_assignment()
        if self.status == "Resolved":
            self.validate_geofence()

    def on_update(self):
        self.send_tracking_email()

    def generate_tracking_id(self):
        """Generate a unique tracking ID for citizen reference."""
        import random
        import string

        prefix = "CT"
        year = now_datetime().strftime("%y")
        random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.tracking_id = f"{prefix}-{year}-{random_part}"

    def set_escalation_time(self):
        """Set escalation time based on SLA defined for the issue type."""
        sla = frappe.db.get_value(
            "Issue SLA",
            {"issue_type": self.issue_type, "is_active": 1},
            ["sla_hours", "escalation_hours"],
        )
        if sla:
            sla_hours, escalation_hours = sla
            self.due_date = add_to_date(self.issue_date, hours=int(sla_hours or 48))
            self.escalation_time = add_to_date(
                self.issue_date, hours=int(escalation_hours or 72)
            )
        else:
            self.due_date = add_to_date(self.issue_date, hours=48)
            self.escalation_time = add_to_date(self.issue_date, hours=72)

    def validate_assignment(self):
        """Validate contractor assignment rules."""
        if self.assigned_contractor and self.ward:
            contractor = frappe.get_doc("Civic Contractor", self.assigned_contractor)
            assigned_wards = [d.ward for d in contractor.assigned_ward]
            if assigned_wards and self.ward not in assigned_wards:
                frappe.msgprint(
                    f"Warning: Contractor {self.assigned_contractor} is not formally assigned to Ward {self.ward}.",
                    alert=True,
                )

    def send_tracking_email(self):
        """Send tracking ID to citizen if email is provided."""
        if self.citizen_email and not self.is_anonymous:
            tracking_url = get_url(f"/track-issue/{self.tracking_id}")
            frappe.sendmail(
                recipients=[self.citizen_email],
                subject=f"Civic Issue Reported - {self.tracking_id}",
                message=f"""
                <p>Dear {self.citizen_name or 'Citizen'},</p>
                <p>Thank you for reporting a civic issue. Your grievance has been registered.</p>
                <p><strong>Tracking ID:</strong> {self.tracking_id}</p>
                <p><strong>Issue Type:</strong> {self.issue_type}</p>
                <p><strong>Ward:</strong> {self.ward}</p>
                <p><strong>Status:</strong> {self.status}</p>
                <p>You can track your issue at: <a href="{tracking_url}">{tracking_url}</a></p>
                <p>Thank you for helping improve our city.</p>
                """,
            )

    def resolve_issue(self, notes=""):
        """Mark issue as resolved."""
        self.status = "Resolved"
        self.resolution_date = now_datetime()
        self.resolution_notes = notes
        self.save(ignore_permissions=True)

    def reopen_issue(self, reason=""):
        """Reopen a resolved issue."""
        self.status = "Reopened"
        self.resolution_date = None
        self.resolution_notes = ""
        self.save(ignore_permissions=True)

    def validate_geofence(self):
        """Day 2 & 3: Geo-Fenced Proof of Work Validation"""
        if not (self.latitude and self.longitude):
            return # Original issue has no location
            
        if not self.actual_resolution_lat_lng:
            frappe.throw("Actual Resolution Lat/Lng is required to mark the issue as Resolved. (Geo-Fencing Enabled)")
            
        try:
            actual_lat, actual_lng = [float(x.strip()) for x in self.actual_resolution_lat_lng.split(',')]
            original_point = (self.latitude, self.longitude)
            resolution_point = (actual_lat, actual_lng)
            
            # Distance in meters
            dist = geodesic(original_point, resolution_point).meters
            
            if dist > 50:
                frappe.throw(f"Fraud Prevention: Resolution photo must be taken at the original site. You are {int(dist)} meters away!")
        except ValueError:
            frappe.throw("Invalid format for Actual Resolution Lat/Lng. Expected format: 'latitude, longitude'")

