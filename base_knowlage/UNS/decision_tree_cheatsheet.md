# comprehensive UNS Decision Tree Cheatsheet

## What's Included

🎯 Three-Pass Framework
- Pass 1: Nature Question (What IS this data?)
- Pass 2: Consumer Question (Who needs it?)
- Pass 3: Lifecycle Question (When does it change?)

🧪 Four Critical Tests
- Mutability Test - Does it change?
- Directionality Test - IN/OUT/ABOUT?
- Calculation Test - Measured or calculated?
- Action Test - What if it's wrong?

📊 Quick Reference Tables
- Consumer perspectives (Operator, Maintenance, Analytics, Config)
- Decision matrix for common parameter types
- Key distinctions table

🚨 Common Pitfalls
- Overloading status/
- Confusing command vs status
- Config vs asset confusion

✅ Validation Checklist
- 4 final tests before committing your design

The cheatsheet distills all the decision trees from the intro.md into a concise, actionable reference guide that you can use while mapping device parameters to UNS namespaces!

---

# UNS Namespace Design: Decision Tree Cheatsheet

Quick reference for mapping device parameters to UNS namespaces.

---

## 🎯 The Three-Pass Framework

### Pass 1: Nature Question `What IS this data fundamentally?`

```cs
┌─ Is this ABOUT or FROM the device?
│  └─ FROM → Continue
│
├─ Does it change during operation?
│  ├─ YES → measurement/, status/, health/, kpi/, alarm/
│  └─ NO → asset/, meta/, config/
│
├─ Is it observed or commanded?
│  ├─ Observed → measurement/ or health/
│  └─ Commanded → command/ or control/
│
└─ Is it about PROCESS or DEVICE?
   ├─ Process → measurement/
   └─ Device → health/
```

### Pass 2: Consumer Question `Who/what needs this data, and why?`

```cs
┌─ Operator dashboard? → status/ (current state)
├─ Maintenance scheduling? → maintenance/
├─ OEE calculation? → kpi/ (derived/accumulated)
├─ Historian trending? → measurement/
└─ Asset registry? → asset/ (static metadata)
```

### Pass 3: Lifecycle Question `When/why does this value change?`

```
┌─ Changes due to command? → status/ + command/
├─ Changes due to process? → status/
├─ Changes due to alarm? → status/
└─ Never changes? → asset/

If writable:
├─ command/set_X ← Intent
└─ status/X ← Reality
```

---

## 🧪 The Four Critical Tests

### 1. Mutability Test `Does this EVER change during operation?`

| Answer | Namespace |
|--------|-----------|
| YES | `measurement/`, `status/`, `health/`, `kpi/`, `alarm/` |
| NO | `asset/`, `meta/`, `config/` |

**Examples:**
- Serial_Number → `asset/`
- IP_Address → `config/`
- Current_Draw → `measurement/`

---

### 2. Directionality Test `Is data flowing IN, OUT, or ABOUT the device?`

#### IN (to device):
- `command/` → Imperative (do this now)
- `control/` → Declarative (maintain this)

#### OUT (from device):
- `measurement/` → Process observations
- `status/` → Device state
- `health/` → Self-diagnostics
- `alarm/` → Exceptions requiring action
- `event/` → Discrete occurrences

#### ABOUT (metadata):
- `asset/` → Physical identity
- `config/` → Operational parameters
- `meta/` → Namespace documentation

---

### 3. Calculation Test `Is this measured or calculated?`

```
Measured directly:
└─ measurement/ (raw sensor data)

Calculated from measurements:
├─ kpi/ (if derived AND business-relevant)
└─ measurement/ (if just unit conversion)

Examples:
├─ Pressure_PSI: 14.7 → measurement/
├─ Pressure_kPa: 101.3 → measurement/ (conversion)
└─ Avg_Pressure_1h: 14.2 → kpi/ (requires history)
```

---

### 4. Action Test `What happens if this value is wrong/missing?`

```
Human must respond urgently:
└─ alarm/

Process continues, operators should know:
└─ status/ or event/

Analytics might flag later:
└─ kpi/ or health/

Nothing immediate:
└─ measurement/
```

