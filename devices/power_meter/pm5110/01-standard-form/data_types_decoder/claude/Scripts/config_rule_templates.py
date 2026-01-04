"""
PRODUCTION TEMPLATES: Config Files & Rule Systems
=================================================
Copy-paste ready templates for any project
"""

# ============================================================================
# TEMPLATE 1: BASIC CONFIG FILE (Minimal)
# ============================================================================
"""
Use this for: Simple projects, getting started, prototyping
"""

BASIC_CONFIG_TEMPLATE = {
    "version": "1.0.0",
    "name": "my_device_config",
    "description": "Configuration for [DEVICE_NAME]",
    
    # Device identification
    "device": {
        "manufacturer": "MANUFACTURER_NAME",
        "model": "MODEL_NUMBER",
        "firmware_version": "1.0.0"
    },
    
    # Connection settings
    "connection": {
        "protocol": "modbus_rtu",  # modbus_rtu, modbus_tcp, mqtt, http
        "address": "192.168.1.100",
        "port": 502,
        "timeout_ms": 1000,
        "retry_count": 3
    },
    
    # Simple register list
    "registers": [
        {
            "name": "temperature",
            "address": 100,
            "data_type": "int16",
            "unit": "°C",
            "scale": 0.1,
            "access": "read_only"
        },
        {
            "name": "setpoint",
            "address": 200,
            "data_type": "int16",
            "unit": "°C",
            "scale": 0.1,
            "access": "read_write",
            "range": {"min": 0, "max": 100}
        }
    ]
}


# ============================================================================
# TEMPLATE 2: HIERARCHICAL CONFIG (Scalable)
# ============================================================================
"""
Use this for: 50+ registers, organized systems, production deployments
"""

HIERARCHICAL_CONFIG_TEMPLATE = {
    "schema_version": "2.0",
    "metadata": {
        "created": "2025-12-28",
        "author": "YOUR_NAME",
        "description": "Full device configuration"
    },
    
    "device": {
        "manufacturer": "MANUFACTURER",
        "model": "MODEL",
        "type": "power_meter",  # Type of device
        "capabilities": ["measurements", "alarms", "configuration"]
    },
    
    "communication": {
        "protocol": "modbus_rtu",
        "default_slave_id": 1,
        "baud_rate": 9600,
        "parity": "none",
        "data_bits": 8,
        "stop_bits": 1
    },
    
    # Organize registers into logical groups
    "register_groups": {
        "measurements": {
            "description": "Real-time measurements",
            "base_address": 3000,
            "function_code": 4,  # Read Input Registers
            "poll_rate_ms": 1000,
            "registers": [
                {
                    "name": "voltage_l1",
                    "offset": 0,  # Actual address = base + offset
                    "data_type": "float32",
                    "unit": "V",
                    "range": {"min": 0, "max": 690}
                }
            ]
        },
        
        "configuration": {
            "description": "User configuration",
            "base_address": 5000,
            "function_code": 3,  # Read Holding Registers
            "poll_rate_ms": null,  # On-demand only
            "registers": [
                {
                    "name": "ct_ratio",
                    "offset": 10,
                    "data_type": "uint16",
                    "unit": "A",
                    "access": "read_write",
                    "range": {"min": 5, "max": 5000}
                }
            ]
        },
        
        "status": {
            "description": "Device status flags",
            "base_address": 4000,
            "function_code": 2,  # Read Discrete Inputs
            "registers": [
                {
                    "name": "alarm_active",
                    "offset": 0,
                    "data_type": "boolean"
                }
            ]
        }
    }
}


# ============================================================================
# TEMPLATE 3: DATA TYPE DEFINITIONS (Reusable)
# ============================================================================
"""
Use this for: Complex data types, bit fields, custom encodings
Define once, reference everywhere
"""

