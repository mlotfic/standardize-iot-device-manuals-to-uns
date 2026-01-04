"""
COMPLETE GUIDE: Device Manual → Config Files + Large Scale Optimization
========================================================================
How to extract from manuals + handle 1000+ registers efficiently
"""

# ============================================================================
# PART 1: MANUAL EXTRACTION PATTERNS
# ============================================================================
"""
Different manual formats and how to map them to config
"""

# ----------------------------------------------------------------------------
# PATTERN 1: Standard Table Format → Config
# ----------------------------------------------------------------------------

MANUAL_TABLE_EXAMPLE = """
Common format in device manuals:

Register | Name              | Type    | R/W | Function | Unit | Range      | Scale
---------|-------------------|---------|-----|----------|------|------------|-------
3000     | Voltage L1-N      | FLOAT32 | R   | 4        | V    | 0-690      | 1
3002     | Voltage L2-N      | FLOAT32 | R   | 4        | V    | 0-690      | 1
3004     | Voltage L3-N      | FLOAT32 | R   | 4        | V    | 0-690      | 1
3010     | Current L1        | INT16U  | R   | 4        | A    | 0-10000    | 0.01
3011     | Current L2        | INT16U  | R   | 4        | A    | 0-10000    | 0.01
3012     | Current L3        | INT16U  | R   | 4        | A    | 0-10000    | 0.01
"""

# Direct mapping strategy
MANUAL_TO_CONFIG_MAPPING = {
    "extraction_rules": {
        "Register": {
            "maps_to": "address",
            "data_type": "integer",
            "required": True
        },
        "Name": {
            "maps_to": "name",
            "transform": "to_snake_case",  # "Voltage L1-N" → "voltage_l1_n"
            "required": True
        },
        "Type": {
            "maps_to": "data_type",
            "transform": "normalize_type",  # "FLOAT32" → "float32"
            "required": True
        },
        "R/W": {
            "maps_to": "access",
            "value_mapping": {
                "R": "read_only",
                "W": "write_only",
                "R/W": "read_write"
            }
        },
        "Function": {
            "maps_to": "function_code",
            "data_type": "integer"
        },
        "Unit": {
            "maps_to": "unit",
            "optional": True
        },
        "Range": {
            "maps_to": "range",
            "transform": "parse_range",  # "0-690" → {"min": 0, "max": 690}
            "optional": True
        },
        "Scale": {
            "maps_to": "scale",
            "data_type": "float",
            "default": 1.0
        }
    },
    
    "transformations": {
        "to_snake_case": {
            "description": "Convert to snake_case",
            "examples": [
                {"input": "Voltage L1-N", "output": "voltage_l1_n"},
                {"input": "Total Active Power", "output": "total_active_power"}
            ],
            "implementation": "re.sub(r'[\\s\\-]+', '_', name).lower()"
        },
        
        "normalize_type": {
            "description": "Normalize data type names",
            "mapping": {
                "FLOAT32": "float32",
                "FLOAT": "float32",
                "INT16U": "uint16",
                "UINT16": "uint16",
                "INT16": "int16",
                "INT32U": "uint32",
                "INT32": "int32"
            }
        },
        
        "parse_range": {
            "description": "Parse range string to min/max object",
            "examples": [
                {"input": "0-690", "output": {"min": 0, "max": 690}},
                {"input": "-40~125", "output": {"min": -40, "max": 125}},
                {"input": "0 to 100", "output": {"min": 0, "max": 100}}
            ]
        }
    }
}

# Result after extraction
EXTRACTED_CONFIG = {
    "registers": [
        {
            "name": "voltage_l1_n",
            "address": 3000,
            "data_type": "float32",
            "function_code": 4,
            "access": "read_only",
            "unit": "V",
            "range": {"min": 0, "max": 690},
            "scale": 1.0
        },
        # ... more registers
    ]
}


# ----------------------------------------------------------------------------
# PATTERN 2: Grouped Registers → Optimized Config
# ----------------------------------------------------------------------------

