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

# ============================================================================
# PHILOSOPHY 2: DECLARATIVE vs IMPERATIVE
# ============================================================================
"""
EXPERT THINKING:
Declarative = Describe WHAT you want (preferred for configs)
Imperative = Describe HOW to do it (code stays in application)
"""

# ============================================================================
# PHILOSOPHY 3: LAYERED CONFIGURATION
# ============================================================================
"""
EXPERT THINKING:
Configs should layer from general → specific
Each layer overrides/extends the previous
"""


# ============================================================================
# PHILOSOPHY 4: RULE COMPOSITION & REUSABILITY
# ============================================================================
"""
EXPERT THINKING:
Break complex rules into reusable atomic pieces
Compose them for specific scenarios
"""


# ============================================================================
# PHILOSOPHY 5: CONDITIONAL RULES (Context-Aware)
# ============================================================================
"""
EXPERT THINKING:
Rules often depend on context
Use 'when' conditions to make rules smart
"""

CONDITIONAL_RULES = {
    "rules": [
        {
            "name": "shipping_validation",
            "when": {
                "field": "country",
                "equals": "USA"
            },
            "then": {
                "field": "zip_code",
                "pattern": r"^\d{5}(-\d{4})?$",
                "required": True
            }
        },
        {
            "name": "shipping_validation",
            "when": {
                "field": "country",
                "equals": "Canada"
            },
            "then": {
                "field": "postal_code",
                "pattern": r"^[A-Z]\d[A-Z] \d[A-Z]\d$",
                "required": True
            }
        },
        {
            "name": "age_verification",
            "when": {
                "field": "product_type",
                "in": ["alcohol", "tobacco"]
            },
            "then": {
                "field": "age",
                "type": "range",
                "min": 21
            }
        },
        {
            "name": "business_hours_pricing",
            "when": {
                "all_of": [
                    {"field": "time", "between": ["09:00", "17:00"]},
                    {"field": "day", "not_in": ["Saturday", "Sunday"]}
                ]
            },
            "then": {
                "field": "price_multiplier",
                "value": 1.0
            },
            "else": {
                "field": "price_multiplier",
                "value": 1.5  # After hours premium
            }
        }
    ]
}


# ============================================================================
# PHILOSOPHY 6: RULE PRIORITY & CONFLICT RESOLUTION
# ============================================================================
"""
EXPERT THINKING:
When multiple rules apply, need clear priority
Experts use explicit ordering or weight systems
"""

# APPROACH A: Explicit Priority (Simple)
PRIORITY_RULES = {
    "rules": [
        {
            "name": "vip_customer_discount",
            "priority": 100,  # Highest
            "when": {"field": "customer_tier", "equals": "VIP"},
            "action": {"discount": 0.30}
        },
        {
            "name": "seasonal_discount",
            "priority": 50,  # Medium
            "when": {"field": "season", "equals": "holiday"},
            "action": {"discount": 0.20}
        },
        {
            "name": "bulk_discount",
            "priority": 10,  # Lowest
            "when": {"field": "quantity", "greater_than": 100},
            "action": {"discount": 0.10}
        }
    ],
    "conflict_resolution": "highest_priority_wins"
}

# APPROACH B: Rule Combination Strategy
COMBINATION_RULES = {
    "rules": [
        {
            "name": "new_customer_discount",
            "discount": 0.10,
            "combinable": True
        },
        {
            "name": "referral_discount",
            "discount": 0.05,
            "combinable": True
        },
        {
            "name": "flash_sale",
            "discount": 0.40,
            "combinable": False,  # Exclusive
            "overrides": ["new_customer_discount", "referral_discount"]
        }
    ],
    "combination_strategy": "additive",  # or "max" or "custom"
    "max_combined_discount": 0.50
}


# ============================================================================
# PHILOSOPHY 7: SCHEMA VERSIONING & EVOLUTION
# ============================================================================
"""
EXPERT THINKING:
Configs change over time
Version them and handle migrations
"""

# Version 1.0 Config
CONFIG_V1 = {
    "version": "1.0",
    "database": {
        "host": "localhost",
        "port": 5432
    }
}

# Version 2.0 Config (Breaking changes)
CONFIG_V2 = {
    "version": "2.0",
    "database": {
        "primary": {  # Changed structure
            "host": "localhost",
            "port": 5432
        },
        "read_replicas": []  # New feature
    },
    "deprecated_fields": ["database.host"]  # Document what changed
}

