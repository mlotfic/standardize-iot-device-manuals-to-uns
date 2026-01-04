"""
Modbus Device Register Specification Extractor
==============================================
Schema Design + Rule-Based System for Python Interpretation
"""

# ============================================================================
# APPROACH 1: FLAT SCHEMA (Simple & Direct)
# ============================================================================

FLAT_SCHEMA_EXAMPLE = {
    "device_info": {
        "manufacturer": "Schneider Electric",
        "model": "PM5560",
        "modbus_address": 1,
        "baud_rate": 9600,
        "protocol": "RTU"
    },
    "registers": [
        {
            "name": "Voltage L1-N",
            "address": 3027,
            "function_code": 3,
            "data_type": "float32",
            "byte_order": "big_endian",
            "word_order": "big_endian",
            "unit": "V",
            "scale": 1.0,
            "offset": 0.0,
            "read_only": True,
            "description": "Phase 1 voltage to neutral"
        },
        {
            "name": "Current L1",
            "address": 3001,
            "function_code": 3,
            "data_type": "uint16",
            "unit": "A",
            "scale": 0.01,
            "offset": 0.0,
            "read_only": True
        }
    ]
}

FLAT_SCHEMA_PROS = """
✅ PROS:
- Simple to understand and implement
- Easy to serialize/deserialize
- Direct mapping from table rows
- Minimal nesting complexity
- Good for basic extraction tasks

❌ CONS:
- No grouping of related registers
- Redundant device info if multiple files
- Harder to manage large register sets
- No semantic relationships
- Limited validation context
"""

# ============================================================================
# APPROACH 2: HIERARCHICAL SCHEMA (Organized & Scalable)
# ============================================================================

HIERARCHICAL_SCHEMA_EXAMPLE = {
    "metadata": {
        "schema_version": "2.0",
        "created_at": "2025-12-28T10:00:00Z",
        "extracted_from": "PM5560_Manual.pdf"
    },
    "device": {
        "manufacturer": "Schneider Electric",
        "model": "PM5560",
        "firmware_version": "2.1.0",
        "communication": {
            "protocol": "RTU",
            "default_address": 1,
            "baud_rate": 9600,
            "parity": "none",
            "stop_bits": 1
        }
    },
    "register_groups": {
        "measurements": {
            "description": "Real-time electrical measurements",
            "base_address": 3000,
            "registers": [
                {
                    "name": "voltage_l1_n",
                    "display_name": "Voltage L1-N",
                    "offset": 27,  # Address = base_address + offset
                    "function_code": 3,
                    "data_type": "float32",
                    "byte_order": "big_endian",
                    "word_order": "big_endian",
                    "unit": "V",
                    "scale": 1.0,
                    "range": {"min": 0, "max": 690},
                    "access": "read_only",
                    "poll_rate": "fast"  # fast/medium/slow
                }
            ]
        },
        "configuration": {
            "description": "Device configuration parameters",
            "base_address": 5000,
            "registers": [
                {
                    "name": "ct_ratio_primary",
                    "display_name": "CT Ratio Primary",
                    "offset": 10,
                    "function_code": 6,
                    "data_type": "uint16",
                    "scale": 1.0,
                    "range": {"min": 1, "max": 32000},
                    "access": "read_write",
                    "validation": "range_check"
                }
            ]
        }
    }
}

HIERARCHICAL_SCHEMA_PROS = """
✅ PROS:
- Logical grouping of related registers
- Supports base address + offset pattern
- Better for large register maps (1000+ registers)
- Easier to maintain and document
- Supports different access patterns (read/write)

❌ CONS:
- More complex to parse initially
- Requires address calculation (base + offset)
- Harder for simple extraction tasks
- More boilerplate for small devices
"""

# ============================================================================
# APPROACH 3: RULE-BASED SCHEMA (Validation-Rich)
# ============================================================================