MANUAL_GROUPED_EXAMPLE = """
Many manuals group similar registers:

VOLTAGE MEASUREMENTS (Base: 3000)
Offset | Name         | Type    | Unit
-------|--------------|---------|-----
0      | Voltage L1-N | FLOAT32 | V
2      | Voltage L2-N | FLOAT32 | V
4      | Voltage L3-N | FLOAT32 | V
6      | Voltage L1-L2| FLOAT32 | V
8      | Voltage L2-L3| FLOAT32 | V
10     | Voltage L3-L1| FLOAT32 | V

CURRENT MEASUREMENTS (Base: 3010)
Offset | Name      | Type   | Unit | Scale
-------|-----------|--------|------|------
0      | Current L1| INT16U | A    | 0.01
1      | Current L2| INT16U | A    | 0.01
2      | Current L3| INT16U | A    | 0.01
"""

# Optimized hierarchical config
GROUPED_CONFIG = {
    "register_groups": {
        "voltage_measurements": {
            "description": "Three-phase voltage measurements",
            "base_address": 3000,
            "function_code": 4,
            "common_properties": {
                "data_type": "float32",
                "unit": "V",
                "scale": 1.0,
                "access": "read_only",
                "range": {"min": 0, "max": 690}
            },
            "registers": [
                {"name": "voltage_l1_n", "offset": 0},
                {"name": "voltage_l2_n", "offset": 2},
                {"name": "voltage_l3_n", "offset": 4},
                {"name": "voltage_l1_l2", "offset": 6},
                {"name": "voltage_l2_l3", "offset": 8},
                {"name": "voltage_l3_l1", "offset": 10}
            ]
        },
        
        "current_measurements": {
            "description": "Three-phase current measurements",
            "base_address": 3010,
            "function_code": 4,
            "common_properties": {
                "data_type": "uint16",
                "unit": "A",
                "scale": 0.01,
                "access": "read_only",
                "range": {"min": 0, "max": 10000}
            },
            "registers": [
                {"name": "current_l1", "offset": 0},
                {"name": "current_l2", "offset": 1},
                {"name": "current_l3", "offset": 2}
            ]
        }
    }
}


# ============================================================================
# PART 2: LARGE SCALE OPTIMIZATION STRATEGIES
# ============================================================================
"""
For devices with 100+ or 1000+ registers
"""

# ----------------------------------------------------------------------------
# STRATEGY 1: Pattern-Based Register Definitions
# ----------------------------------------------------------------------------

PATTERN_BASED_CONFIG = {
    "version": "3.0",
    "description": "Large scale config using patterns",
    
    # Define register patterns (templates)
    "register_patterns": {
        "phase_measurement": {
            "description": "Template for 3-phase measurements",
            "data_type": "float32",
            "unit": "{unit}",
            "access": "read_only",
            "function_code": 4,
            "registers_per_phase": 2,  # FLOAT32 = 2 registers
            "phases": ["L1", "L2", "L3"]
        },
        
        "energy_counter": {
            "description": "Template for energy counters",
            "data_type": "uint64",
            "unit": "Wh",
            "access": "read_only",
            "function_code": 4,
            "registers_per_counter": 4  # UINT64 = 4 registers
        },
        
        "configuration_parameter": {
            "description": "Template for config parameters",
            "data_type": "uint16",
            "access": "read_write",
            "function_code": 3
        }
    },
    
    # Generate registers from patterns
    "generated_register_groups": {
        "voltages": {
            "pattern_ref": "phase_measurement",
            "base_address": 3000,
            "measurements": [
                {
                    "base_name": "voltage_{phase}_n",
                    "unit": "V",
                    "range": {"min": 0, "max": 690}
                },
                {
                    "base_name": "voltage_{phase}_l{next_phase}",
                    "unit": "V",
                    "range": {"min": 0, "max": 1200}
                }
            ]
        },
        
        "currents": {
            "pattern_ref": "phase_measurement",
            "base_address": 3020,
            "measurements": [
                {
                    "base_name": "current_{phase}",
                    "unit": "A",
                    "range": {"min": 0, "max": 10000},
                    "scale": 0.01
                }
            ]
        },
        
        "energy_counters": {
            "pattern_ref": "energy_counter",
            "base_address": 4000,
            "counters": [
                "total_active_energy",
                "total_reactive_energy",
                "total_apparent_energy",
                "import_active_energy",
                "export_active_energy"
            ]
        }
    }
}

# This compact definition expands to 50+ actual registers


# ----------------------------------------------------------------------------
# STRATEGY 2: Range-Based Definitions
# ----------------------------------------------------------------------------

