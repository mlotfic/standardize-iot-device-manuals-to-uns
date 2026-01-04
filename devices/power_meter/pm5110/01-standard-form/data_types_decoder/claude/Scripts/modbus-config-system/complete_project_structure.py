"""
MODBUS DEVICE CONFIGURATION PROJECT
====================================
Complete project structure with all templates as separate files

PROJECT STRUCTURE:
==================

modbus-config-system/
│
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
├── .gitignore                        # Git ignore rules
│
├── config/                           # Configuration files
│   ├── templates/                    # Reusable templates
│   │   ├── basic_config.json
│   │   ├── hierarchical_config.json
│   │   ├── data_type_library.json
│   │   ├── validation_rules.json
│   │   └── compressed_config.json
│   │
│   ├── devices/                      # Device-specific configs
│   │   ├── pm5110/
│   │   │   ├── main_config.json
│   │   │   ├── data_types.json
│   │   │   ├── validation_rules.json
│   │   │   └── registers/
│   │   │       ├── measurements.json
│   │   │       ├── configuration.json
│   │   │       ├── alarms.json
│   │   │       ├── events.json
│   │   │       ├── harmonics.json
│   │   │       └── units.json
│   │   │
│   │   ├── tc100/                    # Temperature Controller example
│   │   │   ├── config.json
│   │   │   └── rules.json
│   │   ├── gps/
│   │   │   ├── config.json
│   │   │   └── rules.json
│   │   │
│   │   └── custom_device/            # Your device here
│   │       └── config.json
│   │
│   └── schemas/                      # JSON schemas for validation
│       ├── config_schema.json
│       ├── rules_schema.json
│       ├── data_types_schema.json
│       └── units_schema.json
│
├── src/                              # Source code
│   ├── __init__.py
│   ├── config_loader.py              # Load and merge configs
│   ├── rule_engine.py                # Validation engine
│   ├── decoder.py                    # Data decoding
│   ├── generator.py                  # Config generation tools
│   └── utils.py                      # Helper functions
│
├── tools/                            # Utility scripts
│   ├── csv_to_config.py              # Convert CSV to JSON config
│   ├── validate_config.py            # Validate config files
│   ├── expand_patterns.py            # Expand compressed configs
│   ├── split_large_config.py         # Split large configs
│   └── manual_extractor.py           # Extract from PDF manuals
│
├── examples/                         # Example usage
│   ├── basic_usage.py
│   ├── large_scale_example.py
│   ├── custom_decoder.py
│   └── batch_processing.py
│
├── tests/                            # Unit tests
│   ├── test_config_loader.py
│   ├── test_rule_engine.py
│   ├── test_decoder.py
│   └── test_generator.py
│
└── docs/                             # Documentation
    ├── getting_started.md
    ├── template_guide.md
    ├── large_scale_optimization.md
    └── api_reference.md
"""

# ============================================================================
# FILE 1: config/templates/basic_config.json
# ============================================================================

BASIC_CONFIG_JSON = '''{
  "$schema": "../schemas/config_schema.json",
  "version": "1.0.0",
  "template_type": "basic",
  "description": "Basic configuration template for simple devices",
  
  "device": {
    "manufacturer": "MANUFACTURER_NAME",
    "model": "MODEL_NUMBER",
    "firmware_version": "1.0.0",
    "device_type": "sensor|actuator|controller|meter",
    "description": "Brief device description"
  },
  
  "connection": {
    "protocol": "modbus_rtu",
    "host": "192.168.1.100",
    "port": 502,
    "slave_id": 1,
    "baudrate": 9600,
    "bytesize": 8,
    "parity": "N",
    "stopbits": 1,
    "timeout_ms": 1000,
    "retry_count": 3
  },
  
  "registers": [
    {
      "name": "register_name",
      "address": 100,
      "function_code": 3,
      "data_type": "int16|uint16|int32|uint32|float32|float64|boolean",
      "access": "read_only|write_only|read_write",
      "unit": "°C|A|V|W|%|...",
      "scale": 1.0,
      "offset": 0.0,
      "range": {
        "min": 0,
        "max": 100
      },
      "description": "Register description",
      "poll_rate_ms": 1000
    }
  ],
  
  "metadata": {
    "created": "2025-12-28",
    "author": "Your Name",
    "notes": "Additional notes"
  }
}'''


