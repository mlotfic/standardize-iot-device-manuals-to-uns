"""
Bitfield Configuration Handler and Decoder for Modbus Registers

This module provides robust parsing and decoding of bitfield-structured registers
commonly found in industrial devices communicating over Modbus (16-bit words).

Usage
-----
Basic decoding workflow::

    from bitfield_decoder import BitfieldDecoder
    
    # Initialize and load configuration
    decoder = BitfieldDecoder()
    decoder.load_config('alarm_config.csv')
    
    # Decode from 16-bit Modbus word list (automatic word combining)
    modbus_data = [0x1234, 0x5678]  # Two 16-bit words from Modbus
    result = decoder.decode_from_words('AlarmAttributes', modbus_data)
    print(decoder.decode_readable('AlarmAttributes', result['combined_value']))
    
    # Decode single 16-bit register
    event_code = 0xF234
    print(decoder.decode_readable('EventCode', event_code))
    
    # Working with built-in data types (DATETIME, DATE, TIME, etc.)
    datetime_words = [0x0715, 0x0000, 0x0B04, 0x010C]  # 64-bit DATETIME
    dt = decoder.decode_datetime(datetime_words)
    print(dt)  # {'year': 2021, 'month': 12, 'day': 11, ...}
    
    # Multi-layer configuration (default + custom overrides)
    decoder.load_default_config('base_config.csv')
    decoder.load_custom_config('device_specific.csv')
    decoder.load_custom_config('site_overrides.csv')
    
    # Cache management
    decoder.save_cache('decoder_cache.json')
    decoder2 = BitfieldDecoder()
    decoder2.load_cache('decoder_cache.json')
    
    # Byte order control
    result = decoder.decode_from_words('AlarmAttributes', [0x12, 0x34], byte_order='little')

Working with Modbus
-------------------
Modbus transmits data in 16-bit words. For wider registers:

- 16-bit registers: Use single Modbus word directly
- 32-bit registers: Combine two consecutive words (check byte order!)
- 64-bit registers: Combine four consecutive words

Always verify your device's byte order (big-endian vs little-endian).

Author: Data Engineering Team
"""

import csv
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime as dt
from enum import Enum


class ByteOrder(Enum):
    """Byte order for multi-word register combining."""
    BIG_ENDIAN = 'big'      # Most significant word first (default)
    LITTLE_ENDIAN = 'little'  # Least significant word first


@dataclass
class EnumValue:
    """
    Single enumeration value definition from bitfield configuration.
    
    Parameters
    ----------
    value : int
        Numeric value of this enum entry
    meaning : str
        Short mnemonic label (e.g., 'VOLTAGE', 'PHASE_A')
    description : str
        Detailed explanation of what this value represents
    
    Examples
    --------
    >>> enum = EnumValue(value=1, meaning='ENABLED', description='Alarm is active')
    >>> print(enum)
    ENABLED (1)
    """
    value: int
    meaning: str
    description: str
    
    def __repr__(self):
        return f"{self.meaning} ({self.value})"


