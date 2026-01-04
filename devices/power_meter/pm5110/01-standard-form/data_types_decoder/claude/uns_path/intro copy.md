This is **practiced wisdom** — the kind you only get after watching a few UNS implementations go sideways. The "one question per branch" test is brilliant because it forces **semantic clarity** before you ever write a line of code.

## What Makes This Framework Bulletproof

Your vocabulary reservation insight is underappreciated. I've seen teams:
- Create `data/` because "measurement" felt too formal → now there's ambiguity
- Split `alarms_critical/` and `alarms_warning/` → now severity is encoded in topology instead of attributes
- Skip `kpi/` entirely → calculated values pollute `measurement/` and break contextualization

The empty branch costs nothing, but **namespace collisions** cost *everything* because:
```
Old dashboards: site/area/line/device/measurement/temp
New reality:     site/area/line/device/readings/temp
Result:          48 hours of "why is everything blank?"
```

## The Edge Cases That Test Your Framework

Here's where it gets interesting:

**1. Bidirectional values** (the classic trap)
```
control/target_speed: 1500  ← What we want
measurement/actual_speed: 1487  ← What we have
```
New engineer asks: "Why isn't speed just in `measurement/`?"  
Answer: Because **intent ≠ outcome** — keeping them separate makes control loops visible.

**2. Soft alarms vs. hard alarms**
```
alarm/high_temp → actionable (stop the process)
status/temp_warning → informational (trending toward alarm)
```
The question "must a human act?" clarifies this instantly.

**3. Derived measurements vs. KPIs**
```
measurement/flow_rate: 150  ← sensor reading
kpi/total_volume: 45000  ← integrated over time
```
If it requires **state/history** to calculate → `kpi/`  
If it's **instantaneous transformation** (like unit conversion) → still `measurement/`

## Your Two Additions Are Perfect

`diagnostic/` solves the "where do I put error codes?" problem that haunts every implementation.

`maintenance/` is essential because predictive maintenance data **isn't operational** — mixing it with `measurement/` makes noise.

## The Real-World Litmus Test

**Scenario**: Motor has a built-in vibration sensor that:
- Measures vibration amplitude (0-100 mm/s)
- Calculates FFT spectrum 
- Flags bearing faults
- Reports device temperature

Where does each go?

```
measurement/vibration_amplitude  ← trending value
measurement/vibration_spectrum   ← still raw sensor data
event/bearing_fault_detected     ← discrete occurrence
health/device_temperature        ← about the sensor itself
```

If someone says "but the fault detection is *derived*..." → **wrong question**. The right question is "*did something happen?*" Yes → `event/`.

---

## The One Addition I'd Consider

```
recipe/ → What's the process definition?
├─ batch_setpoints: {...}
├─ sequence_steps: [...]
└─ quality_targets: {...}
```

