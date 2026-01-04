"""
Device Register Decoder Library
Uses CSV config files to decode device registers
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class EnumValue:
    """Single enum value definition"""
    code: int
    name: str
    description: str
    unit_code: Optional[int] = None


@dataclass
class BitField:
    """Single bit field in a register"""
    name: str
    offset: int
    width: int
    data_type: str  # 'enum', 'number', 'flag'
    values: Dict[int, EnumValue]  # For enum/flag types
    
    def extract(self, raw_value: int) -> int:
        """Extract this field's value from raw register"""
        mask = (1 << self.width) - 1
        return (raw_value >> self.offset) & mask
    
    def decode(self, raw_value: int) -> Dict[str, Any]:
        """Extract and decode this field"""
        value = self.extract(raw_value)
        
        result = {
            'raw_value': value,
            'field_name': self.name
        }
        
        # Look up enum meaning if available
        if value in self.values:
            enum_val = self.values[value]
            result.update({
                'enum_name': enum_val.name,
                'description': enum_val.description,
                'unit_code': enum_val.unit_code
            })
        
        return result


@dataclass
class Register:
    """Complete register definition"""
    group: str
    total_width: int
    fields: Dict[str, BitField]
    
    def decode(self, raw_value: int) -> Dict[str, Any]:
        """Decode entire register"""
        result = {
            'register': self.group,
            'raw_value': raw_value,
            'fields': {}
        }
        
        for field_name, field in self.fields.items():
            result['fields'][field_name] = field.decode(raw_value)
        
        return result


class DeviceConfig:
    """Load and manage device configuration from CSV"""
    
    def __init__(self, config_path: str, units_path: Optional[str] = None):
        self.config_path = Path(config_path)
        self.units_path = Path(units_path) if units_path else None
        
        self.registers: Dict[str, Register] = {}
        self.units: Dict[int, Dict[str, str]] = {}
        
        self._load_config()
        if self.units_path and self.units_path.exists():
            self._load_units()
    
    def _load_config(self):
        """Load register configuration from CSV"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Group rows by register
            register_data = defaultdict(lambda: defaultdict(list))
            
            for row in reader:
                group = row['group']
                field_name = row['name']
                register_data[group][field_name].append(row)
            
            # Build register objects
            for group, fields_data in register_data.items():
                fields = {}
                total_width = None
                
                for field_name, rows in fields_data.items():
                    # Get field metadata from first row
                    first_row = rows[0]
                    offset = int(first_row['offset'])
                    width = int(first_row['width'])
                    data_type = first_row['type']
                    total_width = int(first_row['total_width'])
                    
                    # Build enum values dict
                    values = {}
                    for row in rows:
                        if row.get('value'):
                            try:
                                code = int(row['value'])
                                values[code] = EnumValue(
                                    code=code,
                                    name=row.get('meaning', ''),
                                    description=row.get('description', ''),
                                    unit_code=int(row['unit_code']) if row.get('unit_code') else None
                                )
                            except (ValueError, KeyError):
                                pass
                    
                    fields[field_name] = BitField(
                        name=field_name,
                        offset=offset,
                        width=width,
                        data_type=data_type,
                        values=values
                    )
                
                self.registers[group] = Register(
                    group=group,
                    total_width=total_width or 32,
                    fields=fields
                )
    
    def _load_units(self):
        """Load units reference table"""
        with open(self.units_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    code = int(row['code'])
                    self.units[code] = {
                        'symbol': row['abbreviation'],
                        'name': row['description']
                    }
                except (ValueError, KeyError):
                    pass
    
    def get_register(self, register_name: str) -> Optional[Register]:
        """Get register definition by name"""
        return self.registers.get(register_name)
    
    def decode_register(self, register_name: str, raw_value: int) -> Dict[str, Any]:
        """Decode a register value"""
        register = self.get_register(register_name)
        if not register:
            raise ValueError(f"Unknown register: {register_name}")
        
        result = register.decode(raw_value)
        
        # Enrich with unit information
        for field_data in result['fields'].values():
            if field_data.get('unit_code'):
                unit = self.units.get(field_data['unit_code'])
                if unit:
                    field_data['unit'] = unit
        
        return result
    
    def list_registers(self) -> List[str]:
        """List all available register names"""
        return list(self.registers.keys())


# ============================================================================
# Usage Examples
# ============================================================================

def example_basic_usage():
    """Example 1: Basic decoding"""
    print("=" * 70)
    print("EXAMPLE 1: Basic Register Decoding")
    print("=" * 70)
    
    # Load configuration
    config = DeviceConfig('device_config.csv', 'units.csv')
    
    # Decode a register value (e.g., from Modbus)
    raw_value = 0x12003401
    
    result = config.decode_register('AlarmAttributes', raw_value)
    
    print(f"\nRaw register value: 0x{raw_value:08X}")
    print(f"Register: {result['register']}")
    print("\nDecoded fields:")
    
    for field_name, field_data in result['fields'].items():
        print(f"\n  {field_name}:")
        print(f"    Raw value: {field_data['raw_value']}")
        if 'enum_name' in field_data:
            print(f"    Name: {field_data['enum_name']}")
            print(f"    Description: {field_data['description']}")
            if 'unit' in field_data:
                print(f"    Unit: {field_data['unit']['symbol']} ({field_data['unit']['name']})")


def example_modbus_integration():
    """Example 2: Modbus integration"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Modbus Integration")
    print("=" * 70)
    
    from pymodbus.client import ModbusTcpClient
    
    config = DeviceConfig('device_config.csv', 'units.csv')
    
    # Connect to device
    client = ModbusTcpClient('192.168.1.100', port=502)
    client.connect()
    
    # Read alarm attributes register (address 0x4000)
    response = client.read_holding_registers(address=0x4000, count=2, unit=1)
    
    if not response.isError():
        # Combine two 16-bit registers into 32-bit value
        raw_value = (response.registers[0] << 16) | response.registers[1]
        
        # Decode using config
        result = config.decode_register('AlarmAttributes', raw_value)
        
        print(f"\nAlarm Configuration:")
        print(f"  Type: {result['fields']['type']['enum_name']}")
        print(f"  Description: {result['fields']['type']['description']}")
        print(f"  Enabled: {result['fields']['enable']['enum_name']}")
    
    client.close()


