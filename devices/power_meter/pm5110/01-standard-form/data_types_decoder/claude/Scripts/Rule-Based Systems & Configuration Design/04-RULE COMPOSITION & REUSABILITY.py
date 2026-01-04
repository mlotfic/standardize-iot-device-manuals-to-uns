# ============================================================================
# PHILOSOPHY 4: RULE COMPOSITION & REUSABILITY
# ============================================================================
"""
EXPERT THINKING:
Break complex rules into reusable atomic pieces
Compose them for specific scenarios
"""

# ATOMIC RULES (Building blocks)
ATOMIC_RULES = {
    "rules": {
        "is_positive": {
            "type": "comparison",
            "operator": ">",
            "value": 0
        },
        "is_numeric": {
            "type": "type_check",
            "expected_type": "number"
        },
        "max_length_50": {
            "type": "length",
            "operator": "<=",
            "value": 50
        },
        "is_alphanumeric": {
            "type": "pattern",
            "pattern": "^[a-zA-Z0-9]+$"
        }
    }
}

# COMPOSED RULES (Combinations)
COMPOSED_RULES = {
    "product_code_validation": {
        "description": "Product code must be alphanumeric, positive ID",
        "all_of": [  # AND logic
            {"ref": "is_alphanumeric"},
            {"ref": "max_length_50"}
        ]
    },
    "quantity_validation": {
        "description": "Quantity must be positive number",
        "all_of": [
            {"ref": "is_numeric"},
            {"ref": "is_positive"}
        ]
    },
    "flexible_identifier": {
        "description": "Accept multiple ID formats",
        "any_of": [  # OR logic
            {"ref": "is_numeric"},
            {"ref": "is_alphanumeric"}
        ]
    }
}

# Expert benefit: Reuse "is_positive" in 10 different rules