DATA_TYPE_LIBRARY_TEMPLATE = {
    "version": "1.0",
    "description": "Reusable data type definitions",
    
    "simple_types": {
        "uint16": {
            "size_bits": 16,
            "size_registers": 1,
            "signed": False,
            "byte_order": "big_endian"
        },
        "int16": {
            "size_bits": 16,
            "size_registers": 1,
            "signed": True,
            "byte_order": "big_endian"
        },
        "uint32": {
            "size_bits": 32,
            "size_registers": 2,
            "signed": False,
            "byte_order": "big_endian",
            "word_order": "big_endian"
        },
        "float32": {
            "size_bits": 32,
            "size_registers": 2,
            "format": "ieee754",
            "byte_order": "big_endian",
            "word_order": "big_endian"
        }
    },
    
    "complex_types": {
        # Example: IP Address as 4 bytes
        "ip_address": {
            "size_registers": 2,
            "description": "IPv4 address stored as 4 bytes",
            "structure": {
                "octet1": {"byte_offset": 0, "type": "uint8"},
                "octet2": {"byte_offset": 1, "type": "uint8"},
                "octet3": {"byte_offset": 2, "type": "uint8"},
                "octet4": {"byte_offset": 3, "type": "uint8"}
            },
            "format_string": "{octet1}.{octet2}.{octet3}.{octet4}"
        },
        
        # Example: Status word with bit flags
        "status_word": {
            "size_registers": 1,
            "description": "16-bit status flags",
            "bit_fields": [
                {"name": "running", "bit": 0, "description": "System running"},
                {"name": "alarm", "bit": 1, "description": "Alarm active"},
                {"name": "warning", "bit": 2, "description": "Warning active"},
                {"name": "manual_mode", "bit": 3, "description": "Manual control"},
                {"name": "auto_mode", "bit": 4, "description": "Automatic control"},
                {"name": "maintenance", "bit": 15, "description": "Maintenance mode"}
            ]
        },
        
        # Example: Timestamp
        "timestamp": {
            "size_registers": 4,
            "description": "Unix timestamp (seconds since 1970-01-01)",
            "data_type": "uint32",
            "conversion": "unix_timestamp"
        }
    }
}


# ============================================================================
# TEMPLATE 4: VALIDATION RULES (Comprehensive)
# ============================================================================
"""
Use this for: Data quality, error detection, boundary checking
"""

VALIDATION_RULES_TEMPLATE = {
    "version": "1.0",
    "description": "Validation rules for data quality",
    
    # Simple field validation
    "field_rules": {
        "range_check": {
            "description": "Value must be within specified range",
            "applies_to": ["temperature", "pressure", "voltage"],
            "rule_type": "range",
            "parameters": {
                "min": "field.range.min",  # Reference to config
                "max": "field.range.max"
            },
            "severity": "error",
            "message_template": "{field_name} value {value} outside valid range [{min}, {max}]"
        },
        
        "required_field": {
            "description": "Field must not be null/empty",
            "applies_to": ["device_id", "timestamp"],
            "rule_type": "required",
            "severity": "error",
            "message_template": "{field_name} is required but missing"
        },
        
        "data_type_check": {
            "description": "Value must match expected data type",
            "applies_to": "*",  # All fields
            "rule_type": "type_check",
            "severity": "error"
        }
    },
    
    # Cross-field validation
    "relationship_rules": {
        "temperature_pressure_consistency": {
            "description": "Temp and pressure must correlate",
            "fields": ["temperature", "pressure"],
            "rule_type": "correlation",
            "logic": "if temperature > 100 then pressure must be > 1",
            "severity": "warning"
        },
        
        "min_max_order": {
            "description": "Min must be less than max",
            "fields": ["min_value", "max_value"],
            "rule_type": "comparison",
            "logic": "min_value < max_value",
            "severity": "error"
        }
    },
    
    # Conditional validation (context-aware)
    "conditional_rules": {
        "alarm_requires_threshold": {
            "description": "If alarm enabled, threshold must be set",
            "when": {
                "field": "alarm_enabled",
                "equals": True
            },
            "then": {
                "field": "alarm_threshold",
                "rule": "required"
            },
            "severity": "error"
        }
    },
    
    # Pattern validation
    "pattern_rules": {
        "mac_address_format": {
            "description": "MAC address must be valid format",
            "applies_to": ["mac_address"],
            "rule_type": "regex",
            "pattern": "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",
            "severity": "error",
            "example": "AA:BB:CC:DD:EE:FF"
        },
        
        "serial_number_format": {
            "description": "Serial number format validation",
            "applies_to": ["serial_number"],
            "rule_type": "regex",
            "pattern": "^[A-Z]{2}\\d{8}$",
            "severity": "error",
            "example": "AB12345678"
        }
    },
    
    # Time-based rules
    "temporal_rules": {
        "future_date_check": {
            "description": "Date must not be in the future",
            "applies_to": ["timestamp", "date_*"],
            "rule_type": "temporal",
            "logic": "value <= now()",
            "severity": "warning"
        },
        
        "data_freshness": {
            "description": "Data must be recent",
            "applies_to": ["measurement_timestamp"],
            "rule_type": "temporal",
            "logic": "now() - value < 5 minutes",
            "severity": "warning",
            "message": "Data is stale (>5 minutes old)"
        }
    }
}


