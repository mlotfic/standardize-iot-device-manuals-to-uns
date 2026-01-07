# 02. The Expert's Checklist (For Every Single Parameter)

## The file now includes - For each of the 4 tests:

1. **Mutability Test** 
    - Use cases grouped by: Constant, Rarely, Continuous, Event-driven, Append-only
2. **Directionality Test** 
    - Use cases grouped by: TO device, FROM device, ABOUT device
3. **Calculation Test** 
    - Use cases by calculation type + gray area examples table
4. **Action Test** 
    - Use cases by urgency level (URGENT, INFORM, INVESTIGATE, ANALYZE, AUDIT, etc.)



## 1. **The Mutability Test** `Does this EVER change during operation?`

```cs
YES → measurement/, status/, health/, kpi/, alarm/, event/, diagnostic/, log/, history/, comm/
NO  → asset/, meta/, config/
RARELY → config/, maintenance/, security/, recipe/
```

### Use Cases by Mutability

| Mutability | Namespace | Example | Description |
|------------|-----------|---------|-------------|
| Constant | `asset/` | serial_number | Never changes after install |
| Constant | `meta/` | schema_version | Namespace documentation |
| Rarely | `config/` | alarm_threshold | Admin changes only |
| Rarely | `maintenance/` | last_service_date | Service events |
| Rarely | `security/` | access_level | Auth changes |
| Rarely | `recipe/` | batch_setpoints | Per-product changes |
| Continuous | `measurement/` | temperature | Sensor readings |
| Continuous | `status/` | running | Device state |
| Continuous | `health/` | cpu_load | Self-diagnostics |
| Continuous | `alarm/` | high_temp | Active exceptions |
| Continuous | `kpi/` | runtime_hours | Accumulated metrics |
| Continuous | `comm/` | device_timestamp | Sync data |
| Event-driven | `event/` | batch_complete | Discrete occurrences |
| Event-driven | `diagnostic/` | last_error_code | Error events |
| Append-only | `log/` | operator_actions | Audit trail |
| Append-only | `history/` | alarm_history | Archive |

---

## 2. **The Directionality Test** `Is this data flowing IN or OUT or ABOUT the device?`

```cs
IN (to device):
├─ command/ → imperative (do this now)
├─ control/ → declarative (maintain this)
└─ recipe/ → process definitions (what to make)

OUT (from device):
├─ measurement/ → process observations
├─ status/ → device state
├─ health/ → self-diagnostics
├─ alarm/ → exceptions requiring action
├─ event/ → discrete occurrences
├─ diagnostic/ → troubleshooting data
├─ kpi/ → calculated metrics
├─ log/ → audit trail
├─ history/ → archived data
└─ comm/ → communication metadata

ABOUT (metadata):
├─ asset/ → physical identity
├─ config/ → operational parameters
├─ maintenance/ → service records
├─ security/ → access control
└─ meta/ → namespace documentation
```

### Use Cases by Directionality

| Direction | Namespace | Example | Use Case |
|-----------|-----------|---------|----------|
| **TO** | `command/` | start | Operator presses HMI button |
| **TO** | `control/` | target_speed | PID loop setpoint |
| **TO** | `recipe/` | batch_setpoints | Load product recipe |
| **FROM** | `measurement/` | temperature | Historian trending |
| **FROM** | `status/` | running | Dashboard display |
| **FROM** | `health/` | winding_temp | Predictive maintenance |
| **FROM** | `alarm/` | high_pressure | Operator response |
| **FROM** | `event/` | batch_complete | Analytics correlation |
| **FROM** | `diagnostic/` | error_code | Engineering debug |
| **FROM** | `kpi/` | oee_percent | Business reporting |
| **FROM** | `log/` | operator_action | Compliance audit |
| **FROM** | `history/` | alarm_archive | Post-mortem analysis |
| **FROM** | `comm/` | timestamp | Time synchronization |
| **ABOUT** | `asset/` | serial_number | Asset registry |
| **ABOUT** | `config/` | max_speed | Parameter tuning |
| **ABOUT** | `maintenance/` | next_service | Service scheduling |
| **ABOUT** | `security/` | role | Access control |
| **ABOUT** | `meta/` | schema_version | Self-documentation |

---

## 3. **The Calculation Test** `Is this measured or calculated?`

```cs
Measured directly:
└─ measurement/ → raw sensor data

Calculated from measurements:
├─ kpi/ → if derived and business-relevant
├─ health/ → if diagnostic score
└─ Still measurement/ → if it's just unit conversion

Aggregated over time:
├─ kpi/ → accumulated totals
├─ history/ → archived snapshots
└─ log/ → action records
```

### Use Cases by Calculation Type

