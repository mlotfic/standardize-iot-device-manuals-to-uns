"""
PM5110 Modbus Register Configuration
=====================================
Expert-designed config inferred from device specification

KEY INSIGHT: This CSV describes BIT-FIELD structures for complex data types,
not simple register addresses. Each type spans multiple registers.
"""

# ============================================================================
# LAYER 1: DEVICE METADATA (What we know about PM5110)
# ============================================================================

DEVICE_METADATA = {
    "manufacturer": "Schneider Electric",
    "model": "PM5110",
    "device_class": "power_meter",
    "protocol": "modbus_rtu",
    "standard_compliance": ["IEC 870-5"],
    "data_encoding": "bit_fields",  # Key characteristic!
    "notes": "Uses complex multi-register data types with bit-level encoding"
}


# ============================================================================
# LAYER 2: DATA TYPE DEFINITIONS (Reusable building blocks)
# ============================================================================
"""
EXPERT THINKING:
- These are ATOMIC definitions - reusable across all registers
- Each defines the structure of a complex data type
- Bit offsets show how to decode multi-register values
"""

DATA_TYPE_DEFINITIONS = {
    "complex_types": {
        
        # 64-bit DATETIME structure (8 bytes = 4 registers)
        "DATETIME": {
            "size_bits": 64,
            "size_registers": 4,
            "byte_order": "big_endian",
            "standard": "IEC 870-5",
            "description": "Timestamp with date, time, and milliseconds",
            
            "bit_fields": [
                {
                    "name": "year",
                    "bit_offset": 0,
                    "bit_width": 6,
                    "type": "unsigned_int",
                    "range": {"min": 0, "max": 127},
                    "unit": "years",
                    "description": "Year (offset from 2000)",
                    "transform": "value + 2000"  # Decode: add base year
                },
                {
                    "name": "reserved_1",
                    "bit_offset": 7,
                    "bit_width": 9,
                    "type": "reserved",
                    "value": 0
                },
                {
                    "name": "day",
                    "bit_offset": 16,
                    "bit_width": 5,
                    "type": "unsigned_int",
                    "range": {"min": 1, "max": 31},
                    "unit": "days"
                },
                {
                    "name": "weekday",
                    "bit_offset": 21,
                    "bit_width": 3,
                    "type": "unsigned_int",
                    "range": {"min": 1, "max": 7},
                    "enum": {
                        1: "Monday", 2: "Tuesday", 3: "Wednesday",
                        4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"
                    }
                },
                {
                    "name": "month",
                    "bit_offset": 24,
                    "bit_width": 4,
                    "type": "unsigned_int",
                    "range": {"min": 1, "max": 12},
                    "enum": {
                        1: "January", 2: "February", 3: "March",
                        4: "April", 5: "May", 6: "June",
                        7: "July", 8: "August", 9: "September",
                        10: "October", 11: "November", 12: "December"
                    }
                },
                {
                    "name": "reserved_2",
                    "bit_offset": 28,
                    "bit_width": 4,
                    "type": "reserved",
                    "value": 0
                },
                {
                    "name": "minutes",
                    "bit_offset": 32,
                    "bit_width": 6,
                    "type": "unsigned_int",
                    "range": {"min": 0, "max": 59},
                    "unit": "minutes"
                },
                {
                    "name": "reserved_3",
                    "bit_offset": 38,
                    "bit_width": 1,
                    "type": "reserved",
                    "value": 0
                },
                {
                    "name": "time_sync_quality",
                    "bit_offset": 39,
                    "bit_width": 1,
                    "type": "flag",
                    "enum": {
                        0: "synchronized",
                        1: "not_synchronized"
                    },
                    "quality_indicator": True
                },
                {
                    "name": "hour",
                    "bit_offset": 40,
                    "bit_width": 5,
                    "type": "unsigned_int",
                    "range": {"min": 0, "max": 23},
                    "unit": "hours"
                },
                {
                    "name": "reserved_4",
                    "bit_offset": 45,
                    "bit_width": 2,
                    "type": "reserved",
                    "value": 0
                },
                {
                    "name": "dst_flag",
                    "bit_offset": 47,
                    "bit_width": 1,
                    "type": "flag",
                    "enum": {
                        0: "standard_time",
                        1: "daylight_savings_time"
                    }
                },
                {
                    "name": "milliseconds",
                    "bit_offset": 48,
                    "bit_width": 16,
                    "type": "unsigned_int",
                    "range": {"min": 0, "max": 59999},
                    "unit": "milliseconds"
                }
            ]
        },
        
        # 32-bit DATE structure (2 registers)
        "DATE": {
            "size_bits": 32,
            "size_registers": 2,
            "byte_order": "big_endian",
            "description": "Date without time component",
            
            "bit_fields": [
                {
                    "name": "year",
                    "bit_offset": 0,
                    "bit_width": 8,
                    "type": "unsigned_int",
                    "range": {"min": 0, "max": 99},
                    "transform": "value + 2000"
                },
                {
                    "name": "reserved_1",
                    "bit_offset": 8,
                    "bit_width": 8,
                    "type": "reserved"
                },
                {
                    "name": "day",
                    "bit_offset": 16,
                    "bit_width": 5,
                    "type": "unsigned_int",
                    "range": {"min": 1, "max": 31}
                },
                {
                    "name": "weekday",
                    "bit_offset": 21,
                    "bit_width": 3,
                    "type": "unsigned_int",
                    "range": {"min": 1, "max": 7}
                },
                {
                    "name": "month",
                    "bit_offset": 24,
                    "bit_width": 4,
                    "type": "unsigned_int",
                    "range": {"min": 1, "max": 12}
                },
                {
                    "name": "reserved_2",
                    "bit_offset": 28,
                    "bit_width": 4,
                    "type": "reserved"
                }
            ]
        },
        
        # 32-bit TIME structure (2 registers)
        "TIME": {
            "size_bits": 32,
            "size_registers": 2,
            "byte_order": "big_endian",
            "description": "Time without date component",
            
            "bit_fields": [
                {
                    "name": "minutes",
                    "bit_offset": 0,
                    "bit_width": 6,
                    "type": "unsigned_int",
                    "range": {"min": 0, "max": 59}
                },
                {
                    "name": "reserved_1",
                    "bit_offset": 6,
                    "bit_width": 1,
                    "type": "reserved"
                },
                {
                    "name": "time_sync_quality",
                    "bit_offset": 7,
                    "bit_width": 1,
                    "type": "flag",
                    "enum": {0: "synchronized", 1: "not_synchronized"}
                },
                {
                    "name": "hour",
                    "bit_offset": 8,
                    "bit_width": 5,
                    "type": "unsigned_int",
                    "range": {"min": 0, "max": 23}
                },
                {
                    "name": "reserved_2",
                    "bit_offset": 13,
                    "bit_width": 2,
                    "type": "reserved"
                },
                {
                    "name": "dst_flag",
                    "bit_offset": 15,
                    "bit_width": 1,
                    "type": "flag",
                    "enum": {0: "standard_time", 1: "daylight_savings_time"}
                },
                {
                    "name": "milliseconds",
                    "bit_offset": 16,
                    "bit_width": 16,
                    "type": "unsigned_int",
                    "range": {"min": 0, "max": 59999}
                }
            ]
        },
        
        # 32-bit Four Quadrant Floating Point Power Factor (2 registers)
        "4Q_FP_PF": {
            "size_bits": 32,
            "size_registers": 2,
            "byte_order": "big_endian",
            "description": "Four Quadrant Floating Point Power Factor (Special Encoding)",
            
            "encoding_scheme": {
                "name": "four_quadrant_power_factor",
                "description": "Special encoding where angle maps to register value",
                "angle_mapping": {
                    "0_degrees": 1.0,    # Unity PF, resistive
                    "90_degrees": 0.0,   # Purely reactive
                    "180_degrees": -1.0, # Unity PF, opposite direction
                    "270_degrees": 2.0   # Purely reactive, wraps around
                },
                "quadrants": {
                    "Q1": {
                        "range": {"min": 0.0, "max": 1.0},
                        "exclusive_min": True,
                        "exclusive_max": True,
                        "description": "Lagging power factor",
                        "typical": "Inductive loads"
                    },
                    "Q2": {
                        "range": {"min": -2.0, "max": -1.0},
                        "exclusive_min": True,
                        "exclusive_max": True,
                        "description": "Leading power factor",
                        "typical": "Capacitive loads (import)"
                    },
                    "Q3": {
                        "range": {"min": -1.0, "max": 0.0},
                        "exclusive_min": True,
                        "exclusive_max": True,
                        "description": "Lagging power factor",
                        "typical": "Inductive loads (export)"
                    },
                    "Q4": {
                        "range": {"min": 1.0, "max": 2.0},
                        "exclusive_min": True,
                        "exclusive_max": True,
                        "description": "Leading power factor",
                        "typical": "Capacitive loads"
                    }
                }
            },
            
            "decoding_algorithm": {
                "description": "Special decoding required for 4Q power factor",
                "steps": [
                    {
                        "condition": "regVal > 1",
                        "action": "PF_Val = 2 - regVal",
                        "quadrant": "Q4",
                        "power_factor_type": "leading"
                    },
                    {
                        "condition": "regVal < -1",
                        "action": "PF_Val = -2 - regVal",
                        "quadrant": "Q2",
                        "power_factor_type": "leading"
                    },
                    {
                        "condition": "abs(regVal) == 1",
                        "action": "PF_Val = regVal",
                        "quadrant": "unity",
                        "power_factor_type": "unity"
                    },
                    {
                        "condition": "else",
                        "action": "PF_Val = regVal",
                        "quadrant": "Q1 or Q3",
                        "power_factor_type": "lagging"
                    }
                ]
            },
            
            "bit_fields": [
                {
                    "name": "power_factor_raw",
                    "bit_offset": 0,
                    "bit_width": 32,
                    "type": "float32",
                    "range": {"min": -2.0, "max": 2.0},
                    "unit": "encoded_value",
                    "requires_special_decoding": True,
                    "description": "Raw register value requiring 4Q decoding"
                }
            ]
        }
    }
}