---

## 🎭 Consumer Perspectives

### Operator View
*"What do I need on my HMI right now?"*
- `status/` → Current states
- `measurement/` → Process values
- `alarm/` → Things to handle
- `command/` → Buttons to press

### Maintenance View
*"When/why to service?"*
- `health/` → Device condition
- `kpi/runtime_hours` → Wear accumulation
- `diagnostic/` → Error history
- `event/maintenance_complete` → Service records

### Analytics View
*"What to trend and analyze?"*
- `measurement/` → High-frequency data
- `kpi/` → Performance metrics
- `event/` → State changes

### Configuration View
*"What can I tune?"*
- `config/` → Adjustable parameters
- `control/` → Control loop setpoints
- `config/alarm/` → Alarm thresholds

---

## ⚡ Quick Decision Matrix

| Parameter Type | Primary Namespace | Secondary Options |
|---------------|-------------------|-------------------|
| Voltage/Current (instantaneous) | `measurement/` | - |
| Power (real-time) | `measurement/` | - |
| Energy totals (kWh) | `kpi/energy/` | `measurement/` if counter |
| Demand (15-min avg) | `kpi/demand/` | - |
| Min/Max values | `kpi/min_max/` | - |
| THD, Harmonics | `measurement/power_quality/` | - |
| Active alarms | `alarm/` | - |
| Alarm history | `event/` | - |
| Alarm thresholds | `config/alarm/` | - |
| Device temperature | `health/` | - |
| Process temperature | `measurement/` | - |
| Runtime hours | `kpi/` | - |
| Operating mode | `status/` | - |
| Mode setpoint | `command/` or `control/` | - |
| Serial number | `asset/` | - |
| Firmware version | `asset/` | - |
| IP address | `config/` | - |
| Error codes | `diagnostic/` | `alarm/` if active |

---

## 🚨 Common Pitfalls to Avoid

### ❌ Overloading `status/`
Don't mix current state with totals, history, or metadata.

**BAD:**
```
status/running: true
status/total_parts: 15847
status/firmware: "v2.1"
```

**GOOD:**
```
status/running: true
kpi/total_parts: 15847
asset/firmware: "v2.1"
```

---

### ❌ Confusing Command vs Status
Separate intent from reality.

**GOOD:**
```
command/set_speed: 1500 ← What was requested
status/active_setpoint: 1450 ← What device accepted
measurement/actual_speed: 1447 ← Physical reality
```

---

### ❌ Config vs Asset Confusion
**Rule of thumb:**
- Wrench to change → `asset/`
- Keyboard to change → `config/`

**Examples:**
- Gear_Ratio (physical) → `asset/`
- Effective_Ratio (calculated) → `config/`

---

## ✅ Final Validation Checklist

Before committing namespace design:

1. **Clarity Test**: Can I explain this to a new hire in 30 seconds?
2. **Scale Test**: Will this break if we add 50 more devices?
3. **Query Test**: Can I write one SQL query to get all measurements?
   - `SELECT * WHERE topic LIKE '%/measurement/%'`
4. **Impact Test**: If this value is missing, which dashboard breaks?

---

## 📋 Key Distinctions

| Concept | Namespace | Notes |
|---------|-----------|-------|
| What the device monitors | `measurement/` | Process data |
| Device monitoring itself | `health/` | Self-diagnostics |
| Instantaneous values | `measurement/` | Real-time |
| Windowed/aggregated | `kpi/` | Calculated over time |
| Totalizers/counters | `kpi/` or `measurement/` | Depends on use case |
| Active alarms | `alarm/` | React NOW |
| Alarm history | `event/` | This happened |
| Alarm rules | `config/alarm/` | When to alarm |

---

## 🎯 The Expert Mantra

> "I'm not organizing files.  
> I'm building a semantic API that will outlive me.  
> Every placement is a promise about what this data means,  
> who needs it, and why it exists.  
> 
> When I'm wrong, 47 dashboards break.  
> When I'm right, the system explains itself."

**Intentional semantics over convenient shortcuts.**