# ============================================================================
# TEMPLATE 5: RULE ENGINE IMPLEMENTATION
# ============================================================================
"""
Generic rule engine that works with any of the above templates
"""

class RuleEngine:
    """
    Production-ready rule engine for validating data
    
    Usage:
        engine = RuleEngine(VALIDATION_RULES_TEMPLATE)
        result = engine.validate(data)
    """
    
    def __init__(self, rules_config):
        self.rules = rules_config
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate(self, data, context=None):
        """
        Validate data against all rules
        
        Args:
            data: Dictionary of field:value pairs
            context: Optional context for conditional rules
            
        Returns:
            Dictionary with validation results
        """
        self.errors = []
        self.warnings = []
        self.info = []
        
        # Run field rules
        for rule_name, rule_config in self.rules.get('field_rules', {}).items():
            self._validate_field_rule(rule_name, rule_config, data)
        
        # Run relationship rules
        for rule_name, rule_config in self.rules.get('relationship_rules', {}).items():
            self._validate_relationship_rule(rule_name, rule_config, data)
        
        # Run conditional rules
        for rule_name, rule_config in self.rules.get('conditional_rules', {}).items():
            self._validate_conditional_rule(rule_name, rule_config, data, context)
        
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'summary': {
                'total_checks': len(self.errors) + len(self.warnings),
                'passed': len(self.warnings),
                'failed': len(self.errors)
            }
        }
    
    def _validate_field_rule(self, rule_name, rule_config, data):
        """Validate single field rule"""
        applies_to = rule_config.get('applies_to', [])
        rule_type = rule_config.get('rule_type')
        severity = rule_config.get('severity', 'error')
        
        for field_name in applies_to:
            # Handle wildcard
            if field_name == '*':
                fields = data.keys()
            else:
                fields = [field_name]
            
            for field in fields:
                if field not in data:
                    continue
                
                value = data[field]
                
                # Execute rule based on type
                if rule_type == 'range':
                    self._check_range(field, value, rule_config, severity)
                elif rule_type == 'required':
                    self._check_required(field, value, rule_config, severity)
                elif rule_type == 'type_check':
                    self._check_type(field, value, rule_config, severity)
                elif rule_type == 'regex':
                    self._check_pattern(field, value, rule_config, severity)
    
    def _check_range(self, field, value, rule_config, severity):
        """Check if value is within range"""
        params = rule_config.get('parameters', {})
        min_val = params.get('min')
        max_val = params.get('max')
        
        if min_val is not None and value < min_val:
            self._add_issue(
                severity,
                f"{field} value {value} is below minimum {min_val}"
            )
        
        if max_val is not None and value > max_val:
            self._add_issue(
                severity,
                f"{field} value {value} is above maximum {max_val}"
            )
    
    def _check_required(self, field, value, rule_config, severity):
        """Check if required field has value"""
        if value is None or value == '':
            self._add_issue(
                severity,
                f"{field} is required but missing or empty"
            )
    
    def _check_type(self, field, value, rule_config, severity):
        """Check if value matches expected type"""
        # Implementation depends on your type system
        pass
    
    def _check_pattern(self, field, value, rule_config, severity):
        """Check if value matches regex pattern"""
        import re
        pattern = rule_config.get('pattern')
        if pattern and not re.match(pattern, str(value)):
            example = rule_config.get('example', '')
            self._add_issue(
                severity,
                f"{field} value '{value}' doesn't match expected format. Example: {example}"
            )
    
    def _validate_relationship_rule(self, rule_name, rule_config, data):
        """Validate cross-field relationships"""
        # Implementation depends on your logic expression evaluator
        pass
    
    def _validate_conditional_rule(self, rule_name, rule_config, data, context):
        """Validate conditional rules"""
        when_condition = rule_config.get('when', {})
        field = when_condition.get('field')
        expected = when_condition.get('equals')
        
        # Check if condition is met
        if field in data and data[field] == expected:
            # Apply 'then' rules
            then_rule = rule_config.get('then', {})
            then_field = then_rule.get('field')
            then_rule_type = then_rule.get('rule')
            
            if then_rule_type == 'required':
                if then_field not in data or data[then_field] is None:
                    severity = rule_config.get('severity', 'error')
                    self._add_issue(
                        severity,
                        f"{then_field} is required when {field} is {expected}"
                    )
    
    def _add_issue(self, severity, message):
        """Add validation issue to appropriate list"""
        issue = {
            'severity': severity,
            'message': message,
            'timestamp': 'now'
        }
        
        if severity == 'error':
            self.errors.append(issue)
        elif severity == 'warning':
            self.warnings.append(issue)
        else:
            self.info.append(issue)