RULE_BASED_SCHEMA_EXAMPLE = {
    "device": {
        "manufacturer": "Schneider Electric",
        "model": "PM5560"
    },
    "rules": {
        "address_rules": {
            "holding_registers": {"min": 40001, "max": 49999},
            "input_registers": {"min": 30001, "max": 39999},
            "coils": {"min": 1, "max": 9999},
            "discrete_inputs": {"min": 10001, "max": 19999}
        },
        "data_type_rules": {
            "uint16": {"size": 1, "signed": False},
            "int16": {"size": 1, "signed": True},
            "uint32": {"size": 2, "signed": False},
            "int32": {"size": 2, "signed": True},
            "float32": {"size": 2, "signed": True, "ieee754": True},
            "float64": {"size": 4, "signed": True, "ieee754": True}
        },
        "validation_rules": [
            {
                "rule_id": "voltage_range",
                "applies_to": "voltage_*",
                "type": "range",
                "min": 0,
                "max": 690,
                "unit": "V"
            },
            {
                "rule_id": "frequency_range",
                "applies_to": "*_frequency",
                "type": "range",
                "min": 45,
                "max": 65,
                "unit": "Hz"
            }
        ],
        "naming_conventions": {
            "pattern": "snake_case",
            "forbidden_chars": [" ", "-", "/"],
            "max_length": 64
        }
    },
    "registers": [
        {
            "name": "voltage_l1_n",
            "address": 3027,
            "function_code": 3,
            "data_type": "float32",
            "byte_order": "big_endian",
            "word_order": "big_endian",
            "unit": "V",
            "scale": 1.0,
            "validation_rules": ["voltage_range"]
        }
    ]
}

RULE_BASED_SCHEMA_PROS = """
✅ PROS:
- Comprehensive validation built-in
- Reusable validation rules
- Catches errors early in extraction
- Self-documenting constraints
- Supports pattern matching for rules

❌ CONS:
- Most complex to implement
- Overhead for simple extractions
- Requires rule engine
- Harder to manually edit
- Steeper learning curve
"""

# ============================================================================
# APPROACH 4: EXTENDED METADATA SCHEMA (Production-Ready)
# ============================================================================

EXTENDED_METADATA_SCHEMA = {
    "schema_version": "3.0",
    "metadata": {
        "extraction": {
            "source_type": "pdf",  # pdf, manual, datasheet, csv
            "source_file": "PM5560_Manual.pdf",
            "extraction_date": "2025-12-28T10:00:00Z",
            "extractor_version": "1.2.0",
            "confidence_score": 0.95,  # ML extraction confidence
            "manual_review_required": False
        },
        "device": {
            "manufacturer": "Schneider Electric",
            "model": "PM5560",
            "firmware_version": "2.1.0",
            "manual_version": "Rev 5",
            "release_date": "2024-01-15"
        }
    },
    "communication": {
        "protocol": "modbus_rtu",
        "default_slave_id": 1,
        "baud_rate_options": [9600, 19200, 38400],
        "default_baud_rate": 9600,
        "parity": "none",
        "data_bits": 8,
        "stop_bits": 1,
        "timeout_ms": 1000,
        "retry_count": 3
    },
    "register_map": {
        "version": "1.0",
        "total_registers": 156,
        "register_categories": {
            "measurements": {
                "count": 87,
                "address_range": [3000, 3087],
                "update_rate_ms": 100,
                "priority": "high"
            },
            "status": {
                "count": 23,
                "address_range": [4000, 4023],
                "update_rate_ms": 1000,
                "priority": "medium"
            },
            "configuration": {
                "count": 46,
                "address_range": [5000, 5046],
                "update_rate_ms": null,
                "priority": "low"
            }
        }
    },
    "registers": [
        {
            "register_id": "r_3027",
            "name": "voltage_l1_n",
            "display_name": "Voltage L1-N",
            "category": "measurements",
            "address": 3027,
            "function_code": 3,
            "data_type": "float32",
            "byte_order": "big_endian",
            "word_order": "big_endian",
            "register_count": 2,
            "unit": "V",
            "scale_factor": 1.0,
            "offset": 0.0,
            "decimal_places": 2,
            "range": {
                "min": 0,
                "max": 690,
                "typical_min": 100,
                "typical_max": 480
            },
            "access_mode": "read_only",
            "quality_flags": {
                "has_quality_bit": False,
                "error_value": null
            },
            "alarm_config": {
                "low_alarm": 190,
                "high_alarm": 270,
                "enabled": True
            },
            "documentation": {
                "description": "Phase 1 voltage to neutral",
                "page_reference": "Manual p.45",
                "notes": "Updated in firmware 2.1.0"
            },
            "extraction_metadata": {
                "confidence": 0.98,
                "source_table_row": 27,
                "requires_verification": False
            }
        }
    ]
}