# ============================================================================
# FILE 2: config/templates/hierarchical_config.json
# ============================================================================

HIERARCHICAL_CONFIG_JSON = '''{
  "$schema": "../schemas/config_schema.json",
  "version": "2.0.0",
  "template_type": "hierarchical",
  "description": "Hierarchical configuration for devices with 50+ registers",
  
  "device": {
    "manufacturer": "MANUFACTURER",
    "model": "MODEL",
    "device_type": "power_meter",
    "capabilities": ["measurements", "alarms", "configuration", "events"]
  },
  
  "communication": {
    "protocol": "modbus_rtu",
    "default_slave_id": 1,
    "baudrate": 9600,
    "parity": "none",
    "databits": 8,
    "stopbits": 1
  },
  
  "register_groups": {
    "measurements": {
      "description": "Real-time measurement values",
      "base_address": 3000,
      "function_code": 4,
      "poll_rate_ms": 1000,
      "priority": "high",
      
      "common_properties": {
        "access": "read_only",
        "data_type": "float32",
        "byte_order": "big_endian",
        "word_order": "big_endian"
      },
      
      "registers": [
        {
          "name": "voltage_l1",
          "offset": 0,
          "unit": "V",
          "range": {"min": 0, "max": 690},
          "scale": 1.0
        },
        {
          "name": "current_l1",
          "offset": 10,
          "unit": "A",
          "range": {"min": 0, "max": 10000},
          "scale": 0.01
        }
      ]
    },
    
    "configuration": {
      "description": "Device configuration parameters",
      "base_address": 5000,
      "function_code": 3,
      "poll_rate_ms": null,
      
      "common_properties": {
        "access": "read_write",
        "data_type": "uint16"
      },
      
      "registers": [
        {
          "name": "ct_ratio",
          "offset": 0,
          "unit": "A",
          "range": {"min": 5, "max": 5000},
          "default": 100
        }
      ]
    },
    
    "status": {
      "description": "Device status and flags",
      "base_address": 4000,
      "function_code": 2,
      "poll_rate_ms": 5000,
      
      "registers": [
        {
          "name": "alarm_active",
          "offset": 0,
          "data_type": "boolean"
        }
      ]
    }
  }
}'''


# ============================================================================
# FILE 3: config/templates/data_type_library.json
# ============================================================================