RANGE_BASED_CONFIG = {
    "version": "3.0",
    "description": "Define ranges of similar registers",
    
    "register_ranges": {
        "measurements_block_1": {
            "description": "Main measurements",
            "start_address": 3000,
            "end_address": 3099,
            "function_code": 4,
            "access": "read_only",
            "data_type": "float32",
            "register_increment": 2,  # FLOAT32 uses 2 registers
            
            # Define registers by pattern
            "register_list": [
                {"offset": 0, "name": "voltage_l1_n", "unit": "V"},
                {"offset": 2, "name": "voltage_l2_n", "unit": "V"},
                {"offset": 4, "name": "voltage_l3_n", "unit": "V"},
                {"offset": 6, "name": "current_l1", "unit": "A", "scale": 0.01},
                {"offset": 8, "name": "current_l2", "unit": "A", "scale": 0.01},
                {"offset": 10, "name": "current_l3", "unit": "A", "scale": 0.01}
                # ... continues to offset 98
            ]
        },
        
        "configuration_block": {
            "description": "Device configuration parameters",
            "start_address": 5000,
            "end_address": 5199,
            "function_code": 3,
            "access": "read_write",
            "data_type": "uint16",
            "register_increment": 1,
            
            "register_list": [
                {"offset": 0, "name": "ct_ratio_primary", "range": {"min": 1, "max": 32000}},
                {"offset": 1, "name": "ct_ratio_secondary", "range": {"min": 1, "max": 1000}},
                # ... 200 config parameters
            ]
        },
        
        "status_flags_block": {
            "description": "Device status bits",
            "start_address": 6000,
            "end_address": 6015,
            "function_code": 2,
            "access": "read_only",
            "data_type": "boolean",
            "register_increment": 1,
            
            # For flags, can use bit mapping
            "bit_mapped_registers": [
                {
                    "address": 6000,
                    "name": "system_status",
                    "bits": {
                        0: "power_on",
                        1: "alarm_active",
                        2: "warning_active",
                        3: "communication_error",
                        # ... up to bit 15
                    }
                }
            ]
        }
    }
}


# ----------------------------------------------------------------------------
# STRATEGY 3: Compressed Repetitive Definitions
# ----------------------------------------------------------------------------

COMPRESSED_CONFIG = {
    "version": "3.0",
    "description": "Highly compressed for repetitive registers",
    
    "templates": {
        "harmonic_measurement": {
            "data_type": "float32",
            "unit": "{base_unit}",
            "access": "read_only",
            "function_code": 4
        }
    },
    
    # Define once, generate many
    "expanded_groups": {
        "voltage_harmonics": {
            "template": "harmonic_measurement",
            "base_address": 7000,
            "base_unit": "V",
            "pattern": "voltage_l{phase}_h{harmonic}",
            "phases": [1, 2, 3],
            "harmonics": list(range(1, 64)),  # H1 to H63
            "registers_per_item": 2  # FLOAT32
            # This generates 3 phases × 63 harmonics = 189 registers!
        },
        
        "current_harmonics": {
            "template": "harmonic_measurement",
            "base_address": 8000,
            "base_unit": "A",
            "pattern": "current_l{phase}_h{harmonic}",
            "phases": [1, 2, 3],
            "harmonics": list(range(1, 64)),
            "registers_per_item": 2
            # Another 189 registers
        },
        
        "energy_per_tariff": {
            "template": "energy_counter",
            "base_address": 9000,
            "pattern": "energy_tariff_{tariff}_{direction}",
            "tariffs": list(range(1, 9)),  # 8 tariffs
            "directions": ["import", "export"],
            "registers_per_item": 4  # UINT64
            # 8 tariffs × 2 directions = 16 registers (64 total)
        }
    }
}

# Result: This compact config represents 378+ registers!


# ----------------------------------------------------------------------------
# STRATEGY 4: External Reference Files
# ----------------------------------------------------------------------------

