# Template Filling Guide: Step-by-Step Instructions

> **For:** Anyone filling CSV templates (no programming experience needed)  
> **Prerequisites:** Can use Excel or Google Sheets  
> **Time to Learn:** 1-2 hours with examples

---

## 📚 Quick Navigation

**Choose your task:**
- [I'm defining a new datatype](#task-1-define-new-datatype) (from device manual)
- [I'm mapping device registers](#task-2-map-device-registers) (pointing to datatypes)
- [I'm setting up UNS paths](#task-3-configure-uns-paths) (where data goes)
- [I'm troubleshooting errors](#troubleshooting-common-mistakes)

---

## 🎯 Overview: The Five Templates

```
Template 1: Structure      → "What are the bits?"
Template 2: Validation     → "What's valid?"
Template 3: Enums          → "What do codes mean?"
Template 4: Register Map   → "Which register uses what?"
Template 5: UNS Mapping    → "Where does data go?"
```

**Most common workflow:**
1. Fill Templates 1-3 ONCE per datatype (e.g., DATETIME)
2. Fill Template 4 for EVERY register (points to datatypes)
3. Fill Template 5 for routing (optional, for UNS integration)

---

## 📋 Task 1: Define New Datatype

### When to Do This

**Do this when:** Device manual shows a datatype you've never seen before

**Skip this if:** Datatype already exists (check existing templates first!)

**Example:** Manual shows "DATETIME (IEC 870-5-4)" and it's not in templates yet

### Step-by-Step Process

#### Step 1.1: Open Device Manual

Find the section describing the register structure.

**Example from manual:**
```
DATETIME Register (64-bit, 4 words)
Standard: IEC 870-5-4

Word 1 (16 bits):
  Bits 0-6:   Year (0-127, offset +2000)
  Bits 7-15:  Reserved

Word 2 (16 bits):
  Bits 0-4:   Day (1-31)
  Bits 5-7:   Weekday (1=Mon, 7=Sun, 0=unused)
  Bits 8-11:  Month (1-12)
  Bits 12-15: Reserved

Word 3 (16 bits):
  Bits 0-5:   Minutes (0-59)
  Bit 6:      Reserved
  Bit 7:      Time sync (0=valid, 1=invalid)
  Bits 8-12:  Hour (0-23)
  Bits 13-14: Reserved
  Bit 15:     DST (0=standard, 1=daylight)

Word 4 (16 bits):
  Bits 0-15:  Milliseconds (0-59999)
```

#### Step 1.2: Fill Template 1 (Structure)

**Open:** `1_datatype_structure.csv` in Excel

**Columns to fill:**

| Column | What to Write | Example |
|--------|---------------|---------|
| datatype | Name for this type | DATETIME |
| field_name | Field name from manual | year |
| bit_start | First bit position | 0 |
| bit_end | Last bit position | 6 |
| value_type | number/enum/flag/reserved | number |
| offset | Add this to value | 2000 |
| scale | Multiply value by this | 1 |
| unit | Unit of measurement | year |
| description | Copy from manual | Year (0-127, offset +2000) |

**Filled example:**

```csv
datatype,field_name,bit_start,bit_end,value_type,offset,scale,unit,description
DATETIME,year,0,6,number,2000,1,year,Year (0-127) add 2000
DATETIME,reserved_1,7,15,reserved,0,1,,Reserved bits - do not use
DATETIME,day,16,20,number,0,1,day,Day of month (1-31)
DATETIME,weekday,21,23,enum,0,1,,Day of week (see enum table)
DATETIME,month,24,27,number,0,1,month,Month (1=Jan to 12=Dec)
DATETIME,reserved_2,28,31,reserved,0,1,,Reserved bits
DATETIME,minute,32,37,number,0,1,minute,Minutes (0-59)
DATETIME,reserved_3,38,38,reserved,0,1,,Single reserved bit
DATETIME,time_sync_invalid,39,39,flag,0,1,,Time sync status (0=valid 1=invalid)
DATETIME,hour,40,44,number,0,1,hour,Hour (0-23)
DATETIME,reserved_4,45,46,reserved,0,1,,Reserved bits
DATETIME,dst_active,47,47,flag,0,1,,Daylight saving (0=standard 1=DST)
DATETIME,millisecond,48,63,number,0,1,ms,Milliseconds (0-59999)
```

**Tips:**
- ✅ **Bit numbering:** Count from 0 (rightmost bit)
- ✅ **Reserved bits:** Always mark them! Don't skip
- ✅ **Value types:**
  - `number` = Numeric value (temperature, voltage, etc.)
  - `enum` = Code with meanings (1=Monday, 2=Tuesday)
  - `flag` = On/off, yes/no, 0/1
  - `reserved` = Unused bits
- ✅ **Offset:** If manual says "add 2000", put 2000
- ✅ **Scale:** If manual says "multiply by 0.1", put 0.1

#### Step 1.3: Fill Template 2 (Validation)

**Open:** `2_datatype_validation.csv` in Excel

**For each NUMBER or ENUM field, add validation:**

```csv
datatype,field_name,min_value,max_value,required,health_level,notes
DATETIME,year,0,127,yes,critical,Year must be 0-127
DATETIME,day,1,31,yes,critical,Day must be 1-31
DATETIME,weekday,0,7,no,optional,0 is acceptable (not used)
DATETIME,month,1,12,yes,critical,Must be valid month
DATETIME,minute,0,59,yes,mandatory,Standard minute range
DATETIME,hour,0,23,yes,mandatory,24-hour format
DATETIME,millisecond,0,59999,yes,mandatory,Includes seconds
```

**Tips:**
- ✅ **Min/max:** From manual's "valid range" section
- ✅ **Required:**
  - `yes` = Must have valid value
  - `no` = Can be anything (like weekday=0)
- ✅ **Health level:**
  - `critical` = System fails if invalid
  - `mandatory` = Should be valid
  - `warning` = Nice to have
  - `optional` = Doesn't matter

#### Step 1.4: Fill Template 3 (Enums)

**Open:** `3_datatype_enum_values.csv` in Excel

**For each ENUM or FLAG field, list all possible values:**

```csv
datatype,field_name,value,label,severity,description,action
DATETIME,weekday,0,Not Used,info,Weekday not specified,none
DATETIME,weekday,1,Monday,info,First day of week,none
DATETIME,weekday,2,Tuesday,info,Second day of week,none
DATETIME,weekday,3,Wednesday,info,Third day of week,none
DATETIME,weekday,4,Thursday,info,Fourth day of week,none
DATETIME,weekday,5,Friday,info,Fifth day of week,none
DATETIME,weekday,6,Saturday,info,Sixth day of week,none
DATETIME,weekday,7,Sunday,info,Seventh day of week,none
DATETIME,time_sync_invalid,0,Time Valid,info,Clock synchronized,none
DATETIME,time_sync_invalid,1,Time Invalid,warning,Clock not synchronized,check_time_source
DATETIME,dst_active,0,Standard Time,info,Standard time active,none
DATETIME,dst_active,1,Daylight Saving,info,DST currently active,none
```

**Tips:**
- ✅ **Value:** The numeric code from manual
- ✅ **Label:** Short, clear description
- ✅ **Severity:**
  - `info` = Normal, no action needed
  - `warning` = Pay attention
  - `critical` = Urgent, take action
- ✅ **Action:** What operator should do
  - `none` = Nothing
  - `check_sensor` = Verify sensor
  - `alert_operator` = Notify someone

#### Step 1.5: Verify Your Work

**Checklist:**

- [ ] All bits accounted for (0 to 63 for 64-bit)
- [ ] No gaps except documented reserved bits
- [ ] No overlapping bit positions
- [ ] All enum values from manual included
- [ ] Min/max values match manual
- [ ] Descriptions clear and accurate

**Test:** Ask yourself:
- "If I read this in 6 months, will I understand it?"
- "Can someone else use this without asking me?"

---

## 📋 Task 2: Map Device Registers

### When to Do This

**Do this when:** Adding ANY new device or register

**Every time you:** Install equipment, commission device, integrate sensor

**This is:** The most common task (you'll do this a lot!)

### Step-by-Step Process

#### Step 2.1: Gather Information

**From device manual, find:**

```
✓ Device model name
✓ Register address (Modbus address)
✓ What this register contains (datatype)
✓ Number of words (16-bit registers)
✓ Read/write access
✓ What it's used for (description)
```

**Example from PM8000 manual:**

```
Register: 132-135 (4 consecutive registers)
Description: Date of Manufacture
Type: DATETIME
Size: 4 words (64-bit)
Access: Read-only
Standard: IEC 870-5-4
```

#### Step 2.2: Check if Datatype Exists

**Before filling Template 4:**

1. Open Templates 1-3
2. Search for datatype name (e.g., "DATETIME")
3. If found → Continue to Step 2.3
4. If NOT found → Go back to Task 1 (define new datatype)

#### Step 2.3: Fill Template 4 (Register Map)

**Open:** `4_register_map.csv` in Excel

**Fill ONE row per register:**

```csv
device_model,register_address,register_name,datatype,word_count,access,category,description,manual_page
PM8000,132,manufacturing_date,DATETIME,4,R,Manufacturing,Date device was manufactured,p.45
PM8000,200,last_calibration_date,DATETIME,4,R,Calibration,Last calibration timestamp,p.52
PM8000,500,system_time,DATETIME,4,RW,System,Current system date/time,p.67
PM8000,8000,alarm_config_1,AlarmAttributes,2,RW,Alarms,Alarm 1 configuration,p.150
PM8000,8002,alarm_config_2,AlarmAttributes,2,RW,Alarms,Alarm 2 configuration,p.150
```

**Column guide:**

| Column | What to Write | Example |
|--------|---------------|---------|
| device_model | Exact model number | PM8000 |
| register_address | Modbus starting address | 132 |
| register_name | Descriptive name (no spaces!) | manufacturing_date |
| datatype | Match Template 1 exactly | DATETIME |
| word_count | Number of 16-bit words | 4 |
| access | R, W, or RW | R |
| category | Logical grouping | Manufacturing |
| description | What is this for? | Date device was manufactured |
| manual_page | Where you found this | p.45 |

**Important notes:**

- ✅ **register_name:** Use underscores, not spaces
- ✅ **datatype:** Must match Templates 1-3 EXACTLY (case-sensitive!)
- ✅ **word_count:** Calculate from manual:
  - 16-bit = 1 word
  - 32-bit = 2 words
  - 64-bit = 4 words
- ✅ **access:**
  - `R` = Read-only (can only read)
  - `W` = Write-only (can only write)
  - `RW` = Read-write (both)

#### Step 2.4: Real Example Walkthrough

**Manual page says:**

```
Register 500-501: Temperature Sensor Reading
Type: INT16 with decimal scaling
Size: 32-bit (2 registers)
Range: -40.0°C to +125.0°C
Scaling: Value × 0.1
Access: Read-only
```

**First, check:** Is there a "Temperature" datatype?
- If YES → Use it
- If NO → Create it in Templates 1-3 first

**Assuming it exists, fill:**

```csv
device_model,register_address,register_name,datatype,word_count,access,category,description
PM8000,500,ambient_temperature,Temperature,2,R,Measurements,Ambient temp sensor
```

**Done!** That's all you need for this register.

---

## 📋 Task 3: Configure UNS Paths

### When to Do This

**Do this when:** Setting up Unified Namespace integration

**Skip this if:** Not using UNS / only using local SCADA

**This is:** Advanced topic, optional for basic setups

### The Decision Tree Approach

Template 5 uses a questionnaire to suggest the right namespace path.

#### Step 3.1: Answer Questions for Each Register

**Open:** `5_uns_namespace_mapping.csv` in Excel

**For register 132 (manufacturing_date), answer:**

```
Q1: Is this ABOUT, FROM, or TO the device?
    Answer: ABOUT (it's metadata about the device itself)

Q2: Does it change?
    Answer: FIXED (never changes after manufacturing)

Q3: Is it observed or commanded?
    Answer: N/A (not a control point)

Q4: What kind of data?
    Answer: AUDIT (for traceability, compliance)
```

**Fill the row:**

```csv
register_name,register_address,Q1_about_or_from,Q2_fixed_or_changes,Q3_observed_or_commanded,Q4_process_or_device,recommended_namespace,final_uns_path
manufacturing_date,132,ABOUT,FIXED,N/A,AUDIT,asset,asset/PM8000_001/metadata/manufacturing_date
```

#### Step 3.2: Common Patterns

**Pattern 1: Device Identity**
```csv
serial_number,100,ABOUT,FIXED,N/A,IDENTITY,asset,asset/{device_id}/identity/serial_number
model_number,102,ABOUT,FIXED,N/A,IDENTITY,asset,asset/{device_id}/identity/model
firmware_version,104,ABOUT,RARELY,N/A,PARAMETER,asset,asset/{device_id}/identity/firmware
```

**Pattern 2: Live Measurements**
```csv
temperature,500,FROM,CONTINUOUS,OBSERVED,PROCESS,measurement,measurement/{device_id}/temperature
voltage_l1,600,FROM,CONTINUOUS,OBSERVED,PROCESS,measurement,measurement/{device_id}/voltage/l1
current_l1,700,FROM,CONTINUOUS,OBSERVED,PROCESS,measurement,measurement/{device_id}/current/l1
```

**Pattern 3: Alarms**
```csv
alarm_1,8000,FROM,EVENT,OBSERVED,EXCEPTION,alarm,alarm/{device_id}/high_voltage
alarm_2,8002,FROM,EVENT,OBSERVED,EXCEPTION,alarm,alarm/{device_id}/overcurrent
```

**Pattern 4: Control/Commands**
```csv
setpoint_temp,2000,TO,RARELY,COMMANDED,SETPOINT,command,command/{device_id}/setpoint/temperature
start_command,2100,TO,EVENT,COMMANDED,ACTION,command,command/{device_id}/control/start
```

#### Step 3.3: Use the Checklist

**Full column guide:**

| Question | Options | Meaning |
|----------|---------|---------|
| **Q1: About/From/To** | ABOUT | Metadata about device |
|  | FROM | Data produced by device |
|  | TO | Commands sent to device |
| **Q2: Changes** | FIXED | Never changes |
|  | RARELY | Occasional updates |
|  | CONTINUOUS | Constant updates |
|  | EVENT | Triggered by condition |
| **Q3: Observed/Commanded** | OBSERVED | Read-only |
|  | COMMANDED | Writable |
|  | BOTH | Read and write |
| **Q4: Kind** | PROCESS | Production process data |
|  | DEVICE | Internal device state |
|  | EXCEPTION | Abnormal condition |
|  | AUDIT | Compliance/tracking |

---

## 🐛 Troubleshooting Common Mistakes

### Error 1: "DataType Not Found"

**Symptom:**
```
Error: DataType 'DATETIME' not found for register 132
```

**Cause:** Typo in Template 4 or datatype not defined

**Fix:**
1. Open Template 4 (`4_register_map.csv`)
2. Find the row with error
3. Check `datatype` column: Is it spelled EXACTLY like Template 1?
   - ❌ Wrong: "datetime", "DateTime", "DATE TIME"
   - ✅ Right: "DATETIME"
4. If spelling is correct, check Template 1 - is DATETIME defined there?

### Error 2: "Bit Overlap Detected"

**Symptom:**
```
Error: Bit 16 used by both 'day' and 'month' in DATETIME
```

**Cause:** Two fields claim the same bits

**Fix:**
1. Open Template 1
2. Find both fields mentioned in error
3. Check bit_start and bit_end
4. Verify against manual (manual is always right!)
5. Correct the wrong field

**Example of overlap:**
```csv
# WRONG (bit 20 used twice!)
field_name,bit_start,bit_end
day,16,20
month,20,23

# CORRECT
field_name,bit_start,bit_end
day,16,20
month,21,23
```

### Error 3: "Validation Failed: Value Out of Range"

**Symptom:**
```
month: Value 13 exceeds maximum 12
Health: BAD
```

**Cause 1:** Device is sending bad data (device problem)
**Cause 2:** Wrong offset/scale in Template 1

**Fix for Cause 1:**
1. Check device display - is it showing valid data?
2. If device shows correct → Check Modbus settings
3. If device shows wrong → Device fault, contact vendor

**Fix for Cause 2:**
1. Open Template 1
2. Find the field (e.g., "month")
3. Check `offset` and `scale` columns
4. Verify against manual
5. If manual says "no offset", put 0
6. If manual says "multiply by 0.1", put scale=0.1

### Error 4: "Gap in Bit Coverage"

**Symptom:**
```
Warning: Bits 7-15 not assigned in DATETIME
```

**Cause:** Forgot to mark reserved bits

**Fix:**
1. Open Template 1
2. Add row for missing bits:
```csv
datatype,field_name,bit_start,bit_end,value_type
DATETIME,reserved_1,7,15,reserved
```

### Error 5: "Enum Value Not Defined"

**Symptom:**
```
weekday: Value 8 not found in enum table
Displayed as: "UNKNOWN (8)"
```

**Cause:** Device sent code not in Template 3

**Fix:**
1. Is value 8 documented in manual?
2. If YES → Add to Template 3:
```csv
datatype,field_name,value,label
DATETIME,weekday,8,Reserved
```
3. If NO → Device error or undocumented code
4. Document as "UNDOCUMENTED" and report to vendor

---

## ✅ Quality Checklist

### Before Submitting Templates

**For Templates 1-3 (Datatype Definition):**

- [ ] All bit positions from 0 to (total_width-1) accounted for
- [ ] No overlapping bits
- [ ] Reserved bits explicitly marked
- [ ] All fields have descriptions
- [ ] All enum values from manual included
- [ ] Validation min/max match manual
- [ ] Tested with sample data

**For Template 4 (Register Map):**

- [ ] Device model matches actual hardware
- [ ] Register addresses from manual
- [ ] Datatype names match Template 1 exactly
- [ ] Word count calculated correctly
- [ ] Access permissions (R/W/RW) correct
- [ ] Descriptions clear and useful
- [ ] Manual page numbers noted

**For Template 5 (UNS Mapping):**

- [ ] All questions answered
- [ ] Namespace makes sense for data type
- [ ] Paths follow naming convention
- [ ] No duplicate paths

---

## 📞 Getting Help

### Who to Ask

**Template filling questions:**
- Your supervisor or lead engineer
- Training coordinator
- Documentation in this guide

**Device manual interpretation:**
- Senior field engineer
- Vendor technical support
- Engineering team

**System errors:**
- IT support desk
- System administrator
- GitHub issues (if open source)

### How to Report Issues

**Good bug report:**

```
Title: "Validation error on PM8000 temperature reading"

Details:
- Device: PM8000, Serial PM8K-2024-0157
- Register: 500 (temperature)
- Error: "Value 235 exceeds maximum 125"
- Expected: Temperature should be in °C
- Screenshot: [attached]
- Template version: 1.0.0
- Date: 2025-01-11
```

**Bad bug report:**

```
Title: "It doesn't work"

Details: Temperature is wrong
```

---

## 🎓 Practice Exercise

### Exercise 1: Define Simple Status Word

**Manual says:**

```
StatusWord (16-bit register at address 100)

Bit 0: Running (0=stopped, 1=running)
Bit 1: Fault (0=no fault, 1=fault active)
Bits 2-3: Mode
  00 = Manual
  01 = Automatic
  10 = Maintenance
  11 = Reserved
Bits 4-15: Reserved
```

**Your task:** Fill Templates 1-3 for StatusWord

<details>
<summary>Click to see answer</summary>

**Template 1: Structure**
```csv
datatype,field_name,bit_start,bit_end,value_type,offset,scale,unit,description
StatusWord,running,0,0,flag,0,1,,Running status
StatusWord,fault,1,1,flag,0,1,,Fault status
StatusWord,mode,2,3,enum,0,1,,Operating mode
StatusWord,reserved,4,15,reserved,0,1,,Reserved bits
```

**Template 2: Validation**
```csv
datatype,field_name,min_value,max_value,required,health_level
StatusWord,running,0,1,yes,mandatory
StatusWord,fault,0,1,yes,critical
StatusWord,mode,0,3,yes,mandatory
```

**Template 3: Enums**
```csv
datatype,field_name,value,label,severity
StatusWord,running,0,STOPPED,info
StatusWord,running,1,RUNNING,info
StatusWord,fault,0,NO_FAULT,info
StatusWord,fault,1,FAULT,critical
StatusWord,mode,0,Manual,info
StatusWord,mode,1,Automatic,info
StatusWord,mode,2,Maintenance,warning
StatusWord,mode,3,Reserved,info
```
</details>

---

**You're ready!** Start with a simple register and work your way up. It gets easier with practice.

**Version:** 1.0.0  
**For:** Template Fillers  
**Last Updated:** 2025-01-11