| Calculation | Namespace | Example | Description |
|-------------|-----------|---------|-------------|
| Raw sensor | `measurement/` | pressure_psi | Direct reading |
| Unit conversion | `measurement/` | pressure_kpa | Same data, different unit |
| Real-time transform | `measurement/` | fft_spectrum | No history needed |
| Diagnostic score | `health/` | bearing_condition | Algorithm output |
| Window average | `kpi/` | demand_15min | Rolling calculation |
| Accumulated total | `kpi/` | energy_kwh | Counter/totalizer |
| Historical snapshot | `history/` | alarm_archive | Time-stamped record |
| Audit record | `log/` | action_log | Who did what when |

**Gray areas experts watch for:**

| Parameter | Naive Choice | Expert Choice | Reason |
|-----------|--------------|---------------|--------|
| FFT spectrum | `kpi/` | `measurement/` | Real-time, no history |
| Runtime hours | `measurement/` | `kpi/` | Accumulated, not instant |
| Bearing score | `measurement/` | `health/` | Diagnostic, not process |
| Error count | `diagnostic/` | `health/` | MTBF metric |

---

## 4. **The Action Test** `What happens if this value is wrong or missing?`

```cs
Human must respond urgently:
└─ alarm/

Process continues but operators should know:
├─ status/
└─ event/

Analytics might flag it later:
├─ kpi/
└─ health/

Nothing immediate:
├─ measurement/ (just data)
├─ log/ (audit only)
└─ history/ (archive)

System impact:
├─ comm/ (sync issues)
└─ security/ (access issues)

Configuration impact:
├─ config/ (wrong behavior)
├─ recipe/ (wrong product)
└─ asset/ (identity confusion)
```

### Use Cases by Action Required

| Urgency | Namespace | Example | Action Required |
|---------|-----------|---------|-----------------|
| **URGENT** | `alarm/` | high_pressure | Stop production |
| **URGENT** | `security/` | intrusion_detected | Lock down |
| **INFORM** | `status/` | mode_changed | Update dashboard |
| **INFORM** | `event/` | batch_started | Log occurrence |
| **INVESTIGATE** | `health/` | bearing_score | Schedule maintenance |
| **INVESTIGATE** | `diagnostic/` | error_code | Debug issue |
| **ANALYZE** | `kpi/` | oee_dropped | Review performance |
| **ANALYZE** | `measurement/` | temp_spike | Trend analysis |
| **AUDIT** | `log/` | recipe_changed | Compliance check |
| **REFERENCE** | `history/` | past_alarms | Post-mortem |
| **SYNC** | `comm/` | clock_drift | Fix time sync |
| **TUNE** | `config/` | wrong_threshold | Adjust setting |
| **LOAD** | `recipe/` | wrong_setpoints | Load correct recipe |
| **VERIFY** | `asset/` | wrong_serial | Check installation |

---

## Combined Decision Matrix

```json
{
  "tests": {
    "mutability": ["constant", "rarely", "continuous", "event_driven", "append_only"],
    "directionality": ["to_device", "from_device", "about_device"],
    "calculation": ["raw", "converted", "transformed", "scored", "aggregated", "archived"],
    "action": ["urgent", "inform", "investigate", "analyze", "audit", "reference", "sync", "tune"]
  },
  "namespace_profiles": {
    "measurement/": { "mutability": "continuous", "direction": "from", "calc": "raw", "action": "analyze" },
    "control/": { "mutability": "continuous", "direction": "to", "calc": "n/a", "action": "tune" },
    "command/": { "mutability": "event_driven", "direction": "to", "calc": "n/a", "action": "urgent" },
    "status/": { "mutability": "continuous", "direction": "from", "calc": "n/a", "action": "inform" },
    "alarm/": { "mutability": "event_driven", "direction": "from", "calc": "n/a", "action": "urgent" },
    "event/": { "mutability": "event_driven", "direction": "from", "calc": "n/a", "action": "inform" },
    "health/": { "mutability": "continuous", "direction": "from", "calc": "scored", "action": "investigate" },
    "diagnostic/": { "mutability": "event_driven", "direction": "from", "calc": "n/a", "action": "investigate" },
    "kpi/": { "mutability": "continuous", "direction": "from", "calc": "aggregated", "action": "analyze" },
    "config/": { "mutability": "rarely", "direction": "about", "calc": "n/a", "action": "tune" },
    "asset/": { "mutability": "constant", "direction": "about", "calc": "n/a", "action": "reference" },
    "maintenance/": { "mutability": "rarely", "direction": "about", "calc": "n/a", "action": "investigate" },
    "recipe/": { "mutability": "rarely", "direction": "to", "calc": "n/a", "action": "tune" },
    "log/": { "mutability": "append_only", "direction": "from", "calc": "archived", "action": "audit" },
    "history/": { "mutability": "append_only", "direction": "from", "calc": "archived", "action": "reference" },
    "comm/": { "mutability": "continuous", "direction": "from", "calc": "n/a", "action": "sync" },
    "security/": { "mutability": "rarely", "direction": "about", "calc": "n/a", "action": "urgent" },
    "meta/": { "mutability": "constant", "direction": "about", "calc": "n/a", "action": "reference" }
  }
}
```

---