def example_batch_processing():
    """Example 3: Batch processing of log data"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Batch Processing")
    print("=" * 70)
    
    import pandas as pd
    
    config = DeviceConfig('device_config.csv', 'units.csv')
    
    # Simulated log data
    log_data = [
        {'timestamp': '2025-01-01 10:00', 'alarm_reg': 0x12003401},
        {'timestamp': '2025-01-01 10:05', 'alarm_reg': 0x52003401},
        {'timestamp': '2025-01-01 10:10', 'alarm_reg': 0x12003400},
    ]
    
    # Decode all entries
    decoded = []
    for entry in log_data:
        result = config.decode_register('AlarmAttributes', entry['alarm_reg'])
        decoded.append({
            'timestamp': entry['timestamp'],
            'alarm_type': result['fields']['type']['enum_name'],
            'enabled': result['fields']['enable']['enum_name'],
            'raw_value': f"0x{entry['alarm_reg']:08X}"
        })
    
    df = pd.DataFrame(decoded)
    print("\nDecoded Log Data:")
    print(df.to_string(index=False))


def example_alarm_monitoring():
    """Example 4: Real-time alarm monitoring"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Alarm Monitoring")
    print("=" * 70)
    
    config = DeviceConfig('device_config.csv', 'units.csv')
    
    def check_alarm(raw_value: int) -> Dict[str, Any]:
        """Check if alarm conditions are met"""
        result = config.decode_register('AlarmAttributes', raw_value)
        
        alarm_info = {
            'active': result['fields']['enable']['enum_name'] == 'ENABLED',
            'type': result['fields']['type']['enum_name'],
            'description': result['fields']['type']['description'],
            'severity': 'NONE'
        }
        
        # Determine severity based on type
        if alarm_info['active']:
            alarm_type = alarm_info['type']
            if alarm_type == 'DISTURBANCE':
                alarm_info['severity'] = 'HIGH'
            elif alarm_type in ['STANDARD1S', 'STANDARDHS']:
                alarm_info['severity'] = 'MEDIUM'
            elif alarm_type != 'NONE':
                alarm_info['severity'] = 'LOW'
        
        return alarm_info
    
    # Check some values
    test_values = [0x12003401, 0x52003401, 0x00003400]
    
    for value in test_values:
        alarm = check_alarm(value)
        print(f"\nRegister: 0x{value:08X}")
        print(f"  Active: {alarm['active']}")
        print(f"  Type: {alarm['type']}")
        print(f"  Severity: {alarm['severity']}")


