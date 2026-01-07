# Unified Namespace Best Practices

```css
uns / 
    ├─ measurement/
    ├─ control/
    ├─ event/
    ├─ status/
    ├─ alarm/
    ├─ config/
    ├─ diagnostic/
    ├─ maintenance/
    ├─ kpi/
    ├─ recipe/
    |        ├─ batch_setpoints
    |        ├─ sequence_steps
    |        └─ quality_targets
    ├─ log/
    ├─ history/
    ├─ health/
    ├─ command/
    ├─ comm/
    ├─ security/
    ├─ meta/
    └─ asset/

```

> The empty branch costs nothing, but **namespace collisions** cost **everything**

---

## 01-measurement `What are we observing?`

Real-time process values from sensors.

```css
uns/measurement/temperature: 25.0
uns/measurement/humidity: 50.0
uns/measurement/pressure: 101.3
uns/measurement/voltage: 480.2
uns/measurement/current: 12.5
```

**Key insight**: Instantaneous sensor values only. NOT accumulated totals.

---

## 02-control `What do we want?`

Declarative setpoints - maintain these values.

```css
uns/control/target_temperature: 25.0
uns/control/target_speed: 1500
uns/control/pid_setpoint: 75.0
```

**Key insight**: Continuous setpoints (knobs), not one-time actions.

---

## 03-command `What action now?`

Imperative actions - do this NOW.

```css
uns/command/start: true
uns/command/stop: true
uns/command/reset: true
uns/command/acknowledge_alarm: {user: "john", alarm_id: "high_temp"}
```

**Key insight**: One-time actions (buttons), not continuous setpoints.

---

## 04-status `What mode is it in?`

Current device state - read-only.

```css
uns/status/running: true
uns/status/mode: "auto"
uns/status/connected: true
uns/status/active_recipe: "product_A"
```

**Key insight**: Current state only. NOT accumulated data, NOT errors.

---

## 05-alarm `What needs action NOW?`

Active alarms requiring operator response.

```css
uns/alarm/high_temperature: true
uns/alarm/overcurrent: true
uns/alarm/comm_failure: true
uns/alarm/summary: {
    active_count: 2,
    highest_severity: 1,
    newest: "high_temperature"
}
```

**Multi-level alarm configuration**:

```css
config/alarm/
    ├─ temp_high_high: {setpoint: 90, priority: 1, delay: 0}
    ├─ temp_high: {setpoint: 80, priority: 2, delay: 5}
    ├─ temp_low: {setpoint: 60, priority: 2, delay: 5}
    └─ temp_low_low: {setpoint: 50, priority: 1, delay: 0}
```

---

## 06-event `What happened?`

Discrete occurrences - something happened.

```css
uns/event/batch_started: {timestamp: "...", batch_id: "123"}
uns/event/batch_complete: {timestamp: "...", batch_id: "123"}
uns/event/mode_changed: {from: "auto", to: "manual"}
uns/event/recipe_loaded: {name: "product_A"}
```

**Key insight**: Occurrences, NOT states. NOT audit trail (use log/).

---

## 07-health `How does the device feel?`

Device self-diagnostics - monitoring itself.

```css
uns/health/bearing_condition: 0.72
uns/health/winding_temperature: 85.2
uns/health/cpu_load: 45
uns/health/memory_usage: 68
uns/health/comm_quality: 0.998
```

**Key insight**: Device health, NOT process measurements.

---

## 08-diagnostic `What went wrong?`

Troubleshooting data - for engineers debugging.

```css
uns/diagnostic/last_error_code: "E0423"
uns/diagnostic/last_error_description: "COMM_TIMEOUT"
uns/diagnostic/error_stack: [...]
uns/diagnostic/error_timestamp: "2024-01-01T14:30:00Z"
```

**Key insight**: For troubleshooting, NOT for operations dashboards.

---

## 09-kpi `What are the metrics?`

Calculated/accumulated business metrics.

```css
uns/kpi/runtime_hours: 8547
uns/kpi/total_energy_kwh: 1547892
uns/kpi/oee_percent: 78.5
uns/kpi/availability: 0.92
uns/kpi/parts_produced: 15847
```

**Key insight**: Accumulated or calculated. NOT instantaneous measurements.

---

## 10-config `What can I tune?`

Tunable parameters - keyboard to change.

```css
uns/config/alarm_threshold: 80.0
uns/config/display_units: "metric"
uns/config/ip_address: "192.168.1.100"
uns/config/service_interval_hours: 1000
uns/config/alarm/high_temp/setpoint: 85.0
```

**Key insight**: Admin/engineer changes only. NOT physical identity (use asset/).

---

## 11-asset `What is this device?`

Physical identity - wrench to change.

```css
uns/asset/serial_number: "ABC123456"
uns/asset/model: "PM5110"
uns/asset/manufacturer: "Schneider Electric"
uns/asset/install_date: "2024-06-15"
uns/asset/firmware_version: "1.2.3"
uns/asset/rated_power: 5.5
```

**Key insight**: Fixed at installation. Requires physical work to change.

---

## 12-maintenance `When do we service?`

Service records and schedules.

```css
uns/maintenance/last_service_date: "2024-01-01"
uns/maintenance/next_service_date: "2024-04-01"
uns/maintenance/service_interval: "90 days"
uns/maintenance/service_type: "oil_change"
uns/maintenance/technician: "john.smith"
```

