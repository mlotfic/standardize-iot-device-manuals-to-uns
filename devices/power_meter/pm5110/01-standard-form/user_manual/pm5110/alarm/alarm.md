Good catch. This section is **pure validation logic**, not alarm behavior — and it must live in config, otherwise UIs and APIs will happily accept garbage and the meter will reject it later (or worse: clamp silently).

Below is a **clean, implementation-ready JSON model** that captures **maximum allowable setpoint rules**, exactly as the raw text intends — but structured so SCADA, config tools, and validators can actually use it.

---

## Maximum Allowable Setpoint – Validation Rules (JSON Config)

```json
{
  "config_version": "1.2",
  "scope": "AlarmSetpointValidation",

  "transformer_ratios": {
    "CT_ratio": {
      "description": "Current Transformer ratio = CT primary / CT secondary",
      "data_type": "float",
      "unit": "A/A",
      "min": 0.1
    },
    "VT_ratio": {
      "description": "Voltage Transformer ratio = VT primary / VT secondary",
      "data_type": "float",
      "unit": "V/V",
      "min": 0.1
    }
  },

  "system_parameters": {
    "number_of_phases": {
      "description": "Electrical system phase count",
      "data_type": "uint8",
      "allowed_values": [1, 2, 3]
    },
    "maximum_voltage": {
      "description": "Factory-programmed maximum voltage (secondary side)",
      "data_type": "float",
      "unit": "V"
    },
    "maximum_current": {
      "description": "Factory-programmed maximum current (secondary side)",
      "data_type": "float",
      "unit": "A"
    }
  },

  "standard_alarm_max_setpoints": {
    "Over Phase Current": {
      "formula": "maximum_current * CT_ratio",
      "unit": "A"
    },
    "Under Phase Current": {
      "formula": "maximum_current * CT_ratio",
      "unit": "A"
    },
    "Over Neutral Current": {
      "formula": "maximum_current * CT_ratio * number_of_phases",
      "unit": "A"
    },
    "Over Ground Current": {
      "formula": "maximum_current * CT_ratio",
      "unit": "A"
    },

    "Over Voltage L-L": {
      "formula": "maximum_voltage * VT_ratio",
      "unit": "V"
    },
    "Under Voltage L-L": {
      "formula": "maximum_voltage * VT_ratio",
      "unit": "V"
    },
    "Over Voltage L-N": {
      "formula": "maximum_voltage * VT_ratio",
      "unit": "V"
    },
    "Under Voltage L-N": {
      "formula": "maximum_voltage * VT_ratio",
      "unit": "V"
    },

    "Over Active Power": {
      "formula": "maximum_voltage * maximum_current * number_of_phases",
      "unit": "W"
    },
    "Over Reactive Power": {
      "formula": "maximum_voltage * maximum_current * number_of_phases",
      "unit": "VAR"
    },
    "Over Apparent Power": {
      "formula": "maximum_voltage * maximum_current * number_of_phases",
      "unit": "VA"
    },

    "Over Present Active Power Demand": {
      "formula": "maximum_voltage * maximum_current * number_of_phases",
      "unit": "W"
    },
    "Over Last Active Power Demand": {
      "formula": "maximum_voltage * maximum_current * number_of_phases",
      "unit": "W"
    },
    "Over Predicted Active Power Demand": {
      "formula": "maximum_voltage * maximum_current * number_of_phases",
      "unit": "W"
    },

    "Over Present Reactive Power Demand": {
      "formula": "maximum_voltage * maximum_current * number_of_phases",
      "unit": "VAR"
    },
    "Over Last Reactive Power Demand": {
      "formula": "maximum_voltage * maximum_current * number_of_phases",
      "unit": "VAR"
    },
    "Over Predicted Reactive Power Demand": {
      "formula": "maximum_voltage * maximum_current * number_of_phases",
      "unit": "VAR"
    },

    "Over Present Apparent Power Demand": {
      "formula": "maximum_voltage * maximum_current * number_of_phases",
      "unit": "VA"
    },
    "Over Last Apparent Power Demand": {
      "formula": "maximum_voltage * maximum_current * number_of_phases",
      "unit": "VA"
    },
    "Over Predicted Apparent Power Demand": {
      "formula": "maximum_voltage * maximum_current * number_of_phases",
      "unit": "VA"
    },

    "Over Voltage Unbalance": {
      "formula": "maximum_voltage * VT_ratio",
      "unit": "V"
    },

    "Phase Loss": {
      "formula": "maximum_voltage * VT_ratio",
      "unit": "V"
    }
  }
}
```

---

## How this actually works in a real system (step-by-step)

1. **Meter stores everything internally on secondary values**

   * CT/VT ratios scale *what the user sees*, not what the ADC measures.
2. **Factory limits protect math and firmware**

   * Prevent overflow, nonsense demand values, or impossible physics.
3. **UI / API must validate before write**

   * If user enters `A > max_setpoint`, reject immediately.
4. **Demand alarms reuse the same ceiling**

   * Present / Last / Predicted are *different signals*, same physical ceiling.

This is **not alarm logic** — it’s **input sanitation**.

---

## Example (real numbers)

**System**

* 3-phase
* CT = 800 / 5 → CT ratio = 160
* VT = 11 kV / 110 V → VT ratio = 100
* Max voltage (secondary) = 120 V
* Max current (secondary) = 6 A

**Over Active Power max**

```
120 × 6 × 3 = 2160 W
```

Anything above **2160 W** → UI should refuse entry.

---

## Implementation Watchouts + Dev Wisdom

* ⚠ These limits are **validation**, not alarm pickup A/B
* ⚠ Always compute limits **after** CT/VT changes
* ⚠ Neutral current uses `× number_of_phases` — many miss this
* ⚠ Power limits ignore PF on purpose (worst-case ceiling)
* ✅ Enforce limits client-side **and** server-side
* 🧠 Store formulas as expressions, not hard numbers — ratios change

If you want next:

* JSON that **binds this validation to A/B pickup/dropout**
* Ignition Perspective form auto-validation
* Modbus write-guard logic (block illegal writes before device)

Pick the next brick — structure is now clean and sane.
Alright — this table is **capability + UI contract**, not alarm behavior. Think of it as: *what the meter lets you type*, before **pickup A / dropout B / delays** even come into play.

I’ll break it down like a controls engineer wiring alarms for the first time **without getting bitten later**.

---

# Standard Alarms — What the Table Really Means

## 1️⃣ Two columns = two layers of truth

You see this pattern everywhere:

| ION Setup       | Display    |
| --------------- | ---------- |
| High-resolution | Rounded UI |

Example:

```
ION Setup: 0.000 – 99999.000 A
Display:   0 – 99999 A
```

**Reality:**

* Internally stored as **float with decimals**
* Displayed as **rounded integer** on front panel
* SCADA / ION Setup can write fractional values
* Front panel usually can’t

👉 Never design validation from the *display* column.

---

## 2️⃣ Current alarms (Phase / Neutral / Ground)

```
Over / Under Phase Current
Over Neutral Current
Over Ground Current
```

* Units: **A**
* Range: `0.000 → 99999.000`
* Resolution: **0.001 A internally**

### System quirks

* Neutral current only makes sense in **4-wire systems**
* Ground current requires **residual measurement enabled**
* Maximum allowed setpoint is still clamped by:

  ```
  max_current × CT_ratio (× phases for neutral)
  ```

UI allows 99999 A — firmware won’t.

---

## 3️⃣ Voltage alarms (L-L, L-N)