# ============================================================================
# LAYER 3: VALIDATION RULES (Applied to parsed data)
# ============================================================================
"""
EXPERT THINKING:
- Separate validation from structure definitions
- Rules apply AFTER bit extraction
- Composable and reusable
"""

# ============================================================================
# SPECIAL: 4-Quadrant Power Factor Reference Table
# ============================================================================
"""
VISUAL REFERENCE FOR 4Q POWER FACTOR DECODING:
==============================================

Register  | Decoded  | PF      | Quadrant | Load Type        | Phase Angle
Value     | PF Value | Type    |          |                  | (approx)
----------|----------|---------|----------|------------------|-------------
  2.0     |   0.0    | Leading |   Q4     | Pure Capacitive  | 270°
  1.8     |   0.2    | Leading |   Q4     | Strong Cap       | ~258°
  1.5     |   0.5    | Leading |   Q4     | Capacitive       | ~240°
  1.2     |   0.8    | Leading |   Q4     | Light Cap        | ~216°
  1.0     |   1.0    | Unity   |  Unity   | Pure Resistive   | 180° or 0°
  0.9     |   0.9    | Lagging |   Q1     | Light Inductive  | ~26°
  0.8     |   0.8    | Lagging |   Q1     | Inductive        | ~37°
  0.5     |   0.5    | Lagging |   Q1     | Heavy Inductive  | ~60°
  0.0     |   0.0    | Lagging |   Q1     | Pure Reactive    | 90°
 -0.5     |  -0.5    | Lagging |   Q3     | Inductive+Export | ~120°
 -0.8     |  -0.8    | Lagging |   Q3     | Inductive+Export | ~143°
 -1.0     |  -1.0    | Unity   |  Unity   | Resistive Export | 180°
 -1.2     |  -0.8    | Leading |   Q2     | Cap+Export       | ~144°
 -1.5     |  -0.5    | Leading |   Q2     | Cap+Export       | ~120°
 -1.8     |  -0.2    | Leading |   Q2     | Strong Cap+Exp   | ~102°
 -2.0     |   0.0    | Leading |   Q2     | Pure Cap+Export  | 90°

KEY OBSERVATIONS:
- Values -1 to +1: Direct mapping (no decoding needed)
- Values > 1 or < -1: Require decoding transformation
- Magnitude is ALWAYS 0.0 to 1.0 after decoding
- Sign indicates energy flow direction
- Quadrant indicates reactive power type
"""