**Key insight**: Service scheduling, NOT device health metrics (use health/).

---

## 13-recipe `What's the product definition?`

Product-specific process definitions.

```css
uns/recipe/product_A/
    ├─ batch_setpoints: {temp: 75, time: 60, speed: 1500}
    ├─ sequence_steps: [
    │     {step: 1, action: "heat", duration: 300},
    │     {step: 2, action: "mix", duration: 600}
    │   ]
    └─ quality_targets: {tolerance: 0.5, min_weight: 99.5}
```

**Key insight**: Changes per product, NOT rarely like config/.

---

## 14-log `Who did what when?`

Audit trail - compliance and accountability.

```css
uns/log/operator_action: {user: "john", action: "start", timestamp: "..."}
uns/log/recipe_change: {user: "jane", from: "A", to: "B", timestamp: "..."}
uns/log/alarm_ack: {user: "john", alarm_id: "high_temp", timestamp: "..."}
uns/log/setpoint_change: {user: "jane", param: "speed", old: 1000, new: 1500}
```

**Key insight**: WHO did WHAT for audit. NOT just WHAT happened (use event/).

---

## 15-history `What was the past?`

Archived data for post-mortem analysis.

```css
uns/history/alarm_archive: [
    {id: "high_temp", triggered: "...", cleared: "...", acked_by: "john"}
]
uns/history/measurement_snapshots: [...]
uns/history/production_log: [...]
```

**Key insight**: Archived records, NOT active events.

---

## 16-comm `Is the connection healthy?`

Communication infrastructure metadata.

```css
uns/comm/device_timestamp: "2025-01-04T10:30:00Z"
uns/comm/last_message_received: "2025-01-04T10:29:55Z"
uns/comm/protocol: "Modbus TCP"
uns/comm/address: "192.168.1.50:502"
uns/comm/poll_rate_ms: 100
```

**Key insight**: Infrastructure data, NOT process values.

---

## 17-security `Who has access?`

Authentication and access control.

```css
uns/security/current_user: "operator_1"
uns/security/access_level: 2
uns/security/session_expires: "2025-01-04T12:00:00Z"
uns/security/last_login: "2025-01-04T08:00:00Z"
```

**Key insight**: Access control domain. Never put in status/ or config/.

---

## 18-meta `What does this namespace mean?`

Self-documenting namespace definitions.

```css
uns/meta/schema_version: "2.1"
uns/meta/last_updated: "2025-01-01"
uns/meta/contact: "controls-team@company.com"
uns/meta/branch_descriptions: {
    "measurement": "Process values at 100ms",
    "alarm": "Active alarms requiring action",
    "config": "Tunable parameters, supervisor role"
}
```

**Key insight**: In 3 years, no one remembers why health/ exists. Document it.

---

## Namespace Quick Reference

| Namespace | Purpose | Data Flow | Writable | Primary Consumer |
|-----------|---------|-----------|----------|------------------|
| `measurement/` | Process sensor data | FROM device | ❌ | Historian |
| `control/` | Declarative setpoints | TO device | ✅ | Control System |
| `command/` | Imperative actions | TO device | ✅ | Operator |
| `status/` | Current device state | FROM device | ❌ | Dashboard |
| `alarm/` | Active exceptions | FROM device | ❌ | Notification |
| `event/` | Discrete occurrences | FROM device | ❌ | Analytics |
| `health/` | Device self-diagnostics | FROM device | ❌ | Maintenance |
| `diagnostic/` | Troubleshooting data | FROM device | ❌ | Engineer |
| `kpi/` | Calculated metrics | FROM device | ❌ | BI |
| `config/` | Tunable parameters | ABOUT device | ✅ | Engineer |
| `asset/` | Physical identity | ABOUT device | ❌ | CMMS |
| `maintenance/` | Service records | ABOUT device | ✅ | CMMS |
| `recipe/` | Process definitions | TO device | ✅ | Production |
| `log/` | Audit trail | FROM device | ❌ | Compliance |
| `history/` | Historical archive | FROM device | ❌ | Analyst |
| `comm/` | Communication metadata | FROM device | ❌ | IT |
| `security/` | Access control | ABOUT device | ✅ | Admin |
| `meta/` | Namespace docs | ABOUT namespace | ✅ | Developer |

---

## The Final Expert Tests

Before committing, ask:

1. **"Can I explain this to a new hire in 30 seconds?"**
   - If not, the placement is too clever.

2. **"Will this break if we add 50 more devices?"**
   - Tests scalability of the pattern.

3. **"Can I write one SQL query to get all measurements across all devices?"**
   - Tests query predictability: `SELECT * WHERE topic LIKE '%/measurement/%'`

4. **"If this value is missing, which dashboard breaks?"**
   - Tests if criticality matches branch placement.

5. **"Does this require a WRENCH or a KEYBOARD to change?"**
   - Wrench → `asset/`. Keyboard → `config/`.

6. **"Is this about the DEVICE or the PROCESS?"**
   - Device health → `health/`. Process values → `measurement/`.

7. **"Who needs to see this: Operator, Engineer, or Compliance?"**
   - Operator → `status/`, `alarm/`. Engineer → `diagnostic/`. Compliance → `log/`.

---