EXTENDED_METADATA_PROS = """
✅ PROS:
- Production-ready with full metadata
- Supports ML extraction workflows
- Comprehensive documentation
- Audit trail for extraction
- Alarm configuration built-in
- Quality tracking and confidence scores

❌ CONS:
- Very verbose for simple cases
- High storage overhead
- Complex to manually create
- Requires sophisticated tooling
- Overkill for small projects
"""

# ============================================================================
# RULE-BASED VALIDATION SYSTEM
# ============================================================================

class ModbusRegisterValidator:
    """Rule-based validation system for Modbus register specifications."""
    
    def __init__(self, schema):
        self.schema = schema
        self.errors = []
        self.warnings = []
    
    def validate_all(self):
        """Run all validation rules."""
        self.validate_address_ranges()
        self.validate_data_types()
        self.validate_function_codes()
        self.validate_naming_conventions()
        self.validate_units()
        self.validate_duplicates()
        return len(self.errors) == 0
    
    def validate_address_ranges(self):
        """Rule: Addresses must be within valid Modbus ranges."""
        for reg in self.schema.get('registers', []):
            addr = reg.get('address')
            fc = reg.get('function_code')
            
            # Modbus address ranges
            valid_ranges = {
                1: (1, 9999),      # Coils
                2: (10001, 19999), # Discrete Inputs
                3: (30001, 39999), # Input Registers
                4: (40001, 49999), # Holding Registers
                6: (40001, 49999), # Write Single Register
                16: (40001, 49999) # Write Multiple Registers
            }
            
            if fc in valid_ranges:
                min_addr, max_addr = valid_ranges[fc]
                if not (min_addr <= addr <= max_addr):
                    self.errors.append(
                        f"Register '{reg.get('name')}': Address {addr} "
                        f"out of range for function code {fc}"
                    )
    
    def validate_data_types(self):
        """Rule: Data types must match register count."""
        type_sizes = {
            'uint16': 1, 'int16': 1,
            'uint32': 2, 'int32': 2,
            'float32': 2, 'float64': 4
        }
        
        for reg in self.schema.get('registers', []):
            dtype = reg.get('data_type')
            reg_count = reg.get('register_count', 1)
            expected_size = type_sizes.get(dtype)
            
            if expected_size and reg_count != expected_size:
                self.errors.append(
                    f"Register '{reg.get('name')}': Data type {dtype} "
                    f"requires {expected_size} registers, got {reg_count}"
                )
    
    def validate_function_codes(self):
        """Rule: Function codes must match access mode."""
        read_only_fc = [1, 2, 3, 4]
        write_fc = [5, 6, 15, 16]
        
        for reg in self.schema.get('registers', []):
            fc = reg.get('function_code')
            access = reg.get('access_mode', 'read_only')
            
            if access == 'read_only' and fc not in read_only_fc:
                self.warnings.append(
                    f"Register '{reg.get('name')}': Marked read_only "
                    f"but has write function code {fc}"
                )
            elif access == 'write_only' and fc not in write_fc:
                self.errors.append(
                    f"Register '{reg.get('name')}': Marked write_only "
                    f"but has read function code {fc}"
                )
    
    def validate_naming_conventions(self):
        """Rule: Register names must follow conventions."""
        import re
        pattern = r'^[a-z][a-z0-9_]*$'  # snake_case
        
        for reg in self.schema.get('registers', []):
            name = reg.get('name', '')
            if not re.match(pattern, name):
                self.warnings.append(
                    f"Register name '{name}' doesn't follow snake_case convention"
                )
            if len(name) > 64:
                self.errors.append(
                    f"Register name '{name}' exceeds 64 character limit"
                )
    
    def validate_units(self):
        """Rule: Units must be from standard set."""
        standard_units = {
            'V', 'A', 'W', 'VA', 'VAR', 'Hz', 'Wh', 'kWh', 'VAh', 'VARh',
            'degC', 'degF', '%', 'ppm', 'bar', 'Pa', 'rpm'
        }
        
        for reg in self.schema.get('registers', []):
            unit = reg.get('unit')
            if unit and unit not in standard_units:
                self.warnings.append(
                    f"Register '{reg.get('name')}': Non-standard unit '{unit}'"
                )
    
    def validate_duplicates(self):
        """Rule: No duplicate addresses or names."""
        addresses = {}
        names = {}
        
        for reg in self.schema.get('registers', []):
            addr = reg.get('address')
            name = reg.get('name')
            
            if addr in addresses:
                self.errors.append(
                    f"Duplicate address {addr}: '{addresses[addr]}' and '{name}'"
                )
            else:
                addresses[addr] = name
            
            if name in names:
                self.errors.append(
                    f"Duplicate name '{name}' at addresses {names[name]} and {addr}"
                )
            else:
                names[name] = addr