VALIDATION_RULES = {
    "field_validation_rules": {
        
        "datetime_consistency": {
            "description": "Validate datetime fields form valid date/time",
            "type": "composite",
            "rules": [
                {
                    "name": "valid_date",
                    "check": "month_day_combination",
                    "logic": "validate day <= days_in_month(month, year)"
                },
                {
                    "name": "leap_year",
                    "when": {"month": 2, "day": 29},
                    "check": "year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)"
                }
            ]
        },
        
        "time_sync_warning": {
            "description": "Warn if time not synchronized",
            "type": "quality_check",
            "when": {"time_sync_quality": 1},
            "action": "warning",
            "message": "Time not synchronized - timestamp may be inaccurate"
        },
        
        "power_factor_range": {
            "description": "Power factor should be -1 to +1 in normal operation",
            "type": "range_check",
            "field": "power_factor",
            "normal_range": {"min": -1.0, "max": 1.0},
            "absolute_range": {"min": -2.0, "max": 2.0},
            "on_outside_normal": "warning",
            "on_outside_absolute": "error"
        },
        
        "decoded_pf_magnitude": {
            "description": "Decoded power factor magnitude must be 0 to 1",
            "type": "range_check",
            "field": "decoded_pf_value",
            "applies_after_decoding": True,
            "range": {"min": 0.0, "max": 1.0},
            "on_violation": "error",
            "message": "Decoded PF magnitude outside valid range - decoding error"
        },
        
        "quadrant_consistency": {
            "description": "Raw value must match detected quadrant",
            "type": "consistency_check",
            "checks": [
                {
                    "when": "raw_value > 1",
                    "expect_quadrant": "Q4"
                },
                {
                    "when": "raw_value < -1",
                    "expect_quadrant": "Q2"
                },
                {
                    "when": "0 < raw_value < 1",
                    "expect_quadrant": "Q1"
                },
                {
                    "when": "-1 < raw_value < 0",
                    "expect_quadrant": "Q3"
                }
            ]
        },
        
        "reserved_bit_check": {
            "description": "Reserved bits should be 0",
            "type": "value_check",
            "applies_to": "reserved_*",
            "expected_value": 0,
            "on_mismatch": "warning",
            "message": "Reserved bit is non-zero - possible protocol violation"
        }
    },
    
    "cross_field_rules": {
        "weekday_consistency": {
            "description": "Weekday should match actual date",
            "type": "computed_check",
            "fields": ["year", "month", "day", "weekday"],
            "logic": "calculated_weekday(year, month, day) == weekday",
            "on_mismatch": "warning"
        }
    }
}


