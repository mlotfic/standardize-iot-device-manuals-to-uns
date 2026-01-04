# The Expert's Mental Model: UNS Namespace Design

When an expert stares at a device datasheet with 200+ parameters, they're not just sorting data — they're building a **semantic layer** that will survive the next 10 years of operational evolution. Here's the internal dialogue:

01. The Decision Tree (What's Actually Happening In Their Head)
    - **First Pass**: The Nature Question `What IS this data fundamentally?`
    - **Second Pass**: The Consumer Question `Who/what needs this data, and why?- `
    - **Third Pass**: The Lifecycle Question `When/why does this value change?`

02. The Expert's Checklist (For Every Single Parameter)
    - **Mutability Test** `Does this EVER change during operation?`
    - **Directionality Test** `Is this data flowing IN or OUT or ABOUT the device?`
    - **Calculation Test** `Is this measured or calculated?`
    - **The Action Test** `What happens if this value is wrong or missing?`

---

## The Expert's Checklist (For Every Single Parameter)

### 1. **The Mutability Test** `Does this EVER change during operation?`

```css
YES → measurement/, status/, health/, kpi/, alarm/
NO  → asset/, meta/, config/

Example:
├─ Serial_Number → asset/ (never changes)
├─ IP_Address → config/ (changes rarely, via admin)
└─ Current_Draw → measurement/ (changes constantly)
```

---

### 2. **The Directionality Test** `Is this data flowing IN or OUT or ABOUT the device?`

```css
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

```cs
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

**The gray area experts watch for**

FFT analysis of vibration

- Raw vibration = `measurement/vibration_raw`
- FFT spectrum = `measurement/vibration_spectrum` (real-time transform)
- Bearing fault score = `health/bearing_condition` (diagnostic)

---

### 4. **The Action Test**

```cs
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

**Example decision tree**

```cs
"High_Vibration_Flag" = true

Questions:
├─ Must production stop? → alarm/high_vibration
├─ Just informational? → status/vibration_warning  
├─ Diagnostic only? → health/vibration_score
└─ For trending? → measurement/vibration_level
```

---

