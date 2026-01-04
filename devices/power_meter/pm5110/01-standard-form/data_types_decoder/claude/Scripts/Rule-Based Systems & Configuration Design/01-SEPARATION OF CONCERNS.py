"""
EXPERT GUIDE: Rule-Based Systems & Configuration Design
========================================================
How experts think about and structure rules + configs
"""

# ============================================================================
# PHILOSOPHY 1: SEPARATION OF CONCERNS
# ============================================================================
"""
EXPERT THINKING:
- Configuration = WHAT (data, parameters, values)
- Rules = HOW (logic, validation, transformations)
- Code = WHERE (execution engine)

Keep these THREE separate for maintainability
"""

# BAD: Everything mixed together
BAD_MIXED_CONFIG = {
    "server": "192.168.1.1",
    "port": 8080,
    "validate_port": "lambda p: 1024 <= p <= 65535",  # Logic in config!
    "connection_handler": "def connect()...",  # Code in config!
}

# GOOD: Clean separation
GOOD_CONFIG = {
    "server": "192.168.1.1",
    "port": 8080,
    "timeout": 30
}

GOOD_RULES = {
    "port_validation": {
        "field": "port",
        "type": "range",
        "min": 1024,
        "max": 65535
    }
}

# Code stays in Python, interprets config + rules