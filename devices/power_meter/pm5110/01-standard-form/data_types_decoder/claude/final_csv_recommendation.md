# Final CSV Structure Recommendations

## Summary of Your Current Structure

**Current columns:**
```csv
group,name,total_width,offset,width,type,value,meaning,description,standard
```

**Status:** ✅ **Fundamentally solid** - Good foundation for multi-consumer use

---

## Recommended Improvements

### Version 1: Minimal Changes (Recommended Starting Point)

**New columns:**
```csv
device,group,name,value,type,offset,width,total_width,enum_name,description,unit_code,standard,manual_ref
```

**Changes:**
1. ➕ `device` column (first position) - support multiple devices
2. 🔄 Reorder: keys first (device, group, name, value)
3. 📝 Rename: `meaning` → `enum_name` (clearer purpose)
4. ➕ `unit_code` - explicit link to units table
5. ➕ `manual_ref` - traceability to source documentation
6. 🔧 Simplify `standard` - remove redundant text

**Example:**
```csv
device,group,name,value,type,offset,width,total_width,enum_name,description,unit_code,standard,manual_ref
PM5110,AlarmAttributes,type,0,enum,28,4,32,NONE,No alarm type defined,,vendor,p.45
PM5110,AlarmAttributes,type,1,enum,28,4,32,STANDARD1S,Standard 1-second alarm for continuous monitoring,,vendor,p.45
PM5110,AlarmAttributes,parameter,1,enum,17,4,32,VOLTAGE,Voltage measurement parameter,8,vendor,p.46
PM5110,AlarmAttributes,parameter,2,enum,17,4,32,CURRENT,Current measurement parameter,6,vendor,p.46
PM5110,AlarmAttributes,enable,0,flag,0,1,32,DISABLED,Alarm disabled (not active),,vendor,p.47
PM5110,AlarmAttributes,enable,1,flag,0,1,32,ENABLED,Alarm enabled (active),,vendor,p.47
```

---

### Version 2: Extended (For Mature Projects)

**Additional columns for complex scenarios:**
```csv
device,group,name,value,type,offset,width,total_width,enum_name,description,unit_code,standard,manual_ref,status,access,address
```

**Additional fields:**
- `status` - enum: `active`, `reserved`, `deprecated`, `future`
- `access` - enum: `ro` (read-only), `rw` (read-write), `wo` (write-only)
- `address` - Modbus address (if different fields have different addresses)

**Example with extended fields:**
```csv
device,group,name,value,type,offset,width,total_width,enum_name,description,unit_code,standard,manual_ref,status,access,address
PM5110,AlarmAttributes,type,0,enum,28,4,32,NONE,No alarm type defined,,vendor,p.45,active,rw,0x4000
PM5110,AlarmAttributes,type,31,enum,28,4,32,RESERVED,Reserved for future use,,vendor,p.45,reserved,rw,0x4000
```

---

## Units Table Structure

**Current (inferred):**
```csv
code,abbreviation,description
```

**Recommended enhancement:**
```csv
code,symbol,name,category,si_unit,conversion_factor
```

**Example:**
```csv
code,symbol,name,category,si_unit,conversion_factor
8,V,Volts,voltage,V,1
9,kV,Kilovolts,voltage,V,1000
6,A,Amperes,current,A,1
5,Hz,Hertz,frequency,Hz,1
2,°C,Degrees Celsius,temperature,K,1
3,°F,Degrees Fahrenheit,temperature,K,0.556
```

**Benefits:**
- `category` - group similar units (voltage, current, power)
- `si_unit` - standard SI unit for category
- `conversion_factor` - convert to SI (enables unit conversion)

---

## DataType Table Structure

**Current:**
```csv
group,name,total_width,offset,width,type,value,max,meaning,standard
```

**Recommended:**
```csv
datatype,field_name,offset,width,type,min_value,max_value,description,standard
```

**Changes:**
- `group` → `datatype` (clearer intent)
- `name` → `field_name` (consistency with main table)
- Add `min_value` (not just max)
- Remove redundant `value` column