DATA_TYPE_LIBRARY_JSON = '''{
  "version": "1.0.0",
  "description": "Reusable data type definitions",
  
  "simple_types": {
    "uint16": {
      "size_bits": 16,
      "size_registers": 1,
      "signed": false,
      "byte_order": "big_endian",
      "min": 0,
      "max": 65535
    },
    
    "int16": {
      "size_bits": 16,
      "size_registers": 1,
      "signed": true,
      "byte_order": "big_endian",
      "min": -32768,
      "max": 32767
    },
    
    "uint32": {
      "size_bits": 32,
      "size_registers": 2,
      "signed": false,
      "byte_order": "big_endian",
      "word_order": "big_endian",
      "min": 0,
      "max": 4294967295
    },
    
    "int32": {
      "size_bits": 32,
      "size_registers": 2,
      "signed": true,
      "byte_order": "big_endian",
      "word_order": "big_endian",
      "min": -2147483648,
      "max": 2147483647
    },
    
    "float32": {
      "size_bits": 32,
      "size_registers": 2,
      "format": "ieee754",
      "byte_order": "big_endian",
      "word_order": "big_endian"
    },
    
    "float64": {
      "size_bits": 64,
      "size_registers": 4,
      "format": "ieee754",
      "byte_order": "big_endian",
      "word_order": "big_endian"
    }
  },
  
  "complex_types": {
    "ipv4_address": {
      "size_registers": 2,
      "description": "IPv4 address as 4 bytes",
      "structure": {
        "octet1": {"byte_offset": 0, "type": "uint8"},
        "octet2": {"byte_offset": 1, "type": "uint8"},
        "octet3": {"byte_offset": 2, "type": "uint8"},
        "octet4": {"byte_offset": 3, "type": "uint8"}
      },
      "format_string": "{octet1}.{octet2}.{octet3}.{octet4}",
      "example": "192.168.1.100"
    },
    
    "mac_address": {
      "size_registers": 3,
      "description": "MAC address as 6 bytes",
      "structure": {
        "byte1": {"byte_offset": 0, "type": "uint8"},
        "byte2": {"byte_offset": 1, "type": "uint8"},
        "byte3": {"byte_offset": 2, "type": "uint8"},
        "byte4": {"byte_offset": 3, "type": "uint8"},
        "byte5": {"byte_offset": 4, "type": "uint8"},
        "byte6": {"byte_offset": 5, "type": "uint8"}
      },
      "format_string": "{byte1:02X}:{byte2:02X}:{byte3:02X}:{byte4:02X}:{byte5:02X}:{byte6:02X}",
      "example": "AA:BB:CC:DD:EE:FF"
    },
    
    "unix_timestamp": {
      "size_registers": 2,
      "description": "Unix timestamp (seconds since 1970-01-01)",
      "base_type": "uint32",
      "conversion": "unix_timestamp",
      "format_string": "%Y-%m-%d %H:%M:%S"
    },
    
    "status_word": {
      "size_registers": 1,
      "description": "16-bit status flags",
      "bit_fields": [
        {"name": "running", "bit": 0, "description": "System running"},
        {"name": "alarm", "bit": 1, "description": "Alarm active"},
        {"name": "warning", "bit": 2, "description": "Warning active"},
        {"name": "manual_mode", "bit": 3, "description": "Manual control"},
        {"name": "auto_mode", "bit": 4, "description": "Automatic control"},
        {"name": "remote_control", "bit": 5, "description": "Remote control enabled"},
        {"name": "maintenance", "bit": 15, "description": "Maintenance mode"}
      ]
    },
    
    "datetime_iec": {
      "size_registers": 4,
      "description": "IEC 870-5 timestamp format",
      "standard": "IEC 870-5",
      "bit_fields": [
        {
          "name": "year",
          "bit_offset": 0,
          "bit_width": 7,
          "type": "unsigned_int",
          "range": {"min": 0, "max": 127},
          "transform": "value + 2000"
        },
        {
          "name": "month",
          "bit_offset": 24,
          "bit_width": 4,
          "type": "unsigned_int",
          "range": {"min": 1, "max": 12}
        },
        {
          "name": "day",
          "bit_offset": 16,
          "bit_width": 5,
          "type": "unsigned_int",
          "range": {"min": 1, "max": 31}
        },
        {
          "name": "hour",
          "bit_offset": 40,
          "bit_width": 5,
          "type": "unsigned_int",
          "range": {"min": 0, "max": 23}
        },
        {
          "name": "minute",
          "bit_offset": 32,
          "bit_width": 6,
          "type": "unsigned_int",
          "range": {"min": 0, "max": 59}
        },
        {
          "name": "millisecond",
          "bit_offset": 48,
          "bit_width": 16,
          "type": "unsigned_int",
          "range": {"min": 0, "max": 59999}
        }
      ]
    }
  }
}'''


# ============================================================================
# FILE 4: config/templates/validation_rules.json
# ============================================================================

