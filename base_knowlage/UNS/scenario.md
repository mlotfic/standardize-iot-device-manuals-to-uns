## The Real-World Litmus Test

**Scenario**:

Motor has a built-in vibration sensor that:

- Measures vibration amplitude (0-100 mm/s)
- Calculates FFT spectrum (raw data)
- Flags bearing faults (discrete occurrence)
- Reports device temperature (about the sensor itself)

Where does each go?

```css
measurement/vibration_amplitude  ← trending value
measurement/vibration_spectrum   ← still raw sensor data
event/bearing_fault_detected     ← discrete occurrence
health/device_temperature        ← about the sensor itself
```

- If someone says "but the fault detection is *derived*..." → **wrong question**. The right question is "*did something happen?*" Yes → `event/`.

---

### **1. Bidirectional values** (the classic trap)

```css
control/target_speed: 1500      ← What we want
measurement/actual_speed: 1487  ← What we have
```

- `New engineer asks`:
"Why isn't speed just in `measurement/`?"
- `Answer`:
Because **intent ≠ outcome** — keeping them separate makes control loops visible.

---

### **2. Soft alarms vs. hard alarms**

```css
alarm/high_temp     → actionable (stop the process)
status/temp_warning → informational (trending toward alarm)
```

- The question "must a human act?" clarifies this instantly.

---

### **3. Derived measurements vs. KPIs**

```css
measurement/flow_rate: 150  ← sensor reading
kpi/total_volume: 45000     ← integrated over time
```

- If it requires **state/history** to calculate                     → `kpi/`  
- If it's **instantaneous transformation** (like unit conversion)   → still `measurement/`

---

Where i can put alarm setpoints and setting under?

**The semantic trap**: Alarm setpoints feel like they should go in `alarm/`, but that breaks the "one question per branch" rule.

## The Right Answer

```css
config/alarm/high_temp/  → What are the rules?
            ├─ setpoint: 80.0
            ├─ deadband: 2.0
            ├─ delay: 5.0
            ├─ severity: "critical"
            ├─ priority: 1
            ├─ enabled: true
            └─ notification_group: "ops"
```

**Why?** Because alarm setpoints are **configuration**, not alarm state.

Apply the test:

- `alarm/high_temp` → "Must a human act?" → **Yes** (it's the active alarm)
- `config/alarm/high_temp/` → "What are the rules?" → **Yes** (it defines when to alarm)

---

## The Complete Pattern

```css
enterprise/site/area/line/device/

measurement/
            └─ temperature: 85.2  ← The value being monitored

config/alarm/high_temp/
                        ├─ setpoint: 80.0      ← When to trigger
                        ├─ deadband: 2.0       ← Hysteresis
                        ├─ delay: 5.0          ← Time to alarm (seconds)
                        ├─ priority: 1                   ← Urgency
                        ├─ enabled: true                 ← Can be disabled
                        └─ notification_group: "ops"     ← Who gets notified

alarm/high_temp/
                ├─ state: true               ← Active alarm state
                ├─ triggered_at: "2025-01-01T14:30:00Z"
                ├─ acknowledged: false
                └─ current_value: 85.2           ← Value at alarm time
```

---


**Alarm shelving** (temporary suppression):

```css
config/alarm/
            └─ high_temp_shelved_until: "2025-01-01T16:00:00Z"

alarm/
            └─ high_temp_shelved: true  ← Current shelved state
```

---

## **Rate-of-change alarms**:

```css
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

```css
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