**Example:**
```csv
datatype,field_name,offset,width,type,min_value,max_value,description,standard
DATETIME,year,0,6,number,0,127,Year value (0-127),IEC 870-5-4
DATETIME,day,16,5,number,1,31,Day of month (1-31),IEC 870-5-4
DATETIME,month,24,4,number,1,12,Month (1-12),IEC 870-5-4
DATETIME,minutes,32,6,number,0,59,Minutes (0-59),IEC 870-5-4
DATETIME,hour,40,5,number,0,23,Hour (0-23),IEC 870-5-4
DATETIME,millisecond,48,16,number,0,59999,Milliseconds (0-59999),IEC 870-5-4
DATETIME,dst_flag,47,1,flag,0,1,Daylight saving time flag,IEC 870-5-4
```

---

## File Organization Options

### Option A: Single File (Simple)
```
device_config.csv          # All registers, all devices
units.csv                  # All units
datatypes.csv              # All standard datatypes
```

**Pros:**
- ✅ Simple to manage (3 files total)
- ✅ Easy to search across devices
- ✅ Single source for comparisons

**Cons:**
- ❌ Large file if many devices
- ❌ Merge conflicts in team environment

---

### Option B: Per-Device Files (Recommended)
```
devices/
  ├── schneider/
  │   ├── pm5110_registers.csv
  │   ├── pm5350_registers.csv
  │   └── metadata.json
  ├── abb/
  │   ├── m2m_registers.csv
  │   └── metadata.json
  └── siemens/
      ├── pac3200_registers.csv
      └── metadata.json

common/
  ├── units.csv              # Shared units table
  └── datatypes.csv          # Shared standard datatypes
```

**Pros:**
- ✅ Scales better (100+ devices)
- ✅ Fewer merge conflicts
- ✅ Easier to maintain per-device
- ✅ Can version devices independently

**Cons:**
- ❌ More files to manage
- ❌ Need to load multiple files

---

### Option C: Hybrid (Best of Both)
```
all_devices.csv            # Combined database (generated)
devices/
  ├── pm5110.csv          # Source files
  ├── m2m.csv
  └── pac3200.csv
common/
  ├── units.csv
  └── datatypes.csv

scripts/
  └── combine_devices.py   # Merges device/*.csv → all_devices.csv
```

**Workflow:**
1. Edit individual device CSV files
2. Run `combine_devices.py` to generate `all_devices.csv`
3. Applications load `all_devices.csv` (single file)
4. Version control tracks individual device files

**Pros:**
- ✅ Easy to edit (small files)
- ✅ Easy to use (single combined file)
- ✅ Scalable and maintainable

---

## Column Data Type Standards

**For consistency across all tools:**

| Column | Data Type | Format | Example |
|--------|-----------|--------|---------|
| device | string | UPPERCASE | `PM5110`, `M2M` |
| group | string | CamelCase | `AlarmAttributes` |
| name | string | lowercase_underscore | `type`, `enable`, `power_factor` |
| value | integer | decimal | `0`, `1`, `15` |
| type | enum | lowercase | `enum`, `number`, `flag` |
| offset | integer | decimal | `0`, `28` |
| width | integer | decimal | `1`, `4`, `32` |
| total_width | integer | decimal | `16`, `32`, `64` |
| enum_name | string | UPPERCASE_UNDERSCORE | `NONE`, `STANDARD1S` |
| description | string | natural language | "Standard 1-second alarm" |
| unit_code | integer or empty | decimal | `8` (Volts), `` (no unit) |
| standard | enum | lowercase or standard | `vendor`, `IEC-870-5-4` |
| manual_ref | string | free-form | `p.45`, `sec.3.2`, `Table 5-3` |
| status | enum | lowercase | `active`, `reserved`, `deprecated` |
| access | enum | lowercase | `ro`, `rw`, `wo` |
| address | hex string | 0xHHHH | `0x4000`, `0x2000` |

---

## Validation Rules

**Rules to enforce (via script or schema):**

1. **Bit Math:**
   - `offset + width <= total_width`
   - No negative offsets
   - Width must be 1-64

2. **Enum Values:**
   - For each (group, name, type=enum), value must be unique
   - Value must fit in width: `value < (1 << width)`

3. **Required Fields:**
   - device, group, name, offset, width, total_width always required
   - enum_name required when type=enum
   - unit_code required when parameter is measurement type

