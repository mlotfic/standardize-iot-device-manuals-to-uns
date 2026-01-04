# Universal Device Config CSV - Field Guide

## Purpose
This CSV format is the **single source of truth** used by:
- ✅ Python devs (parse registers in code)
- ✅ Embedded C/C++ devs (decode bit fields)
- ✅ Operators (understand alarm meanings)
- ✅ Web UI developers (display human-readable names)
- ✅ Documentation generators (create user manuals)

**The CSV IS the deliverable** - not a source for code generation, but the reference itself.

---

## Column Definitions

### Column 1: `device_model`
**What:** Device model identifier  
**Format:** Vendor model number exactly as on device label  
**Examples:** `PM5110`, `PAC3200`, `M2M`, `ION7650`  
**Why needed:** Multiple device configs in same database/folder

---

### Column 2: `register_group`
**What:** Register or bitfield structure name  
**Format:** CamelCase, no spaces  
**Examples:** `AlarmAttributes`, `EventCode`, `DateTime`, `MeterStatus`  
**From manual:** Section header or register name  

**Transformation examples:**
- Manual: "Alarm Attributes Register" → `AlarmAttributes`
- Manual: "Event Code" → `EventCode`  
- Manual: "Meter Status Word" → `MeterStatus`

---

### Column 3: `field_name`
**What:** Individual bit field within the register  
**Format:** lowercase_with_underscores  
**Examples:** `type`, `phases`, `event_type`, `dst_flag`  
**From manual:** Field label in register bit map

**Transformation examples:**
- Manual: "Alarm Type" → `type`
- Manual: "Phase Information" → `phases`
- Manual: "DST Flag" → `dst_flag`

---

### Column 4: `total_bits`
**What:** Total width of entire register in bits  
**Format:** Integer (8, 16, 32, 64, 128)  
**Examples:** `32`, `16`, `64`  
**From manual:** Register width specification

---

### Column 5: `bit_offset`
**What:** Starting bit position (LSB = Least Significant Bit)  
**Format:** Integer, 0-indexed from right  
**Examples:** `28`, `7`, `0`  
**From manual:** Lowest bit number in range

**Bit numbering:**
```
31 30 29 28 | 27 26 25 24 | ... | 3 2 1 0
   [Type]   |  [Subtype]  | ... |  [Enable]
offset=28   | offset=24   | ... | offset=0
```

---

### Column 6: `bit_width`
**What:** How many bits this field occupies  
**Format:** Integer (1-64)  
**Examples:** `4`, `2`, `1`  
**Calculation:** If manual says "Bits 28-31" → width = 31-28+1 = 4

---

### Column 7: `data_type`
**What:** Type of data stored in field  
**Format:** One of: `enum`, `number`, `flag`  

| Type | When to Use | Example |
|------|-------------|---------|
| `enum` | Discrete named values (0=None, 1=Standard) | Alarm types, phases |
| `number` | Numeric range (0-59, 1-31) | Minutes, temperature |
| `flag` | Binary on/off (0=disabled, 1=enabled) | Enable bits, flags |

---

### Column 8: `enum_value`
**What:** Numeric value for this enum option  
**Format:** Integer or leave empty for non-enums  
**Examples:** `0`, `1`, `15`  
**From manual:** The number before "=" in manual (e.g., "0 = None")

**Rules:**
- Create **one row per enum value**
- Leave empty for `data_type=number` fields
- Include all values even if reserved

---

### Column 9: `enum_name`
**What:** Name/label for this enum value  
**Format:** UPPERCASE_WITH_UNDERSCORES  
**Examples:** `NONE`, `STANDARD1S`, `OVER_SIGNED`, `ENABLED`  
**From manual:** Text after "=" in manual

**Transformation examples:**
- Manual: "0 = None" → `NONE`
- Manual: "1 = Standard 1-second" → `STANDARD1S`
- Manual: "Over (signed)" → `OVER_SIGNED`
- Manual: "Phase A" → `A`

---

### Column 10: `description`
**What:** Human-readable explanation  
**Format:** Plain text, copy from manual  
**Examples:** "Standard 1-second alarm for continuous monitoring"  
**From manual:** Description text verbatim

**Rules:**
- Copy exact wording from manual (for traceability)
- Include context (e.g., "overvoltage" not just "swell")
- Keep it one line (no line breaks)

---

### Column 11: `unit_code`
**What:** Unit of measurement code (if applicable)  
**Format:** Integer referencing units table, or empty  
**Examples:** `8` (Volts), `6` (Amperes), `5` (Hertz)  
**From manual:** Links parameter to physical unit

**When to fill:**
- Measurement parameters (voltage, current, power)
- Temperature fields
- Leave empty for: enums, flags, dimensionless values

---

