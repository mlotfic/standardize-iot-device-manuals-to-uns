#!/usr/bin/env python3
"""
Schema-to-Code Generator
Demonstrates how to generate decoders from YAML schema
"""

import yaml
from dataclasses import dataclass
from typing import Dict, List, Any
from pathlib import Path


@dataclass
class BitField:
    """Represents a single field in a bitfield register"""
    name: str
    offset: int
    width: int
    field_type: str
    values: Dict[int, Any] = None
    description: str = ""


class SchemaParser:
    """Parses YAML schema into structured data"""
    
    def __init__(self, types_path: str, device_path: str):
        with open(types_path) as f:
            self.base_types = yaml.safe_load(f)
        with open(device_path) as f:
            self.device_schema = yaml.safe_load(f)
    
    def resolve_enum(self, enum_ref: str) -> Dict:
        """Resolve enum reference like 'enum_patterns.phases'"""
        parts = enum_ref.split('.')
        data = self.base_types
        for part in parts:
            data = data[part]
        return data
    
    def parse_register(self, register_name: str) -> List[BitField]:
        """Parse a register definition into BitField objects"""
        register = self.device_schema['registers'][register_name]
        fields = []
        
        for field_name, field_def in register['fields'].items():
            # Handle inheritance from base types
            if 'inherits' in field_def:
                base_enum = self.resolve_enum(field_def['inherits'])
                values = base_enum.get('values', {})
            else:
                values = field_def.get('values', {})
            
            fields.append(BitField(
                name=field_name,
                offset=field_def['offset'],
                width=field_def['width'],
                field_type=field_def.get('type', 'enum'),
                values=values,
                description=field_def.get('description', '')
            ))
        
        return sorted(fields, key=lambda f: f.offset, reverse=True)


class PythonCodeGenerator:
    """Generates Python decoder classes from schema"""
    
    def __init__(self, schema_parser: SchemaParser):
        self.parser = schema_parser
    
    def generate_enum(self, name: str, values: Dict[int, Any]) -> str:
        """Generate Python Enum class"""
        lines = [f"class {name}(Enum):"]
        
        for value, info in values.items():
            if isinstance(info, dict):
                enum_name = info['name']
                comment = f"  # {info.get('desc', '')}"
            else:
                enum_name = str(info)
                comment = ""
            
            # Sanitize name for Python
            enum_name = enum_name.replace(' ', '_').replace('-', '_')
            lines.append(f"    {enum_name} = {value}{comment}")
        
        return "\n".join(lines)
    
    def generate_decoder(self, register_name: str) -> str:
        """Generate decoder class for a register"""
        fields = self.parser.parse_register(register_name)
        
        # Header
        code = [
            f"class {register_name}:",
            f'    """Decoder for {register_name} register"""',
            "",
            "    def __init__(self, raw_value: int):",
            f'        """Parse {register_name} from raw integer value"""'
        ]
        
        # Generate enums first
        enums_generated = set()
        for field in fields:
            if field.values and field.name not in enums_generated:
                enum_name = f"{register_name}_{field.name.title()}"
                # (Would insert enum generation here in full version)
                enums_generated.add(field.name)
        
        # Field extraction
        for field in fields:
            mask = (1 << field.width) - 1
            shift = field.offset
            
            if field.field_type == 'enum':
                code.append(
                    f"        self.{field.name} = "
                    f"(raw_value >> {shift}) & 0x{mask:X}"
                )
            elif field.field_type == 'flag':
                code.append(
                    f"        self.{field.name} = "
                    f"bool((raw_value >> {shift}) & 0x1)"
                )
            else:  # number
                code.append(
                    f"        self.{field.name} = "
                    f"(raw_value >> {shift}) & 0x{mask:X}"
                )
            
            if field.description:
                code[-1] += f"  # {field.description}"
        
        # String representation
        code.extend([
            "",
            "    def __repr__(self) -> str:",
            f'        return f"{register_name}(" + \\',
        ])
        
        field_reprs = [f'f"{f.name}={{self.{f.name}}}"' 
                      for f in fields]
        code.append("            " + " + ', ' + ".join(field_reprs) + " + ')'")
        
        # Validation method
        code.extend([
            "",
            "    def validate(self) -> List[str]:",
            '        """Validate field values against rules"""',
            "        errors = []",
            "        # TODO: Add validation rules from schema",
            "        return errors"
        ])
        
        return "\n".join(code)
    
    def generate_module(self, register_names: List[str]) -> str:
        """Generate complete Python module"""
        code = [
            '"""',
            'Auto-generated decoder from device schema',
            'DO NOT EDIT: Generated from YAML schema',
            '"""',
            "",
            "from enum import Enum",
            "from typing import List, Optional",
            "",
            ""
        ]
        
        for register_name in register_names:
            code.append(self.generate_decoder(register_name))
            code.append("\n\n")
        
        return "\n".join(code)