EXTERNAL_REFERENCE_CONFIG = {
    "version": "3.0",
    "description": "Main config with external register definitions",
    
    "device": {
        "manufacturer": "Schneider Electric",
        "model": "PM5560"
    },
    
    # Reference external files for large register lists
    "register_sources": [
        {
            "source_type": "file",
            "path": "./registers/measurements.json",
            "description": "All measurement registers (500+ items)",
            "address_range": [3000, 3999]
        },
        {
            "source_type": "file",
            "path": "./registers/configuration.json",
            "description": "Configuration parameters (200+ items)",
            "address_range": [5000, 5199]
        },
        {
            "source_type": "file",
            "path": "./registers/alarms.json",
            "description": "Alarm and event registers",
            "address_range": [11000, 12199]
        },
        {
            "source_type": "csv",
            "path": "./registers/harmonics.csv",
            "description": "Harmonic analysis registers (CSV format)",
            "address_range": [7000, 8999]
        }
    ],
    
    # Keep critical registers inline
    "inline_registers": {
        "device_id": {
            "address": 100,
            "data_type": "uint32",
            "access": "read_only",
            "description": "Device identification number"
        },
        "firmware_version": {
            "address": 102,
            "data_type": "uint16",
            "access": "read_only",
            "description": "Firmware version"
        }
    }
}


# ============================================================================
# PART 3: CONFIG GENERATOR TOOLS
# ============================================================================
"""
Tools to generate configs from different sources
"""

