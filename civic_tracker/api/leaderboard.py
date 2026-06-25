import frappe
from frappe.utils import flt


@frappe.whitelist(allow_guest=True)
def get_ward_leaderboard():
    """Calculate and return the Ward Leaderboard data.
    Ranks wards by their SLA resolution percentage to drive
    competitive civic improvement.
    """
    ward_stats = frappe.db.sql(
        """
        SELECT
            ci.ward,
            mw.ward_name,
            mw.ward_code,
            mw.commissioner_name,
            mw.population,
            COUNT(*) as total_issues,
            SUM(CASE WHEN ci.status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) as resolved_issues,
            SUM(CASE WHEN ci.status = 'Overdue' THEN 1 ELSE 0 END) as overdue_issues,
            SUM(CASE WHEN ci.status = 'Open' THEN 1 ELSE 0 END) as open_issues,
            SUM(CASE WHEN ci.status IN ('Assigned', 'In Progress') THEN 1 ELSE 0 END) as active_issues,
            AVG(
                CASE
                    WHEN ci.resolution_date IS NOT NULL AND ci.issue_date IS NOT NULL
                    THEN TIMESTAMPDIFF(HOUR, ci.issue_date, ci.resolution_date)
                    ELSE NULL
                END
            ) as avg_resolution_hours,
            SUM(
                CASE
                    WHEN ci.status IN ('Resolved', 'Closed')
                    AND ci.resolution_date IS NOT NULL
                    AND ci.due_date IS NOT NULL
                    AND ci.resolution_date <= ci.due_date
                    THEN 1 ELSE 0
                END
            ) as within_sla_count
        FROM `tabCivic Issue` ci
        LEFT JOIN `tabMunicipal Ward` mw ON mw.name = ci.ward
        WHERE ci.ward IS NOT NULL
        GROUP BY ci.ward, mw.ward_name, mw.ward_code, mw.commissioner_name, mw.population
        ORDER BY resolved_issues DESC
        """,
        as_dict=True,
    )

    # Calculate derived metrics
    for ward in ward_stats:
        total = ward.total_issues or 1
        resolved = ward.resolved_issues or 0

        ward["resolution_rate"] = round((resolved / total) * 100, 1)
        ward["sla_compliance_rate"] = round(
            ((ward.within_sla_count or 0) / max(resolved, 1)) * 100, 1
        )
        ward["avg_resolution_days"] = round(
            flt(ward.avg_resolution_hours or 0) / 24, 1
        )

        # Score: weighted combination of resolution rate, SLA compliance, and speed
        ward["performance_score"] = round(
            (ward["resolution_rate"] * 0.4)
            + (ward["sla_compliance_rate"] * 0.4)
            + (max(0, 100 - ward["avg_resolution_days"] * 5) * 0.2),
            1,
        )

    # Sort by performance score descending
    ward_stats.sort(key=lambda x: x["performance_score"], reverse=True)

    # Assign ranks
    for i, ward in enumerate(ward_stats, 1):
        ward["rank"] = i
        if i == 1:
            ward["badge"] = "\U0001f947"
        elif i == 2:
            ward["badge"] = "\U0001f948"
        elif i == 3:
            ward["badge"] = "\U0001f949"
        else:
            ward["badge"] = ""

    return ward_stats