```
Over / Under Voltage L-L
Over / Under Voltage L-N
```

* Units: **V**
* Range: `0.00 → 999999.00`
* Resolution: **0.01 V**

### Configuration dependency (this bites people)

* **L-N alarms disabled on delta systems**
* Meter checks:

  * System type
  * VT ratio
* Max setpoint = `max_voltage × VT_ratio`

You *can* enter a value — meter just won’t arm the alarm.

---

## 4️⃣ Power alarms (kW / kVAR / kVA)

```
Over Active Power
Over Reactive Power
Over Apparent Power
```

* Units: **kW / kVAR / kVA**
* Range: `0.0 → 9,999,999.0`
* Resolution: **0.1**

### Why no negative range?

Because **direction is handled separately**:

* Delivered / Received is **not** part of this alarm
* This is magnitude-only logic

Ceiling still enforced as:

```
max_voltage × max_current × phases
```

---

## 5️⃣ Power Factor alarms (this is where confusion starts)

```
Leading True PF
Lagging True PF
Leading Disp PF
Lagging Disp PF
```

### Valid range (weird but intentional)

```
-1.00 → -0.01
 0.01 →  1.00
```

### Why is zero missing?

* PF = 0 → undefined (90° phase)
* Meter blocks zero to avoid chatter

### Why negative allowed?

Because **sign ≠ direction** here:

* *Leading / Lagging* is the alarm selector
* Sign just follows IEC quadrant math

Real rule:

* Alarm logic checks **quadrant + magnitude**
* Not just the number you typed

---

## 6️⃣ Demand alarms (Present / Last / Predicted)

```
Over kW / kVAR / kVA Demand
```

* Same ranges as power alarms
* Different **source signal**
* Demand window logic applies before alarm logic

Meter does:

```
Demand calculation → compare to pickup A → delay → alarm
```

Not the other way around.

---

## 7️⃣ Frequency alarms

```
Over Frequency
Under Frequency
```

* Units: **Hz**
* Range: `0.000 → 99.000`
* Resolution: **0.001 Hz**

### Practical notes

* Meter nominal (50 / 60 Hz) is *not* the limit
* Pickup/dropout hysteresis is mandatory
* Tight bands (<0.1 Hz) will chatter without delay

---

## 8️⃣ Voltage Unbalance & THD

```
Over Voltage Unbalance (%)
Over Voltage THD (%)
```

* Units: **%**
* Range: `0 → 99`
* Integer resolution

### Measurement basis

* Voltage unbalance usually = **NEMA or IEC method**
* THD = RMS harmonic / fundamental

Alarm compares **computed %**, not raw harmonics.

---

## 9️⃣ Phase Loss (special case)

```
Phase Loss
```

* No units (effectively volts)
* Range: `0.00 → 999999.00`

### What it actually does

* Internally compares **voltage magnitude**
* If phase voltage < threshold → phase lost
* Uses VT ratio + system type
* Ignores PF, current, power completely

This is **voltage presence detection**, not protection-relay grade logic.

---

# How this ties back to Pickup A / Dropout B

This table defines:

* **What value types exist**
* **What ranges you may enter**
* **What resolution the firmware supports**

It does **NOT** define:

* Pickup setpoint (A)
* Dropout setpoint (B)
* Pickup delay ΔT1
* Dropout delay ΔT2

Those are **common alarm parameters** applied *after* this validation.

---

## Implementation Watchouts + Dev Wisdom

* ⚠ UI range ≠ firmware limit (CT/VT still clamp)
* ⚠ PF alarms care about **quadrant**, not just sign
* ⚠ L-N alarms silently disabled on delta systems
* ⚠ Demand alarms trigger on **calculated demand**, not instantaneous power
* ⚠ Phase Loss ≠ current-based logic
* ✅ Validate: type → range → system compatibility → pickup/dropout
* 🧠 Treat this table as **schema**, not behavior

If you want next:

* Exact **pickup A / dropout B parameter schema**
* ISA-18.2 mapping (priority, shelving, state)
* Ignition UDT with full alarm math
* Modbus register-level mapping of these alarms

Say which layer you want to lock down next.


Exact pickup A / dropout B parameter schema

Good — now we’re at the **real alarm engine**, not the marketing table.

Below is the **exact, implementable pickup / dropout parameter schema** as it exists conceptually in Schneider PM-class meters (PM5xxx / ION family). This is the part people *assume* and get wrong.

I’ll describe it **signal-agnostic**, then show **examples**, then give a **JSON schema you can actually use**.

---

# Alarm Core Model (Standard Alarms)

Every **standard alarm** is built from **the same state machine**, regardless of whether the signal is current, voltage, PF, THD, etc.

Think in **three layers**:

1. **Signal source** (already validated by the table you sent)
2. **Threshold logic (A/B)**
3. **Timing + latching behavior**

---

## 1️⃣ Core Parameters (Exact Schema)

### Pickup (A) — alarm ON threshold

| Field             | Meaning                              | Type  | Units          |
| ----------------- | ------------------------------------ | ----- | -------------- |
| `pickup_setpoint` | Value that starts alarm evaluation   | float | same as signal |
| `pickup_delay_s`  | Time value must remain beyond pickup | float | seconds        |

Logic:

```
if signal crosses pickup_setpoint
AND stays there ≥ pickup_delay_s
→ alarm ON (EV1)
```

---

### Dropout (B) — alarm OFF threshold

| Field              | Meaning                               | Type  | Units          |
| ------------------ | ------------------------------------- | ----- | -------------- |
| `dropout_setpoint` | Value that clears alarm               | float | same as signal |
| `dropout_delay_s`  | Time value must remain beyond dropout | float | seconds        |

Logic:

```
if signal crosses dropout_setpoint
AND stays there ≥ dropout_delay_s
→ alarm OFF (EV2)
```

---

## 2️⃣ Direction Logic (Over vs Under)

This is **not implicit** — it is configured.

### Over-type alarm

```
pickup condition:   signal ≥ pickup_setpoint
dropout condition:  signal ≤ dropout_setpoint
```

### Under-type alarm

```
pickup condition:   signal ≤ pickup_setpoint
dropout condition:  signal ≥ dropout_setpoint
```

⚠ Firmware enforces:

```
Over alarm:  dropout_setpoint < pickup_setpoint
Under alarm: dropout_setpoint > pickup_setpoint
```

Otherwise the alarm never clears.

---

## 3️⃣ Timing Model (What the meter actually does)

Internally the meter runs a **per-alarm timer state machine**:

```text
NORMAL
  |
  | signal crosses pickup threshold
  v
PICKUP_TIMING (ΔT1)
  |
  | ΔT1 satisfied
  v
ALARM_ACTIVE (EV1 logged)
  |
  | signal crosses dropout threshold
  v
DROPOUT_TIMING (ΔT2)
  |
  | ΔT2 satisfied
  v
NORMAL (EV2 logged)
```

Timers **reset immediately** if the signal exits the required zone.

---

## 4️⃣ Recorded Values (Max / Min)

These are **not configuration**, but part of alarm behavior and often forgotten.

### Over alarm stores:

* `max1` → max during pickup timing
* `max2` → max during active alarm

### Under alarm stores:

* `min1` → min during pickup timing
* `min2` → min during active alarm

These are tied to EV1 / EV2 timestamps.

---

## 5️⃣ Common Optional Flags (Implementation Reality)

Depending on meter / ION Setup access:

