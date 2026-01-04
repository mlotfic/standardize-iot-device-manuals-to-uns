# The Expert's Mental Model: UNS Namespace Design

When an expert stares at a device datasheet with 200+ parameters, they're not just sorting data — they're building a **semantic layer** that will survive the next 10 years of operational evolution.

## The Expert's Inner Voice

> "I'm not organizing files. 
> I'm building a semantic API that will outlive me.
> Every placement is a promise about what this data means,
> who needs it, and why it exists.

> When I'm wrong, 47 dashboards break.
> When I'm right, the system explains itself."


>> That's the mental model. **Intentional semantics over convenient shortcuts.**


Here's the internal dialogue:

01. The Decision Tree (What's Actually Happening In Their Head)
    - **First Pass**: The Nature Question `What IS this data fundamentally?`
    - **Second Pass**: The Consumer Question `Who/what needs this data, and why?- `
    - **Third Pass**: The Lifecycle Question `When/why does this value change?`

02. The Expert's Checklist (For Every Single Parameter)
    - **Mutability Test** `Does this EVER change during operation?`
    - **Directionality Test** `Is this data flowing IN or OUT or ABOUT the device?`
    - **Calculation Test** `Is this measured or calculated?`
    - **The Action Test** `What happens if this value is wrong or missing?`

03. The Real Expert Thinking: Edge Cases
    - Case 1: Alarm Acknowledgement
    - Case 2: Setpoint Echo
    - Case 3: Error Codes
    - Case 4: Timestamps

04. The Mental Model: "Perspectives"
    - Operator Perspective `What do I need on my HMI right now?`
    - Maintenance Perspective `What tells me when/why to service?`
    - Analytics Perspective `What do I trend and analyze?`
    - Configuration Perspective `What can I tune?`

05. The Gotchas Experts Watch For
    - 1. **Overloading `status/`**
    - 2. **The Alarm State Explosion**
    - 3. **The Config vs. Asset Boundary**
    - 4. **The Timestamp Trap**

06. The Real Expert Move: Namespace Documentation
    - They ALWAYS populate `meta/`

07. The Final Expert Test Before committing, they ask:
    - **"Can I explain this to a new hire in 30 seconds?"**
    - **"Will this break if we add 50 more devices?"**
    - **"Can I write one Spark/SQL query to get all measurements across all devices?"**
    - **"If this value is missing, which dashboard breaks?"**

---

## The Real Expert Thinking: Edge Cases

### Case 1: Alarm Acknowledgement
```cs
Parameter: "Alarm_Ack_Button_Pressed"

🧠 Naive placement: event/ (something happened)
🧠 Expert placement: command/acknowledge_alarm

Why? Because it's INTENT from operator, not device reporting.

The complete flow:
├─ alarm/high_pressure: true ← Device reports
├─ command/ack_alarm: {user: "john", timestamp: ...} ← Operator acts
└─ alarm/high_pressure_acknowledged: true ← Device confirms
```

---

### Case 2: Setpoint Echo

```cs
Parameters:
- "Speed_Setpoint_Commanded" 
- "Speed_Setpoint_Active"

🧠 The trap: These sound like the same thing

Expert placement:
├─ control/target_speed: 1500 ← What controller is trying to achieve
├─ status/active_setpoint: 1450 ← What device accepted (after limits)
└─ measurement/actual_speed: 1447 ← What's actually happening

Why three values? Because reality has layers:
- Commanded (before validation)
- Active (after device accepts)  
- Actual (physical reality)
```

---

### Case 3: Error Codes

```cs
Parameter: "Last_Error_Code"

🧠 Decision points:
├─ Is it CURRENTLY in error? → alarm/active_fault
├─ Is it historical? → event/fault_occurred  
├─ Is it for debugging? → diagnostic/last_error
└─ Is it about device health? → health/fault_count

Expert choice often:
├─ diagnostic/last_error_code: "E0423"
├─ diagnostic/last_error_description: "COMM_TIMEOUT"
├─ diagnostic/error_timestamp: "..."
└─ health/error_count_total: 15 (for MTBF)
```

**Why `diagnostic/` is critical**: It's for *troubleshooting*, not *operating*. Mixing these pollutes operator interfaces.

---

### Case 4: Timestamps

```cs
Parameter: "Device_Clock"

🧠 What's it used for?

If it's event correlation:
└─ comm/device_timestamp (trust/sync issue)

If it's just health:
└─ health/clock_drift

If it's embedded in events:
└─ event/batch_complete: {timestamp: "...", id: "..."}

Never standalone in measurement/ unless it's a process variable
```

---

## The Mental Model: "Perspectives"

Expert architects think in **consumer perspectives**:

### Operator Perspective `What do I need on my HMI right now?`

```cs
status/ → Current states (running/stopped)
measurement/ → Process values to monitor
alarm/ → Things I must handle
command/ → Buttons I can press
```

### Maintenance Perspective `What tells me when/why to service?`
```
health/ → Device condition
kpi/runtime_hours → Wear accumulation
diagnostic/ → Error history
event/maintenance_complete → Service records
```

### Analytics Perspective `What do I trend and analyze?`
```
measurement/ → High-frequency process data
kpi/ → Calculated performance metrics
event/ → State changes for correlation
```

### Configuration Perspective `What can I tune?`
```
config/ → Adjustable parameters
control/ → Control loop setpoints
config/alarm/ → Alarm thresholds
```

---

## The Gotchas Experts Watch For

### 1. **Overloading `status/`**

```
❌ BAD:
status/
├─ running: true
├─ total_parts_produced: 15847
├─ last_maintenance_date: "..."
├─ error_message: "..."
└─ firmware_version: "..."

✅ GOOD:
status/running: true
kpi/total_parts_produced: 15847
maintenance/last_service: "..."
diagnostic/last_error: "..."
asset/firmware_version: "..."
```

**Why it matters**: `status/` should answer "*what mode is it in?*" not "*tell me everything.*"

---

### 2. **The Alarm State Explosion**

```cs
❌ BAD (device sends 50 alarm booleans):
alarm/
├─ high_pressure: true
├─ low_pressure: false
├─ high_temp: true
├─ low_temp: false
... (46 more)

✅ GOOD:
alarm/active_alarms: [
  {id: "high_pressure", severity: 1, value: 105.3},
  {id: "high_temp", severity: 2, value: 87.2}
]

OR keep booleans but add:
alarm/summary: {
  active_count: 2,
  highest_severity: 1,
  newest: "high_temp"
}
```

**Why**: Subscribers don't want 50 MQTT topics. They want structured alarm data.

---

### 3. **The Config vs. Asset Boundary**

```cs
Parameter: "Gear_Ratio"

🧠 Expert thinking:
├─ Can operator change it? → config/
├─ Changed only during install? → asset/
├─ Changed by engineering? → config/
└─ Physically fixed? → asset/

Gray area example:
├─ Pulley_Diameter → asset/ (physical hardware)
└─ Effective_Ratio → config/ (calculated from pulley sizes)
```

**Rule of thumb**: If it requires a wrench to change → `asset/`. If it requires a keyboard → `config/`.

---

## The Real Expert Move: Namespace Documentation

They ALWAYS populate `meta/`:

```cs
meta/
├─ schema_version: "2.1"
├─ last_updated: "2025-01-01"
├─ contact: "controls-team@company.com"
├─ documentation_url: "https://docs.../device-xyz"
└─ branch_descriptions: {
      "measurement": "Process values sampled at 100ms",
      "alarm": "Active alarms requiring operator action",
      "config": "Tunable parameters, requires supervisor role"
    }
```

**Why**: Because in 3 years, no one will remember why `health/` exists or what goes there. Self-documenting namespaces survive turnover.

---

## The Final Expert Test

Before committing, they ask:

1. **"Can I explain this to a new hire in 30 seconds?"**
   - If not, the placement is too clever.

2. **"Will this break if we add 50 more devices?"**
   - Tests scalability of the pattern.

3. **"Can I write one Spark/SQL query to get all measurements across all devices?"**
   - Tests query predictability: `SELECT * WHERE topic LIKE '%/measurement/%'`

4. **"If this value is missing, which dashboard breaks?"**
   - Tests if criticality matches branch placement.

---


