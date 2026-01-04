# Manual-to-Config Transformation Rules

## Purpose
Standardized process for developers to convert device manuals into config CSV files.

---

## Step 1: Identify Register Types in Manual

### Rule 1.1: Locate Bitfield Tables
**What to look for in manual:**
- Tables with columns: "Bit Position", "Field Name", "Values", "Description"
- Register maps with bit allocations
- Alarm configuration sections
- Event code definitions

**Example from manual:**
```
Register 4000h - Alarm Attributes (32-bit)
Bits 28-31: Alarm Type
  0 = None
  1 = Standard 1-second
  2 = Custom 1-second
  ...
```

**Transform to CSV row:**
```csv
AlarmAttributes,type,32,28,4,enum,0,NONE,No alarm type defined,Device specific AlarmAttributes
```

---

## Step 2: Standardize Field Extraction

### Rule 2.1: Group Column (Register Name)
**Source:** Section header or register name from manual
**Format:** CamelCase, no spaces
**Examples:**
- "Alarm Attributes Register" → `AlarmAttributes`
- "Event Code" → `EventCode`
- "Date/Time Stamp" → `DateTime`

### Rule 2.2: Name Column (Field Name)
**Source:** Bit field label from manual
**Format:** lowercase, underscores for spaces
**Examples:**
- "Alarm Type" → `type`
- "Phase Information" → `phases`
- "Power Factor" → `power_factor`

### Rule 2.3: Width Calculation
**Rule:** Count bits from manual's bit range
**Examples:**
- Bits 28-31 → width = 4 (31-28+1)
- Bits 3-4 → width = 2
- Bit 0 → width = 1

### Rule 2.4: Offset (LSB Position)
**Rule:** Use the **lowest bit number** from the range
**Examples:**
- Bits 28-31 → offset = 28
- Bits 3-4 → offset = 3
- Bit 7 → offset = 7

---

## Step 3: Enum Value Extraction

### Rule 3.1: Direct Mapping
**When manual shows:**
```
0 = None
1 = Standard 1-second alarm
2 = Custom 1-second alarm
```

**Create separate rows for each:**
```csv
AlarmAttributes,type,32,28,4,enum,0,NONE,No alarm type defined,Device specific
AlarmAttributes,type,32,28,4,enum,1,STANDARD1S,Standard 1-second alarm,Device specific
AlarmAttributes,type,32,28,4,enum,2,CUSTOM1S,Custom 1-second alarm,Device specific
```

### Rule 3.2: Value Name Standardization
**Original from manual → Standardized name:**
- "None" → `NONE`
- "Standard 1-second" → `STANDARD1S`
- "Over (signed)" → `OVER_SIGNED`
- "Phase A" → `A`
- "Line-to-Neutral" → `LN`
- "3-Phase Total" → `3PHASE_TOTAL`

**Pattern:** UPPERCASE, underscores, remove parentheses, abbreviate when clear

### Rule 3.3: Handle Reserved Values
**When manual shows:**
```
12-30 = Reserved
31 = Not Used
```

**Only create row for explicit "Not Used":**
```csv
AlarmAttributes,subtype,32,23,4,enum,31,NOT_USED,Reserved - not used,Device specific
```

**Omit implicit reserved ranges** (12-30) unless manual specifies behavior

---

## Step 4: Type Classification

### Rule 4.1: Enum vs Number vs Flag

| Manual Indicator | Type to Use | Example |
|-----------------|-------------|---------|
| Discrete values listed (0=x, 1=y, 2=z) | `enum` | Alarm types |
| Range (0-59, 1-31) | `number` | Minutes, days |
| Binary (0=disabled, 1=enabled) | `enum` or `flag`* | Enable bits |
| Bitmask for multiple selections | `flag` | Phase combinations |

*Use `enum` for consistency unless clearly a boolean flag

### Rule 4.2: Width Determines Type Hints
- width=1 → Usually boolean/flag
- width=2-4 → Usually enum (up to 16 values)
- width=5+ → Could be enum or number, check manual

---

## Step 5: Description Field

### Rule 5.1: Description Content
**Combine from manual:**
1. Field purpose (what it does)
2. Value meaning (for that specific enum)
3. Units or context (if applicable)

**Examples:**
```csv
# For field header
AlarmAttributes,type,32,28,4,enum,1,STANDARD1S,"Standard 1-second alarm for continuous monitoring",Device specific

# For units
Units,code,,,,,8,V,"Volts",Standard

# For datetime component
DataType,DATETIME,64,16,5,number,1,31,"Day",IEC 870-5-6
```

### Rule 5.2: Keep Original Manual Wording
**Don't editorialize** - use vendor's exact terminology for traceability
- Manual says "Power-up event" → Use "Power-up event"
- Manual says "Phase reversal detected" → Use "Phase reversal detected"

---

## Step 6: Standard Reference