| Flag           | Purpose                         |
| -------------- | ------------------------------- |
| `enabled`      | Alarm armed or not              |
| `latching`     | Alarm requires manual reset     |
| `priority`     | Alarm severity                  |
| `event_action` | LED flash, DO trigger, log only |
| `shelved`      | Temporarily suppressed          |

Even if UI hides them, **engine supports them**.

---

## 6️⃣ Exact JSON Configuration Schema (Practical)

This is what you asked for — **no fluff**.

```json
{
  "alarm_id": "over_phase_current_L1",
  "alarm_type": "standard",
  "mode": "over",
  "signal": {
    "name": "phase_current",
    "phase": "L1",
    "unit": "A"
  },
  "thresholds": {
    "pickup": {
      "setpoint": 450.0,
      "delay_s": 5.0
    },
    "dropout": {
      "setpoint": 430.0,
      "delay_s": 3.0
    }
  },
  "behavior": {
    "latching": false,
    "priority": 3,
    "enabled": true
  },
  "recording": {
    "track_extremes": true,
    "store_pre_alarm": true
  }
}
```

---

## 7️⃣ Under-Voltage Example (Shows polarity flip)

```json
{
  "alarm_id": "under_voltage_LN",
  "alarm_type": "standard",
  "mode": "under",
  "signal": {
    "name": "voltage_LN",
    "unit": "V"
  },
  "thresholds": {
    "pickup": {
      "setpoint": 195.0,
      "delay_s": 10.0
    },
    "dropout": {
      "setpoint": 205.0,
      "delay_s": 5.0
    }
  }
}
```

Interpretation:

* Alarm ON if V ≤ 195 V for 10 s
* Alarm OFF if V ≥ 205 V for 5 s

That hysteresis is **mandatory** in real plants.

---

## 8️⃣ PF Alarm Special Case (Edge Handling)

PF alarms still use **A / B**, but with sign rules:

Example: *Lagging True PF*

```
pickup:  PF ≥ +0.90  (lagging quadrant only)
dropout: PF ≤ +0.92
```

The meter:

1. Checks quadrant (lagging)
2. Applies numeric threshold
3. Applies delays

Zero crossing is ignored to avoid chatter.

---

## Implementation Watchouts + Dev Wisdom

* ⚠ Pickup A ≠ “alarm setpoint” — delay is equally critical
* ⚠ Always enforce hysteresis (A ≠ B) or alarms will stick
* ⚠ Delays are **per alarm**, not global
* ⚠ Max/min recording happens automatically — don’t double-log
* ⚠ PF alarms are **quadrant-aware**, not just numeric
* ⚠ Under alarms invert logic — many SCADA devs get this wrong
* ✅ Model alarms as **state machines**, not `if` statements

If you want next:

* Full **ISA-18.2 mapping** of this schema
* Ignition **UDT alarm implementation**
* Modbus / ION object mapping
* Energy deviation alarms tied to ISO 50001

Pick the next layer.

Full ISA-18.2 mapping of this schema

Good. Now we’re talking **plant-grade alarm management**, not meter menus.

I’ll map your **Pickup A / Dropout B alarm schema** cleanly and *exactly* to **ISA-18.2**, using how real DCS / SCADA systems implement it (Ignition, DeltaV, PCS7, EcoStruxure, etc.).

No theory fluff — this is the **traceability layer** auditors and control engineers care about.

---

# ISA-18.2 Mapping — From Meter Alarm to Managed Alarm

ISA-18.2 doesn’t care about volts or amps.
It cares about **alarm lifecycle, quality, and operator impact**.

So we map your schema into **five ISA objects**.

---

## 1️⃣ Alarm Definition (Static Configuration)

This is **what the alarm *is***.

| ISA-18.2 Field  | Your Schema          | Notes                     |
| --------------- | -------------------- | ------------------------- |
| `AlarmID`       | `alarm_id`           | Must be unique and stable |
| `AlarmType`     | `standard` / `unary` | Event vs condition        |
| `AlarmClass`    | derived              | e.g. Electrical, Energy   |
| `AlarmText`     | generated            | Human-readable            |
| `AlarmCategory` | derived              | Voltage, Current, Power   |
| `Units`         | `signal.unit`        | Mandatory                 |
| `NormalState`   | calculated           | Typically OFF             |
| `Enabled`       | `behavior.enabled`   |                           |

**Important:** ISA requires **Normal vs Alarm state**, not ON/OFF semantics.

---

## 2️⃣ Alarm Condition (Threshold Logic)

This is **where Pickup A / Dropout B live**.

| ISA-18.2 Concept | Meter Parameter       |
| ---------------- | --------------------- |
| `TripPoint`      | `pickup_setpoint`     |
| `ResetPoint`     | `dropout_setpoint`    |
| `TripDelay`      | `pickup_delay_s`      |
| `ResetDelay`     | `dropout_delay_s`     |
| `Direction`      | `mode` (over / under) |

### Exact logic mapping

```text
Over alarm:
  AlarmState = TRUE  if signal ≥ TripPoint for TripDelay
  AlarmState = FALSE if signal ≤ ResetPoint for ResetDelay

Under alarm:
  AlarmState = TRUE  if signal ≤ TripPoint for TripDelay
  AlarmState = FALSE if signal ≥ ResetPoint for ResetDelay
```

ISA explicitly **requires hysteresis** → your A/B model fits perfectly.

---

## 3️⃣ Alarm State Model (Lifecycle)

ISA-18.2 standard alarm states:

| ISA State        | Meter State          |
| ---------------- | -------------------- |
| `Normal`         | Below pickup         |
| `Pending`        | Pickup timing (ΔT1)  |
| `Active`         | Alarm ON (EV1)       |
| `ReturnToNormal` | Dropout timing (ΔT2) |
| `Shelved`        | Operator suppress    |
| `OutOfService`   | `enabled = false`    |

This is why **timers are mandatory**.

---

## 4️⃣ Alarm Event Logging (What gets recorded)

Mapped from your EV1 / EV2 logic.

| ISA Event       | Meter Event |
| --------------- | ----------- |
| `AlarmOn`       | EV1         |
| `AlarmOff`      | EV2         |
| `AlarmDuration` | ΔT3         |
| `TimestampOn`   | EV1 time    |
| `TimestampOff`  | EV2 time    |
| `MaxValue`      | Max1 / Max2 |
| `MinValue`      | Min1 / Min2 |

ISA requires **first-out time** accuracy → PM meters timestamp in seconds (acceptable).

---

## 5️⃣ Alarm Priority & Response (The Human Layer)

This is **not electrical** — it’s operational.

| ISA Field        | Your Schema          |
| ---------------- | -------------------- |
| `Priority`       | `behavior.priority`  |
| `AlarmLimit`     | `pickup_setpoint`    |
| `OperatorAction` | derived / documented |
| `Consequence`    | documented           |
| `TimeToRespond`  | derived from delay   |
| `Latching`       | `behavior.latching`  |

### Priority example (typical)

| Priority | Meaning                   |
| -------- | ------------------------- |
| 1        | Safety / Equipment damage |
| 2        | Production impact         |
| 3        | Energy / quality          |
| 4        | Advisory                  |

Meters usually sit at **P3–P4**, not P1.

---

## 6️⃣ Full ISA-18.2 Alarm Object (JSON)

This is **audit-ready**.

