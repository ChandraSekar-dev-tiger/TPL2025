import re
import logging

logger = logging.getLogger("agent.guardrails")

# Define your policy configuration (can later be loaded from JSON/YAML)
GUARDRAIL_POLICIES = {
    "blocked_keywords": ["DROP", "DELETE", "UPDATE", "INSERT"],
    "pii_fields": ["patient_name", "ssn", "dob", "address", "contact_number"],
    "offensive_language": ["idiot",
    "kill",
    "damn",
    "shut up",
    "stupid",
    "loser",
    "dumb",
    "go to hell"],
    "max_query_length": 500,
    "role_permissions": {
        "non_clinical_staff": ["emergency_department_metrics", "outpatient_department_metrics", "surgery_department_metrics","radiology_department_metrics",
                               "laboratory_department_metrics","quality_safety_metrics",
                               "finance_billing_metrics"],
        "administrative_staff": ["emergency_department_metrics","inpatient_ward_metrics","outpatient_department_metrics",
                                 "surgery_department_metrics","radiology_department_metrics","pharmacy_department_metrics","icu_metrics",
                                 "administration_metrics","quality_safety_metrics","patient_experience_metrics"],
        "manager": ["emergency_department_metrics","inpatient_ward_metrics","outpatient_department_metrics",
                                 "surgery_department_metrics","radiology_department_metrics","laboratory_department_metrics","pharmacy_department_metrics","icu_metrics",
                                 "administration_metrics","quality_safety_metrics","finance_billing_metrics","patient_experience_metrics"]
    }
}

def apply_guardrails(query: str, role: str, intent: str = "", table: str = "", code: str = "") -> list:
    """
    Checks for violations of defined guardrail policies.
    Returns a list of violation messages (empty list = no violations).
    """
    violations = []

    # 1. Check for SQL injection / dangerous code
    for keyword in GUARDRAIL_POLICIES["blocked_keywords"]:
        if keyword in code.upper():
            violations.append(f"Blocked keyword detected in code: {keyword}")

    # 2. Check for privacy violations in query
    for pii in GUARDRAIL_POLICIES["pii_fields"]:
        if re.search(rf"\\b{pii}\\b", query.lower()):
            violations.append(f"Query attempts to access sensitive PII field: {pii}")

    # 3. Check for offensive/abusive language
    for word in GUARDRAIL_POLICIES["offensive_language"]:
        if word in query.lower():
            violations.append(f"Offensive language detected: {word}")

    # 4. Enforce max query length
    if len(query) > GUARDRAIL_POLICIES["max_query_length"]:
        violations.append("Query exceeds maximum length limit")

    # 5. Role-based access to tables
    allowed_tables = GUARDRAIL_POLICIES["role_permissions"].get(role, [])
    if "*" not in allowed_tables and table and table not in allowed_tables:
        violations.append(f"Role '{role}' is not authorized to access table '{table}'")

    # Log violations
    if violations:
        logger.warning(f"Guardrail Violations Detected | Role: {role} | Query: '{query}' | Violations: {violations}")

    return violations