class CppCodeGenerator:
    """Generates C++ decoder structs from schema"""
    
    def __init__(self, schema_parser: SchemaParser):
        self.parser = schema_parser
    
    def generate_struct(self, register_name: str) -> str:
        """Generate C++ struct with bit fields"""
        fields = self.parser.parse_register(register_name)
        
        code = [
            f"struct {register_name} {{",
        ]
        
        # Bit fields (C++20 style)
        for field in reversed(fields):  # LSB first
            cpp_type = "uint32_t"  # Could be more sophisticated
            code.append(
                f"    {cpp_type} {field.name} : {field.width};"
                f"  // Offset {field.offset}"
            )
        
        code.extend([
            "",
            "    // Decode from raw value",
            f"    static {register_name} decode(uint32_t raw) {{",
            f"        {register_name} result;",
        ])
        
        for field in fields:
            mask = (1 << field.width) - 1
            code.append(
                f"        result.{field.name} = "
                f"(raw >> {field.offset}) & 0x{mask:X}u;"
            )
        
        code.extend([
            "        return result;",
            "    }",
            "};",
        ])
        
        return "\n".join(code)


class HTMLDocGenerator:
    """Generates HTML documentation from schema"""
    
    def __init__(self, schema_parser: SchemaParser):
        self.parser = schema_parser
    
    def generate_register_doc(self, register_name: str) -> str:
        """Generate HTML table for register documentation"""
        fields = self.parser.parse_register(register_name)
        register = self.parser.device_schema['registers'][register_name]
        
        html = [
            f"<h2>{register_name}</h2>",
            f"<p>{register.get('description', '')}</p>",
            f"<p><strong>Address:</strong> {register.get('address', 'N/A')}</p>",
            f"<p><strong>Width:</strong> {register['width']} bits</p>",
            "",
            "<table class='register-table'>",
            "  <thead>",
            "    <tr>",
            "      <th>Field</th>",
            "      <th>Bits</th>",
            "      <th>Width</th>",
            "      <th>Type</th>",
            "      <th>Description</th>",
            "    </tr>",
            "  </thead>",
            "  <tbody>",
        ]
        
        for field in fields:
            bit_range = f"{field.offset}:{field.offset + field.width - 1}"
            html.extend([
                "    <tr>",
                f"      <td><code>{field.name}</code></td>",
                f"      <td>{bit_range}</td>",
                f"      <td>{field.width}</td>",
                f"      <td>{field.field_type}</td>",
                f"      <td>{field.description}</td>",
                "    </tr>",
            ])
            
            # Add enum values as sub-rows
            if field.values:
                for value, info in list(field.values.items())[:5]:  # Limit
                    if isinstance(info, dict):
                        desc = info.get('desc', info.get('name', ''))
                    else:
                        desc = str(info)
                    
                    html.extend([
                        "    <tr class='enum-value'>",
                        f"      <td></td>",
                        f"      <td colspan='2'>{value}</td>",
                        f"      <td colspan='2'>{desc}</td>",
                        "    </tr>",
                    ])
        
        html.extend([
            "  </tbody>",
            "</table>",
        ])
        
        return "\n".join(html)


# Example usage
def main():
    """Example of generating decoders from schema"""
    
    # In practice, would use actual file paths
    print("=" * 60)
    print("SCHEMA-DRIVEN CODE GENERATION EXAMPLE")
    print("=" * 60)
    
    print("\n1. YAML Schema → Python Decoder")
    print("-" * 60)
    python_code = """
class AlarmAttributes:
    def __init__(self, raw_value: int):
        self.type = (raw_value >> 28) & 0xF
        self.subtype = (raw_value >> 23) & 0xF
        self.parameter = (raw_value >> 17) & 0xF
        self.phases = (raw_value >> 7) & 0xF
        self.priority = (raw_value >> 3) & 0x3
        self.enable = bool(raw_value & 0x1)
    
    def __repr__(self):
        return f"AlarmAttributes(type={self.type}, priority={self.priority})"
"""
    print(python_code)
    
    print("\n2. YAML Schema → C++ Struct")
    print("-" * 60)
    cpp_code = """
struct AlarmAttributes {
    uint32_t enable : 1;
    uint32_t learning : 1;
    uint32_t setpoints : 1;
    uint32_t priority : 2;
    uint32_t level : 2;
    uint32_t phases : 4;
    uint32_t modifier : 4;
    uint32_t parameter : 4;
    uint32_t subtype : 4;
    uint32_t type : 4;
    
    static AlarmAttributes decode(uint32_t raw);
};
"""
    print(cpp_code)
    
    print("\n3. YAML Schema → HTML Documentation")
    print("-" * 60)
    print("<table>")
    print("  <tr><th>Field</th><th>Bits</th><th>Description</th></tr>")
    print("  <tr><td>type</td><td>28:31</td><td>Alarm type enum</td></tr>")
    print("  <tr><td>priority</td><td>3:4</td><td>HIGH/MEDIUM/LOW</td></tr>")
    print("</table>")
    
    print("\n" + "=" * 60)
    print("Benefits of this approach:")
    print("  ✓ Single source of truth (YAML schema)")
    print("  ✓ Multiple outputs (Python, C++, docs)")
    print("  ✓ Guaranteed consistency")
    print("  ✓ Easy to version and evolve")
    print("=" * 60)


if __name__ == "__main__":
    main()