```json
{
  "isa18_alarm": {
    "alarm_id": "over_phase_current_L1",
    "alarm_type": "standard",
    "alarm_class": "Electrical",
    "alarm_category": "Current",
    "alarm_text": "Over Phase Current L1",
    "units": "A",
    "normal_state": "Normal",
    "enabled": true,
    "condition": {
      "direction": "over",
      "trip_point": 450.0,
      "reset_point": 430.0,
      "trip_delay_s": 5.0,
      "reset_delay_s": 3.0
    },
    "behavior": {
      "priority": 3,
      "latching": false,
      "shelvable": true
    },
    "events": {
      "log_on": true,
      "log_off": true,
      "track_max": true
    },
    "operator_guidance": {
      "cause": "Load exceeds design current",
      "consequence": "Potential overheating",
      "action": "Reduce load or check feeder"
    }
  }
}
```

---

## 7️⃣ Unary Alarms Mapping (Powerup, Reset, Phase Reversal)

Unary alarms skip Pickup/Dropout.

| ISA Concept | Unary Alarm       |
| ----------- | ----------------- |
| Condition   | Boolean event     |
| Delay       | Optional debounce |
| Reset       | Automatic         |
| State       | Event-based       |

Example:

```json
{
  "alarm_id": "phase_reversal",
  "alarm_type": "unary",
  "priority": 2,
  "auto_reset": true
}
```

---

## 8️⃣ Alarm Rationalization Checklist (ISA-18.2 compliant)

For **each alarm**, you must answer:

1. Is it actionable?
2. Does it have a defined response?
3. Is the priority justified?
4. Is hysteresis present?
5. Is shelving allowed?
6. Is it redundant with another alarm?

Meters often fail #1 and #6 if not curated.

---

## Implementation Watchouts + Dev Wisdom

* ⚠ ISA alarms are **stateful**, not events
* ⚠ Pickup A ≠ ISA TripPoint unless delay is included
* ⚠ Dropout B must exist — ISA forbids single threshold
* ⚠ Priority ≠ severity — it’s operator impact
* ⚠ Do not forward *all* meter alarms to operators
* ✅ Group electrical alarms into **alarm classes**
* 🧠 Think “operator response”, not “meter feature”

If you want next:

* Alarm rationalization worksheet (energy-focused)
* Ignition implementation (tag alarms → ISA states)
* SQL materialized alarm views
* ISO 50001 energy deviation alarms using this model

Say the word.
Alarm rationalization worksheet (energy-focused)

Good — this is where **99% of plants fail audits**: too many electrical alarms, zero operational value.

Below is a **practical, energy-focused ISA-18.2 alarm rationalization worksheet**, tuned for **PM5110 / PM-class meters**, ISO 50001 thinking, and real control rooms.

No theory. This is exactly how you justify *why an alarm exists*.

---

# Energy-Focused Alarm Rationalization Worksheet

(ISA-18.2 compliant, meter-driven)

## 1️⃣ Header (Audit Anchor)

| Field       | Value                          |
| ----------- | ------------------------------ |
| Site        | <Plant / Facility>             |
| Area        | <MCC / PFC / Feeder / Utility> |
| Asset       | PM5110-MCC-01                  |
| Alarm Class | Energy / Electrical            |
| Reviewed By | <Name>                         |
| Review Date | YYYY-MM-DD                     |

---

## 2️⃣ Alarm Identification

| Field      | Example                            |
| ---------- | ---------------------------------- |
| Alarm ID   | `over_kw_demand_pred`              |
| Alarm Name | Over Predicted Active Power Demand |
| Signal     | Predicted kW Demand                |
| Source     | PM5110                             |
| Units      | kW                                 |
| Alarm Type | Standard (Over)                    |

---

## 3️⃣ Alarm Condition Definition (Pickup / Dropout)

| Parameter            | Value  | Justification          |
| -------------------- | ------ | ---------------------- |
| Pickup Setpoint (A)  | 920 kW | 95% of contract demand |
| Pickup Delay (ΔT1)   | 60 s   | Avoid transient spikes |
| Dropout Setpoint (B) | 880 kW | 4% hysteresis          |
| Dropout Delay (ΔT2)  | 120 s  | Prevent alarm chatter  |
| Direction            | Over   | Demand ceiling logic   |

✔ **Hysteresis present**
✔ **Delay justified**

---

## 4️⃣ Energy Relevance Test (Critical Section)

| Question                                          | Answer            |
| ------------------------------------------------- | ----------------- |
| Does this alarm indicate excess energy cost?      | ✅ Yes             |
| Does it warn *before* penalty occurs?             | ✅ Yes (Predicted) |
| Is this a control failure or optimization signal? | Optimization      |
| Is there another alarm covering this condition?   | ❌ No              |

👉 **Result:** Alarm is **justified**

---

## 5️⃣ Consequence Analysis (ISA-18.2 Required)

| Aspect           | Description           |
| ---------------- | --------------------- |
| Consequence      | Demand charge penalty |
| Impact Type      | Financial             |
| Estimated Cost   | $ / kW over limit     |
| Equipment Damage | None                  |
| Safety Impact    | None                  |

⚠ This is **not a P1 alarm**.

---

## 6️⃣ Operator Response Definition

| Field                   | Value                       |
| ----------------------- | --------------------------- |
| Required Action         | Shed non-critical loads     |
| Action Time             | < 5 minutes                 |
| Action Owner            | Energy / Shift Engineer     |
| Automation Exists       | Partial (load shedding PLC) |
| Operator Acknowledgment | Required                    |

If no clear action → **alarm must be removed**.

---

## 7️⃣ Priority Assignment (Energy-Correct)

| Priority          | Rationale                      |
| ----------------- | ------------------------------ |
| Priority          | **3**                          |
| Reason            | Financial loss, no safety risk |
| Max Standing Time | 15 minutes                     |

ISA rule: **Priority is about response urgency**, not importance.

---

## 8️⃣ Alarm Quality Checks

| Check          | Pass |
| -------------- | ---- |
| Actionable     | ✅    |
| Unique         | ✅    |
| Timely         | ✅    |
| Understandable | ✅    |
| Not Nuisance   | ✅    |
| Not Chattering | ✅    |

If ≥2 ❌ → redesign or delete.

---

## 9️⃣ Final Decision

| Decision         | Status |
| ---------------- | ------ |
| Keep Alarm       | ✅      |
| Modify           | ❌      |
| Remove           | ❌      |
| Convert to Event | ❌      |

---

# Common Energy Alarms — Keep vs Kill (Reality Table)

| Alarm                    | Decision            | Reason               |
| ------------------------ | ------------------- | -------------------- |
| Over Predicted kW Demand | KEEP                | Prevents penalties   |
| Over Present kW Demand   | MODIFY              | Needs longer delay   |
| Over kVAR                | KEEP (PFC panels)   | Capacitor failure    |
| Lagging PF               | KEEP                | Utility penalty      |
| Over Voltage THD         | KEEP (advisory)     | Power quality        |
| Over Instantaneous kW    | REMOVE              | No operator action   |
| Over Neutral Current     | KEEP (data centers) | Harmonics            |
| Phase Loss               | KEEP                | Equipment protection |

---

## 10️⃣ Machine-Readable Worksheet (JSON)

This is **gold** for tooling, Git, audits.

```json
{
  "alarm_id": "over_kw_demand_pred",
  "alarm_class": "Energy",
  "signal": "Predicted Active Power Demand",
  "units": "kW",
  "thresholds": {
    "pickup": { "value": 920, "delay_s": 60 },
    "dropout": { "value": 880, "delay_s": 120 }
  },
  "priority": 3,
  "consequence": {
    "type": "Financial",
    "description": "Utility demand penalty"
  },
  "operator_response": {
    "action": "Shed non-critical loads",
    "time_to_respond_min": 5
  },
  "decision": "Keep"
}
```