# ============================================================================
# TEMPLATE 6: COMPLETE EXAMPLE (Putting It All Together)
# ============================================================================
"""
Complete example: Temperature controller with all templates integrated
"""

COMPLETE_EXAMPLE = {
    # Main config
    "config": {
        "version": "2.0",
        "device": {
            "name": "Temperature Controller TC-100",
            "manufacturer": "ACME Corp",
            "model": "TC-100"
        },
        
        "register_groups": {
            "measurements": {
                "base_address": 100,
                "registers": [
                    {
                        "name": "current_temperature",
                        "offset": 0,
                        "data_type_ref": "temperature_value",  # Reference!
                        "poll_rate_ms": 1000
                    },
                    {
                        "name": "humidity",
                        "offset": 2,
                        "data_type_ref": "percentage_value",
                        "poll_rate_ms": 1000
                    }
                ]
            },
            "settings": {
                "base_address": 200,
                "registers": [
                    {
                        "name": "temperature_setpoint",
                        "offset": 0,
                        "data_type_ref": "temperature_value",
                        "access": "read_write"
                    },
                    {
                        "name": "alarm_enable",
                        "offset": 2,
                        "data_type_ref": "boolean",
                        "access": "read_write"
                    },
                    {
                        "name": "alarm_threshold",
                        "offset": 3,
                        "data_type_ref": "temperature_value",
                        "access": "read_write"
                    }
                ]
            }
        }
    },
    
    # Data type library
    "data_types": {
        "temperature_value": {
            "base_type": "int16",
            "size_registers": 1,
            "unit": "°C",
            "scale": 0.1,
            "range": {"min": -40, "max": 125}
        },
        "percentage_value": {
            "base_type": "uint16",
            "size_registers": 1,
            "unit": "%",
            "scale": 0.01,
            "range": {"min": 0, "max": 100}
        },
        "boolean": {
            "base_type": "uint16",
            "size_registers": 1,
            "values": {0: False, 1: True}
        }
    },
    
    # Validation rules
    "rules": {
        "field_rules": {
            "temperature_range": {
                "applies_to": ["current_temperature", "temperature_setpoint"],
                "rule_type": "range",
                "parameters": {"min": -40, "max": 125},
                "severity": "error"
            },
            "humidity_range": {
                "applies_to": ["humidity"],
                "rule_type": "range",
                "parameters": {"min": 0, "max": 100},
                "severity": "error"
            }
        },
        "conditional_rules": {
            "alarm_threshold_required": {
                "when": {"field": "alarm_enable", "equals": True},
                "then": {"field": "alarm_threshold", "rule": "required"},
                "severity": "error"
            }
        }
    }
}


# ============================================================================
# TEMPLATE 7: YAML FORMAT (Human-Friendly)
# ============================================================================
"""
Use YAML when humans will edit configs frequently
"""

YAML_CONFIG_EXAMPLE = """
# Temperature Controller Configuration
# File: tc100_config.yaml

version: "2.0"
updated: 2025-12-28

device:
  name: Temperature Controller TC-100
  manufacturer: ACME Corp
  model: TC-100
  serial_number: ${ENV:DEVICE_SERIAL}  # From environment variable

connection:
  protocol: modbus_rtu
  port: /dev/ttyUSB0
  baud_rate: 9600
  timeout_ms: 1000

# Register definitions
registers:
  measurements:
    base_address: 100
    poll_rate_ms: 1000
    items:
      - name: current_temperature
        offset: 0
        type: int16
        unit: °C
        scale: 0.1
        range:
          min: -40
          max: 125
      
      - name: humidity
        offset: 2
        type: uint16
        unit: "%"
        scale: 0.01
        range:
          min: 0
          max: 100
  
  settings:
    base_address: 200
    poll_rate_ms: null  # On-demand
    items:
      - name: temperature_setpoint
        offset: 0
        type: int16
        unit: °C
        scale: 0.1
        access: read_write
        default: 20.0
      
      - name: alarm_enable
        offset: 2
        type: boolean
        access: read_write
        default: false
      
      - name: alarm_threshold
        offset: 3
        type: int16
        unit: °C
        scale: 0.1
        access: read_write
        required_if:
          field: alarm_enable
          value: true

# Validation rules
validation:
  rules:
    - name: temperature_in_range
      field: current_temperature
      type: range
      min: -40
      max: 125
      severity: error
    
    - name: setpoint_reasonable
      field: temperature_setpoint
      type: range
      min: 0
      max: 50
      severity: warning
      message: "Setpoint outside typical range"
    
    - name: alarm_consistency
      type: conditional
      when:
        field: alarm_enable
        equals: true
      then:
        field: alarm_threshold
        must_be: not_null
      severity: error
"""