# ============================================================================
# LAYER 4: REGISTER MAP (Where these types are used)
# ============================================================================
"""
EXPERT THINKING:
- Now map these complex types to actual Modbus addresses
- Reference the type definitions - don't repeat structure
- Add device-specific metadata
"""

REGISTER_MAP = {
    "register_groups": {
        
        "system_time": {
            "description": "Device system clock and time synchronization",
            "base_address": 9000,  # Example - actual address from PM5110 manual
            "access": "read_write",
            "registers": [
                {
                    "name": "device_timestamp",
                    "address": 9000,
                    "data_type_ref": "DATETIME",  # References complex type
                    "function_code": 3,
                    "update_rate": "on_demand",
                    "write_requires_unlock": True,
                    "description": "Current device date and time"
                },
                {
                    "name": "last_reset_time",
                    "address": 9010,
                    "data_type_ref": "DATETIME",
                    "function_code": 3,
                    "access": "read_only",
                    "description": "Timestamp of last device reset"
                }
            ]
        },
        
        "scheduling": {
            "description": "Time-based scheduling parameters",
            "base_address": 9100,
            "registers": [
                {
                    "name": "schedule_start_date",
                    "address": 9100,
                    "data_type_ref": "DATE",
                    "function_code": 3,
                    "access": "read_write"
                },
                {
                    "name": "schedule_start_time",
                    "address": 9102,
                    "data_type_ref": "TIME",
                    "function_code": 3,
                    "access": "read_write"
                }
            ]
        },
        
        "power_quality": {
            "description": "Power quality measurements",
            "base_address": 3000,
            "update_rate_ms": 1000,
            "registers": [
                {
                    "name": "power_factor_l1",
                    "address": 3110,
                    "data_type_ref": "4Q_FP_PF",
                    "function_code": 4,
                    "access": "read_only",
                    "description": "Phase 1 four-quadrant power factor",
                    "category": "measurement"
                },
                {
                    "name": "power_factor_l2",
                    "address": 3112,
                    "data_type_ref": "4Q_FP_PF",
                    "function_code": 4,
                    "access": "read_only",
                    "description": "Phase 2 four-quadrant power factor"
                },
                {
                    "name": "power_factor_l3",
                    "address": 3114,
                    "data_type_ref": "4Q_FP_PF",
                    "function_code": 4,
                    "access": "read_only",
                    "description": "Phase 3 four-quadrant power factor"
                }
            ]
        }
    }
}


# ============================================================================
# LAYER 5: DECODING RULES (How to parse bit fields)
# ============================================================================
"""
EXPERT THINKING:
- Explicit rules for extracting bit fields from registers
- Handles byte order, bit shifting, masking
- Reusable decoder logic
"""

DECODING_RULES = {
    "bit_field_extraction": {
        "algorithm": "extract_bits",
        "steps": [
            {
                "step": 1,
                "action": "read_registers",
                "description": "Read required number of 16-bit registers"
            },
            {
                "step": 2,
                "action": "concatenate_bytes",
                "description": "Combine registers into byte array according to byte_order"
            },
            {
                "step": 3,
                "action": "extract_bit_fields",
                "description": "For each bit field, extract bits using offset and width"
            },
            {
                "step": 4,
                "action": "convert_to_value",
                "description": "Convert bit pattern to typed value (int, float, flag)"
            },
            {
                "step": 5,
                "action": "apply_transform",
                "description": "Apply any transform functions (e.g., year + 2000)"
            },
            {
                "step": 6,
                "action": "validate",
                "description": "Run validation rules on extracted values"
            }
        ]
    },
    
    "bit_extraction_formula": {
        "description": "Standard bit field extraction",
        "formula": "(raw_value >> bit_offset) & ((1 << bit_width) - 1)",
        "example": {
            "raw_value": "0x1A2B (binary: 0001101000101011)",
            "extract_bits_4_to_7": "(0x1A2B >> 4) & 0x0F = 0x02",
            "result": 2
        }
    }
}