---

## Implementation Watchouts + Dev Wisdom

* ⚠ Energy alarms are **predictive**, not reactive
* ⚠ Instantaneous power alarms are usually noise
* ⚠ If no operator action exists → delete the alarm
* ⚠ Priority ≠ cost — it’s response urgency
* ⚠ Demand alarms must align with utility billing logic
* ✅ Always prefer **Predicted > Present > Last**
* 🧠 Fewer alarms = faster response = lower energy cost

If you want next:

* Full **energy alarm set** for MCC vs PFC panels
* Ignition alarm pipeline (UDT → ISA states)
* ISO 50001 deviation alarms mapped to meters
* Auto-generated rationalization sheets from Excel / JSON

Say which one.
Auto-generated rationalization sheets from Excel / JSON

Good. This is a **very real-world problem**, and there *is* a standard way engineers solve it without suffering.

Goal recap (plain English):
You want to **define alarms once (Excel or JSON)** and **auto-generate ISA-18.2–compliant rationalization worksheets** — consistently, audit-ready, and version-controlled.

I’ll walk you through:

1. **Canonical data model (single source of truth)**
2. **Excel layout that actually works**
3. **JSON schema (machine-first)**
4. **Generation logic (Excel → JSON → Worksheet)**
5. **Output formats (Excel / PDF / CSV / DB)**
6. **Edge cases & real-world traps**

No fluff.

---

# 1️⃣ Canonical Model (This Is the Key Insight)

**Never** generate worksheets directly from meter configs.

Instead:

> **Alarm Definition → Canonical Alarm Object → Worksheet**

Everything feeds the same object.

```
PM5110 / SCADA / Excel / JSON
          ↓
   Canonical Alarm Model
          ↓
 ISA-18.2 Rationalization Sheet
```

If you skip this step, consistency dies fast.

---

# 2️⃣ Excel Input Template (Human-Friendly, Not Stupid)

This is the **minimum viable Excel** that works in real plants.

### Sheet: `alarms`

| Column            | Example                 | Notes                  |
| ----------------- | ----------------------- | ---------------------- |
| alarm_id          | over_kw_demand_pred     | Stable key             |
| asset             | MCC-01                  | Logical asset          |
| alarm_class       | Energy                  | ISA class              |
| category          | Demand                  | Grouping               |
| signal            | Predicted kW Demand     |                        |
| direction         | over                    | over / under           |
| pickup_value      | 920                     | numeric                |
| pickup_delay_s    | 60                      | seconds                |
| dropout_value     | 880                     | hysteresis             |
| dropout_delay_s   | 120                     | seconds                |
| units             | kW                      | mandatory              |
| priority          | 3                       | ISA priority           |
| consequence       | Demand penalty          | free text              |
| operator_action   | Shed non-critical loads | free text              |
| response_time_min | 5                       | numeric                |
| decision          | Keep                    | Keep / Modify / Remove |

### Why this works

* One row = one alarm
* No merged cells
* No formulas needed
* Easy for engineers, easy for scripts

---

# 3️⃣ Canonical JSON Schema (Machine-First)

This is the **normalized form** everything converts into.

```json
{
  "alarm_id": "over_kw_demand_pred",
  "asset": "MCC-01",
  "alarm_class": "Energy",
  "category": "Demand",
  "signal": {
    "name": "Predicted Active Power Demand",
    "unit": "kW"
  },
  "condition": {
    "type": "standard",
    "direction": "over",
    "pickup": {
      "value": 920,
      "delay_s": 60
    },
    "dropout": {
      "value": 880,
      "delay_s": 120
    }
  },
  "priority": 3,
  "rationalization": {
    "consequence": "Utility demand penalty",
    "operator_action": "Shed non-critical loads",
    "response_time_min": 5,
    "decision": "Keep"
  }
}
```

This object maps **directly** to ISA-18.2 concepts.

---

# 4️⃣ Auto-Generation Logic (Step-by-Step)

### Step 1 — Load Excel / JSON

* Excel → pandas / openpyxl
* JSON → native load

### Step 2 — Validate (do not skip)

Hard checks:

* pickup ≠ dropout
* delay ≥ 0
* priority ∈ [1..4]
* decision ∈ {Keep, Modify, Remove}

Soft warnings:

* missing operator action
* priority 1 with no safety impact
* zero delay on energy alarms

### Step 3 — Enrich (derived fields)

Automatically calculate:

* Normal state (`Normal`)
* Alarm text (`Over Predicted kW Demand – MCC-01`)
* Alarm type (`Standard`)
* Hysteresis (`|A - B|`)

### Step 4 — Render Worksheet

Each alarm becomes **one worksheet block**.

---

# 5️⃣ Generated Rationalization Sheet (Auto-Filled)

Example (Excel / PDF / HTML):

```
--------------------------------------------------
Alarm ID: over_kw_demand_pred
Asset: MCC-01
Alarm Class: Energy
Category: Demand
--------------------------------------------------
Signal: Predicted Active Power Demand (kW)

Pickup Setpoint (A): 920 kW
Pickup Delay (ΔT1): 60 s
Dropout Setpoint (B): 880 kW
Dropout Delay (ΔT2): 120 s

Direction: Over
Priority: 3

Consequence:
Utility demand penalty

Operator Action:
Shed non-critical loads

Response Time:
< 5 minutes

Decision:
KEEP
--------------------------------------------------
```

Multiply this by 200 alarms → still consistent.

---

# 6️⃣ Multi-Format Output (Real Projects Need This)

From the same canonical object, you can generate:

| Output     | Use                      |
| ---------- | ------------------------ |
| Excel      | Engineering review       |
| PDF        | Audit / ISO / management |
| CSV        | Import to alarm DB       |
| JSON       | Version control / Git    |
| SQL INSERT | Alarm master table       |

**One definition → many views**

---

# 7️⃣ Common Automation Patterns (Seen in Plants)

### Pattern A — Excel-First (Most common)

```
Excel → JSON → Worksheets + SCADA
```

### Pattern B — Git-First (Advanced teams)

```
JSON (Git) → Excel (read-only) → PDF
```

### Pattern C — SCADA-Driven (Risky)

```
SCADA tags → JSON → Worksheet
```

⚠ Pattern C usually leaks garbage alarms into audits.

---

# 8️⃣ Typical Failure Modes (Learned the Hard Way)

* ❌ Letting operators edit worksheets manually
* ❌ No stable `alarm_id`
* ❌ Priority chosen emotionally
* ❌ Energy alarms with zero delay
* ❌ Copy-paste hysteresis with wrong polarity
* ❌ Treating events as alarms

---

## Implementation Watchouts + Dev Wisdom

* ⚠ **Canonical JSON is king** — everything else is a view
* ⚠ Excel is an input tool, not a source of truth
* ⚠ Enforce hysteresis automatically
* ⚠ If `operator_action` is empty → flag the alarm
* ⚠ Version alarms like code (Git tags per review)
* ✅ Generate worksheets, don’t author them
* 🧠 Alarm rationalization is a **data pipeline**, not documentation

If you want next, I can:

* Give you a **ready-to-run Python generator**
* Design a **PostgreSQL alarm master schema**
* Map this directly into **Ignition alarm UDTs**
* Auto-score alarms for nuisance probability

Tell me which one and I’ll go straight to implementation.
Design a PostgreSQL alarm master schema

Good choice. This is the **spine** of everything you discussed so far: meters, ISA-18.2, Excel, JSON, Ignition, audits.
If this schema is wrong, everything downstream is pain.