### Column 12: `manual_ref`
**What:** Page/section reference in device manual  
**Format:** `p.45` or `sec.3.2.1` or `Table 5-3`  
**Examples:** `p.45`, `sec.3.2`, `Tbl.5-3`  
**Why needed:** Traceability back to source document

---

### Column 13: `standard`
**What:** Industry standard this follows  
**Format:** Standard name or "Device specific"  
**Examples:** `IEC 870-5-4`, `IEC 61850`, `Device specific`  
**From manual:** Look for standard references in intro/appendix

---

## How to Fill Template from Different Vendor Manual Formats

### Vendor Format 1: Schneider (Table with bit ranges)

**Manual shows:**
```
Register: Alarm Attributes (32-bit, Address 4000h)
┌──────────┬─────────────┬──────────────────┐
│ Bits     │ Field       │ Values           │
├──────────┼─────────────┼──────────────────┤
│ 28-31    │ Alarm Type  │ 0=None           │
│          │             │ 1=Standard 1sec  │
│          │             │ 2=Custom 1sec    │
├──────────┼─────────────┼──────────────────┤
│ 3-4      │ Priority    │ 0=None           │
│          │             │ 1=High           │
└──────────┴─────────────┴──────────────────┘
```

**Fill CSV as:**
```csv
PM5110,AlarmAttributes,type,32,28,4,enum,0,NONE,No alarm type defined,,p.45,Device specific
PM5110,AlarmAttributes,type,32,28,4,enum,1,STANDARD1S,Standard 1-second alarm,,p.45,Device specific
PM5110,AlarmAttributes,type,32,28,4,enum,2,CUSTOM1S,Custom 1-second alarm,,p.45,Device specific
PM5110,AlarmAttributes,priority,32,3,2,enum,0,NONE,No priority assigned,,p.45,Device specific
PM5110,AlarmAttributes,priority,32,3,2,enum,1,HIGH,High priority alarm,,p.45,Device specific
```

---

### Vendor Format 2: ABB (Narrative description)

**Manual shows:**
```
Alarm Configuration Word (32-bit)
The alarm type is encoded in bits 28-31:
  - Value 0 indicates no alarm
  - Value 1 indicates standard alarm
  
Priority is stored in bits 3-4 where
0=low, 1=medium, 2=high
```

**Fill CSV as:**
```csv
M2M,AlarmConfig,alarm_type,32,28,4,enum,0,NO_ALARM,No alarm configured,,p.23,Device specific
M2M,AlarmConfig,alarm_type,32,28,4,enum,1,STANDARD,Standard alarm type,,p.23,Device specific
M2M,AlarmConfig,priority,32,3,2,enum,0,LOW,Low priority alarm,,p.23,Device specific
M2M,AlarmConfig,priority,32,3,2,enum,1,MEDIUM,Medium priority alarm,,p.23,Device specific
M2M,AlarmConfig,priority,32,3,2,enum,2,HIGH,High priority alarm,,p.23,Device specific
```

---

### Vendor Format 3: Siemens (Hex values and masks)

**Manual shows:**
```
Status Register = 0x0000 to 0xFFFF (16-bit)

Bit mask 0xF000 (bits 12-15): Device State
  0x0000 = Idle
  0x1000 = Running
  0x2000 = Error
  
Bit mask 0x000F (bits 0-3): Phase Status
  0x0001 = Phase A OK
  0x0007 = All phases OK
```

**Fill CSV as:**
```csv
PAC3200,StatusRegister,device_state,16,12,4,enum,0,IDLE,Device is idle,,p.67,Device specific
PAC3200,StatusRegister,device_state,16,12,4,enum,1,RUNNING,Device is running,,p.67,Device specific
PAC3200,StatusRegister,device_state,16,12,4,enum,2,ERROR,Device error state,,p.67,Device specific
PAC3200,StatusRegister,phase_status,16,0,4,enum,1,PHASE_A_OK,Phase A operational,,p.67,Device specific
PAC3200,StatusRegister,phase_status,16,0,4,enum,7,ALL_PHASES_OK,All phases operational,,p.67,Device specific
```

---

### Vendor Format 4: IEC Standard (Dense technical spec)

**Manual shows:**
```
CP56Time2a (IEC 60870-5-4 seven-octet binary time)
Octet 1-2: Milliseconds (UI16, 0-59999)
Octet 3, bits 0-5: Minutes (UI6, 0-59)
Octet 4, bits 0-4: Hours (UI5, 0-23)
Octet 4, bit 7: SU (summer time)
```