VALIDATION_RULES_JSON = '''{
  "version": "1.0.0",
  "description": "Comprehensive validation rules template",
  
  "field_rules": {
    "range_validation": {
      "rule_id": "range_check",
      "description": "Value must be within specified range",
      "rule_type": "range",
      "severity": "error",
      "applies_to": ["*"],
      "parameters": {
        "use_field_range": true
      },
      "message_template": "{field_name} value {value} outside valid range [{min}, {max}]"
    },
    
    "required_fields": {
      "rule_id": "required_check",
      "description": "Required fields must have values",
      "rule_type": "required",
      "severity": "error",
      "applies_to": ["device_id", "timestamp", "address"],
      "message_template": "{field_name} is required but missing"
    },
    
    "data_type_validation": {
      "rule_id": "type_check",
      "description": "Value must match expected data type",
      "rule_type": "type_check",
      "severity": "error",
      "applies_to": ["*"]
    },
    
    "enum_validation": {
      "rule_id": "enum_check",
      "description": "Value must be one of allowed values",
      "rule_type": "enum",
      "severity": "error",
      "examples": [
        {
          "field": "access",
          "allowed_values": ["read_only", "write_only", "read_write"]
        },
        {
          "field": "protocol",
          "allowed_values": ["modbus_rtu", "modbus_tcp", "mqtt", "opcua"]
        }
      ]
    }
  },
  
  "relationship_rules": {
    "min_max_order": {
      "rule_id": "min_less_than_max",
      "description": "Minimum must be less than maximum",
      "rule_type": "comparison",
      "severity": "error",
      "fields": ["range.min", "range.max"],
      "logic": "range.min < range.max",
      "message": "Minimum value must be less than maximum value"
    },
    
    "address_uniqueness": {
      "rule_id": "unique_addresses",
      "description": "Register addresses must be unique",
      "rule_type": "uniqueness",
      "severity": "error",
      "field": "address",
      "scope": "global"
    },
    
    "name_uniqueness": {
      "rule_id": "unique_names",
      "description": "Register names must be unique",
      "rule_type": "uniqueness",
      "severity": "error",
      "field": "name",
      "scope": "global"
    }
  },
  
  "conditional_rules": {
    "write_requires_range": {
      "rule_id": "writable_needs_limits",
      "description": "Writable registers should have range limits",
      "severity": "warning",
      "when": {
        "field": "access",
        "in": ["write_only", "read_write"]
      },
      "then": {
        "field": "range",
        "rule": "required"
      },
      "message": "Writable register should define valid range"
    },
    
    "alarm_threshold_required": {
      "rule_id": "alarm_needs_threshold",
      "description": "Enabled alarms must have thresholds",
      "severity": "error",
      "when": {
        "field": "alarm_enabled",
        "equals": true
      },
      "then": {
        "field": "alarm_threshold",
        "rule": "required"
      }
    }
  },
  
  "pattern_rules": {
    "naming_convention": {
      "rule_id": "snake_case_names",
      "description": "Register names must use snake_case",
      "rule_type": "regex",
      "severity": "warning",
      "applies_to": ["name"],
      "pattern": "^[a-z][a-z0-9_]*$",
      "message": "Register name should use snake_case format",
      "examples": ["voltage_l1", "current_phase_a", "temperature_sensor_1"]
    },
    
    "serial_number_format": {
      "rule_id": "serial_format",
      "description": "Serial number format validation",
      "rule_type": "regex",
      "severity": "error",
      "applies_to": ["serial_number"],
      "pattern": "^[A-Z]{2}[0-9]{8}$",
      "example": "AB12345678"
    }
  },
  
  "temporal_rules": {
    "no_future_dates": {
      "rule_id": "no_future_timestamp",
      "description": "Timestamps cannot be in the future",
      "rule_type": "temporal",
      "severity": "warning",
      "applies_to": ["timestamp", "*_date", "*_time"],
      "logic": "value <= now()",
      "message": "Timestamp is in the future"
    },
    
    "data_freshness": {
      "rule_id": "stale_data_check",
      "description": "Data should be recent",
      "rule_type": "temporal",
      "severity": "warning",
      "applies_to": ["measurement_timestamp"],
      "logic": "now() - value < 300",
      "threshold_seconds": 300,
      "message": "Data is stale (>5 minutes old)"
    }
  },
  
  "custom_rules": {
    "power_factor_range": {
      "rule_id": "pf_normal_range",
      "description": "Power factor typically between -1 and +1",
      "severity": "warning",
      "applies_to": ["power_factor*"],
      "rule_type": "range",
      "normal_range": {"min": -1.0, "max": 1.0},
      "absolute_range": {"min": -2.0, "max": 2.0},
      "message": "Power factor outside normal operating range"
    }
  }
}'''


