# ============================================================================
# PHILOSOPHY 3: LAYERED CONFIGURATION
# ============================================================================
"""
EXPERT THINKING:
Configs should layer from general → specific
Each layer overrides/extends the previous
"""

# Layer 1: System defaults (hardcoded or base config)
SYSTEM_DEFAULTS = {
    "logging": {
        "level": "INFO",
        "format": "json",
        "outputs": ["stdout"]
    },
    "database": {
        "pool_size": 10,
        "timeout": 30,
        "retry_attempts": 3
    },
    "features": {
        "analytics": True,
        "debug_mode": False
    }
}

# Layer 2: Environment config (dev/staging/prod)
PRODUCTION_CONFIG = {
    "logging": {
        "level": "WARNING",  # Override
        "outputs": ["stdout", "file", "sentry"]  # Extend
    },
    "database": {
        "pool_size": 50  # Override for production
    }
}

# Layer 3: User/runtime config
USER_CONFIG = {
    "features": {
        "debug_mode": True  # User enables debug
    }
}

# Expert systems merge these layers intelligently