# Expert Recommendation: Modbus Device Register Definitions

## The Real Answer for Your Use Case

After looking at industry standards, here's what experts actually do for **Modbus/industrial power meters**:

---

## Industry Reality Check

### What Schneider, ABB, Siemens Actually Use:

**Schneider Electric:**
- Internal: Custom XML schemas (proprietary)
- Published: PDF manuals + Modbus register tables
- Tool support: PowerLogic SMS software reads XML device profiles

**ABB:**
- Internal: Device Type Manager (DTM) with XML-based device descriptions
- Published: EDS files for CANopen, custom formats for Modbus
- Tool support: DTM libraries for integration

**Siemens:**
- Internal: GSD files (for Profibus), custom XML for Modbus
- Published: PDF documentation
- Tool support: SIMATIC engineering tools

**Key observation:** Large vendors use **custom XML internally** but don't standardize externally.

---

## What Expert Consultants Do

When building integration systems for multiple vendors:

### Approach 1: Minimal XML Schema (Most Common)

**Format:** Simple, domain-specific XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<modbusDevice xmlns="http://yourcompany.com/modbus/schema/v1">
  <metadata>
    <vendor>Schneider Electric</vendor>
    <model>PM5110</model>
    <firmware>2.3.x</firmware>
    <manual>PM5110_User_Manual_v2.3.pdf</manual>
    <manualPage>45</manualPage>
  </metadata>
  
  <registers>
    <register id="alarm_attributes" address="0x4000" type="holding" width="32" access="rw">
      <description>Alarm configuration and status</description>
      
      <bitfield name="type" offset="28" width="4" datatype="enum">
        <description>Alarm type classification</description>
        <enum value="0" name="NONE">No alarm type defined</enum>
        <enum value="1" name="STANDARD1S">Standard 1-second alarm for continuous monitoring</enum>
        <enum value="2" name="CUSTOM1S">Custom 1-second alarm with user-defined parameters</enum>
        <enum value="5" name="DISTURBANCE">Power quality disturbance alarm</enum>
      </bitfield>
      
      <bitfield name="parameter" offset="17" width="4" datatype="enum">
        <description>Measurement parameter being monitored</description>
        <enum value="0" name="NONE">No parameter specified</enum>
        <enum value="1" name="VOLTAGE" unit="V">Voltage measurement parameter</enum>
        <enum value="2" name="CURRENT" unit="A">Current measurement parameter</enum>
        <enum value="6" name="FREQUENCY" unit="Hz">Frequency parameter</enum>
      </bitfield>
      
      <bitfield name="phases" offset="7" width="4" datatype="enum">
        <description>Phase selection</description>
        <enum value="0" name="NONE">No phase specified</enum>
        <enum value="1" name="A">Phase A only</enum>
        <enum value="7" name="ABC">All three phases (A-B-C)</enum>
      </bitfield>
      
      <bitfield name="enable" offset="0" width="1" datatype="boolean">
        <description>Alarm enable/disable</description>
        <value bit="0" name="DISABLED">Alarm disabled (not active)</value>
        <value bit="1" name="ENABLED">Alarm enabled (active)</value>
      </bitfield>
    </register>
    
    <register id="event_code" address="0x2000" type="holding" width="16" access="ro">
      <description>Event classification and metadata</description>
      
      <bitfield name="category" offset="12" width="4" datatype="enum">
        <enum value="15" name="ALARM_EVENT">Alarm event category</enum>
      </bitfield>
      
      <bitfield name="event_type" offset="8" width="4" datatype="enum">
        <enum value="2" name="PICKUP">Alarm condition detected (pickup)</enum>
        <enum value="3" name="DROPOUT">Alarm condition cleared (dropout)</enum>
      </bitfield>
      
      <bitfield name="phases" offset="4" width="4" datatype="enum" ref="alarm_attributes.phases">
        <description>References same phase enum as alarm_attributes</description>
      </bitfield>
    </register>
  </registers>
  
  <units>
    <unit code="5" symbol="Hz" name="Hertz" category="frequency"/>
    <unit code="6" symbol="A" name="Amperes" category="current"/>
    <unit code="8" symbol="V" name="Volts" category="voltage"/>
  </units>
