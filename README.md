# Device Manuals to UNS

Template + Python utilities to convert chaotic industrial device manuals (PDF, XLS, screenshots) into machine-readable manifests, map Modbus/alarm/energy signals into a Unified Namespace (UNS), and generate Ignition-ready OPC tags. Designed with full Standards Compliance: ISO-9001 traceability, ISO-50001 energy-data protection, ISA-95 level discipline, and ISA-18.2 alarm rules enforcement.

---

## 🚧 Problem

Industrial device data is trapped in:

* PDFs
* mixed tables
* undocumented register behavior
* vendor-specific alarm naming
* inconsistent scaling, endian, units

→ Engineers waste **weeks** manually mapping tags and guessing alarm logic.

---

## 🎯 What This Repo Delivers

### A **template + Python utilities** that:

| Output               | Description                                                 |
| -------------------- | ----------------------------------------------------------- |
| Manifest JSON        | Digital twin of a device’s registers, alarms, metadata      |
| Modbus Map Extractor | Extracts addr/len/datatype/unit/scale/endian from manuals   |
| UNS Mapper           | Generates Sparkplug-style hierarchical tag paths            |
| Ignition Export      | `.json` tag imports for Ignition Designer (Modbus + OPC-UA) |
| Alarm Matrix         | ISA-18.2 lifecycle enforced from manifest                   |
| Energy Security      | ISO-50001 masking rules applied on sensitive energy data    |
| Audit Trail          | ISO-9001 traceability metadata                              |

---

## 📦 Why This Changes the Game

- Instead of retyping PM5110 or VarPlus VC registers every project → 
**build once → reuse forever** and can be used as a version manager for firmware updates

- This repo = standard library + automation →
SCADA/UNS rollout drops from **months → days → hours**.

- This repo = Standards Compliance (Built-In)

  * [x] ISO-9001 → Traceability ensured
  * [x] ISO-50001 → Energy data protected
  * [x] ISA-95 → Level discipline maintained
  * [x] ISA-18.2 → Alarm philosophy and lifecycle enforced
  * [ ] 
---

## 🔍 Pipeline Architecture Overview

> Approach: Multi-Layer Data Processing Pipeline

### Pipeline 1: Device Custom Data Types Decoder (Data Flow for device custom data types decoder)

- Raw Manual Data (human input)
- Template 1 - Structure Definition [1]
- Template 2 - Validation Ranges [1]
- Template 3 - Transformation [1]
- Template 4 - Value Semantics
- Rule Engine - Compiled Rules
- Runtime Decoder
- Output: JSON with health status

Notes:
* 1 (provided by toolkit and filled by human or LLM and reviewed) `one time per device.` can be versioned for firmware updates

```text
Layer 1: Raw Manual Data (Human Input)
    ↓
Layer 2: Template 1 - Structure Definition (Human/LLM + Review)
    ↓
Layer 3: Template 2 - Validation Ranges (Human/LLM + Review)
    ↓
Layer 4: Template 3 - transformation (Human/LLM + Review)
    ↓
Layer 5: Template 4 - Value Semantics (Human/LLM + Review)
    ↓
Layer 6: Rule Engine - Compiled Rules (Code Generated)
    ↓
Layer 7: Runtime Decoder - Live Data Processing
    ↓
Output: Structured JSON with Health Status
```


### Pipeline 2: Device Register Mapping to UNS

- Raw Register Mapping (manual data)
- Template 5 - Register Mapping to custom data types [1]
- Template 6 - Checklist for UNS namespace mapping (with questions Q1-Q4) [1]
- UNS path generation
- Export to Ignition Gateway CSV (Modbus tags)
- Export to Ignition Designer JSON
- Export to Python edge device JSON (OPC-UA/MQTT)

---

### Example: raw input: from manuals

```text
# "DateTime coding format using 4 words as per IEC 870-5-4

Word 1
   b0-b6: Year (0 - 127)
   b7-b15: Reserved
Word 2
   b0-b4: Day (1-31)
   b5-b7: Weekday (1-7, 0 if not used)
   b8-b11: Month (1-12)
   b12-b15: Reserved
Word 3
   b0-b5: Minutes (0-59)
   b6: Reserved
   b7: Time synchronization quality, 1 = non valid or non synchronization
   b8-b12: Hour (0-23)
   b13-b14: Reserved
   b15: 0 = Standard time, 1 = Daylight Savings Time
Word 4
   b0-b15: Millisecond (0 - 59999)
```


---

### 📑 Template 1 - `1_datatype_structure.csv`

#### Column Definition

