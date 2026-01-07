# 05. The Gotchas Experts Watch For

Common mistakes that pollute namespaces and break consumers. Learn from these anti-patterns.

---

## 1. **Overloading `status/`**

```cs
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

**Namespaces misused**: `status/` → should be `kpi/`, `maintenance/`, `diagnostic/`, `asset/`

---

## 2. **The Alarm State Explosion**

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

**Related**: Use `history/alarm/` for historical alarms, `config/alarm/` for thresholds.

---

## 3. **The Config vs. Asset Boundary**

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

**Rule of thumb**: If it requires a **wrench** to change → `asset/`. If it requires a **keyboard** → `config/`.

---

## 4. **Confusing `measurement/` with `kpi/`**

```cs
❌ BAD:
measurement/total_energy_kwh: 1547892
measurement/runtime_hours: 8547
measurement/oee_percent: 78.5

✅ GOOD:
measurement/power_kw: 28.7           ← Instantaneous
kpi/total_energy_kwh: 1547892        ← Accumulated
kpi/runtime_hours: 8547              ← Accumulated
kpi/oee_percent: 78.5                ← Calculated
```

**Why**: `measurement/` is for **instantaneous sensor values**. `kpi/` is for **accumulated or calculated metrics**.

**Test**: Can you reset it? → `kpi/`. Is it real-time? → `measurement/`.

---

## 5. **Mixing `health/` with `measurement/`**

```cs
❌ BAD:
measurement/motor_winding_temp: 85.2
measurement/bearing_vibration: 2.3
measurement/cpu_load: 45

✅ GOOD:
measurement/process_temp: 75.2       ← What device MONITORS
health/winding_temp: 85.2            ← Device MONITORING ITSELF
health/bearing_vibration: 2.3
health/cpu_load: 45
```

**Why**: `measurement/` = what the device is *watching*. `health/` = how the device *feels*.

**Test**: If this fails, does the **device** need service or does the **process** need attention?

---

## 6. **Dumping Everything in `event/`**

```cs
❌ BAD:
event/alarm_triggered
event/operator_login
event/recipe_loaded
event/service_complete
event/error_occurred

✅ GOOD:
alarm/high_pressure: true            ← Active alarm state
security/login: {user, timestamp}    ← Security domain
recipe/active: "ProductA"            ← Recipe state
event/batch_complete                 ← Discrete occurrence
log/operator_action: {...}           ← Audit trail
diagnostic/last_error: {...}         ← Troubleshooting
```

**Why**: `event/` is for **discrete occurrences** (batch started, mode changed), not for state or audit.

---

## 7. **The `control/` vs `command/` Confusion**

```cs
❌ BAD:
control/start_motor: true
control/emergency_stop: true

✅ GOOD:
command/start: true                  ← Imperative (do this NOW)
command/emergency_stop: true
control/target_speed: 1500           ← Declarative (maintain this)
control/target_temp: 75.0
```

**Why**: `command/` = one-time actions (buttons). `control/` = continuous setpoints (knobs).

**Test**: Press once → `command/`. Adjust continuously → `control/`.

---

## 8. **Forgetting `log/` for Audit Trail**

```cs
❌ BAD:
event/operator_changed_recipe
event/alarm_acknowledged
event/setpoint_adjusted

✅ GOOD:
log/recipe_change: {from, to, user, timestamp}      ← WHO did WHAT
log/alarm_ack: {alarm_id, user, timestamp}
log/setpoint_change: {param, old, new, user}
event/batch_complete                                 ← Just WHAT happened
```

**Why**: `log/` includes **who** for compliance/audit. `event/` is just **what** happened.

---

## 9. **Neglecting `diagnostic/` for Troubleshooting**

```cs
❌ BAD:
status/last_error: "COMM_TIMEOUT"
status/error_count: 15
alarm/error_occurred: true

✅ GOOD:
alarm/active_fault: true              ← Needs attention NOW
diagnostic/last_error_code: "E0423"   ← For debugging
diagnostic/last_error_desc: "COMM_TIMEOUT"
diagnostic/error_stack: [...]
health/error_count_total: 15          ← For MTBF
```

**Why**: `diagnostic/` is for **engineers debugging**, not operators. Keep it separate.

---

## 10. **Missing `recipe/` for Batch Manufacturing**

```cs
❌ BAD:
config/product_A_temp: 75
config/product_A_time: 60
config/product_B_temp: 80
config/product_B_time: 45

