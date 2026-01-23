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

### 📑 Template 1

#### Column Definition

```csv
```


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