I’ll design a **PostgreSQL alarm master schema** that is:

* ISA-18.2 aligned
* Energy-focused (ISO 50001 friendly)
* Meter + SCADA agnostic
* Safe for Git / migrations
* Actually usable by engineers

No theory — straight build.

---

# 1️⃣ Design Principles (Why this looks the way it does)

Before tables, the **rules**:

1. **Alarm definition ≠ alarm event**
2. **One alarm = one stable ID**
3. Pickup/Dropout are **data**, not logic
4. Rationalization is **first-class**, not comments
5. Source systems (PM5110, Ignition, PLC) are *inputs*, not owners

This avoids the classic “SCADA owns alarms” trap.

---

# 2️⃣ Core Tables (Minimal but Complete)

## 2.1 `alarm_master` — Canonical Alarm Definition

This is the **single source of truth**.

```sql
CREATE TABLE alarm_master (
    alarm_id            TEXT PRIMARY KEY,     -- stable, human-readable
    asset_id            TEXT NOT NULL,         -- MCC-01, PFC-02, FEEDER-A
    alarm_name          TEXT NOT NULL,
    alarm_class         TEXT NOT NULL,         -- Energy, Electrical, PowerQuality
    category            TEXT NOT NULL,         -- Voltage, Current, Demand, PF
    alarm_type          TEXT NOT NULL CHECK (alarm_type IN ('standard', 'unary')),
    direction           TEXT CHECK (direction IN ('over', 'under')),
    signal_name         TEXT NOT NULL,         -- Predicted Active Power Demand
    signal_unit         TEXT NOT NULL,         -- kW, A, V, %
    enabled             BOOLEAN NOT NULL DEFAULT TRUE,
    priority            INTEGER NOT NULL CHECK (priority BETWEEN 1 AND 4),
    latching            BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMP NOT NULL DEFAULT now(),
    updated_at          TIMESTAMP NOT NULL DEFAULT now()
);
```

**Why this matters**

* `alarm_id` is what SCADA, Excel, JSON, and audits all reference
* `direction` lives here so thresholds stay clean
* Unary alarms stop here — no thresholds needed

---

## 2.2 `alarm_threshold` — Pickup A / Dropout B

Separated on purpose.

```sql
CREATE TABLE alarm_threshold (
    alarm_id            TEXT PRIMARY KEY
                            REFERENCES alarm_master(alarm_id)
                            ON DELETE CASCADE,
    pickup_value        NUMERIC NOT NULL,
    pickup_delay_s      NUMERIC NOT NULL CHECK (pickup_delay_s >= 0),
    dropout_value       NUMERIC NOT NULL,
    dropout_delay_s     NUMERIC NOT NULL CHECK (dropout_delay_s >= 0)
);
```

**Why**

* Makes hysteresis explicit
* Avoids NULL soup in unary alarms
* Easy validation queries

---

## 2.3 `alarm_rationalization` — ISA-18.2 Core

This is what auditors read.

```sql
CREATE TABLE alarm_rationalization (
    alarm_id            TEXT PRIMARY KEY
                            REFERENCES alarm_master(alarm_id)
                            ON DELETE CASCADE,
    consequence_type    TEXT NOT NULL,     -- Financial, Equipment, Safety
    consequence_desc    TEXT NOT NULL,
    operator_action     TEXT NOT NULL,
    response_time_min   INTEGER NOT NULL CHECK (response_time_min > 0),
    decision            TEXT NOT NULL CHECK (decision IN ('Keep', 'Modify', 'Remove')),
    last_reviewed_by    TEXT,
    last_reviewed_at    DATE
);
```

If this table is empty → **alarm should not exist**.

---

## 2.4 `alarm_source` — Where the Alarm Comes From

Meters, SCADA, PLCs — all treated equally.

```sql
CREATE TABLE alarm_source (
    source_id           SERIAL PRIMARY KEY,
    alarm_id            TEXT NOT NULL
                            REFERENCES alarm_master(alarm_id)
                            ON DELETE CASCADE,
    source_type         TEXT NOT NULL,     -- PM5110, Ignition, PLC
    source_ref          TEXT NOT NULL,     -- tag path, meter serial, register
    writable            BOOLEAN NOT NULL DEFAULT FALSE
);
```

This allows:

* Same alarm implemented in multiple systems
* Safe comparison (DB vs SCADA drift detection)

---

## 2.5 `alarm_limit_validation` — Engineering Guardrails

Optional but **extremely useful**.

```sql
CREATE TABLE alarm_limit_validation (
    alarm_id            TEXT PRIMARY KEY
                            REFERENCES alarm_master(alarm_id)
                            ON DELETE CASCADE,
    max_allowed_value   NUMERIC,
    validation_rule     TEXT               -- e.g. "CT_ratio * max_current"
);
```

Used for:

* Preventing impossible setpoints
* Auto-checking Excel imports

---

# 3️⃣ Unary Alarms (Clean Handling)

Unary alarms:

* Do **not** appear in `alarm_threshold`
* Still appear in `alarm_rationalization`

Example insert:

```sql
INSERT INTO alarm_master (
    alarm_id, asset_id, alarm_name, alarm_class,
    category, alarm_type, signal_name, signal_unit,
    priority
)
VALUES (
    'phase_reversal',
    'MCC-01',
    'Phase Reversal',
    'Electrical',
    'Phase',
    'unary',
    'Phase Rotation',
    '-',
    2
);
```

---

# 4️⃣ Example: Energy Demand Alarm (Complete)

```sql
INSERT INTO alarm_master VALUES (
    'over_kw_demand_pred',
    'MCC-01',
    'Over Predicted Active Power Demand',
    'Energy',
    'Demand',
    'standard',
    'over',
    'Predicted Active Power Demand',
    'kW',
    TRUE,
    3,
    FALSE,
    now(),
    now()
);

INSERT INTO alarm_threshold VALUES (
    'over_kw_demand_pred',
    920,
    60,
    880,
    120
);

INSERT INTO alarm_rationalization VALUES (
    'over_kw_demand_pred',
    'Financial',
    'Utility demand penalty',
    'Shed non-critical loads',
    5,
    'Keep',
    'Energy Manager',
    CURRENT_DATE
);
```

This single alarm is now:

* ISA-18.2 compliant
* ISO 50001 defensible
* SCADA-agnostic
* Versionable

---

# 5️⃣ Views You Will Actually Use

### 5.1 Audit View

```sql
CREATE VIEW v_alarm_audit AS
SELECT
    m.alarm_id,
    m.asset_id,
    m.alarm_name,
    m.priority,
    r.consequence_desc,
    r.operator_action,
    r.decision
FROM alarm_master m
JOIN alarm_rationalization r USING (alarm_id)
WHERE r.decision = 'Keep';
```

### 5.2 Alarm Quality Check

```sql
SELECT alarm_id
FROM alarm_master m
LEFT JOIN alarm_rationalization r USING (alarm_id)
WHERE r.operator_action IS NULL;
```

(These alarms should be killed.)

---

# 6️⃣ How This Ties Back to Excel / JSON / Ignition

| Layer      | Role             |
| ---------- | ---------------- |
| Excel      | Authoring input  |
| JSON       | Versioned config |
| PostgreSQL | Authority        |
| Ignition   | Runtime          |
| PM5110     | Signal provider  |

DB **wins every argument**.

---

## Implementation Watchouts + Dev Wisdom