✅ GOOD:
recipe/product_A/setpoints: {temp: 75, time: 60}
recipe/product_A/sequence_steps: [...]
recipe/product_A/quality_targets: {...}
recipe/product_B/setpoints: {temp: 80, time: 45}
status/active_recipe: "product_A"
```

**Why**: Recipes change **per product**, config changes **rarely**. Different lifecycles.

---

## 11. **Ignoring `comm/` for Infrastructure**

```cs
❌ BAD:
measurement/device_timestamp: "..."
status/connected: true
health/message_count: 15847

✅ GOOD:
comm/device_timestamp: "2025-01-04T10:30:00Z"
comm/protocol: "Modbus TCP"
comm/address: "192.168.1.50:502"
comm/last_message: "2025-01-04T10:29:55Z"
status/connected: true                ← OK here too
health/comm_quality: 0.998
```

**Why**: `comm/` is for **infrastructure metadata**, not process data.

---

## 12. **Skipping `meta/` Documentation**

```cs
❌ BAD:
(No meta/ at all - undocumented namespace)

✅ GOOD:
meta/schema_version: "2.1"
meta/last_updated: "2025-01-01"
meta/contact: "controls-team@company.com"
meta/documentation_url: "https://docs.../device-xyz"
meta/branch_descriptions: {
  "measurement": "Process values sampled at 100ms",
  "alarm": "Active alarms requiring operator action",
  "config": "Tunable parameters, requires supervisor role"
}
```

**Why**: In 3 years, no one will remember why `health/` exists. Self-documenting namespaces survive turnover.

---

## 13. **Putting Security Data in Wrong Places**

```cs
❌ BAD:
status/current_user: "operator_1"
config/password: "secret123"
event/login_failed: {...}

✅ GOOD:
security/current_user: "operator_1"
security/access_level: 2
security/session_expires: "2025-01-04T12:00:00Z"
log/login_attempt: {user, success, ip, timestamp}
alarm/intrusion_detected: false
```

**Why**: Security is its own domain. Never put passwords in config or user info in status.

---

## 14. **History vs Event Confusion**

```cs
❌ BAD:
event/alarm_history: [...]
event/production_archive: [...]

✅ GOOD:
event/alarm_triggered              ← Recent occurrence
event/batch_started
history/alarm_archive: [...]       ← Past records
history/production_log: [...]
```

**Why**: `event/` is for **recent/current** discrete occurrences. `history/` is for **archived** data.

---

## Gotcha Summary Matrix

| Gotcha | Namespace Misused | Should Be | Test |
|--------|-------------------|-----------|------|
| Overloading status | `status/` | `kpi/`, `maintenance/`, `asset/` | Is it current mode? |
| Alarm explosion | `alarm/` | Structured + summary | Too many topics? |
| Config vs asset | `config/` ↔ `asset/` | Wrench vs keyboard | How to change it? |
| Measurement vs KPI | `measurement/` | `kpi/` | Instant or accumulated? |
| Health vs measurement | `measurement/` | `health/` | Device or process? |
| Event overload | `event/` | `log/`, `alarm/`, etc. | State or occurrence? |
| Control vs command | `control/` ↔ `command/` | Button vs knob | Once or continuous? |
| Missing log | `event/` | `log/` | Need WHO + WHAT? |
| Troubleshooting mix | `status/` | `diagnostic/` | For debugging? |
| Recipe missing | `config/` | `recipe/` | Changes per product? |
| Comm data | `measurement/` | `comm/` | Infrastructure? |
| No meta | (missing) | `meta/` | Documented? |
| Security leak | `status/`, `config/` | `security/` | Access control? |
| History confusion | `event/` | `history/` | Archived data? |

---

| #	|Gotcha	|Key Test|
|---|---|---|
|1	|Overloading `status/`	|Is it current mode?|
|2	|Alarm explosion	|Too many topics?|
|3	|Config vs Asset	|Wrench or keyboard?|
|4	|Measurement vs KPI	|Instant or accumulated?|
|5	|Health vs Measurement	|Device or process issue?|
|6	|Event overload	|State or occurrence?|
|7	|Control vs Command	|Button or knob?|
|8	|Missing `log/`	|Need WHO + WHAT?|
|9	|Troubleshooting mix	|For debugging?|
|10	|Recipe missing	|Changes per product?|
|11	|Comm data misplaced	|Infrastructure?|
|12	|No `meta/`	|Documented?|
|13	|Security leaks	|Access control?|
|14	|History vs Event	|Archived data?|