### Rule 6.1: Identify Standard Source
**Check manual for:**
- "IEC 61850", "IEC 870-5-4" → Use exact standard name
- "Device specific" → When vendor-proprietary
- "IEEE 1159" → Use for power quality
- "Modbus" → For standard Modbus registers

**Column value:**
```csv
DataType,DATETIME,64,0,6,number,0,127,Year,IEC 870-5-4
AlarmAttributes,type,32,28,4,enum,0,NONE,No alarm type,Device specific AlarmAttributes
```

---

## Step 7: Multi-Document Structures

### Rule 7.1: Units Table
**When manual has unit codes section:**
```
Code 8: Volts (V)
Code 6: Amperes (A)
```

**Create units CSV:**
```csv
code,abbreviation,description
8,V,Volts
6,A,amperes
```

### Rule 7.2: Cross-References
**When field references units:**
```csv
AlarmAttributes,parameter,32,17,4,enum,1,VOLTAGE,"Voltage measurement parameter [unit=8]",Device specific
```

**Add bracketed reference** for developer lookup

---

## Step 8: Validation Checklist

### Developer Self-Check Before Commit:

- [ ] **Bit math correct**: offset + width ≤ total_width
- [ ] **No overlaps**: No two fields use same bit positions (unless manual specifies)
- [ ] **All enum values**: Every value in manual range accounted for
- [ ] **Consistent naming**: CamelCase groups, lowercase_underscore fields
- [ ] **Description completeness**: Every row has meaningful description
- [ ] **Standard accuracy**: Checked manual for standard references
- [ ] **Units linked**: Parameters that measure things reference unit codes

---

## Step 9: Handling Edge Cases

### Edge Case 9.1: Overlapping Bits
**When manual shows:**
```
Bits 0-3: Priority (when Category=15)
Bits 0-3: Reserved (when Category≠15)
```

**Create conditional note:**
```csv
EventCode,priority,16,0,4,enum,0,NONE,"Priority (only valid when category=ALARM_EVENT)",Device specific
```

### Edge Case 9.2: Vendor-Specific Extensions
**When manual says:**
```
Bits 61-63: User Defined
```

**Preserve flexibility:**
```csv
AlarmAttributes,parameter,32,17,4,enum,61,USER_DEFINED1,"User-defined parameter 1",Device specific
AlarmAttributes,parameter,32,17,4,enum,62,USER_DEFINED2,"User-defined parameter 2",Device specific
AlarmAttributes,parameter,32,17,4,enum,63,USER_DEFINED3,"User-defined parameter 3",Device specific
```

### Edge Case 9.3: Implied Values
**When manual shows pattern:**
```
1-16: Harmonic orders
```

**Explicitly list:**
```csv
AlarmAttributes,modifier,32,11,4,enum,1,1,"Harmonic order 1 (fundamental)",Device specific
AlarmAttributes,modifier,32,11,4,enum,2,2,"Harmonic order 2",Device specific
...
AlarmAttributes,modifier,32,11,4,enum,16,16,"Harmonic order 16",Device specific
```

**Don't abbreviate** - explicit is better than implicit

---

## Step 10: Template Files

### Master Template (bitfield_template.csv)
```csv
group,name,total_width,offset,width,type,value,meaning,description,standard
[GROUP],[field],32,[LSB],[bits],enum,[val],[NAME],[Manual text],[IEC/Device specific]
```

### Units Template (units_template.csv)
```csv
code,abbreviation,description
[num],[symbol],[Full name from manual]
```

### DateTime Template (datetime_template.csv)
```csv
group,name,total_width,offset,width,type,value,max,meaning,standard
DataType,DATETIME,64,[LSB],[bits],number,[min],[max],[Component name],IEC 870-5-4
```

---

## Common Mistakes to Avoid

❌ **Don't** assume phases enum is same across vendors
❌ **Don't** skip reserved values if manual mentions them
❌ **Don't** use your own abbreviations - stick to manual's terminology
❌ **Don't** merge multiple enum values into ranges (list them all)
❌ **Don't** forget to check if bits overlap (some registers reuse bits conditionally)

✅ **Do** copy-paste descriptions from manual (for traceability)
✅ **Do** include manual page numbers in commit messages
✅ **Do** test bit extraction math manually
✅ **Do** create one CSV row per enum value
✅ **Do** preserve vendor's exact value names

---

## Transformation Workflow Summary

```
1. Get manual (PDF/HTML) → Section with register maps
2. For each register table:
   a. Extract register name → "group" column
   b. Extract bit fields → "name", "offset", "width"
   c. Extract enum values → separate rows per value
   d. Copy descriptions verbatim → "description" column
   e. Identify standard → "standard" column
3. Self-validate with checklist
4. Commit with manual reference: "Add PM5110 AlarmAttributes (Manual v2.3 p.45)"
```

This is a **repeatable process**, not architecture. Any developer can follow these steps to consistently transform any device manual into standardized CSV config files.
