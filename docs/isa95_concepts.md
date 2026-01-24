# ISA-95 Concepts: Enterprise-Control System Integration

> **Standard:** ANSI/ISA-95 (IEC 62264)  
> **For:** System architects, IT/OT integration teams, MES designers  
> **Reading Time:** 30 minutes

---

## 📑 Table of Contents

1. [What is ISA-95?](#1-what-is-isa-95)
2. [The Five-Level Hierarchy](#2-the-five-level-hierarchy)
3. [Equipment Hierarchy Model](#3-equipment-hierarchy-model)
4. [Our System's ISA-95 Alignment](#4-our-systems-isa-95-alignment)
5. [Template Mapping to ISA-95](#5-template-mapping-to-isa-95)
6. [Practical Implementation](#6-practical-implementation)

---

## 1. What is ISA-95?

### The Simple Explanation

**ISA-95** is like a **universal organization chart** for manufacturing facilities that helps IT systems (ERP, accounting) talk to OT systems (SCADA, PLCs, sensors).

**The Problem It Solves:**
```
IT Department:
"We need production data for the ERP system"

OT Department:
"Here's PLC tag DB45.DBW100"

IT Department:
"What does that mean?!"

ISA-95 provides a common language!
```

### The Official Definition

**ANSI/ISA-95** (International Society of Automation Standard 95) defines:
- Enterprise-control system integration
- Standard terminology and models
- Information exchange between business and manufacturing
- Equipment hierarchy structure

**Also known as:** IEC 62264 (International Electrotechnical Commission)

### Why It Matters for Our System

Our decoder system **implements ISA-95 principles** to:
1. Organize devices in standard hierarchy
2. Use consistent terminology
3. Enable seamless IT/OT integration
4. Support MES/ERP connectivity

---

## 2. The Five-Level Hierarchy

### ISA-95 Functional Hierarchy

```
Level 4: Business Planning & Logistics
         ┌─────────────────────────────┐
         │  ERP, Business Planning     │
         │  (SAP, Oracle, etc.)        │
         └───────────┬─────────────────┘
                     │
                     ↓
Level 3: Manufacturing Operations Management
         ┌─────────────────────────────┐
         │  MES, LIMS, Historian       │
         │  (Production scheduling)    │
         └───────────┬─────────────────┘
                     │
    ─────────────────┼─────────────────  ISA-95 Boundary
                     │                   (Our decoder operates here)
                     ↓
Level 2: Supervisory Control
         ┌─────────────────────────────┐
         │  SCADA, HMI                 │
         │  (Batch control, oversight) │
         └───────────┬─────────────────┘
                     │
                     ↓
Level 1: Basic Control
         ┌─────────────────────────────┐
         │  PLC, DCS                   │
         │  (Process control loops)    │
         └───────────┬─────────────────┘
                     │
                     ↓
Level 0: Physical Process
         ┌─────────────────────────────┐
         │  Sensors, Actuators         │
         │  (The actual equipment)     │
         └─────────────────────────────┘
```

### What Each Level Does

**Level 0: Physical Process**
- **What:** The actual production equipment
- **Examples:** Motors, pumps, valves, sensors, conveyors
- **Data:** Raw sensor signals, actuator positions
- **Our system reads:** Register values from devices at this level

**Level 1: Basic Control**
- **What:** Real-time control and automation
- **Examples:** PLCs, RTUs, smart sensors
- **Data:** Control loops, setpoints, process variables
- **Our system reads:** Modbus registers, OPC-UA nodes

**Level 2: Supervisory Control**
- **What:** Monitoring and supervisory control
- **Examples:** SCADA, HMI, batch management
- **Data:** Aggregated process data, operator interactions
- **Our system publishes to:** SCADA tags, historian

**Level 3: Manufacturing Operations Management**
- **What:** Production workflow and operations
- **Examples:** MES, batch records, quality systems
- **Data:** Production orders, genealogy, quality metrics
- **Our system enables:** MES integration via UNS

**Level 4: Business Planning**
- **What:** Business logistics and planning
- **Examples:** ERP, supply chain, accounting
- **Data:** Orders, inventory, shipping, financials
- **Our system supports:** KPI reporting, energy data for ERP

---

## 3. Equipment Hierarchy Model

### ISA-95 Equipment Model

```
Enterprise
├── Site
│   ├── Area
│   │   ├── Process Cell (Work Center)
│   │   │   ├── Unit
│   │   │   │   ├── Equipment Module
│   │   │   │   │   └── Control Module
```

### Real-World Example

```
Acme Manufacturing (Enterprise)
├── Springfield Plant (Site)
│   ├── Assembly Line 1 (Area)
│   │   ├── Electrical System (Process Cell)
│   │   │   ├── Main Distribution Panel (Unit)
│   │   │   │   ├── PM8000 Power Meter (Equipment Module)
│   │   │   │   │   ├── Voltage Measurement (Control Module)
│   │   │   │   │   ├── Current Measurement (Control Module)
│   │   │   │   │   └── Power Calculation (Control Module)
```

### Equipment Hierarchy Levels Defined

**Enterprise:**
- Entire company or corporation
- May have multiple sites worldwide
- Example: "Acme Manufacturing Inc."

**Site:**
- Physical manufacturing location
- One or more production areas
- Example: "Springfield Plant", "Factory A"

**Area:**
- Collection of equipment for production
- Often a production line or department
- Example: "Assembly Line 1", "Packaging Area"

**Process Cell (Work Center):**
- Logical grouping of equipment
- Produces specific product or performs function
- Example: "Electrical System", "HVAC System", "Filling Station"

**Unit:**
- Collection of equipment modules
- Performs major processing activity
- Example: "Main Distribution Panel", "Tank 101"

**Equipment Module:**
- Individual piece of equipment
- Performs specific function
- Example: "PM8000 Power Meter", "Temperature Sensor"

**Control Module:**
- Functional capability within equipment
- Lowest level of control
- Example: "Voltage Measurement", "PID Loop 1"

---

## 4. Our System's ISA-95 Alignment

### How Our Templates Map to ISA-95

#### Template 4: Register Map → Equipment Module

```csv
device_model,register_address,register_name,category,...
PM8000,500,voltage_l1,Measurements,...

ISA-95 Mapping:
├── Equipment Module: PM8000_001 (the device)
└── Control Module: voltage_l1 (the measurement)
```

#### Template 5: UNS Paths → Equipment Hierarchy

```
UNS Path:
measurement/FactoryA/Line1/Electrical/PM8000_001/voltage/l1

ISA-95 Hierarchy:
├── Site: FactoryA
├── Area: Line1
├── Process Cell: Electrical
├── Unit: (implicit - could be MainFeeder)
├── Equipment Module: PM8000_001
└── Control Module: voltage/l1
```

### ISA-95 Compliant Namespace Structure

**Our standard namespace follows ISA-95:**

```
{namespace}/{site}/{area}/{process_cell}/{equipment}/{parameter}

Examples:
measurement/Springfield/Line1/Electrical/PM8000_001/voltage/l1
         │          │      │        │          │         │
    Namespace    Site   Area   Process Cell  Equip.   Control
                                             Module   Module
```

### Data Flow Aligned to ISA-95

```
Level 0-1: Physical Devices
    ↓ (Modbus/OPC-UA)
Our Decoder System
    ↓ (Validated, decoded data)
Level 2: SCADA/HMI
    ↓ (UNS/MQTT)
Level 3: MES/Historian
    ↓ (Reports, KPIs)
Level 4: ERP/Business Systems
```

**Our decoder sits at the ISA-95 boundary**, translating raw device data into ISA-95 compliant information.

---

## 5. Template Mapping to ISA-95

### Equipment Identification

**ISA-95 Requirement:** Unique equipment identification

**Our Implementation:**
```csv
# Template 4: Register Map
device_model,register_address,register_name,category
PM8000,100,serial_number_high,Identity
PM8000,102,serial_number_low,Identity
PM8000,104,model_code,Identity

ISA-95 Equipment Attributes:
- Equipment ID: PM8000_001
- Equipment Class: Power Meter
- Equipment Definition: Schneider PM8000
- Serial Number: Combination of high + low
```

### Material Definition & Tracking

**ISA-95 Material Model:** Track production materials

**Our Implementation (Energy as Material):**
```csv
# Template 5: UNS Mapping
register_name,final_uns_path,...
active_power_total,measurement/.../power/active/total,...

ISA-95 Material Property:
- Material Class: Electrical Energy
- Property: Active Power
- Unit of Measure: kW
- Value: 3.84
```

### Personnel & Equipment Tracking

**ISA-95 Personnel Model:** Who operated equipment when

**Our Implementation:**
```csv
# Maintenance tracking
last_service_date,asset/.../maintenance/last_service
last_calibration_date,asset/.../maintenance/last_calibration

ISA-95 Equipment Tracking:
- Equipment ID: PM8000_001
- Maintenance Event: Last calibration
- Timestamp: 2024-12-15
- Personnel: (external system records technician)
```

### Process Segments

**ISA-95 Process Segment:** Recipe or procedure

**Our Implementation via Alarm Config:**
```csv
# Template 4: Alarm configurations
alarm_config_1,AlarmAttributes,2,RW,Alarms,...

ISA-95 Process Segment Parameter:
- Parameter: High Voltage Alarm
- Expected Value: 250V
- Actual Value: (runtime measurement)
- Parameter Type: Quality check
```

---

## 6. Practical Implementation

### Example 1: ISA-95 Compliant Device Registration

**Scenario:** Register new power meter per ISA-95 standards

**Step 1: Define Equipment Hierarchy**
```
Enterprise: Acme Manufacturing
└── Site: Springfield
    └── Area: Production Line 1
        └── Process Cell: Electrical Distribution
            └── Unit: Main Feeder
                └── Equipment Module: PM8000_001
                    ├── Control Module: Voltage_L1
                    ├── Control Module: Current_L1
                    └── Control Module: Power_Total
```

**Step 2: Fill Templates with ISA-95 Context**
```csv
# Template 4 with ISA-95 metadata
device_model,register_address,register_name,category,isa95_level,isa95_equipment_id
PM8000,500,voltage_l1,Measurements,Equipment_Module,PM8000_001
PM8000,600,current_l1,Measurements,Equipment_Module,PM8000_001
PM8000,700,active_power,Power,Equipment_Module,PM8000_001
```

**Step 3: Generate ISA-95 XML Export**
```xml
<Equipment>
  <ID>PM8000_001</ID>
  <Description>Main Feeder Power Meter</Description>
  <EquipmentLevel>Equipment Module</EquipmentLevel>
  <HierarchyScope>
    <Enterprise>Acme Manufacturing</Enterprise>
    <Site>Springfield</Site>
    <Area>Line1</Area>
    <ProcessCell>Electrical</ProcessCell>
    <Unit>MainFeeder</Unit>
  </HierarchyScope>
  <EquipmentProperty>
    <ID>voltage_l1</ID>
    <Description>Phase A Voltage</Description>
    <Value>
      <DataType>Double</DataType>
      <UnitOfMeasure>V</UnitOfMeasure>
    </Value>
  </EquipmentProperty>
</Equipment>
```

### Example 2: MES Integration via ISA-95

**Scenario:** Send production data to MES system

**ISA-95 Production Response Message:**
```json
{
  "productionResponse": {
    "id": "PR_20250111_001",
    "timestamp": "2025-01-11T14:30:00Z",
    "equipmentID": "PM8000_001",
    "segmentResponse": [
      {
        "processSegmentID": "LINE1_PRODUCTION",
        "actualStartTime": "2025-01-11T08:00:00Z",
        "actualEndTime": "2025-01-11T16:00:00Z",
        "segmentData": [
          {
            "id": "total_energy_consumed",
            "value": 1250.5,
            "unitOfMeasure": "kWh",
            "dataType": "Double"
          },
          {
            "id": "peak_demand",
            "value": 245.8,
            "unitOfMeasure": "kW",
            "dataType": "Double"
          }
        ]
      }
    ]
  }
}
```

**Our System Provides Data:**
```python
# Decoder reads power meter
decoded_data = decoder.decode_register('PM8000', 706, words)

# Route to MES via ISA-95 message
mes_message = {
    "equipmentID": "PM8000_001",
    "parameter": "active_power_total",
    "value": decoded_data['value'],
    "unit": "kW",
    "timestamp": decoded_data['timestamp'],
    "quality": decoded_data['health']
}

# Publish to MES topic
mqtt.publish('mes/production/Line1/energy', mes_message)
```

### Example 3: ISA-95 Equipment Capability

**Scenario:** Define what measurements a device can provide

**ISA-95 Equipment Capability:**
```json
{
  "equipmentCapability": {
    "equipmentID": "PM8000_001",
    "equipmentClass": "PowerMeter",
    "capabilityType": "Measurement",
    "properties": [
      {
        "propertyID": "voltage_l1_n",
        "description": "Phase A to Neutral Voltage",
        "dataType": "Float",
        "unitOfMeasure": "V",
        "minimumValue": 0,
        "maximumValue": 300,
        "accuracy": "±0.5%",
        "updateRate": "1s"
      },
      {
        "propertyID": "current_l1",
        "description": "Phase A Current",
        "dataType": "Float",
        "unitOfMeasure": "A",
        "minimumValue": 0,
        "maximumValue": 100,
        "accuracy": "±1.0%",
        "updateRate": "1s"
      }
    ]
  }
}
```

**Generated from Our Templates:**
```python
# Template 1 (structure) + Template 2 (validation)
capability = {
    "equipmentID": device_model,
    "properties": []
}

for register in register_map:
    datatype = get_datatype(register.datatype)
    validation = get_validation(register.datatype, field_name)
    
    capability["properties"].append({
        "propertyID": register.register_name,
        "dataType": datatype.value_type,
        "unitOfMeasure": datatype.unit,
        "minimumValue": validation.min_value,
        "maximumValue": validation.max_value,
        "updateRate": register.scan_rate
    })
```

### Benefits of ISA-95 Compliance

**For IT Teams:**
```
✓ Standard data models for ERP integration
✓ Consistent equipment identification
✓ Clear hierarchy for reporting
✓ Reduced custom integration code
```

**For OT Teams:**
```
✓ Clear equipment organization
✓ Standard terminology with IT
✓ Better asset management
✓ Easier troubleshooting
```

**For Business:**
```
✓ Improved IT/OT alignment
✓ Faster system integration (weeks → days)
✓ Better data quality for decisions
✓ Compliance with industry standards
```

---

## 🎯 Quick Reference

### ISA-95 Hierarchy Mapping

| ISA-95 Level | Our System | Example |
|--------------|------------|---------|
| Enterprise | (Optional scope) | Acme Manufacturing |
| Site | {site} in UNS path | Springfield, FactoryA |
| Area | {area} in UNS path | Line1, Packaging |
| Process Cell | {system} in UNS path | Electrical, HVAC |
| Unit | (Logical grouping) | MainFeeder, Tank101 |
| Equipment Module | {device_id} in UNS | PM8000_001 |
| Control Module | {parameter} in UNS | voltage/l1 |

### ISA-95 Data Types in Our System

| ISA-95 Category | Our Implementation | Template |
|-----------------|-------------------|----------|
| Equipment ID | device_model + instance | Template 4 |
| Equipment Properties | Decoded register values | Template 1-3 |
| Material Properties | Energy, production metrics | Template 5 |
| Process Segments | Alarm configurations | Template 4 |
| Personnel | (External CMMS integration) | - |

---

## ✅ Compliance Checklist

### ISA-95 Alignment Review

**Equipment Model:**
- [ ] Unique equipment IDs assigned
- [ ] Hierarchy levels defined (Site → Area → Equipment)
- [ ] Equipment capabilities documented
- [ ] Properties have units of measure

**Data Exchange:**
- [ ] Standard data types used (Float, Integer, Boolean, String)
- [ ] Timestamps in ISO 8601 format
- [ ] Quality indicators included
- [ ] Equipment context in all messages

**Integration:**
- [ ] Level 2 (SCADA) connectivity tested
- [ ] Level 3 (MES) data format validated
- [ ] Level 4 (ERP) KPIs defined
- [ ] ISA-95 XML export capability

---

## 📚 Additional Resources

**Official Standards:**
- ANSI/ISA-95.00.01 (Part 1: Models and Terminology)
- ANSI/ISA-95.00.02 (Part 2: Data Structures)
- ANSI/ISA-95.00.03 (Part 3: Activity Models)
- IEC 62264 (International equivalent)

**Learning Resources:**
- ISA.org - Official ISA-95 documentation
- MESA International - MES implementations
- "The ISA-95 Standard" - WBF white papers

**Next Steps:**
- Review your equipment hierarchy
- Map devices to ISA-95 levels
- Implement consistent naming
- Test MES integration

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-11  
**Standards:** ANSI/ISA-95, IEC 62264