4. **Referential Integrity:**
   - unit_code must exist in units.csv
   - If datatype referenced, must exist in datatypes.csv

5. **Naming Conventions:**
   - group: CamelCase, no spaces
   - name: lowercase_underscore
   - enum_name: UPPERCASE_UNDERSCORE
   - device: UPPERCASE

---

## Sample Validation Script

```python
import csv
import sys

def validate_csv(filepath):
    errors = []
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            # Check bit math
            try:
                offset = int(row['offset'])
                width = int(row['width'])
                total = int(row['total_width'])
                
                if offset + width > total:
                    errors.append(f"Line {i}: Bit overflow")
                    
                # Check value fits in width
                if row['value']:
                    value = int(row['value'])
                    max_val = (1 << width) - 1
                    if value > max_val:
                        errors.append(f"Line {i}: Value {value} too large for width {width}")
                        
            except (ValueError, KeyError) as e:
                errors.append(f"Line {i}: Invalid numeric field - {e}")
            
            # Check naming conventions
            if row['group'] and not row['group'][0].isupper():
                errors.append(f"Line {i}: Group should be CamelCase")
            
            if row.get('enum_name') and row['type'] == 'enum':
                if not row['enum_name'].isupper():
                    errors.append(f"Line {i}: enum_name should be UPPERCASE")
    
    return errors

if __name__ == "__main__":
    errors = validate_csv(sys.argv[1])
    if errors:
        print("Validation errors:")
        for err in errors:
            print(f"  {err}")
        sys.exit(1)
    else:
        print("✓ Validation passed")
```

---

## Migration Guide

### Step 1: Add New Columns (Non-Breaking)
```bash
# Add device column (set to device model name)
awk -F, 'NR==1 {print "device,"$0} NR>1 {print "PM5110,"$0}' old.csv > new.csv

# Add unit_code column (empty initially)
awk -F, 'NR==1 {print $0",unit_code"} NR>1 {print $0","}' new.csv > temp.csv

# Add manual_ref column
awk -F, 'NR==1 {print $0",manual_ref"} NR>1 {print $0","}' temp.csv > final.csv
```

### Step 2: Fill Manual References
- Open in Excel/LibreOffice
- Filter by group
- Bulk-fill manual_ref column (e.g., "p.45" for AlarmAttributes)

### Step 3: Rename Columns
```python
import pandas as pd
df = pd.read_csv('final.csv')
df = df.rename(columns={'meaning': 'enum_name'})
df.to_csv('final.csv', index=False)
```

### Step 4: Validate
```bash
python validate_csv.py final.csv
```

---

## Quick Reference: Before vs After

### Before (Your Current):
```csv
group,name,total_width,offset,width,type,value,meaning,description,standard
AlarmAttributes,type,32,28,4,enum,0,NONE,No alarm type defined,Device specific AlarmAttributes
```

### After (Recommended):
```csv
device,group,name,value,type,offset,width,total_width,enum_name,description,unit_code,standard,manual_ref
PM5110,AlarmAttributes,type,0,enum,28,4,32,NONE,No alarm type defined,,vendor,p.45
```

**Key improvements:**
1. ✅ Device column enables multi-device support
2. ✅ Keys first (device,group,name,value) for better scanning
3. ✅ Clearer column names (meaning → enum_name)
4. ✅ Explicit unit linkage (unit_code)
5. ✅ Traceability (manual_ref)
6. ✅ Cleaner standard field (vendor instead of "Device specific AlarmAttributes")

---

## Bottom Line

**Your current structure: Solid foundation** ✅

**Priority improvements (implement first):**
1. Add `device` column (multi-device support)
2. Add `unit_code` column (explicit linkage)
3. Add `manual_ref` column (traceability)
4. Rename `meaning` → `enum_name` (clarity)
5. Clean up `standard` column (remove redundancy)

**Nice-to-have (implement later):**
1. Add `status` column (lifecycle management)
2. Add `access` column (read/write permissions)
3. Reorder columns (keys first)

**Your CSV format is the right choice** - don't switch to XML/JSON unless you have a specific reason. The flat CSV structure works perfectly for your multi-consumer use case.