@dataclass
class BitField:
    """
    Individual bitfield within a hardware register.
    
    Represents a contiguous range of bits with semantic meaning.
    Handles extraction, validation, and decoding of field values.
    
    Parameters
    ----------
    name : str
        Field identifier (e.g., 'type', 'phases', 'enable')
    offset : int
        Starting bit position from LSB (0 = rightmost bit)
    width : int
        Number of bits this field occupies
    type : str
        Field type: 'enum', 'number', or 'flag'
    total_width : int
        Total register width in bits (16, 32, 64)
    standard : str
        Reference standard or specification (e.g., 'ISA-18.2')
    enum_values : dict
        Mapping of numeric values to EnumValue objects
    
    Raises
    ------
    ValueError
        If field extends beyond register boundary or has invalid dimensions
    
    Examples
    --------
    >>> field = BitField(
    ...     name='type',
    ...     offset=28,
    ...     width=4,
    ...     type='enum',
    ...     total_width=32,
    ...     standard='ISA-18.2'
    ... )
    >>> field.extract(0x12345678)  # Extract 4 bits at offset 28
    1
    """
    name: str
    offset: int
    width: int
    type: str
    total_width: int
    standard: str
    enum_values: Dict[int, EnumValue] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate field constraints against register boundaries."""
        if self.offset + self.width > self.total_width:
            raise ValueError(
                f"Field '{self.name}' extends beyond register boundary: "
                f"offset={self.offset} + width={self.width} > total_width={self.total_width}"
            )
        if self.width <= 0:
            raise ValueError(f"Field '{self.name}' has invalid width: {self.width}")
        if self.offset < 0:
            raise ValueError(f"Field '{self.name}' has invalid offset: {self.offset}")
    
    def extract(self, value: int) -> int:
        """
        Extract this field's value from a register value using bit masking.
        
        Parameters
        ----------
        value : int
            Full register value
        
        Returns
        -------
        int
            Extracted field value (right-justified)
        
        Examples
        --------
        >>> field = BitField('status', offset=4, width=3, type='enum', total_width=16, standard='')
        >>> field.extract(0b0000000011110000)  # Bits [6:4] = 111
        7
        """
        mask = (1 << self.width) - 1  # Create bit mask of appropriate width
        return (value >> self.offset) & mask
    
    def validate_enum_values(self) -> List[str]:
        """
        Check if all enum values fit within field's bit width.
        
        Returns
        -------
        list of str
            Warning messages for values exceeding field capacity
        
        Examples
        --------
        >>> field = BitField('level', offset=0, width=2, type='enum', total_width=16, standard='')
        >>> field.enum_values[5] = EnumValue(5, 'INVALID', 'Too large')
        >>> warnings = field.validate_enum_values()
        >>> len(warnings) > 0
        True
        """
        warnings = []
        max_value = (1 << self.width) - 1  # Maximum value for n-bit field
        
        for enum_val in self.enum_values.values():
            if enum_val.value > max_value:
                warnings.append(
                    f"Enum value {enum_val.value} for '{enum_val.meaning}' "
                    f"exceeds max value {max_value} for {self.width}-bit field"
                )
        
        return warnings
    
    def decode(self, value: int) -> Dict[str, Any]:
        """
        Decode this field from a register value to structured output.
        
        Parameters
        ----------
        value : int
            Full register value
        
        Returns
        -------
        dict
            Decoded field information with keys:
            - 'field': Field name
            - 'raw_value': Extracted numeric value
            - 'type': Field type (enum/number/flag)
            - 'meaning': Human-readable meaning (for enums/flags)
            - 'description': Detailed description (for enums/flags)
            - 'state': SET/CLEAR (for flags)
        
        Examples
        --------
        >>> field = BitField('enable', offset=0, width=1, type='flag', total_width=16, standard='')
        >>> field.enum_values[1] = EnumValue(1, 'ENABLED', 'Feature is active')
        >>> result = field.decode(0x0001)
        >>> result['state']
        'SET'
        """
        extracted = self.extract(value)
        
        result = {
            'field': self.name,
            'raw_value': extracted,
            'type': self.type
        }
        
        if self.type == 'enum' and extracted in self.enum_values:
            enum_val = self.enum_values[extracted]
            result['meaning'] = enum_val.meaning
            result['description'] = enum_val.description
        elif self.type == 'flag':
            result['state'] = 'SET' if extracted else 'CLEAR'
            if extracted in self.enum_values:
                enum_val = self.enum_values[extracted]
                result['meaning'] = enum_val.meaning
                result['description'] = enum_val.description
        elif self.type == 'number':
            result['value'] = extracted
            # Number types may have range descriptions
            if extracted in self.enum_values:
                enum_val = self.enum_values[extracted]
                result['description'] = enum_val.description
        
        return result


@dataclass
class RegisterGroup:
    """
    Collection of bitfields representing a complete hardware register.
    
    Groups related fields (e.g., all fields in AlarmAttributes register)
    and provides validation, visualization, and decoding capabilities.
    
    Parameters
    ----------
    name : str
        Register group identifier (e.g., 'AlarmAttributes', 'EventCode')
    total_width : int
        Register width in bits (typically 16, 32, or 64)
    fields : dict
        Mapping of field names to BitField objects
    
    Notes
    -----
    For Modbus communication:
    - 16-bit registers map to single Modbus word
    - 32-bit registers require two consecutive Modbus words
    - 64-bit registers require four consecutive Modbus words
    
    Examples
    --------
    >>> group = RegisterGroup(name='Status', total_width=16)
    >>> # Add fields, then decode
    >>> result = group.decode(0x1234)
    """
    name: str
    total_width: int
    fields: Dict[str, BitField] = field(default_factory=dict)
    
    def decode(self, value: int) -> Dict[str, Any]:
        """
        Decode all fields from a register value.
        
        Parameters
        ----------
        value : int
            Register value to decode
        
        Returns
        -------
        dict
            Complete decoding with keys:
            - 'group': Register group name
            - 'raw_value': Original integer value
            - 'hex_value': Hexadecimal representation
            - 'binary_value': Binary representation
            - 'fields': Dict of decoded field values
        
        Raises
        ------
        ValueError
            If value exceeds register width
        
        Examples
        --------
        >>> group = RegisterGroup('EventCode', total_width=16)
        >>> result = group.decode(0xF234)
        >>> result['hex_value']
        '0xF234'
        """
        if value.bit_length() > self.total_width:
            raise ValueError(
                f"Value {value} exceeds register width {self.total_width} bits"
            )
        
        result = {
            'group': self.name,
            'raw_value': value,
            'hex_value': f"0x{value:0{self.total_width//4}X}",
            'binary_value': f"0b{value:0{self.total_width}b}",
            'fields': {}
        }
        
        for field_name, field in self.fields.items():
            result['fields'][field_name] = field.decode(value)
        
        return result
    
    def decode_to_readable(self, value: int) -> str:
        """
        Decode register value to formatted human-readable string.
        
        Parameters
        ----------
        value : int
            Register value to decode
        
        Returns
        -------
        str
            Multi-line formatted string showing all field interpretations
        
        Examples
        --------
        >>> group = RegisterGroup('Status', total_width=16)
        >>> print(group.decode_to_readable(0x1234))
        === Status ===
        Raw: 4660 | Hex: 0x1234 | Binary: 0b0001001000110100
        ...
        """
        decoded = self.decode(value)
        lines = [
            f"=== {self.name} ===",
            f"Raw: {decoded['raw_value']} | Hex: {decoded['hex_value']} | Binary: {decoded['binary_value']}",
            ""
        ]
        
        for field_name, field_data in decoded['fields'].items():
            line = f"  {field_name}: "
            
            if field_data['type'] == 'enum':
                line += f"{field_data.get('meaning', 'UNKNOWN')} ({field_data['raw_value']})"
                if 'description' in field_data:
                    line += f"\n    → {field_data['description']}"
            elif field_data['type'] == 'flag':
                line += f"{field_data['state']}"
                if 'meaning' in field_data:
                    line += f" - {field_data['meaning']}"
            elif field_data['type'] == 'number':
                line += f"{field_data['raw_value']}"
                if 'description' in field_data:
                    line += f" ({field_data['description']})"
            
            lines.append(line)
        
        return "\n".join(lines)
    
    def validate_structure(self) -> Dict[str, Any]:
        """
        Validate register structure for overlaps, gaps, and coverage.
        
        Critical for hardware register definitions where:
        - Each bit position should be accounted for
        - Fields must not overlap (indicates configuration error)
        - Gaps indicate reserved/unused bits
        
        Returns
        -------
        dict
            Validation report with keys:
            - 'is_valid': bool, True if no errors
            - 'errors': list of error messages
            - 'warnings': list of warning messages
            - 'coverage': dict with bit coverage statistics
            - 'gaps': list of unassigned bit ranges
            - 'overlaps': list of overlapping field conflicts
        
        Examples
        --------
        >>> group = RegisterGroup('Test', total_width=16)
        >>> validation = group.validate_structure()
        >>> validation['is_valid']
        True
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'coverage': {},
            'gaps': [],
            'overlaps': []
        }
        
        # Create bit coverage map to track field assignments
        bit_map = [None] * self.total_width
        
        for field_name, field in self.fields.items():
            # Mark each bit position used by this field
            for bit_pos in range(field.offset, field.offset + field.width):
                if bit_pos >= self.total_width:
                    validation_result['errors'].append(
                        f"Field '{field_name}' exceeds register width at bit {bit_pos}"
                    )
                    validation_result['is_valid'] = False
                    continue
                
                # Check for overlapping fields (same bit claimed twice)
                if bit_map[bit_pos] is not None:
                    validation_result['overlaps'].append({
                        'bit_position': bit_pos,
                        'fields': [bit_map[bit_pos], field_name]
                    })
                    validation_result['errors'].append(
                        f"Bit {bit_pos} overlap: '{bit_map[bit_pos]}' and '{field_name}'"
                    )
                    validation_result['is_valid'] = False
                else:
                    bit_map[bit_pos] = field_name
            
            # Validate enum values fit in field width
            enum_warnings = field.validate_enum_values()
            validation_result['warnings'].extend(enum_warnings)
        
        # Identify gaps (unassigned bits, typically reserved)
        gap_start = None
        for i, owner in enumerate(bit_map):
            if owner is None:
                if gap_start is None:
                    gap_start = i
            else:
                if gap_start is not None:
                    validation_result['gaps'].append({
                        'start': gap_start,
                        'end': i - 1,
                        'width': i - gap_start
                    })
                    gap_start = None
        
        # Handle gap at end of register
        if gap_start is not None:
            validation_result['gaps'].append({
                'start': gap_start,
                'end': self.total_width - 1,
                'width': self.total_width - gap_start
            })
        
        # Calculate coverage statistics
        covered_bits = sum(1 for b in bit_map if b is not None)
        validation_result['coverage'] = {
            'total_bits': self.total_width,
            'covered_bits': covered_bits,
            'uncovered_bits': self.total_width - covered_bits,
            'coverage_percent': (covered_bits / self.total_width) * 100
        }
        
        return validation_result
    
    def visualize_layout(self) -> str:
        """
        Create ASCII visualization of register bit layout.
        
        Shows which bits belong to which fields, useful for:
        - Debugging configuration
        - Documentation
        - Understanding register structure
        
        Returns
        -------
        str
            Multi-line ASCII art showing bit assignments
        
        Examples
        --------
        >>> group = RegisterGroup('Status', total_width=16)
        >>> print(group.visualize_layout())
        Register: Status (16-bit)
        ================================================================================
        Bit: 0000000000111111
             0123456789012345
        --------------------------------------------------------------------------------
             ████              enable [0:0] (1 bits, flag)
                 ████          mode [4:7] (4 bits, enum)
        """
        lines = [
            f"Register: {self.name} ({self.total_width}-bit)",
            "=" * 80
        ]
        
        # Sort fields by offset for visual clarity
        sorted_fields = sorted(self.fields.values(), key=lambda f: f.offset)
        
        # Create bit position ruler
        ruler_tens = "Bit: "
        ruler_ones = "     "
        for i in range(self.total_width):
            if i % 10 == 0:
                ruler_tens += f"{i//10}"
            else:
                ruler_tens += " "
            ruler_ones += str(i % 10)
        
        lines.append(ruler_tens)
        lines.append(ruler_ones)
        lines.append("-" * 80)
        
        # Show each field with visual bar
        for field in sorted_fields:
            visual = [" "] * self.total_width
            for i in range(field.offset, field.offset + field.width):
                if i < self.total_width:
                    visual[i] = "█"
            
            visual_str = "".join(visual)
            lines.append(
                f"     {visual_str}  {field.name} "
                f"[{field.offset}:{field.offset + field.width - 1}] "
                f"({field.width} bits, {field.type})"
            )
        
        return "\n".join(lines)