def example_validation():
    """Example 5: Validate register values"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Register Validation")
    print("=" * 70)
    
    config = DeviceConfig('device_config.csv', 'units.csv')
    
    def validate_register(register_name: str, raw_value: int) -> List[str]:
        """Validate register value against config"""
        errors = []
        
        register = config.get_register(register_name)
        if not register:
            return [f"Unknown register: {register_name}"]
        
        # Check each field
        for field_name, field in register.fields.items():
            value = field.extract(raw_value)
            
            # For enum fields, check if value is valid
            if field.data_type == 'enum' and field.values:
                if value not in field.values:
                    errors.append(
                        f"Field '{field_name}': Invalid enum value {value}. "
                        f"Valid values: {list(field.values.keys())}"
                    )
        
        return errors
    
    # Test validation
    test_cases = [
        ('AlarmAttributes', 0x12003401, "Valid"),
        ('AlarmAttributes', 0xFF003401, "Invalid (type=15 not defined)"),
    ]
    
    for register_name, value, expected in test_cases:
        errors = validate_register(register_name, value)
        print(f"\nTest: {expected}")
        print(f"  Register: {register_name}, Value: 0x{value:08X}")
        if errors:
            print(f"  Errors: {errors}")
        else:
            print(f"  ✓ Valid")


def example_register_builder():
    """Example 6: Build register values"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Build Register Values")
    print("=" * 70)
    
    config = DeviceConfig('device_config.csv', 'units.csv')
    
    def build_register(register_name: str, **field_values) -> int:
        """Build register value from field names and values"""
        register = config.get_register(register_name)
        if not register:
            raise ValueError(f"Unknown register: {register_name}")
        
        result = 0
        
        for field_name, value in field_values.items():
            field = register.fields.get(field_name)
            if not field:
                raise ValueError(f"Unknown field: {field_name}")
            
            # If value is enum name, convert to code
            if isinstance(value, str):
                # Find enum code by name
                code = None
                for enum_code, enum_val in field.values.items():
                    if enum_val.name == value:
                        code = enum_code
                        break
                if code is None:
                    raise ValueError(f"Unknown enum value '{value}' for field '{field_name}'")
                value = code
            
            # Validate range
            max_value = (1 << field.width) - 1
            if value > max_value:
                raise ValueError(f"Value {value} too large for field '{field_name}' (max: {max_value})")
            
            # Insert into result
            result |= (value << field.offset)
        
        return result
    
    # Build a register value
    register_value = build_register(
        'AlarmAttributes',
        type='STANDARD1S',
        enable='ENABLED'
    )
    
    print(f"\nBuilt register value: 0x{register_value:08X}")
    
    # Verify by decoding
    decoded = config.decode_register('AlarmAttributes', register_value)
    print("\nVerification (decoded):")
    print(f"  Type: {decoded['fields']['type']['enum_name']}")
    print(f"  Enable: {decoded['fields']['enable']['enum_name']}")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("Device Register Decoder - Usage Examples")
    print("=" * 70)
    print("Note: These examples assume 'device_config.csv' and 'units.csv' exist")
    print()
    
    try:
        example_basic_usage()
        # example_modbus_integration()  # Uncomment if pymodbus available
        example_batch_processing()
        example_alarm_monitoring()
        example_validation()
        example_register_builder()
        
        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
        
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nPlease ensure 'device_config.csv' and 'units.csv' exist in the current directory.")