* ⚠ Never let SCADA be the master of alarm logic
* ⚠ `alarm_id` must never change (treat like a primary key in life)
* ⚠ Do not store live alarm states here — that’s historian territory
* ⚠ Enforce hysteresis at insert time (trigger or validation job)
* ⚠ Unary alarms still require rationalization
* ✅ Keep schema boring — boring survives audits
* 🧠 Alarms are **data with consequences**, not events with timestamps

If you want next:

* DB triggers to auto-validate pickup/dropout logic
* Excel → PostgreSQL import pipeline
* Drift detection between DB and Ignition
* Full ISO 50001 energy KPI linkage

Say the word and we’ll wire it properly.

Ignition alarm pipeline (UDT → ISA states)
Good — this is where most Ignition systems quietly rot if not designed **intentionally**.

I’ll walk this like a real plant implementation:

**UDT alarm → Ignition runtime → ISA-18.2 states → historian / DB**

No fluff. This is how you wire it so it survives audits, tuning, and midnight calls.

---

# 1️⃣ Mental Model (Get This Straight First)

**Ignition alarms ≠ ISA alarm states by default**

Ignition gives you:

* `Active`
* `Acked`
* `Cleared`

ISA-18.2 requires:

* **Normal**
* **Active Unacknowledged**
* **Active Acknowledged**
* **Cleared Unacknowledged**
* **Shelved / Suppressed / Out-of-Service**

So we **derive ISA states** explicitly. Do not assume Ignition does it for you.

---

# 2️⃣ UDT Alarm Definition (Correct Way)

## 2.1 UDT Structure (Meter / Process Agnostic)

```
UDT: Alarm_Base
├── Value (Float / Int)
├── Alarm_Enable (Bool)
├── Alarm_Active (Bool)        -- runtime
├── Alarm_Acked (Bool)         -- runtime
├── Alarm_Shelved (Bool)
├── Alarm_Suppressed (Bool)
├── Alarm_OOS (Bool)
├── Alarm_ID (String)          -- matches DB alarm_id
├── Priority (Int)
├── Pickup (Float)
├── Dropout (Float)
├── PickupDelay_s (Float)
├── DropoutDelay_s (Float)
```

**Rule**

* `Alarm_ID` must exactly match PostgreSQL `alarm_master.alarm_id`
* No naming creativity allowed here

---

## 2.2 Ignition Alarm Configuration (Key Fields)

Inside the tag alarm:

| Field          | Value                   |
| -------------- | ----------------------- |
| Mode           | AboveValue / BelowValue |
| Setpoint       | `{[.]Pickup}`           |
| Clear Setpoint | `{[.]Dropout}`          |
| On Delay       | `{[.]PickupDelay_s}`    |
| Off Delay      | `{[.]DropoutDelay_s}`   |
| Enabled        | `{[.]Alarm_Enable}`     |
| Priority       | `{[.]Priority}`         |
| Ack Required   | true                    |
| Latching       | from DB                 |

This maps **1-to-1** with your alarm master schema. No hidden logic.

---

# 3️⃣ ISA-18.2 State Derivation Logic

We now compute ISA states **explicitly**, using Ignition runtime flags.

### Inputs (Ignition Runtime)

Ignition exposes:

* `Active`
* `Acked`
* `Cleared`
* `Shelved`
* `Suppressed`
* `Enabled`

---

## 3.1 ISA State Truth Table (This Is Critical)

| Ignition State      | ISA State                  |
| ------------------- | -------------------------- |
| Not Active          | **Normal**                 |
| Active & Not Acked  | **Active Unacknowledged**  |
| Active & Acked      | **Active Acknowledged**    |
| Cleared & Not Acked | **Cleared Unacknowledged** |
| Cleared & Acked     | **Normal**                 |
| Shelved             | **Shelved**                |
| Suppressed          | **Suppressed**             |
| Disabled            | **Out of Service**         |

This is **standard industry mapping**.

---

## 3.2 Expression Tag (ISA_State)

Create a derived tag in the UDT:

```text
if({[.]Alarm_OOS}, "OutOfService",
if({[.]Alarm_Suppressed}, "Suppressed",
if({[.]Alarm_Shelved}, "Shelved",
if({[.]Alarm_Active} && !{[.]Alarm_Acked}, "Active_Unack",
if({[.]Alarm_Active} && {.[.]Alarm_Acked}, "Active_Ack",
if(!{[.]Alarm_Active} && !{[.]Alarm_Acked}, "Cleared_Unack",
"Normal"
)))))))
```

Yes — ugly.
Yes — necessary.
Auditors love this.

---

# 4️⃣ Alarm Pipeline (End-to-End)

```
Sensor / Meter
   ↓
UDT Value Tag
   ↓
Ignition Alarm Engine
   ↓
Runtime Flags (Active, Acked, Cleared)
   ↓
ISA_State Expression Tag
   ↓
Alarm Journal / Tag Historian
   ↓
PostgreSQL alarm_event table
```

**Important**

* Alarm logic stays in UDT
* Alarm meaning stays in PostgreSQL
* Ignition is execution, not authority

---

# 5️⃣ Alarm Event Storage (PostgreSQL)

Do **not** store raw Ignition states only.

Store **derived ISA state**.

```sql
CREATE TABLE alarm_event (
    event_id        BIGSERIAL PRIMARY KEY,
    alarm_id        TEXT NOT NULL,
    asset_id        TEXT NOT NULL,
    isa_state       TEXT NOT NULL,
    event_time      TIMESTAMP NOT NULL,
    value           NUMERIC,
    operator        TEXT
);
```

This makes:

* KPI calculation trivial
* Nuisance alarm analysis possible
* ISO 50001 energy deviation tracking clean

---

# 6️⃣ Special Cases You Will Hit

### 🔹 Pickup A / Dropout B Missing

→ Alarm stays **Active Unack** forever
→ Catch with DB validation before deployment

### 🔹 Ack After Clear

ISA requires **Cleared Unack**
Ignition hides this unless you track it explicitly

### 🔹 Shelved ≠ Suppressed

* Shelved → operator action
* Suppressed → system logic
  Auditors check this distinction

---

# 7️⃣ How This Aligns with ISA-18.2 Lifecycle

| ISA Stage            | Where                   |
| -------------------- | ----------------------- |
| Identification       | PostgreSQL alarm_master |
| Rationalization      | alarm_rationalization   |
| Design               | UDT templates           |
| Implementation       | Ignition                |
| Operation            | Alarm Journal           |
| Monitoring           | ISA_State KPIs          |
| Management of Change | DB diff + Git           |

This is **textbook-correct** without being academic.

---

## Implementation Watchouts + Dev Wisdom

* ⚠ Never infer ISA state from timestamps alone
* ⚠ Do not store alarms only in Ignition — you’ll lose intent
* ⚠ Ack logic must survive clears (Cleared-Unack exists!)
* ⚠ Shelving must be visible and logged
* ⚠ Alarm_ID mismatch = silent failure
* ✅ Use UDT inheritance aggressively
* 🧠 If you can’t explain an alarm state to an operator in one sentence, it’s wrong

---

If you want next:

* Full Ignition UDT JSON export
* Alarm KPIs (standing, chattering, fleeting)
* Auto-generation of UDTs from PostgreSQL
* ISA-18.2 compliance report SQL

Say which one — we build it properly.

ISA-18.2 compliance report SQL

Good. This is a **real ISA-18.2 compliance report**, not a vanity dashboard.

I’ll assume:

* PostgreSQL
* Your **alarm_master**, **alarm_event**, **alarm_rationalization** already exist
* `isa_state` is already derived (as we discussed)