# ============================================================================
# FILE 5: config/templates/compressed_config.json
# ============================================================================

COMPRESSED_CONFIG_JSON = '''{
  "version": "3.0.0",
  "template_type": "compressed",
  "description": "Compressed configuration for large-scale register maps (1000+)",
  
  "device": {
    "manufacturer": "MANUFACTURER",
    "model": "MODEL",
    "estimated_register_count": 1000
  },
  
  "register_patterns": {
    "phase_measurement": {
      "description": "Template for 3-phase measurements",
      "data_type": "float32",
      "access": "read_only",
      "function_code": 4,
      "registers_per_item": 2,
      "phases": ["l1", "l2", "l3"]
    },
    
    "energy_counter": {
      "description": "Template for energy counters",
      "data_type": "uint64",
      "access": "read_only",
      "function_code": 4,
      "registers_per_item": 4
    },
    
    "config_parameter": {
      "description": "Template for configuration parameters",
      "data_type": "uint16",
      "access": "read_write",
      "function_code": 3,
      "registers_per_item": 1
    }
  },
  
  "generated_register_groups": {
    "voltages": {
      "pattern_ref": "phase_measurement",
      "base_address": 3000,
      "items": [
        {
          "name_template": "voltage_{phase}_n",
          "unit": "V",
          "range": {"min": 0, "max": 690}
        },
        {
          "name_template": "voltage_{phase}_{next_phase}",
          "unit": "V",
          "range": {"min": 0, "max": 1200}
        }
      ]
    },
    
    "currents": {
      "pattern_ref": "phase_measurement",
      "base_address": 3020,
      "items": [
        {
          "name_template": "current_{phase}",
          "unit": "A",
          "range": {"min": 0, "max": 10000},
          "scale": 0.01
        }
      ]
    },
    
    "harmonics": {
      "description": "Harmonic analysis (generates 100+ registers)",
      "base_address": 7000,
      "pattern_ref": "phase_measurement",
      "items": [
        {
          "name_template": "voltage_{phase}_h{harmonic}",
          "unit": "V",
          "harmonic_range": [1, 63]
        },
        {
          "name_template": "current_{phase}_h{harmonic}",
          "unit": "A",
          "harmonic_range": [1, 63]
        }
      ]
    }
  },
  
  "external_definitions": {
    "alarm_queue": {
      "source_type": "file",
      "path": "./registers/alarms.json",
      "description": "Alarm event queue (1200 registers)",
      "address_range": [11000, 12199]
    },
    
    "event_log": {
      "source_type": "file",
      "path": "./registers/events.json",
      "description": "Event log entries",
      "address_range": [13000, 14999]
    }
  }
}'''


# ============================================================================
# FILE 6: config/schemas/config_schema.json
# ============================================================================