</modbusDevice>
```

**Why this works:**
- ✅ Hierarchical: device → register → bitfield → enum
- ✅ Self-documenting: descriptions inline
- ✅ Reusable: Can reference enums across registers
- ✅ Standard XML: Any language can parse
- ✅ Extensible: Add attributes without breaking parsers
- ✅ Validatable: XSD schema can enforce structure

**Tools needed:**
- XML parser (built into every language)
- Simple code generator (300 lines of Python)
- XSD validator (optional but recommended)

---

### Approach 2: JSON (Web-First Projects)

**Format:** JSON with consistent structure

```json
{
  "device": {
    "vendor": "Schneider Electric",
    "model": "PM5110",
    "firmware": "2.3.x"
  },
  "registers": {
    "alarm_attributes": {
      "address": "0x4000",
      "type": "holding",
      "width": 32,
      "access": "rw",
      "description": "Alarm configuration and status",
      "fields": {
        "type": {
          "offset": 28,
          "width": 4,
          "datatype": "enum",
          "description": "Alarm type classification",
          "values": {
            "0": {"name": "NONE", "description": "No alarm type defined"},
            "1": {"name": "STANDARD1S", "description": "Standard 1-second alarm"},
            "5": {"name": "DISTURBANCE", "description": "Power quality disturbance"}
          }
        },
        "parameter": {
          "offset": 17,
          "width": 4,
          "datatype": "enum",
          "values": {
            "0": {"name": "NONE", "description": "No parameter"},
            "1": {"name": "VOLTAGE", "unit": "V", "description": "Voltage measurement"},
            "2": {"name": "CURRENT", "unit": "A", "description": "Current measurement"}
          }
        },
        "enable": {
          "offset": 0,
          "width": 1,
          "datatype": "boolean",
          "values": {
            "0": {"name": "DISABLED"},
            "1": {"name": "ENABLED"}
          }
        }
      }
    }
  },
  "units": {
    "5": {"symbol": "Hz", "name": "Hertz"},
    "6": {"symbol": "A", "name": "Amperes"},
    "8": {"symbol": "V", "name": "Volts"}
  }
}
```

**Why this works:**
- ✅ Native to JavaScript/Python/Go
- ✅ No parsing libraries needed
- ✅ Human-readable
- ✅ Easy to edit
- ✅ JSON Schema for validation

---

### Approach 3: TOML (Emerging Preference)

**Format:** TOML (Tom's Obvious Minimal Language)

```toml
[device]
vendor = "Schneider Electric"
model = "PM5110"
firmware = "2.3.x"

[registers.alarm_attributes]
address = "0x4000"
type = "holding"
width = 32
access = "rw"
description = "Alarm configuration and status"

[registers.alarm_attributes.fields.type]
offset = 28
width = 4
datatype = "enum"
description = "Alarm type classification"

[[registers.alarm_attributes.fields.type.values]]
code = 0
name = "NONE"
description = "No alarm type defined"

[[registers.alarm_attributes.fields.type.values]]
code = 1
name = "STANDARD1S"
description = "Standard 1-second alarm"

[registers.alarm_attributes.fields.enable]
offset = 0
width = 1
datatype = "boolean"

[[registers.alarm_attributes.fields.enable.values]]
bit = 0
name = "DISABLED"

[[registers.alarm_attributes.fields.enable.values]]
bit = 1
name = "ENABLED"

[units.5]
symbol = "Hz"
name = "Hertz"

[units.6]
symbol = "A"
name = "Amperes"
```

**Why experts increasingly prefer TOML:**
- ✅ More readable than JSON (no quotes everywhere)
- ✅ More concise than XML
- ✅ Better for hierarchical config than CSV
- ✅ Native support in Rust, Python, Go
- ✅ Comments allowed

---

## The Practical Expert Decision Tree

```
START: What's your primary consumer?

├─ Embedded C/C++ firmware?
│  ├─ ARM Cortex? → Use CMSIS-SVD
│  └─ Other MCU? → Custom XML + code gen
│
├─ Web/cloud application?
│  └─ Use JSON (with JSON Schema validation)
│
├─ Python-heavy data processing?
│  └─ Use TOML or JSON
│
├─ Multi-language (Python + C++ + JavaScript)?
│  └─ Use XML + code generators for each language
│
└─ Legacy system integration?
   └─ Whatever format they already use (probably custom)
```

---

## What I'd Actually Build (Expert Opinion)

**For Modbus device integration at a company:**

### File Structure:
```
device-definitions/
├── schema/
│   └── modbus-device.xsd          # XML Schema for validation
├── devices/
│   ├── schneider/
│   │   ├── pm5110.xml             # Device definition
│   │   └── pm5350.xml
│   ├── abb/
│   │   └── m2m.xml
│   └── siemens/
│       └── pac3200.xml
├── codegen/
│   ├── generate_python.py         # Generate Python decoder
│   ├── generate_cpp.py             # Generate C++ headers
│   ├── generate_docs.py            # Generate HTML docs
│   └── templates/
│       ├── python_class.jinja2
│       ├── cpp_header.jinja2
│       └── doc_template.html
├── output/                         # Generated files (gitignored)
│   ├── python/
│   │   ├── pm5110.py
│   │   └── m2m.py
│   ├── cpp/
│   │   ├── pm5110.h
│   │   └── m2m.h
│   └── docs/
│       ├── pm5110.html
│       └── m2m.html
└── tools/
    ├── validate.py                 # Validate XML against XSD
    └── convert_csv_to_xml.py       # Migrate existing CSV files
