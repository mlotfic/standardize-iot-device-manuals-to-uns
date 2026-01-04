#!/usr/bin/env python3
"""
CSV Config Validator
Validates transformed device manual CSVs against transformation rules
"""

import csv
import sys
from collections import defaultdict
from typing import List, Dict, Tuple


class ConfigValidator:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.rows = []
        self.errors = []
        self.warnings = []
        
    def load_csv(self):
        """Load CSV file"""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.rows = list(reader)
    
    def validate_all(self):
        """Run all validation checks"""
        print(f"Validating: {self.filepath}")
        print("=" * 60)
        
        self.check_bit_math()
        self.check_overlaps()
        self.check_naming_conventions()
        self.check_missing_descriptions()
        self.check_enum_gaps()
        
        self.print_results()
    
    def check_bit_math(self):
        """Rule: offset + width must be <= total_width"""
        for i, row in enumerate(self.rows, start=2):
            try:
                total_width = int(row.get('total_width', 0))
                offset = int(row.get('offset', 0))
                width = int(row.get('width', 0))
                
                if offset + width > total_width:
                    self.errors.append(
                        f"Line {i}: Bit overflow - "
                        f"offset({offset}) + width({width}) = {offset+width} "
                        f"> total_width({total_width})"
                    )
            except (ValueError, TypeError):
                self.errors.append(
                    f"Line {i}: Invalid numeric values in bit fields"
                )
    
    def check_overlaps(self):
        """Rule: No overlapping bits within same group (unless conditional)"""
        groups = defaultdict(list)
        
        for i, row in enumerate(self.rows, start=2):
            group = row.get('group')
            name = row.get('name')
            
            # Group by register (group,name pair)
            key = (group, name)
            
            try:
                offset = int(row.get('offset', 0))
                width = int(row.get('width', 0))
                groups[key].append((offset, width, i))
            except (ValueError, TypeError):
                continue
        
        # Check each group for overlaps
        for (group, name), fields in groups.items():
            if len(fields) < 2:
                continue
            
            # Sort by offset
            fields.sort()
            
            for j in range(len(fields) - 1):
                offset1, width1, line1 = fields[j]
                offset2, width2, line2 = fields[j + 1]
                
                end1 = offset1 + width1 - 1
                
                if offset2 <= end1:
                    self.warnings.append(
                        f"Lines {line1},{line2}: Possible overlap in {group}.{name} - "
                        f"bits {offset1}-{end1} and {offset2}-{offset2+width2-1}"
                    )
    
    def check_naming_conventions(self):
        """Rule: Check naming conventions"""
        for i, row in enumerate(self.rows, start=2):
            group = row.get('group', '')
            name = row.get('name', '')
            meaning = row.get('meaning', '')
            
            # Check group is CamelCase
            if group and not group[0].isupper():
                self.warnings.append(
                    f"Line {i}: Group '{group}' should be CamelCase"
                )
            
            # Check name is lowercase/underscore
            if name and not name.islower() and '_' not in name:
                if not name.isupper():  # Allow all-caps like DATETIME
                    self.warnings.append(
                        f"Line {i}: Field name '{name}' should be lowercase_underscore"
                    )
            
            # Check meaning is UPPERCASE
            if meaning and row.get('type') == 'enum':
                if not meaning.isupper() and meaning != '':
                    self.warnings.append(
                        f"Line {i}: Enum meaning '{meaning}' should be UPPERCASE"
                    )
    
    def check_missing_descriptions(self):
        """Rule: Every row should have description"""
        for i, row in enumerate(self.rows, start=2):
            desc = row.get('description', '').strip()
            if not desc:
                self.warnings.append(
                    f"Line {i}: Missing description for "
                    f"{row.get('group')}.{row.get('name')}"
                )
    
    def check_enum_gaps(self):
        """Rule: Warn about gaps in enum sequences"""
        enums = defaultdict(lambda: defaultdict(list))
        
        for i, row in enumerate(self.rows, start=2):
            if row.get('type') != 'enum':
                continue
            
            group = row.get('group')
            name = row.get('name')
            
            try:
                value = int(row.get('value', -1))
                enums[group][(name, row.get('offset'), row.get('width'))].append(value)
            except (ValueError, TypeError):
                continue
        
        # Check for gaps
        for group, fields in enums.items():
            for (name, offset, width), values in fields.items():
                values.sort()
                
                try:
                    max_value = (1 << int(width)) - 1
                except (ValueError, TypeError):
                    continue
                
                # Check for gaps in sequence
                for j in range(len(values) - 1):
                    if values[j+1] - values[j] > 1:
                        gap_start = values[j] + 1
                        gap_end = values[j+1] - 1
                        
                        # Don't warn about large reserved ranges
                        if gap_end - gap_start < 5:
                            self.warnings.append(
                                f"Enum gap in {group}.{name}: "
                                f"values {gap_start}-{gap_end} missing"
                            )
    
    def print_results(self):
        """Print validation results"""
        print()
        
        if self.errors:
            print(f"❌ ERRORS ({len(self.errors)}):")
            print("-" * 60)
            for error in self.errors:
                print(f"  {error}")
            print()
        
        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)}):")
            print("-" * 60)
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        if not self.errors and not self.warnings:
            print("✅ All validation checks passed!")
            print()
        
        # Summary
        print("=" * 60)
        print(f"Total rows: {len(self.rows)}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if self.errors:
            print("\n⛔ Validation FAILED - fix errors before commit")
            return False
        else:
            print("\n✅ Validation PASSED")
            return True


def main():
    """Run validator on CSV file"""
    if len(sys.argv) < 2:
        print("Usage: python validate_config.py <config.csv>")
        sys.exit(1)
    
    validator = ConfigValidator(sys.argv[1])
    
    try:
        validator.load_csv()
        passed = validator.validate_all()
        sys.exit(0 if passed else 1)
    
    except FileNotFoundError:
        print(f"❌ Error: File not found: {sys.argv[1]}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


# Example usage with your data
def example_validation():
    """Example of what validator catches"""
    
    print("\nEXAMPLE VALIDATION OUTPUT:")
    print("=" * 60)
    
    print("\n✅ PASS Example:")
    print("AlarmAttributes,type,32,28,4,enum,0,NONE,No alarm type defined,Device specific")
    print("  → offset(28) + width(4) = 32 ≤ total_width(32) ✓")
    
    print("\n❌ FAIL Example:")
    print("AlarmAttributes,type,32,28,6,enum,0,NONE,No alarm type defined,Device specific")
    print("  → offset(28) + width(6) = 34 > total_width(32) ✗")
    print("  → ERROR: Bit overflow")
    
    print("\n⚠️  WARNING Example:")
    print("AlarmAttributes,Type,32,28,4,enum,0,none,No alarm type,Device specific")
    print("  → Group 'Type' should be lowercase: 'type' ⚠")
    print("  → Meaning 'none' should be UPPERCASE: 'NONE' ⚠")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Show example if no file provided
        example_validation()
        print("\nTo validate a file, run:")
        print("  python validate_config.py your_config.csv")
    else:
        main()