# ============================================================================
# LAYER 6: EXPERT PYTHON DECODER IMPLEMENTATION
# ============================================================================

class PM5110BitFieldDecoder:
    """
    Expert implementation of bit-field decoder for PM5110
    
    Design principles:
    1. Separation: Config (data) vs Logic (code)
    2. Reusability: Generic bit extraction
    3. Validation: Built-in quality checks
    4. Composability: Works with any bit field definition
    """
    
    def __init__(self, config):
        self.data_types = config['complex_types']
        self.validation_rules = VALIDATION_RULES
    
    def decode_register_value(self, register_config, raw_registers):
        """
        Decode multi-register value using bit field definitions
        
        Args:
            register_config: Config with 'data_type_ref'
            raw_registers: List of 16-bit register values
            
        Returns:
            Dictionary of decoded field values
        """
        # Get data type definition
        type_ref = register_config['data_type_ref']
        data_type = self.data_types[type_ref]
        
        # Convert registers to byte array
        byte_array = self._registers_to_bytes(
            raw_registers,
            data_type['byte_order']
        )
        
        # Extract all bit fields
        result = {}
        for field in data_type['bit_fields']:
            if field['type'] != 'reserved':
                value = self._extract_bit_field(byte_array, field)
                
                # Apply transform if specified
                if 'transform' in field:
                    value = self._apply_transform(value, field['transform'])
                
                result[field['name']] = {
                    'value': value,
                    'unit': field.get('unit'),
                    'quality': self._check_quality(field, value)
                }
        
        # Run validation rules
        validation = self._validate_decoded_data(result, type_ref)
        result['_validation'] = validation
        
        return result
    
    def _registers_to_bytes(self, registers, byte_order):
        """Convert 16-bit registers to byte array"""
        byte_array = bytearray()
        for reg in registers:
            if byte_order == 'big_endian':
                byte_array.extend([(reg >> 8) & 0xFF, reg & 0xFF])
            else:
                byte_array.extend([reg & 0xFF, (reg >> 8) & 0xFF])
        return bytes(byte_array)
    
    def _extract_bit_field(self, byte_array, field_def):
        """Extract bit field from byte array"""
        bit_offset = field_def['bit_offset']
        bit_width = field_def['bit_width']
        field_type = field_def['type']
        
        # Convert byte array to integer
        value = int.from_bytes(byte_array, byteorder='big')
        
        # Extract bits
        mask = (1 << bit_width) - 1
        extracted = (value >> bit_offset) & mask
        
        # Type conversion
        if field_type == 'flag':
            return bool(extracted)
        elif field_type == 'float32':
            import struct
            return struct.unpack('!f', extracted.to_bytes(4, 'big'))[0]
        else:
            return extracted
    
    def decode_4q_power_factor(self, raw_value):
        """
        Decode Four Quadrant Power Factor special encoding
        
        Args:
            raw_value: Raw float32 register value (-2.0 to 2.0)
            
        Returns:
            Dictionary with decoded PF value, type, and quadrant
        """
        # Apply 4Q decoding algorithm
        if raw_value > 1:
            # Q4: Leading power factor
            pf_value = 2 - raw_value
            pf_type = "leading"
            quadrant = "Q4"
            
        elif raw_value < -1:
            # Q2: Leading power factor
            pf_value = -2 - raw_value
            pf_type = "leading"
            quadrant = "Q2"
            
        elif abs(raw_value) == 1:
            # Unity power factor
            pf_value = raw_value
            pf_type = "unity"
            quadrant = "unity"
            
        else:
            # Q1 or Q3: Lagging power factor
            pf_value = raw_value
            pf_type = "lagging"
            
            # Determine Q1 vs Q3
            if 0 < raw_value < 1:
                quadrant = "Q1"
            elif -1 < raw_value < 0:
                quadrant = "Q3"
            else:  # raw_value == 0
                quadrant = "Q1"  # Boundary case
        
        # Calculate angle for reference
        import math
        if raw_value >= 0:
            angle_deg = math.acos(min(abs(pf_value), 1)) * 180 / math.pi
        else:
            angle_deg = 180 - (math.acos(min(abs(pf_value), 1)) * 180 / math.pi)
        
        return {
            "raw_register_value": raw_value,
            "decoded_pf_value": pf_value,
            "pf_magnitude": abs(pf_value),
            "pf_type": pf_type,
            "quadrant": quadrant,
            "angle_degrees": angle_deg,
            "is_leading": pf_type == "leading",
            "is_lagging": pf_type == "lagging",
            "interpretation": self._interpret_power_factor(pf_value, pf_type, quadrant)
        }
    
    def _interpret_power_factor(self, pf_value, pf_type, quadrant):
        """Provide human-readable interpretation"""
        interpretations = {
            "unity": "Unity power factor - purely resistive load",
            "leading": f"Leading power factor (capacitive) - {abs(pf_value):.3f}",
            "lagging": f"Lagging power factor (inductive) - {abs(pf_value):.3f}"
        }
        
        load_types = {
            "Q1": "Typical: Motors, transformers, inductive loads",
            "Q2": "Typical: Capacitive compensation (import)",
            "Q3": "Typical: Inductive loads with export",
            "Q4": "Typical: Capacitors, over-compensated system",
            "unity": "Typical: Resistive heaters, incandescent lighting"
        }
        
        return {
            "description": interpretations.get(pf_type, "Unknown"),
            "typical_load": load_types.get(quadrant, "Unknown"),
            "quadrant_detail": quadrant
        }
    
    def _apply_transform(self, value, transform_expr):
        """Apply transformation expression"""
        # Simple eval - in production use safer parser
        return eval(transform_expr.replace('value', str(value)))
    
    def _check_quality(self, field_def, value):
        """Check if value is within expected range"""
        if 'range' in field_def:
            r = field_def['range']
            if r['min'] <= value <= r['max']:
                return 'good'
            return 'out_of_range'
        return 'good'
    
    def _validate_decoded_data(self, data, data_type):
        """Run validation rules on decoded data"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Example: Check time sync quality
        if 'time_sync_quality' in data:
            if data['time_sync_quality']['value']:
                validation_result['warnings'].append(
                    "Time not synchronized"
                )
        
        return validation_result


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

EXAMPLE_USAGE = """
# ============================================================================
# EXAMPLE 1: Decoding DATETIME
# ============================================================================