# Expert migration rules
MIGRATION_RULES = {
    "migrations": [
        {
            "from_version": "1.0",
            "to_version": "2.0",
            "transformations": [
                {
                    "action": "move",
                    "from": "database.host",
                    "to": "database.primary.host"
                },
                {
                    "action": "move",
                    "from": "database.port",
                    "to": "database.primary.port"
                },
                {
                    "action": "add",
                    "path": "database.read_replicas",
                    "default": []
                }
            ]
        }
    ]
}


# ============================================================================
# PHILOSOPHY 8: HUMAN vs MACHINE READABILITY
# ============================================================================
"""
EXPERT THINKING:
Balance between human editing and machine parsing
Choose format based on who edits it more
"""

# For HUMANS editing frequently - Use YAML/TOML
HUMAN_FRIENDLY = """
# config.yaml
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: ${ENV:DB_PASSWORD}  # Environment variable

rules:
  - name: Rate limiting
    limit: 1000 requests/hour
    applies_to:
      - /api/*
      - /graphql
"""

# For MACHINES primarily - Use JSON
MACHINE_FRIENDLY = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
            "username": "admin",
            "password_env": "DB_PASSWORD"
        }
    },
    "rules": [
        {
            "name": "rate_limiting",
            "limit": {"count": 1000, "period": "hour", "unit": "requests"},
            "applies_to": ["/api/*", "/graphql"]
        }
    ]
}

# For COMPLEX logic - Use DSL
DSL_CONFIG = """
# Custom Domain-Specific Language
RULE rate_limiting:
    LIMIT 1000 requests PER hour
    APPLY TO /api/*, /graphql
    ON VIOLATION RETURN 429

RULE authentication:
    REQUIRE token IN header
    VALIDATE WITH jwt_validator
    ON FAILURE RETURN 401
"""


# ============================================================================
# PHILOSOPHY 9: CONFIGURATION VALIDATION SCHEMA
# ============================================================================
"""
EXPERT THINKING:
Configs should be validated against a schema
Catch errors early before runtime
"""

# JSON Schema for validation
CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["database", "api"],
    "properties": {
        "database": {
            "type": "object",
            "required": ["host", "port"],
            "properties": {
                "host": {
                    "type": "string",
                    "format": "hostname"
                },
                "port": {
                    "type": "integer",
                    "minimum": 1024,
                    "maximum": 65535
                },
                "pool_size": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10
                }
            }
        },
        "api": {
            "type": "object",
            "properties": {
                "rate_limit": {
                    "type": "integer",
                    "minimum": 1
                },
                "timeout": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 300
                }
            }
        }
    }
}


# ============================================================================
# PHILOSOPHY 10: SMART DEFAULTS & CONVENTIONS
# ============================================================================
"""
EXPERT THINKING:
Minimize required configuration
Use smart defaults and conventions over configuration
"""

# MINIMAL CONFIG (Expert approach)
MINIMAL_CONFIG = {
    "database_url": "postgresql://localhost/mydb"
    # Everything else uses smart defaults
}

# System derives:
# - host: localhost (from URL)
# - port: 5432 (PostgreSQL default)
# - pool_size: 10 (conventional default)
# - timeout: 30s (sensible default)

# EXPLICIT CONFIG (When you need control)
EXPLICIT_CONFIG = {
    "database": {
        "url": "postgresql://localhost/mydb",
        "pool_size": 50,  # Override default
        "timeout": 60,  # Override default
        "ssl_mode": "require"  # Explicit need
    }
}


# ============================================================================
# PHILOSOPHY 11: ENVIRONMENT-AWARE CONFIGURATION
# ============================================================================
"""
EXPERT THINKING:
Never hardcode secrets or environment-specific values
Use environment variables and key vaults
"""

ENVIRONMENT_AWARE_CONFIG = {
    "database": {
        "host": "${DB_HOST:localhost}",  # Env var with default
        "port": "${DB_PORT:5432}",
        "password": "${vault:secret/db/password}",  # From vault
        "ssl_cert": "${file:/etc/ssl/certs/db.pem}"  # From file
    },
    "api": {
        "key": "${API_KEY}",  # Required env var (no default)
        "endpoint": "${API_ENDPOINT:https://api.example.com}"
    }
}


# ============================================================================
# PHILOSOPHY 12: RULE EVALUATION STRATEGIES
# ============================================================================
"""
EXPERT THINKING:
How rules are evaluated affects performance and behavior
Choose strategy based on use case
"""