```

### Workflow:
```bash
# 1. Developer creates XML device definition
vim devices/schneider/pm5110.xml

# 2. Validate it
python tools/validate.py devices/schneider/pm5110.xml

# 3. Generate all outputs
python codegen/generate_python.py --all
python codegen/generate_cpp.py --all
python codegen/generate_docs.py --all

# 4. Commit ONLY the XML (output is generated)
git add devices/schneider/pm5110.xml
git commit -m "Add PM5110 device definition"

# 5. CI/CD regenerates outputs on merge
```

### Key Principle:
**Source of truth:** XML device definitions  
**Deliverables:** Generated code + docs  
**Never edit:** Generated files (regenerate instead)

---

## Why XML Over JSON/TOML for This Case

**XML advantages:**
1. **Attributes + content** (clean for metadata)
   ```xml
   <enum value="1" name="STANDARD1S">Standard 1-second alarm</enum>
   ```
   vs JSON:
   ```json
   {"value": 1, "name": "STANDARD1S", "description": "Standard 1-second alarm"}
   ```

2. **Schema validation** (XSD is mature)
3. **References and linking** (`ref="alarm_attributes.phases"`)
4. **Namespace support** (mix multiple schemas)
5. **Tool ecosystem** (XSLT, XPath, etc.)

**JSON advantages:**
1. **Web native** (parse directly in browser)
2. **Simpler syntax** (no closing tags)
3. **Better for REST APIs**

**TOML advantages:**
1. **Most human-readable**
2. **Config-file focused**
3. **Comments supported**

---

## My Expert Recommendation

**For your Modbus device case:**

### Use: **XML with this structure**

**Reasons:**
1. Hierarchical data fits naturally (device → register → field → enum)
2. XSD validation catches errors before deployment
3. Mature tooling (every language has XML parsers)
4. Can evolve schema without breaking existing files
5. Industry precedent (CMSIS-SVD, IP-XACT use XML)

**Don't use CSV because:**
- ❌ No hierarchy (flat structure forces repetition)
- ❌ No validation (typos break parsers)
- ❌ No references (can't reuse enum definitions)
- ❌ Poor for nested structures (register → field → enum)

**If you really hate XML:**
- Use JSON with JSON Schema validation
- Or use TOML for human readability

**Never invent a custom format** - pick XML, JSON, or TOML and stick to it.

---

## Validation is Critical

**XSD Schema Example:**
```xml
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="modbusDevice">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="metadata" type="MetadataType"/>
        <xs:element name="registers" type="RegistersType"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
  
  <xs:complexType name="BitfieldType">
    <xs:sequence>
      <xs:element name="description" type="xs:string"/>
      <xs:element name="enum" maxOccurs="unbounded" minOccurs="0">
        <xs:complexType>
          <xs:simpleContent>
            <xs:extension base="xs:string">
              <xs:attribute name="value" type="xs:integer" use="required"/>
              <xs:attribute name="name" type="xs:string" use="required"/>
            </xs:extension>
          </xs:simpleContent>
        </xs:complexType>
      </xs:element>
    </xs:sequence>
    <xs:attribute name="name" type="xs:string" use="required"/>
    <xs:attribute name="offset" type="xs:integer" use="required"/>
    <xs:attribute name="width" type="xs:integer" use="required"/>
  </xs:complexType>
</xs:schema>
```

This catches errors like:
- Missing required attributes
- Invalid bit offsets
- Type mismatches
- Duplicate enum values

---

## Summary: The Expert Way

1. **Format:** XML (or JSON if web-focused, TOML if config-focused)
2. **Structure:** Hierarchical (device → register → field → enum)
3. **Validation:** XSD/JSON Schema (catch errors early)
4. **Tooling:** Code generators (one XML → many outputs)
5. **Workflow:** XML is source, everything else is generated
6. **Version control:** Track XML only, regenerate outputs

**The pattern:** Device description → Code generation → Runtime usage

This is how experts at ARM, Intel, Linux kernel, and industrial automation companies actually do it.