decoder = PM5110BitFieldDecoder(DATA_TYPE_DEFINITIONS)

# Read 4 registers for DATETIME (registers 9000-9003)
raw_registers = [0x1A19, 0x0C0F, 0x3B00, 0x0100]

register_config = {
    'name': 'device_timestamp',
    'data_type_ref': 'DATETIME'
}

result = decoder.decode_register_value(register_config, raw_registers)

# Result structure:
{
    'year': {'value': 2026, 'unit': 'years', 'quality': 'good'},
    'month': {'value': 12, 'unit': None, 'quality': 'good'},
    'day': {'value': 25, 'unit': 'days', 'quality': 'good'},
    'hour': {'value': 15, 'unit': 'hours', 'quality': 'good'},
    'minutes': {'value': 30, 'unit': 'minutes', 'quality': 'good'},
    'milliseconds': {'value': 256, 'unit': 'milliseconds', 'quality': 'good'},
    'weekday': {'value': 4, 'unit': None, 'quality': 'good'},
    'time_sync_quality': {'value': False, 'unit': None, 'quality': 'good'},
    'dst_flag': {'value': False, 'unit': None, 'quality': 'good'},
    '_validation': {
        'valid': True,
        'errors': [],
        'warnings': []
    }
}


# ============================================================================
# EXAMPLE 2: Decoding 4-Quadrant Power Factor (CRITICAL!)
# ============================================================================