CONFIG_SCHEMA_JSON = '''{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://example.com/modbus-config-schema.json",
  "title": "Modbus Device Configuration Schema",
  "description": "JSON Schema for validating Modbus device configurations",
  "type": "object",
  "required": ["version", "device"],
  
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\\\.[0-9]+(\\\\.[0-9]+)?$",
      "description": "Semantic version (e.g., 1.0.0, 2.1.3)"
    },
    
    "template_type": {
      "type": "string",
      "enum": ["basic", "hierarchical", "compressed", "custom"]
    },
    
    "device": {
      "type": "object",
      "required": ["manufacturer", "model"],
      "properties": {
        "manufacturer": {
          "type": "string",
          "minLength": 1
        },
        "model": {
          "type": "string",
          "minLength": 1
        },
        "firmware_version": {
          "type": "string"
        },
        "device_type": {
          "type": "string",
          "enum": ["sensor", "actuator", "controller", "meter", "gateway", "other"]
        }
      }
    },
    
    "connection": {
      "type": "object",
      "properties": {
        "protocol": {
          "type": "string",
          "enum": ["modbus_rtu", "modbus_tcp", "modbus_ascii"]
        },
        "host": {"type": "string"},
        "port": {"type": "integer", "minimum": 1, "maximum": 65535},
        "slave_id": {"type": "integer", "minimum": 1, "maximum": 247},
        "baudrate": {
          "type": "integer",
          "enum": [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
        },
        "timeout_ms": {"type": "integer", "minimum": 100}
      }
    },
    
    "registers": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/register"
      }
    },
    
    "register_groups": {
      "type": "object",
      "patternProperties": {
        "^[a-z_]+$": {
          "$ref": "#/definitions/register_group"
        }
      }
    }
  },
  
  "definitions": {
    "register": {
      "type": "object",
      "required": ["name", "address", "data_type"],
      "properties": {
        "name": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9_]*$"
        },
        "address": {
          "type": "integer",
          "minimum": 0,
          "maximum": 65535
        },
        "offset": {
          "type": "integer",
          "minimum": 0
        },
        "function_code": {
          "type": "integer",
          "enum": [1, 2, 3, 4, 5, 6, 15, 16]
        },
        "data_type": {
          "type": "string",
          "enum": ["int16", "uint16", "int32", "uint32", "int64", "uint64", 
                   "float32", "float64", "boolean"]
        },
        "access": {
          "type": "string",
          "enum": ["read_only", "write_only", "read_write"]
        },
        "unit": {"type": "string"},
        "scale": {"type": "number"},
        "offset": {"type": "number"},
        "range": {
          "type": "object",
          "required": ["min", "max"],
          "properties": {
            "min": {"type": "number"},
            "max": {"type": "number"}
          }
        }
      }
    },
    
    "register_group": {
      "type": "object",
      "required": ["base_address", "registers"],
      "properties": {
        "description": {"type": "string"},
        "base_address": {"type": "integer", "minimum": 0},
        "function_code": {"type": "integer"},
        "poll_rate_ms": {"type": ["integer", "null"]},
        "common_properties": {"type": "object"},
        "registers": {
          "type": "array",
          "items": {"$ref": "#/definitions/register"}
        }
      }
    }
  }
}'''


# ============================================================================
# FILE 7: README.md
# ============================================================================

