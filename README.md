# Standardize IoT Device Manuals to UNS

Template + Python utilities to convert chaotic industrial device manuals (PDF, XLS, screenshots) into machine-readable manifests, map Modbus/alarm/energy signals into a Unified Namespace (UNS), and generate Ignition-ready OPC tags. Designed with full Standards Compliance: ISO-9001 traceability, ISO-50001 energy-data protection, ISA-95 level discipline, and ISA-18.2 alarm rules enforcement.

---

### 🚧 Problem

Industrial device data is trapped in:

* PDFs
* mixed tables
* undocumented register behavior
* vendor-specific alarm naming
* inconsistent scaling, endian, units

→ Engineers waste **weeks** manually mapping tags and guessing alarm logic.

---

### 🎯 What This Repo Delivers

A **template + Python utilities** that:

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

### 📦 Why This Changes the Game

Instead of retyping PM5110 or VarPlus VC registers every project →
**build once → reuse forever**.

This repo = standard library + automation →
SCADA/UNS rollout drops from **months → days → hours**.

---

### 📑 Example Device Manifests

**Schneider PM5110 – Energy Meter**

```json

```

**Schneider VarPlus VC – Power Factor Controller**

```json

```

---

### 🧠 Standards Compliance (Built-In)

* [x] ISO-9001 → Traceability ensured
* [x] ISO-50001 → Energy data protected
* [x] ISA-95 → Level discipline maintained
* [x] ISA-18.2 → Alarm philosophy and lifecycle enforced

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