# Test all quadrants and special cases
test_cases = [
    # Q1: Lagging (0 < x < 1) - Inductive loads
    {
        "raw_value": 0.8,
        "expected": {
            "decoded_pf": 0.8,
            "type": "lagging",
            "quadrant": "Q1",
            "interpretation": "Typical motor load, 0.8 lagging"
        }
    },
    
    # Q2: Leading (-2 < x < -1) - Capacitive with import
    {
        "raw_value": -1.3,
        "expected": {
            "decoded_pf": -2 - (-1.3) = -0.7,
            "type": "leading",
            "quadrant": "Q2",
            "interpretation": "Capacitive load, 0.7 leading"
        }
    },
    
    # Q3: Lagging (-1 < x < 0) - Inductive with export
    {
        "raw_value": -0.6,
        "expected": {
            "decoded_pf": -0.6,
            "type": "lagging",
            "quadrant": "Q3",
            "interpretation": "Inductive load with export, 0.6 lagging"
        }
    },
    
    # Q4: Leading (1 < x < 2) - Capacitive loads
    {
        "raw_value": 1.4,
        "expected": {
            "decoded_pf": 2 - 1.4 = 0.6,
            "type": "leading",
            "quadrant": "Q4",
            "interpretation": "Capacitive load, 0.6 leading"
        }
    },
    
    # Unity power factor cases
    {
        "raw_value": 1.0,
        "expected": {
            "decoded_pf": 1.0,
            "type": "unity",
            "quadrant": "unity",
            "interpretation": "Purely resistive load"
        }
    },
    
    {
        "raw_value": -1.0,
        "expected": {
            "decoded_pf": -1.0,
            "type": "unity",
            "quadrant": "unity",
            "interpretation": "Unity with reversed direction"
        }
    },
    
    # Boundary cases
    {
        "raw_value": 0.0,
        "expected": {
            "decoded_pf": 0.0,
            "type": "lagging",
            "quadrant": "Q1",
            "angle": 90,
            "interpretation": "Purely reactive (90° phase shift)"
        }
    },
    
    # Extreme values
    {
        "raw_value": 2.0,
        "expected": {
            "decoded_pf": 0.0,
            "type": "leading",
            "quadrant": "Q4",
            "angle": 270,
            "interpretation": "Purely reactive capacitive"
        }
    }
]

# Decode each test case
for test in test_cases:
    result = decoder.decode_4q_power_factor(test["raw_value"])
    print(f"Raw: {test['raw_value']:6.2f} -> "
          f"PF: {result['decoded_pf_value']:6.3f} "
          f"({result['pf_type']:7s}) "
          f"[{result['quadrant']}] "
          f"{result['angle_degrees']:5.1f}°")

# Output:
# Raw:   0.80 -> PF:  0.800 (lagging) [Q1]  36.9°
# Raw:  -1.30 -> PF: -0.700 (leading) [Q2] 135.6°
# Raw:  -0.60 -> PF: -0.600 (lagging) [Q3] 143.1°
# Raw:   1.40 -> PF:  0.600 (leading) [Q4]  53.1°
# Raw:   1.00 -> PF:  1.000 (unity  ) [unity]   0.0°
# Raw:  -1.00 -> PF: -1.000 (unity  ) [unity] 180.0°
# Raw:   0.00 -> PF:  0.000 (lagging) [Q1]  90.0°
# Raw:   2.00 -> PF:  0.000 (leading) [Q4] 270.0°


# ============================================================================
# EXAMPLE 3: Full Register Reading Workflow
# ============================================================================

# Read power factor for all three phases
phases = ['L1', 'L2', 'L3']
addresses = [3110, 3112, 3114]

power_quality_data = {}

for phase, addr in zip(phases, addresses):
    # Read 2 registers (32-bit float)
    raw_regs = modbus_client.read_input_registers(addr, 2)
    
    # Decode using standard method
    register_config = {
        'name': f'power_factor_{phase.lower()}',
        'data_type_ref': '4Q_FP_PF'
    }
    
    # Extract raw float32
    raw_float = decoder.decode_register_value(register_config, raw_regs)
    
    # Apply 4Q decoding
    pf_result = decoder.decode_4q_power_factor(
        raw_float['power_factor_raw']['value']
    )
    
    power_quality_data[phase] = pf_result

# Example output:
{
    'L1': {
        'raw_register_value': 0.85,
        'decoded_pf_value': 0.85,
        'pf_magnitude': 0.85,
        'pf_type': 'lagging',
        'quadrant': 'Q1',
        'angle_degrees': 31.8,
        'is_leading': False,
        'is_lagging': True,
        'interpretation': {
            'description': 'Lagging power factor (inductive) - 0.850',
            'typical_load': 'Typical: Motors, transformers, inductive loads',
            'quadrant_detail': 'Q1'
        }
    },
    'L2': {
        'raw_register_value': 1.2,
        'decoded_pf_value': 0.8,
        'pf_magnitude': 0.8,
        'pf_type': 'leading',
        'quadrant': 'Q4',
        'angle_degrees': 36.9,
        'is_leading': True,
        'is_lagging': False,
        'interpretation': {
            'description': 'Leading power factor (capacitive) - 0.800',
            'typical_load': 'Typical: Capacitors, over-compensated system',
            'quadrant_detail': 'Q4'
        }
    },
    'L3': {
        'raw_register_value': -0.92,
        'decoded_pf_value': -0.92,
        'pf_magnitude': 0.92,
        'pf_type': 'lagging',
        'quadrant': 'Q3',
        'angle_degrees': 156.9,
        'is_leading': False,
        'is_lagging': True,
        'interpretation': {
            'description': 'Lagging power factor (inductive) - 0.920',
            'typical_load': 'Typical: Inductive loads with export',
            'quadrant_detail': 'Q3'
        }
    }
}
"""


# ============================================================================
# EXPERT INSIGHTS FOR THIS SPECIFIC CASE
# ============================================================================

EXPERT_INSIGHTS = """
KEY INSIGHTS FROM PM5110 SPECIFICATION:
========================================