**Fill CSV as:**
```csv
IEC60870,CP56Time2a,milliseconds,64,0,16,number,,,Milliseconds (0-59999),,sec.4.2.3,IEC 60870-5-4
IEC60870,CP56Time2a,minutes,64,16,6,number,,,Minutes (0-59),,sec.4.2.3,IEC 60870-5-4
IEC60870,CP56Time2a,hours,64,24,5,number,,,Hours (0-23),,sec.4.2.3,IEC 60870-5-4
IEC60870,CP56Time2a,summer_time,64,31,1,flag,0,STANDARD,Standard time,,sec.4.2.3,IEC 60870-5-4
IEC60870,CP56Time2a,summer_time,64,31,1,flag,1,DAYLIGHT,Daylight saving time,,sec.4.2.3,IEC 60870-5-4
```

---

## Common Transformation Patterns

### Pattern 1: Range notation → Multiple rows
**Manual:** "0-15 = Harmonic orders 1-16"  
**CSV:** Create 16 separate rows (enum_value: 0-15)

### Pattern 2: Reserved values
**Manual:** "Values 10-30 reserved"  
**CSV:** Skip them UNLESS manual explicitly says "31=Not Used"

### Pattern 3: Bit masks as individual bits
**Manual:** "Bit mask 0x0007 for phases A, B, C"  
**CSV:** Often better as single enum field if values are discrete combinations

### Pattern 4: Conditional fields
**Manual:** "Bits 0-3 are priority when category=15"  
**CSV:** Add note in description: "Priority (only valid when category=ALARM_EVENT)"

---

## Usage Examples

### For Python Developer:
```python
import csv

# Load config
config = {}
with open('device_config.csv') as f:
    for row in csv.DictReader(f):
        if row['device_model'] == 'PM5110':
            key = (row['register_group'], row['field_name'])
            config[key] = row

# Decode alarm register
raw_value = 0x12003401  # From Modbus
alarm_type = (raw_value >> 28) & 0xF
print(f"Alarm type code: {alarm_type}")

# Look up meaning
for row in csv.DictReader(open('device_config.csv')):
    if (row['register_group'] == 'AlarmAttributes' and 
        row['field_name'] == 'type' and 
        row['enum_value'] == str(alarm_type)):
        print(f"Meaning: {row['enum_name']} - {row['description']}")
```

### For Embedded C Developer:
```c
// Read CSV to understand bit layout
// Bits 28-31: type (4 bits)
// Bits 3-4: priority (2 bits)

uint32_t raw = read_register(0x4000);
uint8_t alarm_type = (raw >> 28) & 0xF;
uint8_t priority = (raw >> 3) & 0x3;

if (alarm_type == 1) {  // STANDARD1S from CSV
    if (priority == 1) {  // HIGH from CSV
        trigger_immediate_response();
    }
}
```

### For Operator (Direct CSV Reading):
Open CSV in Excel, filter by `device_model=PM5110`, search for alarm code → read `description` column

### For Web UI Developer:
```javascript
// Load CSV, build dropdown options
fetch('device_config.csv')
  .then(r => r.text())
  .then(csv => {
    const rows = parseCSV(csv);
    const alarmTypes = rows
      .filter(r => r.register_group === 'AlarmAttributes' && 
                   r.field_name === 'type')
      .map(r => ({
        value: r.enum_value,
        label: `${r.enum_name}: ${r.description}`
      }));
    
    // Populate <select> dropdown
    populateDropdown(alarmTypes);
  });
```

---

## Quality Checklist

Before committing your filled CSV, verify:

- [ ] `device_model` matches device label exactly
- [ ] All bit positions: `bit_offset + bit_width ≤ total_bits`
- [ ] No overlapping bits (unless conditional, noted in description)
- [ ] Every enum value from manual has its own row
- [ ] `enum_name` is UPPERCASE_UNDERSCORE format
- [ ] `field_name` is lowercase_underscore format
- [ ] `description` copied verbatim from manual
- [ ] `manual_ref` filled for traceability
- [ ] `unit_code` filled for measurement parameters
- [ ] `standard` identified (IEC, IEEE, or "Device specific")

---

## File Naming Convention

```
{vendor}_{model}_{register_type}.csv

Examples:
schneider_pm5110_alarms.csv
abb_m2m_status.csv
siemens_pac3200_measurements.csv
```

Or single unified file:
```
device_configs.csv  (all devices, filtered by device_model column)
```

---

## Summary

This CSV format solves the "multiple vendor formats" problem by:

1. ✅ **Standardized structure** - Same columns regardless of vendor
2. ✅ **Human readable** - Operators can read it directly
3. ✅ **Machine parseable** - Code can extract bit positions
4. ✅ **Self-documenting** - Descriptions and references included
5. ✅ **Traceable** - Links back to manual page numbers
6. ✅ **Universal** - Works for any device that uses bitfield registers

**The CSV itself is the deliverable** - no code generation needed. Everyone works from the same file.