class BitfieldDecoder:
    """
    Main decoder for bitfield-structured hardware registers.
    
    Loads CSV configuration files defining register layouts and provides
    decoding, validation, and visualization capabilities. Designed for
    industrial protocols like Modbus where data arrives as 16-bit words.
    
    Features:
    - Multi-word register combining (16-bit Modbus words → 32/64-bit values)
    - Built-in data type decoders (DATETIME, DATE, TIME, 4QPF, RecordType)
    - Multi-layer configuration (default + custom overrides)
    - Configuration caching for performance
    
    Attributes
    ----------
    groups : dict
        Loaded register group definitions keyed by group name
    config_layers : list
        Stack of loaded configuration files (default + customs)
    
    Notes
    -----
    Modbus Data Width Considerations:
    - Modbus transmits in 16-bit (2-byte) words
    - Wider registers require combining multiple words
    - Always check device documentation for byte order (endianness)
    
    Examples
    --------
    >>> decoder = BitfieldDecoder()
    >>> decoder.load_default_config('base.csv')
    >>> decoder.load_custom_config('device_overrides.csv')
    >>> 
    >>> # Decode from Modbus word list
    >>> modbus_data = [0x1234, 0x5678]
    >>> result = decoder.decode_from_words('AlarmAttributes', modbus_data)
    >>> 
    >>> # Decode built-in DATETIME
    >>> dt_words = [0x0715, 0x0000, 0x0B04, 0x010C]
    >>> dt = decoder.decode_datetime(dt_words)
    >>> print(f"{dt['year']}-{dt['month']}-{dt['day']}")
    """
    
    def __init__(self):
        """Initialize empty decoder with configuration tracking."""
        self.groups: Dict[str, RegisterGroup] = {}
        self.config_layers: List[str] = []  # Track loaded configs for caching
        self._default_config: Optional[str] = None
        self._custom_configs: List[str] = []
    
    @staticmethod
    def combine_words(words: List[int], byte_order: str = 'big') -> int:
        """
        Combine multiple 16-bit words into single integer value.
        
        Critical for Modbus where 32/64-bit values span multiple registers.
        
        Parameters
        ----------
        words : list of int
            List of 16-bit words to combine
        byte_order : str, optional
            'big' (MSW first) or 'little' (LSW first), default 'big'
        
        Returns
        -------
        int
            Combined value
        
        Examples
        --------
        >>> BitfieldDecoder.combine_words([0x1234, 0x5678], 'big')
        305419896  # 0x12345678
        >>> BitfieldDecoder.combine_words([0x5678, 0x1234], 'little')
        305419896  # Same result with reversed order
        """
        if byte_order == 'little':
            words = list(reversed(words))
        
        result = 0
        for word in words:
            result = (result << 16) | (word & 0xFFFF)
        
        return result
    
    @staticmethod
    def get_required_words(total_width: int) -> int:
        """
        Calculate number of 16-bit words needed for register width.
        
        Parameters
        ----------
        total_width : int
            Register width in bits
        
        Returns
        -------
        int
            Number of 16-bit words required
        
        Examples
        --------
        >>> BitfieldDecoder.get_required_words(16)
        1
        >>> BitfieldDecoder.get_required_words(32)
        2
        >>> BitfieldDecoder.get_required_words(64)
        4
        """
        return (total_width + 15) // 16  # Ceiling division
    
    def decode_from_words(self, group_name: str, words: List[int], 
                         byte_order: str = 'big') -> Dict[str, Any]:
        """
        Decode register from list of 16-bit Modbus words.
        
        Automatically combines words based on register width and decodes.
        
        Parameters
        ----------
        group_name : str
            Register group name
        words : list of int
            List of 16-bit words from Modbus
        byte_order : str, optional
            'big' or 'little', default 'big'
        
        Returns
        -------
        dict
            Decoding result with additional keys:
            - 'words': Original word list
            - 'combined_value': Integer value after word combining
            - 'byte_order': Byte order used
        
        Raises
        ------
        ValueError
            If group not found or word count mismatch
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_config('config.csv')
        >>> # Decode 32-bit register from two Modbus words
        >>> result = decoder.decode_from_words('AlarmAttributes', [0x1234, 0x5678])
        >>> result['combined_value']
        305419896
        """
        if group_name not in self.groups:
            raise ValueError(f"Unknown register group: {group_name}")
        
        group = self.groups[group_name]
        required_words = self.get_required_words(group.total_width)
        
        if len(words) != required_words:
            raise ValueError(
                f"Group '{group_name}' requires {required_words} words "
                f"({group.total_width}-bit), but {len(words)} provided"
            )
        
        # Combine words into single value
        combined = self.combine_words(words, byte_order)
        
        # Decode combined value
        result = group.decode(combined)
        
        # Add word-level metadata
        result['words'] = words
        result['combined_value'] = combined
        result['byte_order'] = byte_order
        
        return result
    
    def decode_datetime(self, words: List[int], byte_order: str = 'big') -> Dict[str, Any]:
        """
        Decode IEC 870-5-4 DATETIME structure (64-bit).
        
        Parameters
        ----------
        words : list of int
            Four 16-bit words containing datetime data
        byte_order : str, optional
            Word combining byte order, default 'big'
        
        Returns
        -------
        dict
            Decoded datetime with keys:
            - 'year', 'month', 'day', 'weekday'
            - 'hour', 'minute', 'millisecond'
            - 'dst': bool, Daylight Saving Time flag
            - 'time_valid': bool, Time synchronization quality
            - 'timestamp': ISO format string if valid
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> dt_words = [0x0715, 0x0000, 0x0B04, 0x010C]
        >>> dt = decoder.decode_datetime(dt_words)
        >>> print(f"{dt['year']}-{dt['month']:02d}-{dt['day']:02d}")
        2021-12-11
        """
        if len(words) != 4:
            raise ValueError(f"DATETIME requires 4 words (64-bit), got {len(words)}")
        
        value = self.combine_words(words, byte_order)
        
        # Extract fields according to IEC 870-5-4 structure
        result = {
            'year': (value & 0x7F) + 2000,  # Bits [6:0], offset by 2000
            'month': (value >> 24) & 0x0F,  # Bits [27:24]
            'day': (value >> 16) & 0x1F,    # Bits [20:16]
            'weekday': (value >> 21) & 0x07,  # Bits [23:21]
            'hour': (value >> 40) & 0x1F,   # Bits [44:40]
            'minute': (value >> 32) & 0x3F,  # Bits [37:32]
            'millisecond': (value >> 48) & 0xFFFF,  # Bits [63:48]
            'dst': bool((value >> 47) & 0x01),  # Bit 47
            'time_valid': not bool((value >> 39) & 0x01),  # Bit 39 (inverted)
        }
        
        # Generate ISO timestamp if data is valid
        try:
            if result['time_valid'] and 1 <= result['month'] <= 12 and 1 <= result['day'] <= 31:
                seconds = result['millisecond'] // 1000
                ms = result['millisecond'] % 1000
                result['timestamp'] = (
                    f"{result['year']:04d}-{result['month']:02d}-{result['day']:02d} "
                    f"{result['hour']:02d}:{result['minute']:02d}:{seconds:02d}.{ms:03d}"
                )
        except:
            pass  # Invalid datetime components
        
        return result
    
    def decode_date(self, words: List[int], byte_order: str = 'big') -> Dict[str, Any]:
        """
        Decode DATE structure (32-bit).
        
        Parameters
        ----------
        words : list of int
            Two 16-bit words containing date data
        byte_order : str, optional
            Word combining byte order, default 'big'
        
        Returns
        -------
        dict
            Decoded date with keys: 'year', 'month', 'day', 'weekday'
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> date_words = [0x15, 0x0B04]
        >>> date = decoder.decode_date(date_words)
        >>> print(f"{date['year']}-{date['month']}-{date['day']}")
        """
        if len(words) != 2:
            raise ValueError(f"DATE requires 2 words (32-bit), got {len(words)}")
        
        value = self.combine_words(words, byte_order)
        
        return {
            'year': (value & 0xFF) + 2000,  # Bits [7:0], offset by 2000
            'month': (value >> 24) & 0x0F,  # Bits [27:24]
            'day': (value >> 16) & 0x1F,    # Bits [20:16]
            'weekday': (value >> 21) & 0x07,  # Bits [23:21]
        }
    
    def decode_time(self, words: List[int], byte_order: str = 'big') -> Dict[str, Any]:
        """
        Decode TIME structure (32-bit).
        
        Parameters
        ----------
        words : list of int
            Two 16-bit words containing time data
        byte_order : str, optional
            Word combining byte order, default 'big'
        
        Returns
        -------
        dict
            Decoded time with keys: 'hour', 'minute', 'millisecond', 'dst', 'time_valid'
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> time_words = [0x0C, 0x010E]
        >>> time = decoder.decode_time(time_words)
        >>> print(f"{time['hour']:02d}:{time['minute']:02d}")
        """
        if len(words) != 2:
            raise ValueError(f"TIME requires 2 words (32-bit), got {len(words)}")
        
        value = self.combine_words(words, byte_order)
        
        result = {
            'hour': (value >> 8) & 0x1F,    # Bits [12:8]
            'minute': value & 0x3F,         # Bits [5:0]
            'millisecond': (value >> 16) & 0xFFFF,  # Bits [31:16]
            'dst': bool((value >> 15) & 0x01),  # Bit 15
            'time_valid': not bool((value >> 7) & 0x01),  # Bit 7 (inverted)
        }
        
        # Calculate seconds and milliseconds
        if result['time_valid']:
            seconds = result['millisecond'] // 1000
            ms = result['millisecond'] % 1000
            result['time_string'] = f"{result['hour']:02d}:{result['minute']:02d}:{seconds:02d}.{ms:03d}"
        
        return result
    
    def decode_4qpf(self, words: List[int], byte_order: str = 'big') -> float:
        """
        Decode Four-Quadrant Power Factor (32-bit floating point).
        
        Range: -2.0 to +2.0 where sign indicates leading/lagging.
        
        Parameters
        ----------
        words : list of int
            Two 16-bit words containing 4QPF data
        byte_order : str, optional
            Word combining byte order, default 'big'
        
        Returns
        -------
        float
            Power factor value (-2.0 to 2.0)
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> pf_words = [0x3F80, 0x0000]  # 1.0 in IEEE 754
        >>> pf = decoder.decode_4qpf(pf_words)
        """
        if len(words) != 2:
            raise ValueError(f"4QPF requires 2 words (32-bit), got {len(words)}")
        
        value = self.combine_words(words, byte_order)
        
        # Interpret as IEEE 754 single precision float
        import struct
        bytes_val = value.to_bytes(4, byteorder='big')
        float_val = struct.unpack('>f', bytes_val)[0]
        
        # Clamp to valid range
        return max(-2.0, min(2.0, float_val))
    
    def decode_record_type(self, word: int) -> Dict[str, Any]:
        """
        Decode RecordType structure (16-bit).
        
        Lower 8 bits: Record number (0-255)
        Upper 8 bits: Data type enum
        
        Parameters
        ----------
        word : int
            16-bit word containing record type
        
        Returns
        -------
        dict
            Decoded with keys: 'record_num', 'data_type', 'data_type_name'
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_config('datatypes.csv')
        >>> rt = decoder.decode_record_type(0x4001)
        >>> print(rt['data_type_name'])
        FLOAT32
        """
        record_num = word & 0xFF
        data_type = (word >> 8) & 0xFF
        
        # Data type enumeration mapping
        type_map = {
            0x00: 'Boolean',
            0x10: 'INT16U',
            0x11: 'INT16',
            0x20: 'INT32U',
            0x21: 'INT32',
            0x30: 'INT64U',
            0x31: 'INT64',
            0x40: 'FLOAT32',
            0x41: 'FLOAT64',
        }
        
        return {
            'record_num': record_num,
            'data_type': data_type,
            'data_type_name': type_map.get(data_type, f'UNKNOWN_0x{data_type:02X}')
        }
    
    def load_default_config(self, filepath: Union[str, Path]) -> None:
        """
        Load default (base) configuration.
        
        This becomes the foundation that custom configs override.
        
        Parameters
        ----------
        filepath : str or Path
            Path to default CSV configuration file
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_default_config('base_registers.csv')
        """
        self._default_config = str(filepath)
        self.config_layers = [self._default_config]
        self._load_config_file(filepath)
        self._validate_all_groups()
    
    def load_custom_config(self, filepath: Union[str, Path]) -> None:
        """
        Load custom configuration layer (overlays defaults).
        
        Custom configs can:
        - Add new register groups
        - Add new fields to existing groups
        - Override enum values
        
        Parameters
        ----------
        filepath : str or Path
            Path to custom CSV configuration file
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_default_config('base.csv')
        >>> decoder.load_custom_config('device_specific.csv')
        >>> decoder.load_custom_config('site_overrides.csv')
        """
        filepath_str = str(filepath)
        if filepath_str not in self._custom_configs:
            self._custom_configs.append(filepath_str)
        self.config_layers.append(filepath_str)
        self._load_config_file(filepath)
        self._validate_all_groups()
    
    def load_config(self, filepath: Union[str, Path]) -> None:
        """
        Load configuration from CSV file (standalone mode).
        
        Use this for simple single-config loading.
        For layered configs, use load_default_config() + load_custom_config().
        
        Parameters
        ----------
        filepath : str or Path
            Path to CSV configuration file
        
        Raises
        ------
        FileNotFoundError
            If configuration file doesn't exist
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_config('alarm_config.csv')
        """
        self.load_default_config(filepath)
    
    def _load_config_file(self, filepath: Union[str, Path]) -> None:
        """Internal method to load a single config file."""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Skip comment lines (start with #)
                if row['group'].strip().startswith('#'):
                    continue
                
                self._process_row(row)
    
    def load_config_from_string(self, csv_content: str) -> None:
        """
        Load bitfield configuration from CSV string.
        
        Useful for testing or loading from embedded configurations.
        
        Parameters
        ----------
        csv_content : str
            CSV-formatted configuration data
        
        Examples
        --------
        >>> config = '''group,name,total_width,offset,width,type,value,meaning
        ... Status,enable,16,0,1,flag,1,ENABLED'''
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_config_from_string(config)
        """
        lines = csv_content.strip().split('\n')
        reader = csv.DictReader(lines)
        
        for row in reader:
            # Skip comment lines
            if row['group'].strip().startswith('#'):
                continue
            
            self._process_row(row)
        
        # Validate all loaded groups
        self._validate_all_groups()
    
    def save_cache(self, cache_path: Union[str, Path]) -> None:
        """
        Save current decoder state to JSON cache file.
        
        Caches:
        - All register group definitions
        - Configuration layer stack
        - Enum values and field definitions
        
        Parameters
        ----------
        cache_path : str or Path
            Path to cache file (will be created/overwritten)
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_default_config('base.csv')
        >>> decoder.load_custom_config('custom.csv')
        >>> decoder.save_cache('decoder_cache.json')
        """
        cache_data = {
            'version': '1.0',
            'config_layers': self.config_layers,
            'default_config': self._default_config,
            'custom_configs': self._custom_configs,
            'groups': {}
        }
        
        # Serialize register groups
        for group_name, group in self.groups.items():
            cache_data['groups'][group_name] = {
                'name': group.name,
                'total_width': group.total_width,
                'fields': {}
            }
            
            for field_name, field in group.fields.items():
                cache_data['groups'][group_name]['fields'][field_name] = {
                    'name': field.name,
                    'offset': field.offset,
                    'width': field.width,
                    'type': field.type,
                    'total_width': field.total_width,
                    'standard': field.standard,
                    'enum_values': {
                        str(val): {
                            'value': enum.value,
                            'meaning': enum.meaning,
                            'description': enum.description
                        }
                        for val, enum in field.enum_values.items()
                    }
                }
        
        # Write to file
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
    
    def load_cache(self, cache_path: Union[str, Path]) -> None:
        """
        Load decoder state from JSON cache file.
        
        Restores all register groups and configuration without re-parsing CSVs.
        Much faster than loading from CSV for large configurations.
        
        Parameters
        ----------
        cache_path : str or Path
            Path to cache file
        
        Raises
        ------
        FileNotFoundError
            If cache file doesn't exist
        ValueError
            If cache file is corrupted or wrong version
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_cache('decoder_cache.json')
        >>> result = decoder.decode('EventCode', 0xF234)
        """
        cache_path = Path(cache_path)
        
        if not cache_path.exists():
            raise FileNotFoundError(f"Cache file not found: {cache_path}")
        
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        if cache_data.get('version') != '1.0':
            raise ValueError("Incompatible cache version")
        
        # Restore metadata
        self.config_layers = cache_data.get('config_layers', [])
        self._default_config = cache_data.get('default_config')
        self._custom_configs = cache_data.get('custom_configs', [])
        
        # Restore register groups
        self.groups = {}
        for group_name, group_data in cache_data['groups'].items():
            group = RegisterGroup(
                name=group_data['name'],
                total_width=group_data['total_width']
            )
            
            for field_name, field_data in group_data['fields'].items():
                field = BitField(
                    name=field_data['name'],
                    offset=field_data['offset'],
                    width=field_data['width'],
                    type=field_data['type'],
                    total_width=field_data['total_width'],
                    standard=field_data['standard']
                )
                
                # Restore enum values
                for val_str, enum_data in field_data['enum_values'].items():
                    val = int(val_str)
                    field.enum_values[val] = EnumValue(
                        value=enum_data['value'],
                        meaning=enum_data['meaning'],
                        description=enum_data['description']
                    )
                
                group.fields[field_name] = field
            
            self.groups[group_name] = group
        
        print(f"✓ Loaded cache: {len(self.groups)} register groups from {cache_path}")
    
    def clear_cache(self) -> None:
        """
        Clear all loaded configurations and reset decoder.
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_config('config.csv')
        >>> decoder.clear_cache()
        >>> len(decoder.groups)
        0
        """
        self.groups = {}
        self.config_layers = []
        self._default_config = None
        self._custom_configs = []
    
    def _validate_all_groups(self) -> None:
        """
        Validate all loaded register groups and print reports.
        
        Prints errors, warnings, gap information, and coverage statistics
        to console for each loaded register group.
        """
        for group_name, group in self.groups.items():
            validation = group.validate_structure()
            
            if not validation['is_valid']:
                print(f"\n⚠️  ERRORS in {group_name}:")
                for error in validation['errors']:
                    print(f"  ❌ {error}")
            
            if validation['warnings']:
                print(f"\n⚠️  WARNINGS in {group_name}:")
                for warning in validation['warnings']:
                    print(f"  ⚠️  {warning}")
            
            if validation['gaps']:
                print(f"\nℹ️  Reserved/Gap bits in {group_name}:")
                for gap in validation['gaps']:
                    print(f"  📍 Bits {gap['start']}:{gap['end']} ({gap['width']} bits) - UNASSIGNED")
            
            coverage = validation['coverage']
            print(f"\n📊 Coverage for {group_name}: "
                  f"{coverage['covered_bits']}/{coverage['total_bits']} bits "
                  f"({coverage['coverage_percent']:.1f}%)\n")
    
    def _process_row(self, row: Dict[str, str]) -> None:
        """
        Process single CSV row and update internal structures.
        
        Parameters
        ----------
        row : dict
            CSV row as dictionary with keys matching column headers
        """
        group_name = row['group'].strip()
        field_name = row['name'].strip()
        total_width = int(row['total_width'])
        offset = int(row['offset'])
        width = int(row['width'])
        field_type = row['type'].strip()
        standard = row.get('standard', '').strip()
        
        # Get or create the register group
        if group_name not in self.groups:
            self.groups[group_name] = RegisterGroup(
                name=group_name,
                total_width=total_width
            )
        
        group = self.groups[group_name]
        
        # Get or create the bitfield
        if field_name not in group.fields:
            group.fields[field_name] = BitField(
                name=field_name,
                offset=offset,
                width=width,
                type=field_type,
                total_width=total_width,
                standard=standard
            )
        
        bitfield = group.fields[field_name]
        
        # Add enum value if applicable
        if field_type in ('enum', 'flag') and row.get('value'):
            value_str = row['value'].strip()
            
            # Handle hex values (0x prefix)
            if value_str.startswith('0x'):
                value = int(value_str, 16)
            else:
                value = int(value_str)
            
            meaning = row.get('meaning', '').strip()
            description = row.get('description', '').strip()
            
            bitfield.enum_values[value] = EnumValue(
                value=value,
                meaning=meaning,
                description=description
            )
    
    def decode(self, group_name: str, value: int) -> Dict[str, Any]:
        """
        Decode a register value according to its group configuration.
        
        Parameters
        ----------
        group_name : str
            Register group name (e.g., 'AlarmAttributes', 'EventCode')
        value : int
            Register value to decode (16-bit for single Modbus word,
            32-bit for combined words, etc.)
        
        Returns
        -------
        dict
            Complete decoding with all fields interpreted
        
        Raises
        ------
        ValueError
            If group_name is not found in loaded configuration
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_config('config.csv')
        >>> result = decoder.decode('EventCode', 0xF234)
        >>> result['fields']['category']['meaning']
        'ALARM_EVENT'
        """
        if group_name not in self.groups:
            raise ValueError(f"Unknown register group: {group_name}")
        
        return self.groups[group_name].decode(value)
    
    def decode_readable(self, group_name: str, value: int) -> str:
        """
        Decode register value to human-readable formatted string.
        
        Parameters
        ----------
        group_name : str
            Register group name
        value : int
            Register value to decode
        
        Returns
        -------
        str
            Multi-line formatted string with all field interpretations
        
        Raises
        ------
        ValueError
            If group_name is not found
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_config('config.csv')
        >>> print(decoder.decode_readable('EventCode', 0xF234))
        === EventCode ===
        Raw: 62004 | Hex: 0xF234 | Binary: 0b1111001000110100
        
          category: ALARM_EVENT (15)
            → Alarm event category
          eventType: PICKUP (2)
            → Alarm condition detected (pickup)
        """
        if group_name not in self.groups:
            raise ValueError(f"Unknown register group: {group_name}")
        
        return self.groups[group_name].decode_to_readable(value)
    
    def get_field_value(self, group_name: str, field_name: str, 
                       register_value: int) -> Any:
        """
        Extract and decode a specific field from register value.
        
        Useful when you only need one field instead of full decode.
        
        Parameters
        ----------
        group_name : str
            Register group name
        field_name : str
            Specific field to extract
        register_value : int
            Full register value
        
        Returns
        -------
        dict
            Decoded field information
        
        Raises
        ------
        ValueError
            If group_name or field_name not found
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_config('config.csv')
        >>> category = decoder.get_field_value('EventCode', 'category', 0xF234)
        >>> category['meaning']
        'ALARM_EVENT'
        """
        if group_name not in self.groups:
            raise ValueError(f"Unknown register group: {group_name}")
        
        group = self.groups[group_name]
        
        if field_name not in group.fields:
            raise ValueError(f"Unknown field '{field_name}' in group '{group_name}'")
        
        return group.fields[field_name].decode(register_value)
    
    def list_groups(self) -> List[str]:
        """
        Get list of available register groups.
        
        Returns
        -------
        list of str
            Names of all loaded register groups
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_config('config.csv')
        >>> decoder.list_groups()
        ['AlarmAttributes', 'EventCode', 'DataType']
        """
        return list(self.groups.keys())
    
    def get_group_info(self, group_name: str) -> Dict[str, Any]:
        """
        Get metadata about a register group.
        
        Parameters
        ----------
        group_name : str
            Register group name
        
        Returns
        -------
        dict
            Group information including validation results
        
        Raises
        ------
        ValueError
            If group_name not found
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_config('config.csv')
        >>> info = decoder.get_group_info('EventCode')
        >>> info['total_width']
        16
        >>> info['field_count']
        3
        """
        if group_name not in self.groups:
            raise ValueError(f"Unknown register group: {group_name}")
        
        group = self.groups[group_name]
        validation = group.validate_structure()
        
        return {
            'name': group.name,
            'total_width': group.total_width,
            'fields': list(group.fields.keys()),
            'field_count': len(group.fields),
            'validation': validation
        }
    
    def visualize_register(self, group_name: str) -> str:
        """
        Create ASCII visualization of register bit layout.
        
        Parameters
        ----------
        group_name : str
            Register group name
        
        Returns
        -------
        str
            Multi-line ASCII art showing field positions
        
        Raises
        ------
        ValueError
            If group_name not found
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_config('config.csv')
        >>> print(decoder.visualize_register('EventCode'))
        Register: EventCode (16-bit)
        ...
        """
        if group_name not in self.groups:
            raise ValueError(f"Unknown register group: {group_name}")
        
        return self.groups[group_name].visualize_layout()
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Validate all loaded register groups.
        
        Returns comprehensive validation report.
        
        Returns
        -------
        dict
            Validation reports keyed by group name
        
        Examples
        --------
        >>> decoder = BitfieldDecoder()
        >>> decoder.load_config('config.csv')
        >>> validation = decoder.validate_all()
        >>> for group, report in validation.items():
        ...     if not report['is_valid']:
        ...         print(f"Errors in {group}")
        """
        report = {}
        
        for group_name, group in self.groups.items():
            report[group_name] = group.validate_structure()
        
        return report


# Example usage
if __name__ == "__main__":
    print("BitfieldDecoder - Industrial Register Decoder for Modbus")
    print("=" * 60)
    print("\nQuick Start:")
    print("-" * 60)
    print("decoder = BitfieldDecoder()")
    print("decoder.load_config('alarm_attributes.csv')")
    print("")
    print("# Decode from Modbus words")
    print("words = [0x1234, 0x5678]  # Two 16-bit registers")
    print("result = decoder.decode_from_words('AlarmAttributes', words)")
    print("")
    print("# Decode built-in types")
    print("dt = decoder.decode_datetime([0x0715, 0x0000, 0x0B04, 0x010C])")
    print("")
    print("# Multi-layer configs")
    print("decoder.load_default_config('base.csv')")
    print("decoder.load_custom_config('overrides.csv')")
    print("")
    print("# Caching")
    print("decoder.save_cache('cache.json')")
    print("decoder.load_cache('cache.json')")