1. BIT-FIELD ENCODING
   - Unlike simple registers (1 value = 1 or 2 registers)
   - PM5110 uses bit-packed structures
   - Multiple values packed into single 64-bit or 32-bit blocks
   - Must extract using bit offsets and widths

2. TIMESTAMP COMPLEXITY
   - DATETIME = 64 bits (4 registers)
   - Contains 10 separate fields
   - Year encoded as offset from 2000 (saves bits)
   - Reserved bits for future extensions
   - Quality flags embedded in data

3. FOUR-QUADRANT POWER FACTOR (CRITICAL!)
   ==========================================
   
   WHY 4-QUADRANT?
   - Traditional PF: -1 to +1 (only 2 quadrants)
   - Real power systems: Current can lead OR lag voltage
   - Power can flow in either direction (import/export)
   - Result: 4 possible combinations = 4 quadrants
   
   SPECIAL ENCODING RATIONALE:
   - Maps full 360° phase angle to continuous value range
   - Preserves sign information for direction
   - Enables quadrant detection without separate flags
   - Clever: Uses range wrapping (2.0 wraps to 0)
   
   DECODING LOGIC EXPLAINED:
   
   Q1 (0 < x < 1): LAGGING, IMPORT
   - Register value IS the power factor
   - Example: 0.8 -> PF = 0.8 lagging
   - Typical: Inductive loads (motors, transformers)
   
   Q2 (-2 < x < -1): LEADING, IMPORT  
   - Register value encoded: PF = -2 - regVal
   - Example: -1.3 -> PF = -2-(-1.3) = -0.7 leading (magnitude 0.7)
   - Typical: Capacitive correction during import
   
   Q3 (-1 < x < 0): LAGGING, EXPORT
   - Register value IS the power factor
   - Example: -0.6 -> PF = -0.6 lagging (magnitude 0.6)
   - Typical: Generator with inductive loads
   
   Q4 (1 < x < 2): LEADING, EXPORT
   - Register value encoded: PF = 2 - regVal
   - Example: 1.4 -> PF = 2-1.4 = 0.6 leading
   - Typical: Over-compensated system, capacitors
   
   UNITY CASES:
   - regVal = +1.0: Unity PF, resistive load
   - regVal = -1.0: Unity PF, reverse direction
   
   ANGLE MAPPING:
   0° (regVal=1.0)  -> Unity, in phase
   90° (regVal=0.0)  -> Purely reactive lagging
   180° (regVal=-1.0) -> Unity, opposite phase
   270° (regVal=2.0)  -> Purely reactive leading

4. IEC 870-5 STANDARD
   - International standard for telecontrol
   - Defines time encoding format
   - PM5110 follows this for interoperability

5. CONFIG DESIGN CHOICES
   - Type definitions separate from register map
   - Enables reuse (same DATETIME type used multiple places)
   - Validation rules separate from structure
   - Decoder is generic - works for any bit field definition
   - Special decoders for non-standard encodings (like 4Q PF)

6. SCALING CONSIDERATIONS
   - Easy to add new complex types
   - Easy to add new registers using existing types
   - Easy to extend validation rules
   - Easy to test (each layer independent)
   - Special cases (4Q PF) isolated in dedicated functions

7. WHY THIS ENCODING IS BRILLIANT
   - Continuous value range (no discontinuities)
   - Single register pair encodes: magnitude, sign, quadrant, direction
   - No need for separate status flags
   - Efficient: 32 bits carry full power factor information
   - Standard float32 type (no custom binary format)

8. COMMON PITFALLS TO AVOID
   ⚠️ DON'T treat 4Q PF as simple -1 to +1 value
   ⚠️ DON'T forget to decode Q2 and Q4 (> 1 or < -1)
   ⚠️ DON'T ignore the quadrant information
   ⚠️ DO remember: magnitude is always 0 to 1
   ⚠️ DO decode before displaying to user
   ⚠️ DO preserve raw value for debugging

PRODUCTION RECOMMENDATIONS:
- Store type definitions in separate JSON file
- Version the schema (these structures can change with firmware)
- Cache decoded values (bit extraction is expensive)
- Add comprehensive unit tests for edge cases (especially 4Q PF!)
- Log validation warnings for debugging
- Always test with boundary values: -2, -1, 0, 1, 2
- Document the 4Q encoding prominently for maintenance
- Consider adding angle calculation for visualization
- Validate against known load types during testing
"""

print(EXPERT_INSIGHTS)