I’ll build this **exactly how auditors expect it**.

---

# 0️⃣ Assumed Core Tables (Minimal)

```sql
alarm_master (
  alarm_id,
  asset_id,
  alarm_name,
  priority,
  alarm_class,
  safety_critical BOOLEAN,
  enabled BOOLEAN
)

alarm_event (
  event_id,
  alarm_id,
  asset_id,
  isa_state,          -- Normal, Active_Unack, Active_Ack, Cleared_Unack, Shelved, Suppressed, OOS
  event_time,
  value
)

alarm_rationalization (
  alarm_id,
  cause,
  consequence,
  operator_response,
  time_to_respond_sec,
  justification,
  approved BOOLEAN
)
```

If you’re missing any of these → you’re already **non-compliant**.

---

# 1️⃣ Alarm Inventory Completeness (ISA-18.2 Clause 5)

> Every alarm must be rationalized

```sql
SELECT
  am.alarm_id,
  am.asset_id,
  am.alarm_name,
  CASE
    WHEN ar.alarm_id IS NULL THEN 'MISSING'
    WHEN ar.approved = false THEN 'NOT_APPROVED'
    ELSE 'OK'
  END AS rationalization_status
FROM alarm_master am
LEFT JOIN alarm_rationalization ar
  ON am.alarm_id = ar.alarm_id
ORDER BY rationalization_status DESC;
```

✅ Auditor question: *“Which alarms are not rationalized?”*
You answer with this.

---

# 2️⃣ Standing Alarms (> 24h Active)

ISA-18.2 red flag.

```sql
WITH active_alarms AS (
  SELECT
    alarm_id,
    asset_id,
    MIN(event_time) AS first_active_time
  FROM alarm_event
  WHERE isa_state IN ('Active_Unack', 'Active_Ack')
  GROUP BY alarm_id, asset_id
)
SELECT
  alarm_id,
  asset_id,
  first_active_time,
  NOW() - first_active_time AS duration
FROM active_alarms
WHERE NOW() - first_active_time > INTERVAL '24 hours'
ORDER BY duration DESC;
```

📌 Any alarm here = design or operational failure.

---

# 3️⃣ Alarm Rate (10-Minute Window)

ISA-18.2 recommended:

* ≤ 1 alarm / 10 min average
* ≤ 10 alarms / 10 min peak

```sql
WITH alarm_counts AS (
  SELECT
    date_trunc('minute', event_time)
      - INTERVAL '1 minute' * (EXTRACT(minute FROM event_time)::int % 10)
      AS window_start,
    COUNT(*) AS alarm_count
  FROM alarm_event
  WHERE isa_state = 'Active_Unack'
  GROUP BY window_start
)
SELECT
  window_start,
  alarm_count,
  CASE
    WHEN alarm_count > 10 THEN 'PEAK_VIOLATION'
    WHEN alarm_count > 1 THEN 'AVG_VIOLATION'
    ELSE 'OK'
  END AS compliance_status
FROM alarm_counts
ORDER BY window_start DESC;
```

Auditors love this one.

---

# 4️⃣ Chattering Alarms (Bad Configuration)

Definition (common practice):

> Same alarm activates ≥ 3 times in 10 minutes

```sql
WITH alarm_bursts AS (
  SELECT
    alarm_id,
    COUNT(*) AS activations,
    MIN(event_time) AS start_time,
    MAX(event_time) AS end_time
  FROM alarm_event
  WHERE isa_state = 'Active_Unack'
  GROUP BY alarm_id,
           date_trunc('minute', event_time)
           - INTERVAL '1 minute' * (EXTRACT(minute FROM event_time)::int % 10)
)
SELECT *
FROM alarm_bursts
WHERE activations >= 3
ORDER BY activations DESC;
```

🔧 These usually mean:

* Pickup/dropout too close
* No delay
* Bad sensor

---

# 5️⃣ Fleeting Alarms (< 10 seconds)

ISA-18.2 discourages these.

```sql
WITH transitions AS (
  SELECT
    alarm_id,
    event_time,
    isa_state,
    LEAD(event_time) OVER (PARTITION BY alarm_id ORDER BY event_time) AS next_time
  FROM alarm_event
)
SELECT
  alarm_id,
  event_time AS active_time,
  next_time AS clear_time,
  next_time - event_time AS duration
FROM transitions
WHERE isa_state = 'Active_Unack'
  AND next_time IS NOT NULL
  AND next_time - event_time < INTERVAL '10 seconds'
ORDER BY duration;
```

If many rows appear → filter or redesign.

---

# 6️⃣ Shelved / Suppressed Abuse

ISA requires justification.

```sql
SELECT
  alarm_id,
  isa_state,
  COUNT(*) AS occurrences,
  MAX(event_time) AS last_seen
FROM alarm_event
WHERE isa_state IN ('Shelved', 'Suppressed')
GROUP BY alarm_id, isa_state
ORDER BY occurrences DESC;
```

If an alarm is **permanently shelved**, it should be:

* Disabled
* Or removed from alarm_master

---

# 7️⃣ Operator Response Compliance

Did operators acknowledge within required time?

```sql
WITH response_times AS (
  SELECT
    ae.alarm_id,
    ae.event_time AS active_time,
    MIN(ae2.event_time) AS ack_time
  FROM alarm_event ae
  JOIN alarm_event ae2
    ON ae.alarm_id = ae2.alarm_id
   AND ae2.isa_state = 'Active_Ack'
   AND ae2.event_time > ae.event_time
  WHERE ae.isa_state = 'Active_Unack'
  GROUP BY ae.alarm_id, ae.event_time
)
SELECT
  rt.alarm_id,
  rt.ack_time - rt.active_time AS response_time,
  ar.time_to_respond_sec,
  CASE
    WHEN EXTRACT(EPOCH FROM (rt.ack_time - rt.active_time))
         <= ar.time_to_respond_sec
    THEN 'COMPLIANT'
    ELSE 'LATE'
  END AS response_status
FROM response_times rt
JOIN alarm_rationalization ar
  ON rt.alarm_id = ar.alarm_id;
```

This is **gold** for audits.

---

# 8️⃣ Final Compliance Summary (Executive View)

```sql
SELECT
  COUNT(*) FILTER (WHERE compliance_status <> 'OK') AS violations,
  COUNT(*) AS total_windows
FROM (
  SELECT
    CASE
      WHEN COUNT(*) > 10 THEN 'PEAK_VIOLATION'
      WHEN COUNT(*) > 1 THEN 'AVG_VIOLATION'
      ELSE 'OK'
    END AS compliance_status
  FROM alarm_event
  WHERE isa_state = 'Active_Unack'
  GROUP BY date_trunc('minute', event_time)
       - INTERVAL '1 minute' * (EXTRACT(minute FROM event_time)::int % 10)
) t;
```

---

## Implementation Watchouts + Dev Wisdom

* ⚠ **ISA-18.2 is evidence-based**, not configuration-based
* ⚠ If you can’t prove it in SQL, it didn’t happen
* ⚠ Standing alarms are the #1 audit failure
* ⚠ Shelving without justification = violation
* ⚠ Chattering alarms are engineering debt
* ✅ Store **state transitions**, not snapshots
* 🧠 Compliance reports should be **read-only**, reproducible, and versioned

---

If you want next:

* Auto-generated **PDF ISA-18.2 audit report**
* ISO 50001 energy deviation overlay
* Alarm KPI materialized views
* Ignition → PostgreSQL real-time alarm bridge

Say the word.