##### Example 
```csv
datatype,field_name,bit_start,bit_end,value_type,offset,scale,unit,description
DATETIME,year,0,6,number,2000,1,year,Year value (0-127) add 2000
DATETIME,reserved_1,7,15,reserved,0,1,,Reserved bits - do not use
DATETIME,day,16,20,number,0,1,day,Day of month (1-31)
DATETIME,weekday,21,23,enum,0,1,,Day of week (see enum table)
DATETIME,month,24,27,number,0,1,month,Month (1=Jan to 12=Dec)
DATETIME,reserved_2,28,31,reserved,0,1,,Reserved bits - do not use
DATETIME,minute,32,37,number,0,1,minute,Minutes (0-59)
DATETIME,reserved_3,38,38,reserved,0,1,,Single reserved bit
DATETIME,time_sync_invalid,39,39,flag,0,1,,Time sync status flag
DATETIME,hour,40,44,number,0,1,hour,Hour (0-23)
DATETIME,reserved_4,45,46,reserved,0,1,,Reserved bits
DATETIME,dst_active,47,47,flag,0,1,,Daylight saving time flag
DATETIME,millisecond,48,63,number,0,1,ms,Milliseconds (0-59999)
```

**How to fill:**
- Look at manual's bit table
- Copy bit numbers to `bit_start` and `bit_end`
- Choose `value_type`: number, enum, flag, or reserved
- Add `offset` if manual says "add 2000 to value"
- Add `scale` if manual says "multiply by 0.1"

---

### 📑 Template 2

#### Column Definition

```csv
```


---

### 📑 Template 4

#### Column Definition

```csv
```

---

### 📑 Template 5

#### Column Definition

```csv
```

---

### 📑 Template 6

#### Column Definition

```csv
```

---

### 📑 Template 7

#### Column Definition

```csv
```

---



### 📑 Example Device Manifests

**Schneider PM5110 – Energy Meter**

```json

```

**Schneider VarPlus VC – Power Factor Controller**

```json

```

---
## ✅ Production Checklist

### For Each Register Type:

- [ ] **Structure template** filled from manual (bit positions, data types)
- [ ] **Enum values** defined for all enum/flag fields
- [ ] **Validation rules** set (min/max, health checks)
- [ ] **Metadata** recorded (device model, firmware version, Modbus address)
- [ ] **Dependencies** documented (if any fields relate to others)
- [ ] **Test vectors** created (known good/bad examples)
- [ ] **Engineer review** completed (someone verified against device)
- [ ] **Version control** commit (track who/when/why changed)

### Quality Gates:

1. **Completeness**: All bit positions accounted for (no gaps except documented reserved)
2. **Consistency**: Field names match across all templates
3. **Validation**: Rules cover all edge cases from manual
4. **Testability**: Test vectors exist for common and edge cases
5. **Traceability**: Engineer notes reference manual page numbers

---

## 🚀 Workflow Integration Points

### For Electrical Engineer:
1. Open manual to register definition page
2. Fill structure template (bit positions, types)
3. Fill enum template (for any enum/flag fields)
4. Fill validation template (min/max from manual specs)
5. Add engineer notes (manual page refs, quirks found)
6. Submit for review

### For LLM Agent:
1. Receive: PDF manual + blank templates
2. Extract: Bit positions, ranges, enum values
3. Pre-fill: All templates with high confidence
4. Flag: Ambiguous entries for human review
5. Output: Filled templates + confidence scores

### For QA/Validation:
1. Compare generated rules vs. templates (consistency check)
2. Run test vectors through decoder
3. Compare output vs. expected (from manual examples)
4. Verify edge cases (min, max, invalid values)
5. Sign off on config version

### For Production Deployment:
1. Templates → Rule generator → Rules CSV
2. Rules CSV → Python decoder → Runtime
3. Cache compiled rules (JSON) for performance
4. Version-tag deployment (device_v3.2.1_config_v2.1)
5. Monitor decoder health metrics

---

## 💡 Key Insights for Production

### Keep It Simple:
- **One row per field** in structure template (engineer fills once)
- **One row per enum value** in enum template (clear mapping)
- **One row per validation** in validation template (explicit rules)

### Make It Traceable:
- **Engineer notes** column (why decisions were made)
- **Manual page refs** (where info came from)
- **Validation by** (who verified this)
- **Version tracking** (when it changed)

### Enable Automation:
- **Consistent naming** (field names match across templates)
- **Standard formats** (CSV, clear delimiters)
- **No ambiguity** (explicit types, ranges)
- **Machine-parseable** (no free text in critical columns)

### Support Evolution:
- **Reserved bits** (document for future)
- **Firmware versions** (templates per version)
- **Backward compat** (old data still decodable)
- **Migration paths** (v1 → v2 rules)

---


---

### 🤝 Contribute / Get Help

Upload a manual via an Issue →
I’ll help produce a full manifest + Ignition tag file.

---

### 🛣️ Roadmap

* Add drag-drop web UI for PDF ingestion
* Add Sparkplug-B birth metric generator
* OEM certification program

---

### ⭐ Support

Star the repo if you want OEMs to finally publish **machine-readable manuals**.

---

### Implementation Watchouts + Dev Wisdom

* Meaningful example files > empty repo — include **PM5110.json** day one.
* Badge + screenshots → credibility. Add them early.
* Repo name permanence matters — spelling and SEO cannot be fixed later.

---

If you want, I can now:
**→ generate full repo ZIP** with directories, code, and example manifests.