# ============================================================================
# TEMPLATE 8: JSON SCHEMA (For Validation)
# ============================================================================
"""
JSON Schema to validate your config files
"""

JSON_SCHEMA_FOR_CONFIG = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Device Configuration Schema",
    "type": "object",
    "required": ["version", "device", "registers"],
    
    "properties": {
        "version": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+(\\.\\d+)?$",
            "description": "Semantic version (e.g., 1.0.0)"
        },
        
        "device": {
            "type": "object",
            "required": ["manufacturer", "model"],
            "properties": {
                "manufacturer": {"type": "string", "minLength": 1},
                "model": {"type": "string", "minLength": 1},
                "firmware_version": {"type": "string"}
            }
        },
        
        "registers": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["name", "address", "data_type"],
                "properties": {
                    "name": {
                        "type": "string",
                        "pattern": "^[a-z][a-z0-9_]*$",
                        "description": "Snake_case name"
                    },
                    "address": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 65535
                    },
                    "data_type": {
                        "type": "string",
                        "enum": ["int16", "uint16", "int32", "uint32", 
                                "float32", "float64", "boolean"]
                    },
                    "unit": {"type": "string"},
                    "scale": {"type": "number"},
                    "access": {
                        "type": "string",
                        "enum": ["read_only", "write_only", "read_write"]
                    },
                    "range": {
                        "type": "object",
                        "properties": {
                            "min": {"type": "number"},
                            "max": {"type": "number"}
                        }
                    }
                }
            }
        }
    }
}


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

USAGE_EXAMPLES = """
# Example 1: Using Basic Template
# ================================

import json

# Start with basic template
my_config = BASIC_CONFIG_TEMPLATE.copy()

# Customize for your device
my_config['device']['manufacturer'] = 'My Company'
my_config['device']['model'] = 'WIDGET-3000'

my_config['registers'] = [
    {
        'name': 'sensor_1',
        'address': 100,
        'data_type': 'float32',
        'unit': 'V',
        'scale': 1.0,
        'access': 'read_only'
    }
]

# Save to file
with open('my_device_config.json', 'w') as f:
    json.dump(my_config, f, indent=2)


# Example 2: Using Rule Engine
# =============================

# Load config and rules
config = json.load(open('device_config.json'))
rules = VALIDATION_RULES_TEMPLATE

# Create engine
engine = RuleEngine(rules)

# Validate data
data = {
    'temperature': 125.5,  # Too high!
    'pressure': 50,
    'device_id': 'DEV001'
}

result = engine.validate(data)

if not result['valid']:
    print("Validation errors:")
    for error in result['errors']:
        print(f"  - {error['message']}")


# Example 3: Loading YAML Config
# ===============================

import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Access nested values
base_addr = config['registers']['measurements']['base_address']
print(f"Measurements base address: {base_addr}")


# Example 4: Validating Config Against Schema
# ============================================

import jsonschema

config = json.load(open('my_config.json'))
schema = JSON_SCHEMA_FOR_CONFIG

try:
    jsonschema.validate(instance=config, schema=schema)
    print("✓ Config is valid!")
except jsonschema.ValidationError as e:
    print(f"✗ Config validation failed: {e.message}")


# Example 5: Environment Variables in Config
# ===========================================

import os

def expand_env_vars(config):
    '''Replace ${ENV:VAR_NAME} with environment variable value'''
    import re
    
    def replace_env(match):
        var_name = match.group(1)
        return os.getenv(var_name, match.group(0))
    
    if isinstance(config, str):
        return re.sub(r'\\$\\{ENV:([^}]+)\\}', replace_env, config)
    elif isinstance(config, dict):
        return {k: expand_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [expand_env_vars(item) for item in config]
    return config

# Usage
os.environ['DB_PASSWORD'] = 'secret123'
config = {'password': '${ENV:DB_PASSWORD}'}
config = expand_env_vars(config)
print(config)  # {'password': 'secret123'}
"""

print(USAGE_EXAMPLES)