EVALUATION_STRATEGIES = {
    "strategies": {
        
        "eager_evaluation": {
            "description": "Evaluate all rules immediately",
            "use_when": "Need complete validation results",
            "example": "Form validation - show all errors at once"
        },
        
        "lazy_evaluation": {
            "description": "Evaluate rules only when needed",
            "use_when": "Performance critical, rules are expensive",
            "example": "Large dataset validation - stop at first error"
        },
        
        "short_circuit": {
            "description": "Stop at first matching rule",
            "use_when": "Rules are mutually exclusive",
            "example": "Route matching - first match wins"
        },
        
        "all_matches": {
            "description": "Find all matching rules and apply all",
            "use_when": "Rules are independent and combinable",
            "example": "Discount stacking - apply all valid discounts"
        },
        
        "best_match": {
            "description": "Evaluate all, pick best by scoring",
            "use_when": "Need optimal result from multiple options",
            "example": "Recommendation engine - highest score wins"
        }
    }
}


# ============================================================================
# EXPERT RULE ENGINE PATTERNS
# ============================================================================

class ExpertRuleEngine:
    """
    How experts structure rule engines in code
    
    Key principles:
    1. Separate rule definition from execution
    2. Make rules data-driven
    3. Support rule composition
    4. Enable easy testing
    5. Provide clear audit trails
    """
    
    def __init__(self, rules_config):
        self.rules = self._load_rules(rules_config)
        self.context = {}
        self.audit_log = []
    
    def _load_rules(self, config):
        """Load and validate rules from config"""
        # Parse, validate schema, compile patterns
        return config.get('rules', [])
    
    def evaluate(self, data, strategy='eager'):
        """
        Evaluate rules against data
        
        Expert pattern: Strategy pattern for evaluation
        """
        if strategy == 'eager':
            return self._evaluate_all(data)
        elif strategy == 'lazy':
            return self._evaluate_lazy(data)
        elif strategy == 'short_circuit':
            return self._evaluate_short_circuit(data)
    
    def _evaluate_all(self, data):
        """Evaluate all rules, collect all results"""
        results = []
        for rule in self.rules:
            result = self._evaluate_single_rule(rule, data)
            results.append(result)
            self._audit(rule, result)
        return results
    
    def _evaluate_lazy(self, data):
        """Evaluate until first failure"""
        for rule in self.rules:
            result = self._evaluate_single_rule(rule, data)
            self._audit(rule, result)
            if not result['passed']:
                return result  # Stop at first failure
        return {'passed': True}
    
    def _evaluate_single_rule(self, rule, data):
        """Evaluate one rule - core logic"""
        # Check 'when' conditions
        if not self._check_conditions(rule.get('when'), data):
            return {'passed': True, 'skipped': True}
        
        # Apply rule logic
        rule_type = rule.get('type')
        if rule_type == 'range':
            return self._check_range(rule, data)
        elif rule_type == 'pattern':
            return self._check_pattern(rule, data)
        # ... more types
    
    def _check_conditions(self, conditions, data):
        """Check if rule should apply"""
        if not conditions:
            return True
        # Evaluate condition logic
        return True
    
    def _audit(self, rule, result):
        """Expert pattern: Always log rule execution"""
        self.audit_log.append({
            'rule': rule.get('name'),
            'timestamp': 'now',
            'result': result,
            'context': self.context.copy()
        })


# ============================================================================
# SUMMARY: EXPERT MENTAL MODEL
# ============================================================================

EXPERT_MENTAL_MODEL = """
When experts design rule-based systems and configs, they think:

1. SEPARATION
   ├─ Config = Data (WHAT)
   ├─ Rules = Logic (HOW)  
   └─ Code = Engine (WHERE)

2. LAYERING
   ├─ Defaults (system)
   ├─ Environment (dev/prod)
   ├─ User (overrides)
   └─ Runtime (temporary)

3. COMPOSITION
   ├─ Atomic rules (small, reusable)
   ├─ Composed rules (combinations)
   └─ Rule chains (pipelines)

4. EVOLUTION
   ├─ Version configs
   ├─ Migrate old → new
   ├─ Deprecation strategy
   └─ Backward compatibility

5. VALIDATION
   ├─ Schema-driven
   ├─ Fail early
   ├─ Clear error messages
   └─ Type safety

6. CONTEXT-AWARENESS
   ├─ Conditional rules (when/then)
   ├─ Environment variables
   ├─ Runtime context
   └─ User preferences

7. AUDIT & DEBUG
   ├─ Log rule evaluation
   ├─ Explain decisions
   ├─ Trace rule chains
   └─ Performance metrics

GOLDEN RULES:
✓ Make it declarative (describe WHAT not HOW)
✓ Make it composable (small pieces → big systems)
✓ Make it versioned (change safely over time)
✓ Make it validated (catch errors early)
✓ Make it auditable (understand what happened)
✗ Don't mix code and config
✗ Don't hardcode everything
✗ Don't ignore versioning
✗ Don't skip validation
"""

print(EXPERT_MENTAL_MODEL)