Because in batch/discrete manufacturing, **recipe data** doesn't fit cleanly anywhere:
- Not `control/` (that's live setpoints)
- Not `kpi/` (it's prescriptive, not calculated)
- Not `asset/` (it changes per product)

But maybe that's just `control/recipe/`? The question would be: "*What should happen?*" vs. control's "*What am I commanding right now?*"

---

**Your framework's killer feature**: When someone says "I don't know where to put this," you hand them 9 questions. If they can't answer any of them clearly, **the data model is wrong** — not the namespace.

That's architectural elegance.

---

where i can put alarm setpoints and setting under


---

**The semantic trap**: Alarm setpoints feel like they should go in `alarm/`, but that breaks the "one question per branch" rule.

## The Right Answer

```
config/alarm/ → What are the rules?
├─ high_temp_setpoint: 80.0
├─ high_temp_deadband: 2.0
├─ high_temp_delay: 5.0
├─ severity: "critical"
└─ enabled: true
```

**Why?** Because alarm setpoints are **configuration**, not alarm state.

Apply the test:
- `alarm/high_temp` → "Must a human act?" → **Yes** (it's the active alarm)
- `config/alarm/high_temp_setpoint` → "What are the rules?" → **Yes** (it defines when to alarm)

## The Complete Pattern

```
enterprise/site/area/line/device/

measurement/
└─ temperature: 85.2  ← The value being monitored

config/alarm/
├─ high_temp_setpoint: 80.0      ← When to trigger
├─ high_temp_deadband: 2.0       ← Hysteresis
├─ high_temp_delay: 5.0          ← Time to alarm (seconds)
├─ priority: 1                   ← Urgency
├─ enabled: true                 ← Can be disabled
└─ notification_group: "ops"     ← Who gets notified

alarm/
├─ high_temp: true               ← Active alarm state
├─ triggered_at: "2025-01-01T14:30:00Z"
├─ acknowledged: false
└─ current_value: 85.2           ← Value at alarm time
```

## Why Not Other Branches?

❌ **`alarm/setpoint`** → Breaks semantics  
The question is "must a human act?" — setpoints don't require action, **alarms** do.

❌ **`control/alarm/`** → Wrong domain  
`control/` is for *process control* (PID setpoints, valve positions). Alarm thresholds aren't controlling the process.

❌ **`asset/alarm_config/`** → Could work, but...  
This is operational config that changes semi-frequently. `asset/` should be static metadata (serial numbers, model, location).

❌ **`measurement/setpoint`** → Category error  
Measurements are observed values. Setpoints are configured limits.

## The Edge Cases

**Multi-level alarms** (high-high, high, low, low-low):
```
config/alarm/
├─ temp_high_high: {setpoint: 90, priority: 1, delay: 0}
├─ temp_high: {setpoint: 80, priority: 2, delay: 5}
├─ temp_low: {setpoint: 60, priority: 2, delay: 5}
└─ temp_low_low: {setpoint: 50, priority: 1, delay: 0}
```

**Alarm shelving** (temporary suppression):
```
config/alarm/
└─ high_temp_shelved_until: "2025-01-01T16:00:00Z"

alarm/
└─ high_temp_shelved: true  ← Current shelved state
```

**Rate-of-change alarms**:
```
config/alarm/
└─ temp_roc_limit: 5.0  ← degrees per minute

measurement/
└─ temperature: 85.2

alarm/
└─ high_temp_roc: true  ← Triggered when ROC > limit
```

## The Litmus Test

Ask: **"If I change this value, does it trigger an alarm or does it change *when* alarms trigger?"**

- Changes **when** alarms trigger → `config/alarm/`
- **Is** the alarm → `alarm/`

---

## The Alternative View (I've seen this work too)

Some teams use:
```
control/alarm/ → "What behavior am I commanding?"
└─ high_temp_setpoint: 80.0
```

**Argument for it**: Alarm setpoints *control* alarm behavior, similar to how PID setpoints control process behavior.

**Argument against it**: Overloads `control/` with two different semantics (process control vs. alarm logic).

I prefer `config/alarm/` because it keeps `control/` focused on **process manipulation** and makes alarm configuration **searchable** (`config/**` = "things operators tune").

---

**Practical test**: When commissioning, engineers need to find "all the thresholds I can adjust." Would they look in `control/` or `config/`? 

If the answer is `config/`, you've made the right choice.

----

talk about what expert thinking while putting and placing  all device parameters and info under unified namespace hierarchy .../{device}/    ├─ asset/    ├─ measurement/    ├─ alarm/    ├─ event/    ├─ status/    ├─ health/    ├─ kpi/    ├─ command/    ├─ control/    ├─ comm/    ├─ security/    ├─ config/    └─ meta/ ...

---

# The Expert's Mental Model: UNS Namespace Design

When an expert stares at a device datasheet with 200+ parameters, they're not just sorting data — they're building a **semantic layer** that will survive the next 10 years of operational evolution. Here's the internal dialogue:

---

## The Decision Tree (What's Actually Happening In Their Head)

### First Pass: The Nature Question
*"What IS this data fundamentally?"*

```
Parameter: "Motor_Temperature_Deg_C"

🧠 Internal dialogue:
├─ Is this ABOUT the device or FROM the device?
│  └─ FROM the device → Continue...
│
├─ Does it change, or is it fixed?
│  └─ Changes → Continue...
│
├─ Is it observed or commanded?
│  └─ Observed → measurement/ or health/
│
└─ Is it about the PROCESS or the DEVICE itself?
   ├─ Process → measurement/temperature
   └─ Device → health/winding_temperature
```

**The key insight**: `measurement/` is for *what the device monitors*. `health/` is for *the device monitoring itself*.

---

### Second Pass: The Consumer Question
*"Who/what needs this data, and why?"*

```
Parameter: "Total_Runtime_Hours"

🧠 Thinking through use cases:
├─ Operator dashboard? → status/ (current state)
├─ Maintenance scheduling? → Could be maintenance/
├─ OEE calculation? → kpi/ (it's derived/accumulated)
├─ Historian trending? → measurement/ if it's a counter
└─ Asset registry? → asset/ if it's static metadata

Decision: It ACCUMULATES over time → kpi/runtime_hours
NOT measurement/ (not an instantaneous sensor value)
NOT asset/ (changes continuously)
```

**The trap they're avoiding**: "Runtime" *feels* like status, but it's **calculated state**, not instantaneous state.

---

### Third Pass: The Lifecycle Question
*"When/why does this value change?"*

```
Parameter: "Operating_Mode"

🧠 Change triggers:
├─ Changes due to command? → status/ (commanded mode)
├─ Changes due to process? → status/ (automatic mode)
├─ Changes due to alarm? → status/ (safe mode)
└─ Never changes (firmware)? → asset/firmware_mode

If it can be SET:
├─ command/set_mode ← The intent
└─ status/mode ← The reality

Rule: status/ is READ-ONLY from external systems
      command/ is WRITE (intent to change)
```

**Critical distinction**: `status/mode` ≠ `command/set_mode`  
One is *what is*, one is *what was requested*. The gap between them is **control loop feedback**.

---

## The Expert's Checklist (For Every Single Parameter)

### 1. **The Mutability Test**
```
"Does this EVER change during operation?"

YES → measurement/, status/, health/, kpi/, alarm/
NO  → asset/, meta/, config/

Example:
├─ Serial_Number → asset/ (never changes)
├─ IP_Address → config/ (changes rarely, via admin)
└─ Current_Draw → measurement/ (changes constantly)
```

---

### 2. **The Directionality Test**
```
"Is this data flowing IN or OUT or ABOUT the device?"

IN (to device):
├─ command/ → imperative (do this now)
└─ control/ → declarative (maintain this)

OUT (from device):
├─ measurement/ → process observations
├─ status/ → device state
├─ health/ → self-diagnostics
├─ alarm/ → exceptions requiring action
└─ event/ → discrete occurrences

ABOUT (metadata):
├─ asset/ → physical identity
├─ config/ → operational parameters
└─ meta/ → namespace documentation
```

---

### 3. **The Calculation Test**
```
"Is this measured or calculated?"

Measured directly:
└─ measurement/ → raw sensor data

Calculated from measurements:
├─ kpi/ → if derived and business-relevant
└─ Still measurement/ → if it's just unit conversion

Example:
├─ Pressure_PSI: 14.7 → measurement/
├─ Pressure_kPa: 101.3 → measurement/ (just conversion)
└─ Average_Pressure_Last_Hour: 14.2 → kpi/ (requires history)
```

**The gray area experts watch for**: FFT analysis of vibration
- Raw vibration = `measurement/vibration_raw`
- FFT spectrum = `measurement/vibration_spectrum` (real-time transform)
- Bearing fault score = `health/bearing_condition` (diagnostic)

---

### 4. **The Action Test**
```
"What happens if this value is wrong or missing?"

Human must respond urgently:
└─ alarm/

Process continues but operators should know:
└─ status/ or event/

Analytics might flag it later:
└─ kpi/ or health/

Nothing immediate:
└─ measurement/ (just data)
```

**Example decision tree**:
```
"High_Vibration_Flag" = true

Questions:
├─ Must production stop? → alarm/high_vibration
├─ Just informational? → status/vibration_warning  
├─ Diagnostic only? → health/vibration_score
└─ For trending? → measurement/vibration_level
```

---

## The Real Expert Thinking: Edge Cases

### Case 1: Alarm Acknowledgement
```
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
```
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
```
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
```
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

### Operator Perspective
*"What do I need on my HMI right now?"*
```
status/ → Current states (running/stopped)
measurement/ → Process values to monitor
alarm/ → Things I must handle
command/ → Buttons I can press
```

### Maintenance Perspective  
*"What tells me when/why to service?"*
```
health/ → Device condition
kpi/runtime_hours → Wear accumulation
diagnostic/ → Error history
event/maintenance_complete → Service records
```

### Analytics Perspective
*"What do I trend and analyze?"*
```
measurement/ → High-frequency process data
kpi/ → Calculated performance metrics
event/ → State changes for correlation
```

### Configuration Perspective
*"What can I tune?"*
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
```
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
```
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

```
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

## Summary: The Expert's Inner Voice

```
"I'm not organizing files. 
I'm building a semantic API that will outlive me.
Every placement is a promise about what this data means,
who needs it, and why it exists.

When I'm wrong, 47 dashboards break.
When I'm right, the system explains itself."
```

That's the mental model. **Intentional semantics over convenient shortcuts.**

--

apply and align  the The Expert's Mental Model: UNS Namespace Design to power meter PM5110 Schneider


---

# PM5110 Power Meter: Expert UNS Namespace Design

Let me walk through the **actual thinking process** an expert would use when mapping a Schneider PM5110 to UNS.

---

## Phase 1: Understanding the Device

**First question**: *What does this device DO?*

```
PM5110 = Power Quality Meter
- Monitors electrical parameters (V, I, kW, kWh)
- Provides energy billing data
- Detects power quality issues
- Self-diagnoses communication health
```

**Implication**: This device serves **multiple consumers**:
- Operations (real-time power monitoring)
- Maintenance (meter health)
- Billing/finance (energy totals)
- Engineering (power quality analysis)

---

## Phase 2: Parameter-by-Parameter Analysis

### Starting with the datasheet: ~150 parameters

Expert mental flow for each one...

---

### **Voltage Parameters**

```
Device provides:
- Voltage_L1_N
- Voltage_L2_N  
- Voltage_L3_N
- Voltage_L1_L2
- Voltage_L2_L3
- Voltage_L3_L1
- Voltage_Average
- Voltage_Unbalance_%
```

**🧠 Expert thinking:**

**Q: Is this measured or calculated?**
- L1, L2, L3 voltages → Direct measurement
- Average → Calculated, but it's a *real-time transform* not historical
- Unbalance → Calculated from phase voltages

**Q: Process data or device health?**
- This is *what the meter is monitoring* (the electrical system), not the meter itself
- → `measurement/`

**Q: Why not `status/`?**
- Status is for *discrete states* (on/off, mode), not *continuous values*

**Placement:**
```
measurement/voltage/
├─ l1_n: 230.5
├─ l2_n: 229.8
├─ l3_n: 231.2
├─ l1_l2: 398.7
├─ l2_l3: 399.1
├─ l3_l1: 398.3
├─ average: 230.5
└─ unbalance_pct: 0.3
```

**Why grouped under `/voltage/`?**  
Expert decision: These are *always queried together* for power analysis. Flattening to `measurement/voltage_l1_n` works too, but grouping aids consumption patterns.

---

### **Current Parameters**

```
Device provides:
- Current_L1
- Current_L2
- Current_L3
- Current_Neutral
- Current_Average
- Current_Unbalance_%
```

**🧠 Expert thinking:**

**Q: Same pattern as voltage?**
- Yes → `measurement/current/`

**Q: What about peak current or demand current?**
- Peak_Current_L1 → `measurement/current/l1_peak`
- Demand_Current_L1 → `kpi/demand/current_l1` (15-min averaged window)

**Key distinction**: 
- **Instantaneous** = `measurement/`
- **Windowed/aggregated** = `kpi/`

**Placement:**
```
measurement/current/
├─ l1: 45.2
├─ l2: 43.8
├─ l3: 44.6
├─ neutral: 2.1
├─ average: 44.5
└─ unbalance_pct: 1.5
```

---

### **Power Parameters**

```
Device provides:
- Active_Power_Total (kW)
- Reactive_Power_Total (kVAr)
- Apparent_Power_Total (kVA)
- Power_Factor_Total
- Active_Power_L1/L2/L3
- Reactive_Power_L1/L2/L3
```

**🧠 Expert thinking:**

**Q: Is power "measured" or "calculated"?**
- It's *calculated* from V×I, but it's **real-time**, not historical
- Treat it like measurement for consumption purposes

**Q: Why not `kpi/`?**
- KPI implies *business metrics* (OEE, efficiency %)
- Power is a *process variable* that operators trend

**Critical decision point**: Some experts put **instantaneous power** in `measurement/` and **energy totals** (kWh) in `kpi/`. Let's see...

**Placement:**
```
measurement/power/
├─ active_total_kw: 28.7
├─ reactive_total_kvar: 3.2
├─ apparent_total_kva: 28.9
├─ power_factor: 0.99
├─ active_l1_kw: 9.5
├─ active_l2_kw: 9.8
└─ active_l3_kw: 9.4
```

---

### **Energy Parameters (The Tricky One)**

```
Device provides:
- Total_Active_Energy_kWh (accumulated)
- Total_Reactive_Energy_kVArh
- Partial_Energy_kWh (resettable)
- Energy_This_Month_kWh
```

**🧠 Expert thinking:**

**Q: These accumulate over time → Should they be `kpi/`?**

**Critical distinction:**
- `Total_Active_Energy_kWh` = **Totalizer** (like an odometer, never resets)
- `Energy_This_Month_kWh` = **Calculated KPI** (derived, time-windowed)

**Expert decision:**
```
kpi/energy/
├─ total_active_kwh: 1_547_892.3  ← Lifetime accumulator
├─ total_reactive_kvarh: 234_567.1
├─ partial_active_kwh: 15_234.7   ← Resettable counter
└─ this_month_kwh: 8_456.2        ← Calculated window

OR (alternate view):
measurement/energy_total_kwh: 1_547_892.3  ← If treated as "counter" type
kpi/energy_this_month: 8_456.2             ← If calculated
```

**Why the debate?**
- Some say totalizers are "measurements" (they're read from registers)
- Others say they're "KPIs" (they're cumulative business metrics for billing)

**Expert resolution**: Use **consumption pattern**:
- If operators trend it → `measurement/`
- If billing/finance uses it → `kpi/`

**PM5110 decision**: Energy is for **billing** → `kpi/energy/`

---

### **Power Quality Parameters**

```
Device provides:
- Frequency
- THD_Voltage_L1/L2/L3 (%)
- THD_Current_L1/L2/L3 (%)
- Harmonic_Voltage_3rd/5th/7th (per phase)
- Harmonic_Current_3rd/5th/7th (per phase)
```

**🧠 Expert thinking:**

**Q: Is THD a measurement or health metric?**
- It's *measured*, but it indicates **power quality**
- High THD doesn't mean the *meter* is sick, it means the *electrical system* has issues

**Q: Separate branch or under measurement?**

**Option A**: Flat structure
```
measurement/thd_voltage_l1
measurement/harmonic_voltage_3rd_l1
```

**Option B**: Grouped structure
```
measurement/power_quality/
├─ thd_voltage_l1_pct: 2.3
├─ thd_current_l1_pct: 4.7
└─ harmonic_voltage_3rd_l1: 1.8
```

**Expert choice**: **Option B** — because power quality analysis pulls *all harmonics together*. Grouping matches consumption.

**Frequency placement**:
```
measurement/frequency: 50.02
```
**Why not grouped?** Frequency is fundamental and queried independently.

---

### **Min/Max Parameters**

```
Device provides:
- Max_Voltage_L1 (since last reset)
- Min_Voltage_L1
- Max_Current_L1
- Timestamp_Max_Voltage_L1
```

**🧠 Expert thinking:**

**Q: Are these measurements or KPIs?**
- They're **statistical aggregates** over time
- → `kpi/`

**Q: Should they be grouped?**
```
kpi/min_max/
├─ voltage_l1_max: 245.3
├─ voltage_l1_max_timestamp: "2025-01-01T14:23:11Z"
├─ voltage_l1_min: 215.7
├─ current_l1_max: 52.3
└─ demand_kw_max: 32.1
```

**Why `kpi/` not `measurement/`?**  
Because these require **state/memory** — they're not instantaneous readings.

---

### **Demand Parameters**

```
Device provides:
- Demand_Active_Power_kW (15-min average)
- Demand_Apparent_Power_kVA
- Peak_Demand_kW
- Peak_Demand_Timestamp
```

**🧠 Expert thinking:**

**Q: What is "demand"?**
- Utility billing term = average power over sliding window (typically 15 min)
- Used for calculating demand charges

**Q: Is this measurement or KPI?**
- It's **calculated** (sliding window average)
- It's **business-critical** (affects billing)
- → `kpi/demand/`

**Placement:**
```
kpi/demand/
├─ active_power_kw: 26.5      ← Current 15-min average
├─ apparent_power_kva: 27.1
├─ peak_kw: 31.8              ← Highest demand this billing period
└─ peak_timestamp: "2025-01-01T15:45:00Z"
```

---

### **Alarm/Event Parameters**

```
Device provides:
- Voltage_Sag_Alarm
- Voltage_Swell_Alarm  
- Overcurrent_Alarm
- THD_Alarm
- Last_Alarm_Code
- Alarm_Status_Register (bitmap)
```

**🧠 Expert thinking:**

**Q: Active alarms vs. alarm history?**
- `Voltage_Sag_Alarm = TRUE` → **Active alarm** → `alarm/`
- `Last_Voltage_Sag_Event` → **Historical** → `event/`

**Q: Should alarm thresholds go here?**
- NO → They go in `config/alarm/`

**Placement:**
```
alarm/
├─ voltage_sag_l1: false
├─ voltage_swell_l1: false
├─ overcurrent_l1: true         ← Active right now
├─ thd_voltage_l1: false
└─ active_alarm_count: 1

event/
├─ last_voltage_sag: {
│     timestamp: "2025-01-01T14:32:11Z",
│     phase: "L1",
│     voltage: 198.3,
│     duration_ms: 150
│   }
└─ alarm_history: [...]         ← Last 100 events

config/alarm/
├─ voltage_sag_threshold: 207   ← 90% of nominal
├─ voltage_sag_duration_ms: 100
├─ overcurrent_threshold_l1: 50
└─ thd_voltage_threshold_pct: 8
```

**Key distinction**: 
- `alarm/` = "React NOW"
- `event/` = "This happened"
- `config/alarm/` = "Rules for alarming"

---

### **Device Health Parameters**

```
Device provides:
- Internal_Temperature_°C
- Uptime_Hours
- Memory_Usage_%
- CPU_Load_%
- Watchdog_Resets_Count
```

**🧠 Expert thinking:**

**Q: Is internal temperature a measurement?**
- NO — it's not *what the meter measures*, it's *the meter's condition*
- → `health/`

**The critical test**: "If this fails, does the **device** need maintenance or does the **process** need attention?"
- Internal temp high → Device needs cooling/replacement
- Phase voltage high → Electrical system issue

**Placement:**
```
health/
├─ internal_temperature_c: 42.3
├─ uptime_hours: 8_456
├─ memory_usage_pct: 34
├─ cpu_load_pct: 12
├─ watchdog_resets: 0
└─ last_restart_reason: "power_cycle"
```

---

### **Communication Parameters**

```
Device provides:
- Modbus_Address
- Baud_Rate
- Communication_Errors_Count
- Last_Communication_Time
- Network_Link_Status
```

**🧠 Expert thinking:**

**Q: Is this config or status or health?**

**Decision matrix**:
```
Modbus_Address → config/comm/ (it's configured)
Baud_Rate → config/comm/ (it's configured)
Communication_Errors_Count → comm/ (indicates quality)
Last_Communication_Time → comm/ (freshness check)
Network_Link_Status → comm/ (connectivity state)
```

**Why separate `comm/` branch?**
- Distinguishes *device health* from *communication health*
- Edge/gateway systems need to monitor connectivity separately

**Placement:**
```
comm/
├─ errors_count: 3
├─ last_successful_read: "2025-01-01T14:45:32Z"
├─ link_status: "connected"
├─ signal_quality_pct: 98
└─ latency_ms: 23

config/comm/
├─ modbus_address: 10
├─ baud_rate: 19200
├─ parity: "even"
├─ timeout_ms: 1000
└─ retries: 3
```

---

### **Asset/Identity Parameters**

```
Device provides:
- Serial_Number
- Firmware_Version
- Hardware_Revision
- Model_Number
- Manufacture_Date
- Calibration_Date
- Next_Calibration_Due
```

**🧠 Expert thinking:**

**Q: Do any of these change during operation?**
- Serial, model, manufacture date → **Never change** → `asset/`
- Firmware version → **Rarely changes** (via update) → Still `asset/`
- Calibration date → **Changes annually** → `asset/` or `maintenance/`?

**Expert decision**:
```
asset/
├─ serial_number: "PM5110-2024-A15823"
├─ model: "PM5110"
├─ firmware_version: "v2.4.1"
├─ hardware_revision: "B"
├─ manufacture_date: "2024-03-15"
└─ rated_voltage: "400V"

maintenance/
├─ last_calibration: "2024-06-01"
├─ next_calibration_due: "2025-06-01"
├─ calibration_certificate: "CAL-2024-06-1523"
└─ hours_to_pm: 720
```

**Why split?**
- `asset/` = Permanent identity (never changes)
- `maintenance/` = Service lifecycle (changes with PM)

---

### **Configuration Parameters**

```
Device provides:
- CT_Primary_Rating (current transformer ratio)
- VT_Primary_Rating (voltage transformer ratio)
- Measurement_Mode (3P4W, 3P3W, etc.)
- Display_Language
- Password_Protected
```

**🧠 Expert thinking:**

**Q: Configured once or tuned frequently?**
- CT/VT ratios → **Set during commissioning**, rarely changed → `config/`
- Password protected → **Security setting** → `security/`
- Display language → **User preference** → `config/`

**Placement:**
```
config/
├─ ct_primary_rating: 100
├─ ct_secondary_rating: 5
├─ vt_primary_rating: 11000
├─ vt_secondary_rating: 110
├─ measurement_mode: "3P4W"
├─ display_language: "EN"
└─ data_logging_interval_sec: 60

security/
├─ password_enabled: true
├─ access_level_required: 2
├─ last_config_change_user: "admin"
└─ last_config_change_time: "2024-12-15T10:23:00Z"
```

---

### **Control/Command Parameters**

**🧠 Expert thinking:**

**Q: Can I command a power meter?**

Power meters are typically **read-only** devices, but PM5110 supports:
- Reset demand values
- Reset energy counters (partial)
- Sync device clock
- Acknowledge alarms

These are **commands** (imperative actions):

```
command/
├─ reset_demand: {requested_by: "operator", timestamp: "..."}
├─ reset_partial_energy: {requested_by: "billing_system", timestamp: "..."}
├─ sync_clock: {requested_by: "gateway", timestamp: "..."}
└─ acknowledge_alarms: {user: "john.doe", timestamp: "..."}
```

**Why separate from `status/`?**
- `command/` = Write operations (user intent)
- `status/` = Read operations (device state)

The PM5110 doesn't have *control* loops (no PID, no setpoints), so `control/` branch stays empty.

---

## Phase 3: The Complete Namespace

```
enterprise/site/area/panel_3/pm5110_main/

├─ asset/
│  ├─ serial_number: "PM5110-2024-A15823"
│  ├─ model: "PM5110"
│  ├─ firmware_version: "v2.4.1"
│  ├─ hardware_revision: "B"
│  ├─ manufacture_date: "2024-03-15"
│  ├─ rated_voltage: "400V"
│  ├─ rated_current: "100A"
│  └─ accuracy_class: "0.5S"
│
├─ measurement/
│  ├─ voltage/
│  │  ├─ l1_n: 230.5
│  │  ├─ l2_n: 229.8
│  │  ├─ l3_n: 231.2
│  │  ├─ l1_l2: 398.7
│  │  ├─ l2_l3: 399.1
│  │  ├─ l3_l1: 398.3
│  │  ├─ average: 230.5
│  │  └─ unbalance_pct: 0.3
│  │
│  ├─ current/
│  │  ├─ l1: 45.2
│  │  ├─ l2: 43.8
│  │  ├─ l3: 44.6
│  │  ├─ neutral: 2.1
│  │  ├─ average: 44.5
│  │  └─ unbalance_pct: 1.5
│  │
│  ├─ power/
│  │  ├─ active_total_kw: 28.7
│  │  ├─ reactive_total_kvar: 3.2
│  │  ├─ apparent_total_kva: 28.9
│  │  ├─ power_factor: 0.99
│  │  ├─ active_l1_kw: 9.5
│  │  ├─ active_l2_kw: 9.8
│  │  ├─ active_l3_kw: 9.4
│  │  ├─ reactive_l1_kvar: 1.1
│  │  ├─ reactive_l2_kvar: 1.0
│  │  └─ reactive_l3_kvar: 1.1
│  │
│  ├─ frequency: 50.02
│  │
│  └─ power_quality/
│     ├─ thd_voltage_l1_pct: 2.3
│     ├─ thd_voltage_l2_pct: 2.1
│     ├─ thd_voltage_l3_pct: 2.4
│     ├─ thd_current_l1_pct: 4.7
│     ├─ thd_current_l2_pct: 4.2
│     ├─ thd_current_l3_pct: 4.9
│     ├─ harmonic_voltage_3rd_l1: 1.8
│     ├─ harmonic_voltage_5th_l1: 0.9
│     └─ harmonic_voltage_7th_l1: 0.5
│
├─ alarm/
│  ├─ voltage_sag_l1: false
│  ├─ voltage_sag_l2: false
│  ├─ voltage_sag_l3: false
│  ├─ voltage_swell_l1: false
│  ├─ voltage_swell_l2: false
│  ├─ voltage_swell_l3: false
│  ├─ overcurrent_l1: true
│  ├─ overcurrent_l2: false
│  ├─ overcurrent_l3: false
│  ├─ thd_voltage_l1: false
│  ├─ phase_loss: false
│  ├─ active_alarm_count: 1
│  └─ highest_severity: 2
│
├─ event/
│  ├─ last_voltage_sag: {
│  │     timestamp: "2025-01-01T14:32:11Z",
│  │     phase: "L1",
│  │     voltage: 198.3,
│  │     duration_ms: 150
│  │   }
│  ├─ last_power_outage: {
│  │     timestamp: "2024-12-28T03:15:42Z",
│  │     duration_sec: 8
│  │   }
│  ├─ demand_reset: {
│  │     timestamp: "2025-01-01T00:00:01Z",
│  │     user: "billing_system"
│  │   }
│  └─ calibration_performed: {
│        timestamp: "2024-06-01T09:30:00Z",
│        technician: "J.Smith",
│        certificate: "CAL-2024-06-1523"
│      }
│
├─ status/
│  ├─ measurement_mode: "3P4W"
│  ├─ logging_active: true
│  ├─ display_state: "normal"
│  └─ alarm_relay_state: "energized"
│
├─ health/
│  ├─ internal_temperature_c: 42.3
│  ├─ uptime_hours: 8_456
│  ├─ memory_usage_pct: 34
│  ├─ cpu_load_pct: 12
│  ├─ watchdog_resets: 0
│  ├─ last_restart_reason: "power_cycle"
│  └─ device_status: "healthy"
│
├─ kpi/
│  ├─ energy/
│  │  ├─ total_active_kwh: 1_547_892.3
│  │  ├─ total_reactive_kvarh: 234_567.1
│  │  ├─ partial_active_kwh: 15_234.7
│  │  ├─ partial_reactive_kvarh: 2_456.3
│  │  ├─ today_kwh: 687.4
│  │  ├─ this_week_kwh: 4_823.1
│  │  └─ this_month_kwh: 18_456.2
│  │
│  ├─ demand/
│  │  ├─ active_power_kw: 26.5
│  │  ├─ apparent_power_kva: 27.1
│  │  ├─ peak_kw: 31.8
│  │  ├─ peak_kva: 32.4
│  │  ├─ peak_kw_timestamp: "2025-01-01T15:45:00Z"
│  │  └─ average_power_factor: 0.98
│  │
│  └─ min_max/
│     ├─ voltage_l1_max: 245.3
│     ├─ voltage_l1_max_timestamp: "2025-01-01T14:23:11Z"
│     ├─ voltage_l1_min: 215.7
│     ├─ voltage_l1_min_timestamp: "2025-01-01T06:12:08Z"
│     ├─ current_l1_max: 52.3
│     └─ power_factor_min: 0.92
│
├─ command/
│  ├─ reset_demand: null
│  ├─ reset_partial_energy: null
│  ├─ sync_clock: null
│  └─ acknowledge_alarms: null
│
├─ control/
│  └─ (empty - power meters don't have control loops)
│
├─ comm/
│  ├─ modbus_errors_count: 3
│  ├─ modbus_success_rate_pct: 99.7
│  ├─ last_successful_read: "2025-01-01T14:45:32Z"
│  ├─ last_failed_read: "2025-01-01T12:15:11Z"
│  ├─ link_status: "connected"
│  ├─ response_time_avg_ms: 23
│  └─ packets_lost_count: 15
│
├─ security/
│  ├─ password_enabled: true
│  ├─ access_level_required: 2
│  ├─ failed_login_attempts: 0
│  ├─ last_successful_login: "2024-12-20T08:45:00Z"
│  ├─ last_config_change_user: "admin"
│  └─ last_config_change_time: "2024-12-15T10:23:00Z"
│
├─ config/
│  ├─ ct_primary_rating: 100
│  ├─ ct_secondary_rating: 5
│  ├─ vt_primary_rating: 11000
│  ├─ vt_secondary_rating: 110
│  ├─ measurement_mode: "3P4W"
│  ├─ display_language: "EN"
│  ├─ display_contrast: 75
│  ├─ data_logging_interval_sec: 60
│  ├─ demand_window_min: 15
│  └─ nominal_frequency: 50
│  │
│  └─ alarm/
│     ├─ voltage_sag_threshold_pct: 90
│     ├─ voltage_sag_duration_ms: 100
│     ├─ voltage_swell_threshold_pct: 110
│     ├─ voltage_swell_duration_ms: 100
│     ├─ overcurrent_threshold_l1: 50
│     ├─ overcurrent_threshold_l2: 50
│     ├─ overcurrent_threshold_l3: 50
│     ├─ thd_voltage_threshold_pct: 8
│     ├─ thd_current_threshold_pct: 20
│     └─ alarm_delay_sec: 2
│  │
│  └─ comm/
│     ├─ modbus_address: 10
│     ├─ baud_rate: 19200
│     ├─ parity: "even"
│     ├─ stop_bits: 1
│     ├─ timeout_ms: 1000
│     └─ retries: 3
│
├─ maintenance/
│  ├─ last_calibration: "2024-06-01"
│  ├─ next_calibration_due: "2025-06-01"
│  ├─ calibration_certificate: "CAL-2024-06-1523"
│  ├─ install_date: "2024-03-20"
│  ├─ warranty_expiry: "2027-03-20"
│  └─ last_firmware_update: "2024-09-15"
│
└─ meta/
   ├─ namespace_version: "1.0"
   ├─ last_updated: "2025-01-01"
   ├─ device_type: "power_meter"
   ├─ manufacturer: "Schneider Electric"
   ├─ data_sheet_url: "https://www.se.com/.../PM5110"
   ├─ support_contact: "electrical-team@company.com"
   └─ notes: "Main incoming feeder meter for production area"
```

---

## Phase 4: Expert Validation Questions

The expert now **stress-tests** the design:

### **1. Dashboard Query Test**
*"Can I build an operator HMI by querying one branch?"*

```sql
-- Get all real-time electrical measurements
SELECT * FROM uns WHERE topic LIKE '%/pm5110_main/measurement/%'

Result: ✅ All V, I, kW values in one query
```

### **2. Billing System Test**
*"Can billing pull energy without getting flooded with real-time data?"*

```sql
-- Get monthly energy totals
SELECT * FROM uns WHERE topic LIKE '%/pm5110_main/kpi/energy/%'

Result: ✅ Only cumulative/windowed values
```

### **3. Alarm Response Test**
*"If overcurrent trips, what do I need to show the operator?"*

```
1. alarm/overcurrent_l1 = true  ← The alarm
2. measurement/current/l1 = 52.8  ← Current value
3. config/alarm/overcurrent_threshold_l1 = 50  ← Why it tripped
4. event/last_overcurrent → Historical context

Result: ✅ All related data is semantically grouped
```

### **4. Predictive Maintenance Test**
*"Can I trend device health separate from process measurements?"*

```sql
-- Meter health over time
SELECT * FROM uns WHERE topic LIKE '%/pm5110_main/health/%'

Result: ✅ Internal temp, uptime, watchdog resets isolated
```

### **5. Communication Quality Test**
*"If Modbus drops out, how do I diagnose it?"*

```
comm/link_status = "disconnected"
comm/modbus_errors_count = 47
comm/last_successful_read = "2025-01-01T12:05:32Z"
health/device_status = "healthy"  ← Device is fine, comms aren't

Result: ✅ Network issues separated from device issues
```

---

## Phase 5: Expert's Final Decisions (The Gray Areas)

### **Decision 1: Energy in measurement/ or kpi/?**

**Final call**: `kpi/energy/`

**Rationale**: 
- Energy is **billing-critical** and **cumulative**
- Operators don't trend kWh on HMIs (they trend kW)
- Finance queries `kpi/**` for reports

### **Decision 2: Flatten or group sub-branches?**

**Final call**: **Group** voltage, current, power

**Rationale**:
- Consumption patterns: "Give me all voltages" is common
- Query optimization: `WHERE topic LIKE '%/voltage/%'`
- Visual clarity: Easier to browse in MQTT explorer

### **Decision 3: Separate `diagnostic/` branch?**

**Final call**: **No** — use `health/` for device diagnostics

**Rationale**:
- PM5110 doesn't have deep debug modes
- `health/` already covers internal metrics
- Adding `diagnostic/` would be premature (only add if device has error logs, debug traces, etc.)

### **Decision 4: Where does "power factor" go?**

**Final call**: `measurement/power/power_factor`

**Rationale**:
- It's a **real-time measurement** (even though calculated)
- Operators monitor it live (not a KPI)
- Test: "Would this go on an HMI?" → Yes → `measurement/`

---

## The Expert's Closing Thoughts

```
PM5110 namespace design reveals:

✅ Clean separation of concerns
   - Operators see measurement/status/alarm
   - Billing sees kpi/energy
   - Maintenance sees health/maintenance

✅ Scales to 100 meters
   - Pattern is repeatable
   - Queries work across all devices
   - New parameters have clear homes

✅ Survives evolution
   - Adding new harmonics? → measurement/power_quality/
   - New billing windows? → kpi/energy/
   - New alarms? → alarm/ + config/alarm/

⚠️ Remaining ambiguity:
   - Should CT/VT ratios be config/ or asset/?
   - Should demand be kpi/ or measurement/?
   
   These are *reasonable disagreements* — 
   document the decision in meta/ and be consistent.
```

---

## Key Takeaway

The expert doesn't just "organize data" — they build a **semantic API** where:
- **Branch names are contracts** about data meaning
- **Hierarchy predicts queries** (what's grouped is queried together)
- **Placement survives turnover** (new engineers can infer intent)

That's the difference between *a working UNS* and *an architecture that lasts 10 years*.

---

```json
what best prctice for uns 
                /measurement/power_quality/min_max/current/min/Ix",
                or
                /measurement/power_quality/current/min_max/min/Ix",
```

# UNS Hierarchy Ordering: The Expert Mental Model

This is a **critical design decision** that affects query performance, maintainability, and cognitive load. Let me walk through the expert thinking process.

---

## The Two Patterns

```
Option A: Group by statistical type first
/measurement/power_quality/min_max/current/min/l1
/measurement/power_quality/min_max/current/min/l2
/measurement/power_quality/min_max/current/max/l1
/measurement/power_quality/min_max/voltage/min/l1

Option B: Group by measurement type first
/measurement/power_quality/current/min_max/min/l1
/measurement/power_quality/current/min_max/max/l1
/measurement/power_quality/voltage/min_max/min/l1
/measurement/power_quality/voltage/min_max/max/l1
```

---

## Expert Decision Framework

### **Question 1: What gets queried together?**

**Scenario A**: Dashboard showing "all min/max values regardless of type"
```sql
-- Query pattern for Option A
SELECT * WHERE topic LIKE '%/min_max/%'

Result: Gets all min/max for current, voltage, power, THD, etc.
```

**Scenario B**: Dashboard showing "all current metrics (including min/max)"
```sql
-- Query pattern for Option B  
SELECT * WHERE topic LIKE '%/current/%'

Result: Gets instantaneous current, THD current, min/max current
```

**Expert insight**: **Scenario B is more common** in real operations.

**Why?** Because operators think in **measurement domains**:
- "Show me everything about current"
- "Show me everything about voltage"
- NOT "Show me all min/max values across different types"

---

### **Question 2: What's the dominant characteristic?**

This is the **semantic hierarchy principle**: Order from **most defining** to **least defining**.

```
For "minimum L1 current in power quality analysis":

What is it fundamentally?
├─ It's a CURRENT measurement (domain)
│  └─ It's a power quality metric (subdomain)
│     └─ It's a statistical aggregate (min/max)
│        └─ It's specifically the minimum (min vs max)
│           └─ It's for phase L1 (phase identifier)

Hierarchy principle: Domain → Subdomain → Statistical type → Specific value
```

**Result**: `/measurement/power_quality/current/min_max/min/l1`

---

### **Question 3: How does this scale?**

**Option A (statistical grouping first):**
```
/measurement/power_quality/min_max/
├─ current/min/l1
├─ current/min/l2
├─ current/min/l3
├─ current/max/l1
├─ voltage/min/l1
├─ power/min/
├─ thd/min/
└─ frequency/min/
```

**Problem**: As you add metrics, `min_max/` becomes a **dumping ground** for unrelated measurements. Browsing `min_max/` shows a random mix of voltage, current, power, THD...

**Option B (measurement grouping first):**
```
/measurement/power_quality/
├─ current/
│  ├─ l1 (instantaneous)
│  ├─ min_max/min/l1
│  └─ min_max/max/l1
├─ voltage/
│  ├─ l1 (instantaneous)
│  └─ min_max/min/l1
└─ thd_current/
   ├─ l1 (instantaneous)
   └─ min_max/max/l1
```

**Advantage**: **All current-related data is co-located**. When troubleshooting current issues, you have instantaneous + min/max in the same branch.

---

### **Question 4: What's the cognitive load?**

When a new engineer browses the namespace, which is clearer?

**Option A navigation**:
```
📁 power_quality
  📁 min_max
    📁 current
      📁 min
        📄 l1, l2, l3
      📁 max
        📄 l1, l2, l3
```

**Thought process**: "I'm looking at min/max stats... of what? Oh, current. Which phase? Oh, L1."

**Option B navigation**:
```
📁 power_quality  
  📁 current
    📄 l1 (instantaneous)
    📁 min_max
      📁 min
        📄 l1
      📁 max  
        📄 l1
```

**Thought process**: "I'm looking at current. Here's the live value. Here's historical min/max."

**Winner**: Option B — **domain-first hierarchy matches mental models**.

---

### **Question 5: What about time-series queries?**

**Scenario**: "Show me current L1 trend with min/max bands"

**Option A query**:
```sql
SELECT 
  time,
  '/measurement/power_quality/current/l1' AS current,
  '/measurement/power_quality/min_max/current/min/l1' AS min,
  '/measurement/power_quality/min_max/current/max/l1' AS max
```

**Problem**: Min/max are in a **different branch** from the live value. Less intuitive.

**Option B query**:
```sql
SELECT
  time,
  '/measurement/power_quality/current/l1' AS current,
  '/measurement/power_quality/current/min_max/min/l1' AS min,
  '/measurement/power_quality/current/min_max/max/l1' AS max
```

**Advantage**: All three values share the **same parent path** (`/current/`). Easier to construct queries programmatically.

---

## The Expert's Decision: **Option B**

```
✅ RECOMMENDED:
/measurement/power_quality/current/min_max/min/l1
/measurement/power_quality/current/min_max/max/l1

❌ NOT RECOMMENDED:
/measurement/power_quality/min_max/current/min/l1
```

---

## The General Principle

### **Hierarchy Ordering Rules** (from most to least important)

1. **Domain** (what is being measured)
2. **Sub-domain** (category within domain)  
3. **Phase/Location** (where it's measured)
4. **Statistical Type** (how it's processed)
5. **Specific Value** (min/max/avg)

### **Applied to PM5110**:

```
CORRECT hierarchy:
/measurement/
  └─ power_quality/              ← Domain
     ├─ current/                 ← Sub-domain (measurement type)
     │  ├─ l1                    ← Phase (instantaneous value)
     │  ├─ l2
     │  ├─ l3
     │  ├─ average               ← Calculated instant value
     │  └─ min_max/              ← Statistical processing
     │     ├─ min/
     │     │  ├─ l1
     │     │  ├─ l2
     │     │  └─ l3
     │     └─ max/
     │        ├─ l1
     │        ├─ l2
     │        └─ l3
     │
     ├─ voltage/
     │  ├─ l1
     │  └─ min_max/
     │     ├─ min/l1
     │     └─ max/l1
     │
     └─ thd_current/
        ├─ l1
        └─ min_max/
           └─ max/l1
```

---

## Why This Pattern Wins

### ✅ **Query Efficiency**
```javascript
// Get all current metrics (instant + historical)
const currentMetrics = topics.filter(t => 
  t.includes('/current/')
);

// Get all min/max for current
const currentMinMax = topics.filter(t => 
  t.includes('/current/min_max/')
);
```

### ✅ **Mental Model Alignment**
Operators think: "I need current data" → They explore `/current/` and find everything related.

### ✅ **Scales Cleanly**
Adding new statistical types (avg, stddev, percentiles):
```
/current/
  ├─ l1 (instant)
  ├─ min_max/min/l1
  ├─ min_max/max/l1
  ├─ average/1min/l1      ← New: rolling averages
  ├─ average/15min/l1
  └─ percentile/p95/l1    ← New: percentiles
```

### ✅ **Self-Documenting**
Path reads naturally: "Current → min/max → minimum → phase L1"

---

## The Edge Cases

### **What about multi-dimensional aggregates?**

Example: "Max current in the last hour per phase"

```
OPTION 1 (time-based aggregation mixed with phase):
/current/min_max/max_1hour/l1
/current/min_max/max_1hour/l2

OPTION 2 (separate time dimension):
/current/min_max/max/1hour/l1
/current/min_max/max/1hour/l2

OPTION 3 (attributes instead of hierarchy):
/current/min_max/max/l1 
  └─ {window: "1hour", timestamp: "..."}
```

**Expert recommendation**: **Option 3** — Use **attributes for time windows**, not hierarchy.

**Why?** Time windows change frequently (1min, 5min, 15min, 1hour, 1day). Encoding them in paths creates **path explosion**.

```
GOOD:
/measurement/power_quality/current/min_max/max/l1
  payload: {
    value: 52.3,
    window: "1hour",
    window_start: "2025-01-01T14:00:00Z",
    window_end: "2025-01-01T15:00:00Z"
  }

BAD:
/measurement/power_quality/current/min_max/1hour/max/l1
/measurement/power_quality/current/min_max/15min/max/l1
/measurement/power_quality/current/min_max/1day/max/l1
```

---

### **What about demand values?**

**Scenario**: 15-minute demand current (utility billing)

**Wrong placement**:
```
❌ /measurement/current/min_max/avg_15min/l1
   (Demand isn't min/max, it's a windowed average for billing)
```

**Correct placement**:
```
✅ /kpi/demand/current/l1
   (It's a KPI used for billing, not a measurement stat)
```

---

## The Anti-Pattern to Avoid

### ❌ **Statistical-type-first hierarchy**

```
DON'T DO THIS:
/measurement/
  ├─ instantaneous/
  │  ├─ current/l1
  │  └─ voltage/l1
  ├─ min_max/
  │  ├─ current/min/l1
  │  └─ voltage/min/l1
  └─ averages/
     ├─ current/1min/l1
     └─ voltage/1min/l1
```

**Why it fails**:
- Forces users to know statistical type before measurement type
- Fragments related data across multiple branches
- Makes "show me all current data" queries complex

---

## The Final Expert Test

**Scenario**: New engineer needs to build a dashboard showing current with min/max bands.

### **With Option A** (stat-first):
```
1. Find instantaneous: /measurement/power_quality/current/l1
2. Find min: /measurement/power_quality/min_max/current/min/l1
3. Find max: /measurement/power_quality/min_max/current/max/l1

Cognitive load: HIGH (must know three different path patterns)
```

### **With Option B** (domain-first):
```
1. Navigate to: /measurement/power_quality/current/
2. See structure:
   - l1 (instant value)
   - min_max/min/l1
   - min_max/max/l1

Cognitive load: LOW (everything is under /current/)
```

---

## Summary: The Expert's Rule

> **"Group by WHAT is measured, then HOW it's processed"**

```
Hierarchy order:
1. Measurement type (current, voltage, power)
2. Statistical processing (min_max, average, percentile)
3. Specific statistic (min, max, p95)
4. Phase/location (l1, l2, l3)

Result:
/current/min_max/min/l1  ✅
NOT
/min_max/current/min/l1  ❌
```

**Final answer for PM5110**:
```json
{
  "best_practice": "/measurement/power_quality/current/min_max/min/l1",
  "rationale": "Domain-first hierarchy matches consumption patterns",
  "avoid": "/measurement/power_quality/min_max/current/min/l1"
}
```

This pattern **survives scale**, **matches mental models**, and **optimizes for the 80% use case** (querying by measurement type).

---
# Expert Analysis: PM5110 Namespace Alignment

Looking at this real-world implementation, I can see **good intentions** but several **semantic violations** that will cause pain at scale. Let me walk through the expert critique.

---

## 🔴 Critical Issues (Breaking the "One Question Per Branch")

### **Issue 1: KPI nested under measurement/**

```
❌ CURRENT (WRONG):
.../measurement/kpi/energy/p/delivery
.../measurement/kpi/energy/p/received
.../measurement/kpi/energy/p/total

🧠 Expert thinking:
Q: "Can I trend it?" (measurement/ question)
A: Yes, but it's ACCUMULATED, not instantaneous

Q: "Is it derived?" (kpi/ question)  
A: YES - it's a totalizer for billing

VIOLATION: measurement/ should be instantaneous values
           kpi/ should be at root level, not nested
```

**✅ CORRECTED:**
```
.../measurement/power/p/total        ← Instantaneous active power (kW)
.../kpi/energy/p/delivered           ← Accumulated energy (kWh)
.../kpi/energy/p/received
.../kpi/energy/p/total
.../kpi/energy/p/net
```

**Why this matters**: Analytics systems query `measurement/**` for high-frequency trending and `kpi/**` for business metrics. Mixing them breaks query patterns.

---

### **Issue 2: Demand in measurement/power/**

```
❌ CURRENT (WRONG):
.../measurement/power/p/demand/last
.../measurement/power/p/demand/present
.../measurement/power/p/demand/predicted
.../measurement/power/p/demand/peak/datetime

🧠 Expert thinking:
Q: "Can I trend it?" → No, it's a 15-minute windowed average
Q: "Is it derived?" → Yes, it's calculated for billing
Q: "Is it business-critical?" → Yes (utility charges based on this)

VIOLATION: Demand is a KPI, not a measurement
```

**✅ CORRECTED:**
```
.../measurement/power/p/total              ← Instantaneous power (now)
.../kpi/demand/p/present                   ← Current 15-min window
.../kpi/demand/p/last                      ← Previous window
.../kpi/demand/p/predicted                 ← Forecasted peak
.../kpi/demand/p/peak                      ← Highest demand this period
.../kpi/demand/p/peak_timestamp
```

**Pattern**: Instantaneous = `measurement/`, Windowed/aggregated = `kpi/`

---

### **Issue 3: "Summary" is semantically unclear**

```
❌ CURRENT (AMBIGUOUS):
.../measurement/summary/Vavg
.../measurement/summary/Iavg
.../measurement/summary/Ptot
.../measurement/summary/EDel

🧠 Expert thinking:
Q: What IS "summary"?
- Vavg = Average of 3 phase voltages → Real-time calculation
- Iavg = Average of 3 phase currents → Real-time calculation  
- Ptot = Total active power → Real-time measurement
- EDel = Delivered energy → Accumulated KPI

PROBLEM: "Summary" mixes instantaneous and accumulated values
```

**✅ CORRECTED:**
```
.../measurement/voltage/average           ← Real-time avg (V1+V2+V3)/3
.../measurement/current/average           ← Real-time avg (I1+I2+I3)/3
.../measurement/power/p/total             ← Instantaneous total kW
.../kpi/energy/p/delivered                ← Accumulated kWh
```

**Rule**: Never use ambiguous names like "summary", "data", "values". Use semantic names that answer the branch question.

---

### **Issue 4: Alarm structure using display names**

```
❌ CURRENT (WRONG):
.../alarm/count/Over Phase Current
.../alarm/count/Under Phase Current
.../alarm/count/Over Voltage L-L
.../alarm/count/Leading True PF

🧠 Expert problems:
1. Spaces in MQTT topics (parsing hell)
2. Display names change (translations, rebrand)
3. Not machine-readable
4. Inconsistent naming (Over vs Under, L-L vs L-N)
```

**✅ CORRECTED:**
```
.../alarm/count/overcurrent_phase
.../alarm/count/undercurrent_phase
.../alarm/count/overvoltage_line
.../alarm/count/undervoltage_line
.../alarm/count/power_factor_leading_true
.../alarm/count/power_factor_lagging_true

Plus metadata:
.../meta/alarm_labels: {
  "overcurrent_phase": "Over Phase Current",
  "undercurrent_phase": "Under Phase Current"
}
```

**Expert rule**: Paths are APIs (machine-first). Display names are metadata (human-first).

---

### **Issue 5: Maintenance mixing commands and configuration**

```
❌ CURRENT (MIXED SEMANTICS):
.../maintenance/reset/GlobalResets
.../maintenance/reset/SingleReset
.../maintenance/setup/Meter/Basic/PowerSystem
.../maintenance/setup/Comm/Protocol
.../maintenance/Diagnostic/Info

🧠 Expert thinking:
- reset → COMMAND (imperative action)
- setup → CONFIG (declarative parameters)
- Diagnostic → HEALTH or DIAGNOSTIC branch

VIOLATION: One branch, three different questions
```

**✅ CORRECTED:**
```
.../command/
├─ reset_energy_accumulators
├─ reset_demand_values
├─ reset_min_max
├─ reset_alarm_counts
└─ reset_meter  ← Command intent

.../config/
├─ meter/
│  ├─ power_system: "3P4W"
│  ├─ vt_primary: 11000
│  ├─ vt_secondary: 110
│  ├─ ct_primary: 100
│  ├─ ct_secondary: 5
│  └─ frequency_nominal: 50
├─ comm/
│  ├─ protocol: "modbus_rtu"
│  ├─ address: 10
│  ├─ baud_rate: 19200
│  └─ parity: "even"
└─ alarm/
   ├─ overcurrent_phase_setpoint: 50
   └─ undervoltage_line_setpoint: 360

.../diagnostic/
├─ meter_info
├─ calculated_power
└─ phase_angles

.../maintenance/
├─ last_calibration: "2024-06-01"
├─ next_calibration_due: "2025-06-01"
└─ firmware_last_update: "2024-09-15"
```

---

### **Issue 6: Clock placement**

```
❌ CURRENT (WRONG LEVEL):
.../Clock/Date
.../Clock/Time
.../Clock/Meter Time
.../Clock/GMT Offset (h)

🧠 Expert thinking:
Q: Is this about the device or about time sync?
- Date/Time → COMM or HEALTH (is clock synced?)
- GMT Offset → CONFIG (time zone setting)
```

**✅ CORRECTED:**
```
.../health/
├─ clock_time: "2025-01-02T14:35:22Z"
└─ clock_drift_ms: -150

.../comm/
├─ last_time_sync: "2025-01-02T12:00:05Z"
├─ time_sync_source: "NTP"
└─ time_sync_status: "synchronized"

.../config/
└─ timezone_offset_hours: 2
```

**Why**: Clock isn't a top-level concern—it's about device health and configuration.

---

## 🟡 Design Inconsistencies (Will cause query problems)

### **Issue 7: Inconsistent phase notation**

```
CURRENT (INCONSISTENT):
.../Current/I1, I2, I3, In
.../Voltage/phase/V1, V2, V3
.../Voltage/line/U12, U23, U31

🧠 Problems:
- Mixing I/V/U notation (electrical engineering vs software)
- Inconsistent patterns (I1 vs V1 vs U12)
- Makes programmatic queries harder
```

**✅ CORRECTED (Choose one standard):**

**Option A: Software-friendly**
```
.../measurement/current/l1, l2, l3, neutral
.../measurement/voltage/phase/l1, l2, l3
.../measurement/voltage/line/l1_l2, l2_l3, l3_l1
```

**Option B: Electrical engineering notation**
```
.../measurement/current/i1, i2, i3, in
.../measurement/voltage/phase/v1, v2, v3
.../measurement/voltage/line/u12, u23, u31
```

**Expert preference**: Option A (lowercase, descriptive) because it's **language-agnostic** and **self-documenting**.

---

### **Issue 8: Min/Max placement is backwards**

You got this RIGHT in your implementation! Let me highlight it:

```
✅ CURRENT (CORRECT):
.../measurement/power_quality/min_max/current/min/Ix
.../measurement/power_quality/min_max/current/max/Ix

🧠 Expert analysis:
Wait... this violates the domain-first principle we discussed!
```

**✅ SHOULD BE:**
```
.../measurement/power_quality/current/min_max/min/l1
.../measurement/power_quality/current/min_max/max/l1
.../measurement/power_quality/voltage/line/min_max/min/u12
```

**Reasoning**: Domain (current) → Statistical type (min_max) → Specific stat (min) → Phase (l1)

---

## 🟢 What You Got Right

### **1. Grouping voltage by line/phase**
```
✅ GOOD:
.../Voltage/line/U12, U23, U31
.../Voltage/phase/V1, V2, V3
```
This correctly distinguishes line-to-line from phase-to-neutral.

### **2. Power type separation**
```
✅ GOOD:
.../power/p/total    ← Active power
.../power/q/total    ← Reactive power
.../power/s/total    ← Apparent power
```
Using p/q/s is standard electrical notation.

### **3. THD method separation**
```
✅ GOOD:
.../THD/thd_fundamental/...
.../THD/thd_rms/...
```
Distinguishes calculation methods (IEEE vs IEC standards).

### **4. Alarm structure attempt**
```
✅ CONCEPT IS GOOD:
.../alarm/active/...
.../alarm/history/...
.../alarm/unacknowledged/...
```
Separates alarm states (though execution needs refinement—see below).

---

## ✅ The Expert-Aligned Refactor

Here's the complete corrected structure:

```
enterprise/site/area/panel/pm5110_main/

├─ asset/
│  ├─ serial_number: "PM5110-2024-A15823"
│  ├─ model: "PM5110"
│  ├─ firmware_version: "v2.4.1"
│  ├─ rated_voltage: 400
│  ├─ rated_current: 100
│  └─ accuracy_class: "0.5S"
│
├─ measurement/
│  ├─ voltage/
│  │  ├─ phase/
│  │  │  ├─ l1: 230.5
│  │  │  ├─ l2: 229.8
│  │  │  └─ l3: 231.2
│  │  ├─ line/
│  │  │  ├─ l1_l2: 398.7
│  │  │  ├─ l2_l3: 399.1
│  │  │  └─ l3_l1: 398.3
│  │  └─ average: 230.5
│  │
│  ├─ current/
│  │  ├─ l1: 45.2
│  │  ├─ l2: 43.8
│  │  ├─ l3: 44.6
│  │  ├─ neutral: 2.1
│  │  └─ average: 44.5
│  │
│  ├─ power/
│  │  ├─ active/
│  │  │  ├─ total: 28.7         ← Instantaneous kW
│  │  │  ├─ l1: 9.5
│  │  │  ├─ l2: 9.8
│  │  │  └─ l3: 9.4
│  │  ├─ reactive/
│  │  │  ├─ total: 3.2          ← Instantaneous kVAr
│  │  │  ├─ l1: 1.1
│  │  │  ├─ l2: 1.0
│  │  │  └─ l3: 1.1
│  │  └─ apparent/
│  │     └─ total: 28.9         ← Instantaneous kVA
│  │
│  ├─ frequency: 50.02
│  │
│  └─ power_quality/
│     ├─ power_factor/
│     │  ├─ true/
│     │  │  ├─ l1: 0.99
│     │  │  ├─ l2: 0.98
│     │  │  ├─ l3: 0.99
│     │  │  ├─ total: 0.99
│     │  │  └─ min_max/
│     │  │     ├─ min: 0.92
│     │  │     └─ max: 1.00
│     │  └─ displacement/
│     │     ├─ l1: 0.99
│     │     ├─ total: 0.99
│     │     └─ min_max/
│     │        ├─ min: 0.90
│     │        └─ max: 1.00
│     │
│     ├─ thd/
│     │  ├─ fundamental/        ← THD_F calculation
│     │  │  ├─ current/
│     │  │  │  ├─ l1: 4.7
│     │  │  │  ├─ l2: 4.2
│     │  │  │  ├─ l3: 4.9
│     │  │  │  ├─ neutral: 2.1
│     │  │  │  └─ min_max/
│     │  │  │     ├─ min/
│     │  │  │     │  ├─ l1: 3.2
│     │  │  │     │  ├─ l2: 3.0
│     │  │  │     │  └─ l3: 3.5
│     │  │  │     └─ max/
│     │  │  │        ├─ l1: 6.8
│     │  │  │        ├─ l2: 6.2
│     │  │  │        └─ l3: 7.1
│     │  │  └─ voltage/
│     │  │     ├─ phase/
│     │  │     │  ├─ l1: 2.3
│     │  │     │  ├─ l2: 2.1
│     │  │     │  └─ l3: 2.4
│     │  │     └─ line/
│     │  │        ├─ l1_l2: 2.2
│     │  │        ├─ l2_l3: 2.0
│     │  │        └─ l3_l1: 2.3
│     │  │
│     │  └─ rms/                ← THD_R calculation
│     │     ├─ current/
│     │     │  ├─ l1: 4.9
│     │     │  └─ min_max/...
│     │     └─ voltage/
│     │        ├─ phase/
│     │        │  ├─ l1: 2.4
│     │        │  └─ min_max/...
│     │        └─ line/...
│     │
│     ├─ harmonics/
│     │  ├─ tdd: 5.2            ← Total demand distortion
│     │  ├─ current/
│     │  │  ├─ h3_magnitude: 1.8
│     │  │  ├─ h5_magnitude: 0.9
│     │  │  ├─ h7_magnitude: 0.5
│     │  │  ├─ h9_magnitude: 0.3
│     │  │  ├─ h11_magnitude: 0.2
│     │  │  ├─ h13_magnitude: 0.1
│     │  │  └─ h15_magnitude: 0.1
│     │  └─ voltage/
│     │     ├─ phase/
│     │     │  ├─ h3_magnitude: 0.8
│     │     │  ├─ h5_magnitude: 0.4
│     │     │  └─ h7_magnitude: 0.2
│     │     └─ line/
│     │        ├─ h3_magnitude: 0.9
│     │        └─ h5_magnitude: 0.5
│     │
│     └─ unbalance/
│        ├─ current: 1.5
│        ├─ voltage_phase: 0.3
│        ├─ voltage_line: 0.2
│        └─ min_max/
│           ├─ current/
│           │  ├─ min: 0.8
│           │  └─ max: 2.3
│           └─ voltage_phase/
│              ├─ min: 0.1
│              └─ max: 0.5
│
├─ status/
│  ├─ measurement_mode: "3P4W"
│  ├─ logging_active: true
│  ├─ digital_output_1: false
│  └─ digital_output_2: false
│
├─ alarm/
│  ├─ active/                   ← Currently alarming
│  │  ├─ count: 2
│  │  ├─ highest_priority: 1
│  │  └─ list: [
│  │       {
│  │         id: "overcurrent_phase_l1",
│  │         timestamp: "2025-01-02T14:32:11Z",
│  │         phase: "l1",
│  │         value: 52.3,
│  │         priority: 1
│  │       },
│  │       {...}
│  │     ]
│  │
│  ├─ unacknowledged/          ← Needs operator response
│  │  ├─ count: 1
│  │  └─ list: [...]
│  │
│  ├─ counts/                  ← Historical alarm frequency
│  │  ├─ overcurrent_phase: 15
│  │  ├─ undercurrent_phase: 3
│  │  ├─ overvoltage_line: 8
│  │  ├─ undervoltage_line: 12
│  │  ├─ overvoltage_phase: 5
│  │  ├─ undervoltage_phase: 7
│  │  ├─ overpower_active: 22
│  │  ├─ overpower_reactive: 4
│  │  ├─ overpower_apparent: 18
│  │  ├─ power_factor_leading_true: 0
│  │  ├─ power_factor_lagging_true: 2
│  │  ├─ power_factor_leading_displacement: 0
│  │  ├─ power_factor_lagging_displacement: 1
│  │  ├─ over_frequency: 1
│  │  ├─ under_frequency: 3
│  │  ├─ voltage_unbalance: 5
│  │  ├─ voltage_thd: 8
│  │  └─ phase_loss: 2
│  │
│  └─ state/                   ← Current alarm states (booleans)
│     ├─ overcurrent_phase_l1: true
│     ├─ overcurrent_phase_l2: false
│     ├─ overcurrent_phase_l3: false
│     ├─ overvoltage_line: false
│     ├─ undervoltage_line: false
│     └─ phase_loss: false
│
├─ event/
│  ├─ last_alarm_triggered: {
│  │     alarm_id: "overcurrent_phase_l1",
│  │     timestamp: "2025-01-02T14:32:11Z",
│  │     phase: "l1",
│  │     value: 52.3
│  │   }
│  ├─ last_power_outage: {
│  │     timestamp: "2024-12-28T03:15:42Z",
│  │     duration_sec: 8
│  │   }
│  └─ alarm_history: [...]     ← Last 100 events
│
├─ health/
│  ├─ internal_temperature_c: 42.3
│  ├─ uptime_hours: 8456
│  ├─ clock_time: "2025-01-02T14:35:22Z"
│  ├─ clock_drift_ms: -150
│  └─ device_status: "healthy"
│
├─ kpi/
│  ├─ energy/                  ← Accumulated totals
│  │  ├─ active/
│  │  │  ├─ delivered: 1_547_892.3
│  │  │  ├─ received: 12_456.8
│  │  │  ├─ total: 1_560_349.1
│  │  │  └─ net: 1_535_435.5
│  │  ├─ reactive/
│  │  │  ├─ delivered: 234_567.1
│  │  │  ├─ received: 5_432.2
│  │  │  ├─ total: 239_999.3
│  │  │  └─ net: 229_134.9
│  │  └─ apparent/
│  │     ├─ delivered: 1_589_234.5
│  │     ├─ received: 13_245.7
│  │     ├─ total: 1_602_480.2
│  │     └─ net: 1_575_988.8
│  │
│  ├─ demand/                  ← 15-minute windowed averages
│  │  ├─ active/
│  │  │  ├─ present: 26.5      ← Current window
│  │  │  ├─ last: 28.3         ← Previous window
│  │  │  ├─ predicted: 29.1    ← Forecasted peak
│  │  │  ├─ peak: 31.8         ← Highest this billing period
│  │  │  └─ peak_timestamp: "2025-01-01T15:45:00Z"
│  │  ├─ reactive/
│  │  │  ├─ present: 3.2
│  │  │  ├─ last: 3.5
│  │  │  └─ peak: 4.1
│  │  ├─ apparent/
│  │  │  ├─ present: 27.1
│  │  │  ├─ last: 28.9
│  │  │  └─ peak: 32.4
│  │  └─ current/             ← Demand current (billing)
│  │     ├─ present_l1: 44.2
│  │     └─ peak_l1: 51.3
│  │
│  └─ timers/
│     ├─ active_load_hours: 8234.5
│     └─ operating_hours: 8456.2
│
├─ command/
│  ├─ reset_energy_accumulators: null
│  ├─ reset_demand_values: null
│  ├─ reset_min_max: null
│  ├─ reset_alarm_counts: null
│  ├─ reset_active_load_timer: null
│  ├─ reset_meter: null
│  ├─ acknowledge_alarm: null
│  └─ sync_clock: null
│
├─ comm/
│  ├─ modbus_errors_count: 3
│  ├─ modbus_success_rate_pct: 99.7
│  ├─ last_successful_read: "2025-01-02T14:45:32Z"
│  ├─ last_failed_read: "2025-01-02T12:15:11Z"
│  ├─ link_status: "connected"
│  ├─ response_time_avg_ms: 23
│  ├─ time_sync_status: "synchronized"
│  ├─ time_sync_source: "NTP"
│  └─ last_time_sync: "2025-01-02T12:00:05Z"
│
├─ config/
│  ├─ meter/
│  │  ├─ power_system: "3P4W"
│  │  ├─ vt_connect: "wye"
│  │  ├─ vt_primary: 11000
│  │  ├─ vt_secondary: 110
│  │  ├─ ct_terminal: "standard"
│  │  ├─ ct_primary: 100
│  │  ├─ ct_secondary: 5
│  │  ├─ frequency_nominal: 50
│  │  ├─ phase_rotation: "ABC"
│  │  ├─ label: "Main Incoming Feeder"
│  │  ├─ load_timer_setpoint: 30
│  │  └─ peak_current_for_tdd: 50
│  │
│  ├─ demand/
│  │  ├─ power/
│  │  │  ├─ method: "thermal"
│  │  │  └─ interval_min: 15
│  │  └─ current/
│  │     ├─ method: "block"
│  │     └─ interval_min: 15
│  │
│  ├─ comm/
│  │  ├─ protocol: "modbus_rtu"
│  │  ├─ address: 10
│  │  ├─ baud_rate: 19200
│  │  ├─ parity: "even"
│  │  ├─ data_bits: 8
│  │  ├─ stop_bits: 1
│  │  └─ flow_control: "none"
│  │
│  ├─ alarm/
│  │  ├─ overcurrent_phase_setpoint: 50
│  │  ├─ undercurrent_phase_setpoint: 5
│  │  ├─ overvoltage_line_setpoint: 440
│  │  ├─ undervoltage_line_setpoint: 360
│  │  ├─ overvoltage_phase_setpoint: 253
│  │  ├─ undervoltage_phase_setpoint: 207
│  │  ├─ overpower_active_setpoint: 35
│  │  ├─ overpower_reactive_setpoint: 10
│  │  ├─ over_frequency_setpoint: 51
│  │  ├─ under_frequency_setpoint: 49
│  │  ├─ voltage_unbalance_setpoint: 2
│  │  └─ voltage_thd_setpoint: 8
│  │
│  ├─ io/
│  │  ├─ led_mode: "alarm"
│  │  └─ digital_output_function: "pulse"
│  │
│  ├─ hmi/
│  │  ├─ display_contrast: 75
│  │  ├─ backlight_timeout_min: 5
│  │  ├─ screen_timeout_min: 10
│  │  ├─ qr_code_enabled: true
│  │  ├─ language: "EN"
│  │  ├─ date_format: "YYYY-MM-DD"
│  │  ├─ time_format: "24h"
│  │  └─ hmi_mode: "advanced"
│  │
│  └─ timezone_offset_hours: 2
│
├─ security/
│  ├─ password_setup_enabled: true
│  ├─ password_energy_reset_enabled: true
│  ├─ password_demand_reset_enabled: true
│  ├─ password_min_max_reset_enabled: true
│  ├─ password_diagnostics_enabled: false
│  ├─ last_config_change_user: "admin"
│  └─ last_config_change_timestamp: "2024-12-15T10:23:00Z"
│
├─ diagnostic/
│  ├─ meter_info: {...}
│  ├─ calculated_power: {...}
│  └─ phase_angles: {
│       l1: 0,
│       l2: 120,
│       l3: 240
│     }
│
├─ maintenance/
│  ├─ last_calibration: "2024-06-01"
│  ├─ next_calibration_due: "2025-06-01"
│  ├─ calibration_certificate: "CAL-2024-06-1523"
│  ├─ install_date: "2024-03-20"
│  ├─ warranty_expiry: "2027-03-20"
│  └─ last_firmware_update: "2024-09-15"
│
└─ meta/
   ├─ namespace_version: "2.0"
   ├─ last_updated: "2025-01-02"
   ├─ device_type: "power_meter"
   ├─ manufacturer: "Schneider Electric"
   ├─ model: "PM5110"
   ├─ data_sheet_url: "https://www.se.com/.../PM5110"
   ├─ support_contact: "electrical-team@company.com"
   ├─ notes: "Main incoming feeder meter for production area"
   └─ alarm_labels: {
        "overcurrent_phase": "Over Phase Current",
        "undercurrent_phase": "Under Phase Current",
        "overvoltage_line": "Over Voltage L-L",
        "undervoltage_line": "Under Voltage L-L",
        "power_factor_leading_true": "Leading True PF",
        ...
      }
```

---

## Key Transformations Summary

| Original | Issue | Corrected | Reasoning |
|----------|-------|-----------|-----------|
| `measurement/kpi/energy/` | KPI nested in measurement | `kpi/energy/` | KPIs are top-level, not measurements |
| `measurement/power/p/demand/` | Demand in measurement | `kpi/demand/p/` | Demand is windowed KPI for billing |
| `measurement/summary/Vavg` | Ambiguous grouping | `measurement/voltage/average` | Semantic clarity |
| `alarm/count/Over Phase Current` | Display names in path | `alarm/counts/overcurrent_phase` + metadata | Machine-readable paths |
| `maintenance/reset/` | Commands mixed with config | `command/reset_*` | Commands are imperative actions |
| `maintenance/setup/` | Config in wrong branch | `config/meter/`, `config/comm/` | Setup is configuration |
| `Clock/` at root | Wrong hierarchy level | `health/clock_time`, `config/timezone` | Clock is device health + config |
| `min_max/current/min/` | Stat-first ordering | `current/min_max/min/` | Domain-first hierarchy |

---

## The Expert's Final Verdict

**What you had**:
- 70% semantically correct
- Good intentions on structure
- Real-world constraints visible (device firmware limitations)

**What needed alignment**:
- ❌ Branch semantics violated (kpi under measurement)
- ❌ Commands mixed with config
- ❌ Display names in paths
- ❌ Inconsistent hierarchy (stat-first vs domain-first)

**What the refactor achieves**:
- ✅ Every branch answers ONE question
- ✅ Queries are predictable (`kpi/**` = business metrics)
- ✅ Scales to 100 meters without path collisions
- ✅ Machine-readable, human-documented (via `meta/`)
- ✅ Survives firmware updates, operator turnover

**The measurement**: Can a new engineer query for "all real-time measurements" vs "all billing metrics" in one line?

```sql
-- Real-time trending
SELECT * WHERE topic LIKE '%/measurement/%'

-- Billing data
SELECT * WHERE topic LIKE '%/kpi/%'

-- Operator alarms
SELECT * WHERE topic LIKE '%/alarm/active/%'
```

**If yes** → You've built architecture that lasts a decade.  
**If no** → You've built a database that requires documentation to query.

Your original structure showed **understanding**. The corrected structure shows **mastery**.

---


the original structure is the from device screens display tree


---

# 🎯 The Critical Insight: Device UI ≠ Data Architecture

**This changes everything.** You've just revealed the **most common UNS design mistake** in industrial IoT.

---

## The Problem: Screen Tree vs. Semantic Model

**What happened**:
```
Schneider PM5110 HMI Menu Tree
    ↓
  (copied directly)
    ↓
UNS Namespace Structure
```

**Why this fails**:

### **Device vendors optimize for:**
- **Technician navigation** (finding settings during commissioning)
- **Logical grouping for humans** ("All resets in one menu")
- **Screen real estate** (limited buttons, nested menus)
- **Installation workflow** (setup wizard order)

### **UNS namespaces optimize for:**
- **System queries** (get all measurements across 100 devices)
- **Semantic clarity** (what IS this data fundamentally?)
- **Analytics patterns** (time-series, aggregations, correlations)
- **Application consumption** (dashboards, ML models, billing systems)

---

## The Expert's Realization Moment

```
🧠 Expert thinking when they see device menu structure:

"Ah, this is the HMI tree. Let me translate this to 
proper data architecture. The device shows:

├─ Measurement
│  ├─ Summary (quick view for operator)
│  ├─ Current
│  ├─ Voltage
│  └─ Power Quality
├─ Alarm (operator needs)
├─ Maintenance (technician needs)
└─ Setup (commissioning needs)

But the UNS needs to answer:
- What's instantaneous vs accumulated?
- What's measured vs commanded?
- What's process data vs device health?
- What's operational vs configuration?"
```

**The device tree is organized by USER ROLE.**  
**The UNS tree is organized by DATA SEMANTICS.**

---

## Why Device Trees Fail at Scale

### **Scenario: Query all voltage measurements across 50 meters**

**With device-tree structure** (your original):
```sql
-- Have to know the exact device menu path
SELECT * WHERE topic LIKE '%/measurement/Voltage/phase/%'
  OR topic LIKE '%/measurement/Voltage/line/%'
  OR topic LIKE '%/measurement/summary/Vavg'  -- Wait, voltage is also here?
  OR topic LIKE '%/measurement/power_quality/min_max/voltage/%'  -- And here?
```

**With semantic structure** (expert design):
```sql
-- Predictable pattern
SELECT * WHERE topic LIKE '%/measurement/voltage/%'
```

**The difference**: Device tree scatters **related data** across **multiple user contexts**. Semantic tree groups data by **what it fundamentally is**.

---

## The Translation Matrix

Here's how an expert **maps** device screen structure → UNS structure:

### **Device Screen: "Measurement > Summary"**
```
HMI shows:
├─ Vavg (for quick glance)
├─ Iavg (for quick glance)
├─ Ptot (for quick glance)
└─ EDel (for billing)

🧠 Expert translation:
"This is a DASHBOARD VIEW, not a data category.
The device is aggregating disparate data for operator convenience."

UNS placement:
├─ measurement/voltage/average
├─ measurement/current/average
├─ measurement/power/active/total
└─ kpi/energy/active/delivered
```

**Why different?**  
- Device: Optimized for "operator wants quick overview"
- UNS: Optimized for "system queries by measurement type"

---

### **Device Screen: "Maintenance > Setup > Meter > Basic"**
```
HMI shows:
├─ Power System
├─ VT Primary
├─ VT Secondary
├─ CT Primary
├─ CT Secondary

🧠 Expert translation:
"These are CONFIGURATION parameters, but the device 
groups them by installation workflow. UNS should 
group them by semantic meaning."

UNS placement:
config/meter/
├─ power_system: "3P4W"
├─ vt_primary: 11000
├─ vt_secondary: 110
├─ ct_primary: 100
└─ ct_secondary: 5
```

**The device path "Maintenance > Setup > Meter > Basic"** tells you nothing about whether it's:
- A command (reset)
- A configuration (setpoint)
- A diagnostic (status check)

**The UNS path "config/meter/"** tells you: "These are tunable parameters"

---

### **Device Screen: "Maintenance > Reset > Global Resets"**
```
HMI shows:
├─ Meter Initialization
├─ Energies
├─ Demands
├─ Min/Max
└─ Alarm Counts

🧠 Expert translation:
"These are COMMANDS (imperative actions), but the 
device groups them under 'Maintenance' because 
technicians perform them during service."

UNS placement:
command/
├─ reset_meter
├─ reset_energy_accumulators
├─ reset_demand_values
├─ reset_min_max
└─ reset_alarm_counts
```

**Why not "maintenance/"?**  
Because maintenance is about **when work happens**, not **what the data is**.

---

### **Device Screen: "Alarm > Count > Over Phase Current"**
```
HMI shows:
Alarm > Count > Over Phase Current

🧠 Expert translation:
"The device uses display names because humans 
read screens. But MQTT topics need machine-readable IDs."

Device path: .../alarm/count/Over Phase Current
UNS path:    .../alarm/counts/overcurrent_phase
Display:     meta/alarm_labels/overcurrent_phase = "Over Phase Current"
```

**The principle**: Paths are APIs (machine-first). Labels are metadata (human-first).

---

## The Real-World Pattern: Gateway Translation Layer

In practice, you need a **mapping layer** between device and UNS:

```javascript
// Gateway code
const deviceToUNS = {
  // Device path → UNS path
  'measurement/summary/Vavg': 'measurement/voltage/average',
  'measurement/summary/Iavg': 'measurement/current/average',
  'measurement/summary/Ptot': 'measurement/power/active/total',
  'measurement/summary/EDel': 'kpi/energy/active/delivered',
  
  'measurement/power/p/demand/present': 'kpi/demand/active/present',
  'measurement/power/p/demand/last': 'kpi/demand/active/last',
  
  'maintenance/setup/Meter/Basic/PowerSystem': 'config/meter/power_system',
  'maintenance/setup/Meter/Basic/VT Primary': 'config/meter/vt_primary',
  
  'alarm/count/Over Phase Current': 'alarm/counts/overcurrent_phase',
  'alarm/count/Over Voltage L-L': 'alarm/counts/overvoltage_line',
};

// Translation function
function translateDeviceToUNS(devicePath, value) {
  const unsPath = deviceToUNS[devicePath];
  if (!unsPath) {
    console.warn(`No UNS mapping for device path: ${devicePath}`);
    return null;
  }
  
  return {
    topic: `enterprise/site/area/panel/pm5110/${unsPath}`,
    payload: value,
    timestamp: new Date().toISOString()
  };
}
```

---

## Why Manufacturers Build UI Trees This Way

**Schneider's perspective** when designing PM5110 menus:

```
Target user: Electrician during commissioning

Workflow:
1. Install meter
2. Navigate to "Setup"
3. Configure CT/VT ratios
4. Set alarm thresholds
5. Verify measurements
6. Done

Menu structure optimizes for:
- Minimal button presses
- Logical installation flow
- Role-based access (Setup needs password)
- Screen constraints (4-line LCD display)
```

**Their goal**: Make commissioning easy for one technician.  
**Your goal**: Make data consumption easy for 1000 applications.

---

## The Expert's Decision Framework

For each device menu item, ask:

### **1. What USER ROLE is this menu serving?**
```
"Maintenance > Reset" → Technician role
"Alarm > Active" → Operator role
"Measurement > Summary" → Quick-view role
```

### **2. What DATA SEMANTIC does this represent?**
```
Reset commands → command/
Active alarms → alarm/active/
Summary values → (split by measurement type)
```

### **3. Would I query this with other similar data?**
```
Query: "All current measurements"
Should include:
- Instantaneous current
- Min/max current
- THD current
- Demand current

Device tree scatters these across:
- Measurement/Current
- Measurement/power_quality/min_max
- Measurement/power_quality/THD
- Measurement/power/demand

UNS groups them under:
- measurement/current/**
```

---

## The Anti-Pattern in the Wild

**Common mistakes when copying device trees**:

### ❌ **Anti-pattern 1: "Data" or "Values" branches**
```
❌ Device has: Menu > Data > Current > I1
   Creates:    .../data/current/i1

Why it fails: "Data" is meaningless - everything is data
Should be:    .../measurement/current/l1
```

### ❌ **Anti-pattern 2: User role paths**
```
❌ Device has: Technician > Setup > CT Ratio
   Creates:    .../technician/setup/ct_ratio

Why it fails: Role-based organization doesn't scale
Should be:    .../config/meter/ct_primary
```

### ❌ **Anti-pattern 3: Workflow paths**
```
❌ Device has: Commissioning > Verify > Voltage
   Creates:    .../commissioning/verify/voltage

Why it fails: Workflow is temporary, data is permanent
Should be:    .../measurement/voltage/l1
```

### ❌ **Anti-pattern 4: Display grouping**
```
❌ Device has: Quick View > All Currents
   Creates:    .../quick_view/all_currents/l1

Why it fails: Display views change, semantics don't
Should be:    .../measurement/current/l1
```

---

## The Correct Approach: Semantic Mapping

```
Step 1: Document device tree structure
├─ Understand vendor's HMI organization
├─ Note which menus serve which roles
└─ Identify navigation convenience groupings

Step 2: Extract raw data points
├─ List every parameter (ignoring menu structure)
├─ Note: data type, units, update rate, purpose
└─ Identify relationships (phase voltages are related)

Step 3: Apply semantic questions
For each parameter:
├─ Can I trend it? → measurement/
├─ Is it derived/accumulated? → kpi/
├─ Must a human act? → alarm/
├─ Did something happen? → event/
├─ What is true now? → status/
├─ Is the device OK? → health/
├─ Was intent sent? → command/
├─ What's the setpoint? → control/
└─ Is it configured? → config/

Step 4: Create mapping table
Device Path → UNS Path + Transform Rules

Step 5: Implement translation layer
Gateway reads device tree, publishes to UNS structure
```

---

## Example: The "Summary" Screen Translation

**Device HMI Screen (what you saw)**:
```
MEASUREMENT > SUMMARY
┌─────────────────────────┐
│ Vavg:  230.2 V          │
│ Iavg:   44.5 A          │
│ Ptot:   28.7 kW         │
│ EDel: 1547.9 MWh        │
└─────────────────────────┘
```

**Why the device has this**: Operator wants **quick glance** at system status—one screen, four key values.

**UNS semantic translation**:
```javascript
// Device publishes to Modbus registers
const deviceRegisters = {
  40001: { name: 'Vavg', value: 230.2, unit: 'V' },
  40002: { name: 'Iavg', value: 44.5, unit: 'A' },
  40003: { name: 'Ptot', value: 28.7, unit: 'kW' },
  40004: { name: 'EDel', value: 1547892.3, unit: 'kWh' }
};

// Gateway maps to UNS
const unsMapping = {
  'Vavg': {
    path: 'measurement/voltage/average',
    semantic: 'Real-time calculated average of L1+L2+L3'
  },
  'Iavg': {
    path: 'measurement/current/average',
    semantic: 'Real-time calculated average of L1+L2+L3'
  },
  'Ptot': {
    path: 'measurement/power/active/total',
    semantic: 'Instantaneous total active power'
  },
  'EDel': {
    path: 'kpi/energy/active/delivered',
    semantic: 'Accumulated energy delivered (billing totalizer)'
  }
};

// Publish to UNS
publish('enterprise/site/area/panel/pm5110/measurement/voltage/average', 230.2);
publish('enterprise/site/area/panel/pm5110/measurement/current/average', 44.5);
publish('enterprise/site/area/panel/pm5110/measurement/power/active/total', 28.7);
publish('enterprise/site/area/panel/pm5110/kpi/energy/active/delivered', 1547892.3);
```

**Key insight**: The device's "Summary" screen is a **VIEW**, not a **DATA CATEGORY**.

---

## When Device Structure IS Useful

**Don't throw away the device tree entirely!**

### ✅ **Use device tree for:**

**1. Configuration documentation**
```
config/meta/device_menu_mapping: {
  "To change CT ratio": "HMI > Maintenance > Setup > Meter > Basic > CT Primary",
  "To reset energy": "HMI > Maintenance > Reset > Single Reset > Energy",
  "To view alarms": "HMI > Alarm > Active"
}
```

**2. Commissioning guides**
```
maintenance/commissioning_checklist: [
  {step: 1, action: "Set Power System", hmi_path: "Setup > Meter > Basic"},
  {step: 2, action: "Configure CT/VT", hmi_path: "Setup > Meter > Basic"},
  {step: 3, action: "Verify measurements", hmi_path: "Measurement > Summary"}
]
```

**3. Troubleshooting references**
```
diagnostic/device_access: {
  "Check internal temperature": "HMI > Diagnostics > Meter",
  "View communication stats": "HMI > Diagnostics > Comm",
  "See phase angles": "HMI > Diagnostics > PhAng"
}
```

---

## The Final Expert Insight

```
Device manufacturers think:
"How do I help ONE electrician commission ONE meter?"

UNS architects think:
"How do I help 1000 applications query 1000 meters?"

The device tree answers: "Where do I click?"
The UNS tree answers: "What is this data?"
```

---

## Practical Next Steps

### **For your PM5110 implementation:**

**1. Keep device documentation**
```
/docs/pm5110_hmi_structure.json  ← Original device tree
/docs/pm5110_modbus_map.xlsx     ← Register addresses
/docs/pm5110_datasheet.pdf       ← Vendor specs
```

**2. Create mapping table**
```
/config/pm5110_uns_mapping.json  ← Device path → UNS path
```

**3. Implement gateway translator**
```javascript
// Edge gateway
const deviceData = readModbusRegisters(pm5110);
const unsTopics = translateToUNS(deviceData);
publishToMQTT(unsTopics);
```

**4. Document in meta/**
```
.../meta/device_integration: {
  "hmi_structure": "https://docs/pm5110_hmi_structure.json",
  "mapping_table": "https://docs/pm5110_uns_mapping.json",
  "modbus_map": "https://docs/pm5110_modbus_map.xlsx"
}
```

---

## The Validation Test

**Ask yourself**:

❌ **Bad**: "Can an operator find this on the device screen?"  
✅ **Good**: "Can an analyst query all similar data across all devices?"

❌ **Bad**: "Does this match the device manual's table of contents?"  
✅ **Good**: "Does this answer one semantic question clearly?"

❌ **Bad**: "Will technicians recognize this path from the HMI?"  
✅ **Good**: "Will applications understand what this data represents?"

---

## Summary

| Perspective | Optimizes For | Structure Type |
|-------------|---------------|----------------|
| **Device Vendor** | Commissioning workflow | Role-based menu tree |
| **UNS Architect** | Data consumption patterns | Semantic hierarchy |

**The transformation**:
```
Device Tree (navigation)
        ↓
  (mapping layer)
        ↓
UNS Tree (semantics)
```

**Your original structure**: Device screen tree (role-based)  
**Expert structure**: Semantic tree (query-optimized)  
**The bridge**: Translation layer at the gateway

The device tree is **documentation**. The UNS tree is **architecture**.

Never conflate the two. 🎯

generate two json files , -map uns to screen tree [{"uns":"", "hmi_path"],...], - the fix path of original structure




# PM5110 UNS Mapping Files

I'll generate two JSON files for your PM5110 implementation:Perfect! I've generated two comprehensive JSON files:

## **File 1: `pm5110_uns_to_hmi_mapping.json`**
**Purpose**: Operational mapping for gateway translation

This file provides:
- **UNS path → HMI screen path** mapping
- Modbus register addresses
- Data types and units
- Access control (read/write, password requirements)
- Update rates
- Valid ranges and values

**Use case**: Your edge gateway reads this file to know:
- Which Modbus register maps to which UNS topic
- How to transform device data to semantic structure
- Where technicians find settings on the HMI

## **File 2: `pm5110_corrected_uns_structure.json`**
**Purpose**: Architectural documentation

This file shows:
- Complete corrected semantic structure
- The semantic question each branch answers
- What changed from the original device tree (via `changed_from` fields)
- Why transformations were made (descriptions)
- Data types and constraints

**Use case**: Engineers reference this to:
- Understand the semantic design decisions
- See the transformation logic from device tree to UNS
- Maintain consistency when adding new devices

---

## How to Use These Files

### **1. Gateway Implementation**
```javascript
// Load mapping file
const mapping = require('./pm5110_uns_to_hmi_mapping.json');

// Translate device data to UNS
function translateToUNS(modbusData) {
  const unsMessages = [];
  
  mapping.mappings.forEach(map => {
    const deviceValue = modbusData[map.modbus_register];
    if (deviceValue !== undefined) {
      unsMessages.push({
        topic: `${baseDevicePath}/${map.uns}`,
        payload: deviceValue,
        metadata: {
          unit: map.unit,
          timestamp: new Date().toISOString(),
          source_register: map.modbus_register,
          hmi_path: map.hmi_path
        }
      });
    }
  });
  
  return unsMessages;
}
```

### **2. Commissioning Documentation**
```javascript
// Find HMI path for configuration
function getHMIPath(unsPath) {
  const mapping = mappings.find(m => m.uns === unsPath);
  return mapping?.hmi_path;
}

// Example: "To change CT ratio, navigate to:"
console.log(getHMIPath('config/meter/ct_primary'));
// Output: "maintenance > setup > Meter > Basic > CT Primary"
```

### **3. Dashboard Development**
```javascript
// Query all real-time measurements
const measurements = correctedStructure.branches.measurement.paths;

// Build MQTT subscriptions
const topics = Object.keys(flattenObject(measurements))
  .map(path => `${devicePath}/measurement/${path}`);
```

---

## Key Transformations Highlighted

Both files document these critical changes:

| Original Device Path | Corrected UNS Path | Reason |
|---------------------|-------------------|---------|
| `measurement/summary/Vavg` | `measurement/voltage/average` | "Summary" is a view, not a semantic category |
| `measurement/kpi/energy/p/delivery` | `kpi/energy/active/delivered` | KPIs are top-level, not nested under measurement |
| `measurement/power/p/demand/present` | `kpi/demand/active/present` | Demand is a calculated KPI, not instantaneous measurement |
| `alarm/count/Over Phase Current` | `alarm/state/overcurrent_phase` + `alarm/counts/overcurrent_phase` | Machine-readable IDs with display names in meta |
| `maintenance/reset/GlobalResets/Engeries` | `command/reset_energy_accumulators` | Resets are commands, not maintenance category |
| `maintenance/setup/Meter/Basic/CT Primary` | `config/meter/ct_primary` | Setup is configuration |
| `Clock/Meter Time` | `health/clock_time` | Clock time is device health metric |

---

## Next Steps

1. **Load mapping file into your gateway**
2. **Implement translation layer** using the register mappings
3. **Reference corrected structure** for query patterns
4. **Document using meta/** branch for operational support

These files bridge the gap between **device vendor's navigation tree** and **semantic data architecture**. They're your Rosetta Stone for PM5110 integration! 🎯


You're absolutely right. Let me simplify to what you actually need:Much better! Two simple files:

## **File 1: Simple Mapping Table**
- Original path → Corrected path → HMI screen location
- Easy to load into gateway for translation
- Quick reference for commissioning

## **File 2: High-Level Corrections**
- Summary of key changes
- Branch-level issues and fixes
- Naming standards

Use these like:

```javascript
// Gateway translation
const map = require('./mapping.json');
const corrected = map.mappings.find(m => 
  m.original === devicePath
)?.corrected;

// Or generate reverse lookup
const hmiPaths = {};
map.mappings.forEach(m => {
  hmiPaths[m.corrected] = m.hmi;
});
```

Simple, practical, no over-engineering. 👍