class ConfigGenerator:
    """Generate optimized configs for large register maps"""
    
    @staticmethod
    def from_csv(csv_path, output_path):
        """
        Generate config from CSV manual table
        
        CSV Format:
        address,name,type,rw,function,unit,min,max,scale
        3000,Voltage L1-N,FLOAT32,R,4,V,0,690,1
        """
        import csv
        import json
        
        config = {
            "version": "2.0",
            "registers": []
        }
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                register = {
                    "name": row['name'].lower().replace(' ', '_').replace('-', '_'),
                    "address": int(row['address']),
                    "data_type": row['type'].lower(),
                    "function_code": int(row['function']),
                    "access": "read_only" if row['rw'] == 'R' else "read_write",
                    "unit": row['unit'],
                    "scale": float(row['scale']) if row['scale'] else 1.0
                }
                
                if row['min'] and row['max']:
                    register['range'] = {
                        "min": float(row['min']),
                        "max": float(row['max'])
                    }
                
                config['registers'].append(register)
        
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    @staticmethod
    def detect_patterns(registers):
        """
        Analyze registers and detect patterns for optimization
        
        Returns suggested optimizations
        """
        # Group by base address ranges
        ranges = {}
        for reg in registers:
            base = (reg['address'] // 100) * 100
            if base not in ranges:
                ranges[base] = []
            ranges[base].append(reg)
        
        # Detect common properties within ranges
        suggestions = []
        for base_addr, regs in ranges.items():
            if len(regs) < 3:
                continue
            
            # Check for common data_type
            types = [r.get('data_type') for r in regs]
            if len(set(types)) == 1:
                suggestions.append({
                    "type": "common_data_type",
                    "address_range": [base_addr, base_addr + 99],
                    "data_type": types[0],
                    "registers": len(regs),
                    "optimization": "Use common_properties in group"
                })
            
            # Check for sequential naming patterns
            names = [r.get('name') for r in regs]
            if ConfigGenerator._has_pattern(names):
                suggestions.append({
                    "type": "naming_pattern",
                    "address_range": [base_addr, base_addr + 99],
                    "pattern": "detected sequential pattern",
                    "optimization": "Use pattern-based generation"
                })
        
        return suggestions
    
    @staticmethod
    def _has_pattern(names):
        """Detect if names follow pattern like sensor_1, sensor_2, sensor_3"""
        import re
        
        # Extract numbers from names
        numbers = []
        for name in names:
            match = re.search(r'(\d+)', name)
            if match:
                numbers.append(int(match.group(1)))
        
        if len(numbers) < 3:
            return False
        
        # Check if sequential
        return numbers == list(range(numbers[0], numbers[-1] + 1))
    
    @staticmethod
    def expand_pattern_config(pattern_config):
        """
        Expand pattern-based config to full register list
        
        Takes compressed config, returns all registers
        """
        expanded = {"registers": []}
        
        for group_name, group in pattern_config.get('generated_register_groups', {}).items():
            pattern = pattern_config['register_patterns'][group['pattern_ref']]
            base_addr = group['base_address']
            
            phases = pattern.get('phases', [])
            measurements = group.get('measurements', [])
            
            current_addr = base_addr
            
            for measurement in measurements:
                for phase in phases:
                    name_template = measurement['base_name']
                    name = name_template.replace('{phase}', phase)
                    
                    register = {
                        "name": name,
                        "address": current_addr,
                        "data_type": pattern['data_type'],
                        "unit": measurement.get('unit'),
                        "access": pattern['access'],
                        "function_code": pattern['function_code']
                    }
                    
                    if 'range' in measurement:
                        register['range'] = measurement['range']
                    if 'scale' in measurement:
                        register['scale'] = measurement['scale']
                    
                    expanded['registers'].append(register)
                    current_addr += pattern['registers_per_phase']
        
        return expanded
    
    @staticmethod
    def split_large_config(config, max_registers_per_file=100):
        """
        Split large config into multiple files by address range
        
        Args:
            config: Large config dictionary
            max_registers_per_file: Max registers per split file
            
        Returns:
            List of (filename, config_subset) tuples
        """
        registers = config.get('registers', [])
        registers.sort(key=lambda r: r['address'])
        
        files = []
        current_batch = []
        batch_num = 1
        
        for reg in registers:
            current_batch.append(reg)
            
            if len(current_batch) >= max_registers_per_file:
                files.append((
                    f"registers_batch_{batch_num}.json",
                    {
                        "version": config.get('version'),
                        "description": f"Registers batch {batch_num}",
                        "address_range": [
                            current_batch[0]['address'],
                            current_batch[-1]['address']
                        ],
                        "registers": current_batch
                    }
                ))
                current_batch = []
                batch_num += 1
        
        # Last batch
        if current_batch:
            files.append((
                f"registers_batch_{batch_num}.json",
                {
                    "version": config.get('version'),
                    "description": f"Registers batch {batch_num}",
                    "address_range": [
                        current_batch[0]['address'],
                        current_batch[-1]['address']
                    ],
                    "registers": current_batch
                }
            ))
        
        return files


# ============================================================================
# PART 4: REAL-WORLD EXAMPLE
# ============================================================================
"""
PM5560 Power Meter: 1000+ registers optimized
"""

PM5560_OPTIMIZED_CONFIG = {
    "version": "3.0",
    "device": {
        "manufacturer": "Schneider Electric",
        "model": "PM5560",
        "register_count": "1200+"
    },
    
    # -------------------------------------------------------------------------
    # Compressed definitions for repetitive registers
    # -------------------------------------------------------------------------
    
    "measurement_groups": {
        "voltages": {
            "base_address": 3000,
            "common": {"data_type": "float32", "unit": "V", "function_code": 4},
            "items": [
                {"name": "voltage_l{n}_n", "phases": [1, 2, 3], "range": [0, 690]},
                {"name": "voltage_l{n}_l{m}", "pairs": [[1,2], [2,3], [3,1]], "range": [0, 1200]}
            ]
        },
        
        "currents": {
            "base_address": 3020,
            "common": {"data_type": "uint16", "unit": "A", "function_code": 4, "scale": 0.01},
            "items": [
                {"name": "current_l{n}", "phases": [1, 2, 3], "range": [0, 10000]},
                {"name": "current_neutral", "range": [0, 10000]}
            ]
        },
        
        "power": {
            "base_address": 3050,
            "common": {"data_type": "float32", "function_code": 4},
            "items": [
                {"name": "active_power_l{n}", "phases": [1, 2, 3], "unit": "W"},
                {"name": "reactive_power_l{n}", "phases": [1, 2, 3], "unit": "VAR"},
                {"name": "apparent_power_l{n}", "phases": [1, 2, 3], "unit": "VA"},
                {"name": "total_active_power", "unit": "W"},
                {"name": "total_reactive_power", "unit": "VAR"},
                {"name": "total_apparent_power", "unit": "VA"}
            ]
        }
    },
    
    # -------------------------------------------------------------------------
    # Harmonics: 63 harmonics × 6 measurements × 3 phases = 1134 registers!
    # -------------------------------------------------------------------------
    
    "harmonic_analysis": {
        "base_address": 7000,
        "common": {"data_type": "float32", "function_code": 4, "access": "read_only"},
        "measurements": [
            {"type": "voltage_thd_l{phase}", "unit": "%"},
            {"type": "current_thd_l{phase}", "unit": "%"},
            {"type": "voltage_h{n}_l{phase}", "unit": "V", "harmonics": range(1, 64)},
            {"type": "current_h{n}_l{phase}", "unit": "A", "harmonics": range(1, 64)}
        ],
        "phases": [1, 2, 3]
        # Note: This compact definition represents 1100+ registers
    },
    
    # -------------------------------------------------------------------------
    # Energy counters: Multiple tariffs
    # -------------------------------------------------------------------------
    
    "energy_counters": {
        "base_address": 9000,
        "common": {"data_type": "uint64", "unit": "Wh", "function_code": 4},
        "tariffs": range(1, 9),  # 8 tariffs
        "types": [
            "active_import_tariff_{t}",
            "active_export_tariff_{t}",
            "reactive_import_tariff_{t}",
            "reactive_export_tariff_{t}"
        ]
        # 8 tariffs × 4 types = 32 counters = 128 registers
    },
    
    # -------------------------------------------------------------------------
    # Reference external files for huge sections
    # -------------------------------------------------------------------------
    
    "external_definitions": {
        "alarm_queue": {
            "file": "pm5560_alarms.json",
            "description": "100 alarm entries × 12 registers = 1200 registers",
            "address_range": [11000, 12199]
        },
        
        "event_log": {
            "file": "pm5560_events.json",
            "description": "Event log entries",
            "address_range": [13000, 14999]
        }
    },
    
    # -------------------------------------------------------------------------
    # Keep frequently accessed registers inline for quick reference
    # -------------------------------------------------------------------------
    
    "quick_access": {
        "device_info": {
            "firmware_version": {"address": 100, "data_type": "uint32"},
            "serial_number": {"address": 102, "data_type": "uint32"},
            "device_id": {"address": 104, "data_type": "uint16"}
        },
        
        "system_status": {
            "system_status_word": {"address": 4000, "data_type": "uint16"},
            "alarm_status_word": {"address": 4001, "data_type": "uint16"}
        }
    }
}


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

USAGE_EXAMPLES = """
# Example 1: Generate config from manual CSV
# ===========================================

generator = ConfigGenerator()

# Extract from CSV manual
config = generator.from_csv(
    'PM5560_register_map.csv',
    'pm5560_config.json'
)

print(f"Generated {len(config['registers'])} register definitions")


# Example 2: Detect optimization opportunities
# =============================================

# Load existing config
import json
config = json.load(open('device_config.json'))

# Analyze for patterns
suggestions = generator.detect_patterns(config['registers'])

for suggestion in suggestions:
    print(f"{suggestion['type']}: {suggestion['registers']} registers")
    print(f"  Optimization: {suggestion['optimization']}")
    print(f"  Address range: {suggestion['address_range']}")


# Example 3: Expand compressed config
# ====================================

# Load compressed config
compressed = COMPRESSED_CONFIG

# Expand to full register list
expanded = generator.expand_pattern_config(compressed)

print(f"Compressed config with {len(compressed['expanded_groups'])} groups")
print(f"Expands to {len(expanded['registers'])} registers")


# Example 4: Split large config into multiple files
# ==================================================

# Load large config (1000+ registers)
large_config = json.load(open('pm5560_full.json'))

# Split into manageable files
files = generator.split_large_config(
    large_config,
    max_registers_per_file=100
)

# Save each file
for filename, subset in files:
    with open(filename, 'w') as f:
        json.dump(subset, f, indent=2)
    print(f"Created {filename} with {len(subset['registers'])} registers")


# Example 5: Load config with external references
# ================================================

import json

def load_config_with_externals(main_config_path):
    '''Load main config and merge external register files'''
    
    with open(main_config_path) as f:
        config = json.load(f)
    
    # Load external register files
    all_registers = {}
    
    for source in config.get('register_sources', []):
        if source['source_type'] == 'file':
            with open(source['path']) as f:
                external = json.load(f)
                all_registers.update(external.get('registers', {}))
    
    # Merge with inline registers
    all_registers.update(config.get('inline_registers', {}))
    
    config['all_registers'] = all_registers
    return config

# Usage
config = load_config_with_externals('pm5560_main.json')
print(f"Total registers loaded: {len(config['all_registers'])}")
"""

print(USAGE_EXAMPLES)