README_MD = '''# Modbus Device Configuration System

A comprehensive, scalable configuration system for Modbus devices with support for simple to complex (1000+) register maps.

## Features

✅ **Multiple Template Types**
- Basic: Simple flat configuration (< 50 registers)
- Hierarchical: Organized groups (50-500 registers)
- Compressed: Pattern-based for large scale (1000+ registers)

✅ **Reusable Components**
- Data type library (simple + complex types)
- Validation rules engine
- JSON schema validation

✅ **Large Scale Optimization**
- Pattern-based register generation
- External file references
- Compressed definitions

✅ **Automation Tools**
- CSV to JSON converter
- Config validator
- Pattern expander
- Manual extractor

## Quick Start

### 1. Choose Your Template

```bash
# For simple devices (< 50 registers)
cp config/templates/basic_config.json config/devices/my_device/config.json

# For medium devices (50-500 registers)
cp config/templates/hierarchical_config.json config/devices/my_device/config.json

# For large devices (1000+ registers)
cp config/templates/compressed_config.json config/devices/my_device/config.json
```

### 2. Customize Your Config

Edit the copied file with your device details:
- Device info (manufacturer, model)
- Connection settings
- Register definitions

### 3. Validate Your Config

```bash
python tools/validate_config.py config/devices/my_device/config.json
```

### 4. Use in Your Application

```python
from src.config_loader import ConfigLoader

# Load config
loader = ConfigLoader()
config = loader.load('config/devices/my_device/config.json')

# Access registers
voltage_register = config.get_register('voltage_l1')
print(f"Address: {voltage_register['address']}")
```

## Project Structure

```
modbus-config-system/
├── config/
│   ├── templates/          # Copy-paste ready templates
│   ├── devices/            # Your device configs
│   └── schemas/            # JSON schemas for validation
├── src/                    # Python source code
├── tools/                  # Utility scripts
├── examples/               # Usage examples
└── tests/                  # Unit tests
```

## Template Guide

### Basic Template
**Use when:** < 50 registers, simple device
**Format:** Flat register list
**Example:** Temperature sensor, simple controller

### Hierarchical Template
**Use when:** 50-500 registers, organized device
**Format:** Grouped registers with common properties
**Example:** Power meter, multi-sensor device

### Compressed Template
**Use when:** 1000+ registers, repetitive patterns
**Format:** Pattern-based generation
**Example:** Harmonic analyzer, large power meter

## Common Workflows

### Extracting from Device Manual

```bash
# If manual has CSV table
python tools/csv_to_config.py manual.csv config.json

# If manual is PDF
python tools/manual_extractor.py manual.pdf config.json
```

### Validating Configuration

```bash
# Validate against JSON schema
python tools/validate_config.py config.json

# Validate with rules engine
python tools/validate_config.py config.json --rules rules.json
```

### Expanding Compressed Config

```bash
# Expand pattern-based config to full register list
python tools/expand_patterns.py compressed_config.json expanded_config.json
```

### Splitting Large Config

```bash
# Split large config into multiple files
python tools/split_large_config.py large_config.json output_dir/ --max-per-file 100
```

## Examples

See `examples/` directory for complete working examples:

- `basic_usage.py` - Simple device configuration
- `large_scale_example.py` - 1000+ register device
- `custom_decoder.py` - Custom data type decoding
- `batch_processing.py` - Processing multiple devices

## Documentation

- [Getting Started](docs/getting_started.md)
- [Template Guide](docs/template_guide.md)
- [Large Scale Optimization](docs/large_scale_optimization.md)
- [API Reference](docs/api_reference.md)

## Requirements

```
Python 3.7+
jsonschema>=4.0.0
pyyaml>=6.0
pymodbus>=3.0.0
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

- Issues: GitHub Issues
- Discussions: GitHub Discussions
- Email: support@example.com
'''


# ============================================================================
# FILE 8: requirements.txt
# ============================================================================

REQUIREMENTS_TXT = '''# Core dependencies
jsonschema>=4.20.0
pyyaml>=6.0.1
pymodbus>=3.5.0

# Utilities
python-dotenv>=1.0.0
click>=8.1.0

# Data processing
pandas>=2.0.0
numpy>=1.24.0

# Optional: PDF extraction
pdfplumber>=0.10.0

# Optional: Excel support
openpyxl>=3.1.0

# Development dependencies
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.1.0
mypy>=1.7.0
'''


# ============================================================================
# FILE 9: .gitignore
# ============================================================================