# ============================================================================
# PYTHON INTERPRETER EXAMPLE
# ============================================================================

class ModbusRegisterInterpreter:
    """Interprets and executes Modbus register specifications."""
    
    def __init__(self, schema):
        self.schema = schema
        self.validator = ModbusRegisterValidator(schema)
    
    def load_and_validate(self):
        """Load schema and validate it."""
        if not self.validator.validate_all():
            raise ValueError(f"Validation errors: {self.validator.errors}")
        return True
    
    def get_register_by_name(self, name):
        """Retrieve register config by name."""
        for reg in self.schema.get('registers', []):
            if reg.get('name') == name:
                return reg
        return None
    
    def get_registers_by_category(self, category):
        """Get all registers in a category."""
        return [
            reg for reg in self.schema.get('registers', [])
            if reg.get('category') == category
        ]
    
    def calculate_absolute_address(self, register):
        """Calculate absolute address from base + offset if needed."""
        if 'base_address' in register:
            return register['base_address'] + register.get('offset', 0)
        return register.get('address')
    
    def decode_value(self, register, raw_bytes):
        """Decode raw Modbus bytes according to register specification."""
        import struct
        
        dtype = register['data_type']
        byte_order = register.get('byte_order', 'big_endian')
        word_order = register.get('word_order', 'big_endian')
        
        # Handle byte swapping based on orders
        if dtype == 'float32':
            if word_order == 'little_endian':
                raw_bytes = raw_bytes[2:4] + raw_bytes[0:2]
            value = struct.unpack('>f' if byte_order == 'big_endian' else '<f', 
                                 raw_bytes)[0]
        elif dtype == 'uint16':
            value = struct.unpack('>H' if byte_order == 'big_endian' else '<H',
                                 raw_bytes)[0]
        # Add more types as needed
        
        # Apply scaling
        value = value * register.get('scale', 1.0) + register.get('offset', 0.0)
        return value


# ============================================================================
# RECOMMENDATIONS
# ============================================================================

RECOMMENDATIONS = """
SCHEMA SELECTION GUIDE:
=======================

Use FLAT SCHEMA when:
- Extracting from simple tables (<50 registers)
- Quick prototyping or one-off extractions
- Simple devices with no grouping needed
- JSON will be manually edited

Use HIERARCHICAL SCHEMA when:
- Device has 100+ registers
- Registers naturally group by function
- Need to support multiple firmware versions
- Working with register address ranges

Use RULE-BASED SCHEMA when:
- Extracting from multiple similar devices
- Need automated validation
- Building reusable extraction pipeline
- Data quality is critical

Use EXTENDED METADATA SCHEMA when:
- Production ML extraction pipeline
- Need full audit trail
- Multiple team members/tools
- Long-term maintenance required
- Regulatory compliance needed

HYBRID APPROACH (Recommended for most cases):
- Use HIERARCHICAL structure for organization
- Add RULES for validation
- Include metadata selectively based on needs
- Start simple, add complexity as needed
"""

print(RECOMMENDATIONS)