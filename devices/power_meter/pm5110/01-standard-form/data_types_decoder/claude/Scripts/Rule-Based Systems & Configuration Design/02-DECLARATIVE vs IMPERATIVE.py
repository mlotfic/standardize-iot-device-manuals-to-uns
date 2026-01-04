# ============================================================================
# PHILOSOPHY 2: DECLARATIVE vs IMPERATIVE
# ============================================================================
"""
EXPERT THINKING:
Declarative = Describe WHAT you want (preferred for configs)
Imperative = Describe HOW to do it (code stays in application)
"""

# DECLARATIVE (Expert approach) - Just state the rules
DECLARATIVE_RULES = {
    "validation_rules": [
        {
            "name": "email_format",
            "field": "email",
            "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "error_message": "Invalid email format"
        },
        {
            "name": "age_range",
            "field": "age",
            "type": "range",
            "min": 18,
            "max": 120,
            "error_message": "Age must be between 18 and 120"
        },
        {
            "name": "password_strength",
            "field": "password",
            "rules": ["min_length:8", "has_uppercase", "has_number"],
            "error_message": "Password too weak"
        }
    ]
}

# IMPERATIVE (Avoid in configs) - Too much "how"
IMPERATIVE_RULES = {
    "email_validation": """
        def validate_email(email):
            if '@' not in email:
                return False
            parts = email.split('@')
            if len(parts) != 2:
                return False
            # Too much code in config!
    """
}