GITIGNORE = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
ENV/
env/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
config/devices/*/secrets.json
*.log
temp/
output/
*.bak

# Test coverage
.coverage
htmlcov/
.pytest_cache/
'''


# ============================================================================
# SUMMARY: ALL FILES AT A GLANCE
# ============================================================================

PROJECT_FILES_SUMMARY = {
    "core_templates": {
        "config/templates/basic_config.json": "Simple flat configuration",
        "config/templates/hierarchical_config.json": "Grouped configuration",
        "config/templates/compressed_config.json": "Large-scale patterns",
        "config/templates/data_type_library.json": "Reusable data types",
        "config/templates/validation_rules.json": "Validation rules",
    },
    
    "schemas": {
        "config/schemas/config_schema.json": "JSON Schema for validation",
        "config/schemas/rules_schema.json": "Rules schema",
        "config/schemas/data_types_schema.json": "Data types schema",
    },
    
    "documentation": {
        "README.md": "Main project documentation",
        "docs/getting_started.md": "Quick start guide",
        "docs/template_guide.md": "Template selection guide",
        "docs/large_scale_optimization.md": "Optimization strategies",
        "docs/api_reference.md": "API documentation",
    },
    
    "tools": {
        "tools/csv_to_config.py": "Convert CSV to JSON",
        "tools/validate_config.py": "Validate configurations",
        "tools/expand_patterns.py": "Expand compressed configs",
        "tools/split_large_config.py": "Split large files",
        "tools/manual_extractor.py": "Extract from PDFs",
    },
    
    "source_code": {
        "src/config_loader.py": "Load and merge configs",
        "src/rule_engine.py": "Validation engine",
        "src/decoder.py": "Data decoding logic",
        "src/generator.py": "Config generation tools",
        "src/utils.py": "Helper functions",
    },
    
    "examples": {
        "examples/basic_usage.py": "Simple example",
        "examples/large_scale_example.py": "1000+ registers",
        "examples/custom_decoder.py": "Custom decoders",
        "examples/batch_processing.py": "Multiple devices",
    },
    
    "configuration": {
        "requirements.txt": "Python dependencies",
        ".gitignore": "Git ignore rules",
    }
}


# ============================================================================
# EXPORT ALL FILES AS DICTIONARY
# ============================================================================

ALL_PROJECT_FILES = {
    "config/templates/basic_config.json": BASIC_CONFIG_JSON,
    "config/templates/hierarchical_config.json": HIERARCHICAL_CONFIG_JSON,
    "config/templates/data_type_library.json": DATA_TYPE_LIBRARY_JSON,
    "config/templates/validation_rules.json": VALIDATION_RULES_JSON,
    "config/templates/compressed_config.json": COMPRESSED_CONFIG_JSON,
    "config/schemas/config_schema.json": CONFIG_SCHEMA_JSON,
    "README.md": README_MD,
    "requirements.txt": REQUIREMENTS_TXT,
    ".gitignore": GITIGNORE,
}


# ============================================================================
# GENERATE PROJECT SCRIPT
# ============================================================================

def generate_project_structure(base_path="."):
    """
    Generate complete project structure with all files
    
    Usage:
        generate_project_structure("./my_modbus_project")
    """
    import os
    import json
    
    # Create directory structure
    directories = [
        "config/templates",
        "config/devices",
        "config/schemas",
        "src",
        "tools",
        "examples",
        "tests",
        "docs",
    ]
    
    for directory in directories:
        os.makedirs(os.path.join(base_path, directory), exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Write all files
    for filepath, content in ALL_PROJECT_FILES.items():
        full_path = os.path.join(base_path, filepath)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Created file: {filepath}")
    
    print(f"\n✅ Project structure created at: {base_path}")
    print(f"\nNext steps:")
    print(f"1. cd {base_path}")
    print(f"2. python -m venv venv")
    print(f"3. source venv/bin/activate  # or venv\\\\Scripts\\\\activate on Windows")
    print(f"4. pip install -r requirements.txt")
    print(f"5. Copy a template from config/templates/ to config/devices/your_device/")
    print(f"6. Customize the config for your device")
    print(f"7. python tools/validate_config.py config/devices/your_device/config.json")


if __name__ == "__main__":
    print("MODBUS CONFIGURATION SYSTEM - PROJECT STRUCTURE")
    print("=" * 60)
    print("\nTo generate this project structure, run:")
    print("    python this_file.py generate /path/to/project")
    print("\nOr use in Python:")
    print("    generate_project_structure('./my_project')")
    print("\n" + "=" * 60)
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        path = sys.argv[2] if len(sys.argv) > 2 else "./modbus-config-system"
        generate_project_structure(path)
