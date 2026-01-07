# 04. The Mental Model: "Perspectives"

Expert architects think in **consumer perspectives** - who will use this data and why?

---

## Operator Perspective `What do I need on my HMI right now?`

The operator needs real-time visibility and control.

```cs
status/      → Current states (running/stopped/faulted)
measurement/ → Process values to monitor (temp, pressure, flow)
alarm/       → Active exceptions I must handle NOW
command/     → Buttons I can press (start, stop, reset)
control/     → Setpoints I can adjust (speed, temperature)
event/       → Recent state changes (batch started, mode changed)
```

### Operator Use Cases

| Namespace | Example | Operator Action |
|-----------|---------|-----------------|
| `status/` | running: true | Verify machine is operating |
| `measurement/` | temperature: 75.2 | Monitor process values |
| `alarm/` | high_pressure: true | Respond urgently |
| `command/` | start_button | Press to start machine |
| `control/` | target_speed: 1500 | Adjust setpoint |
| `event/` | batch_started | Acknowledge occurrence |

---

## Maintenance Perspective `What tells me when/why to service?`

Maintenance needs predictive insights and service history.

```cs
health/       → Device condition scores (bearing, motor temp)
kpi/          → Wear accumulation (runtime_hours, cycles)
maintenance/  → Service records (last_service, next_due)
diagnostic/   → Error history (last_error, error_count)
event/        → Service events (maintenance_complete)
alarm/        → Critical failures needing immediate attention
config/       → Service intervals to adjust
asset/        → Equipment identity (serial, install_date)
```

### Maintenance Use Cases

| Namespace | Example | Maintenance Action |
|-----------|---------|-------------------|
| `health/` | bearing_score: 0.72 | Schedule replacement |
| `kpi/` | runtime_hours: 8547 | Plan preventive service |
| `maintenance/` | next_service: "2025-04-01" | Schedule work order |
| `diagnostic/` | error_count: 15 | Investigate root cause |
| `event/` | service_completed | Log service record |
| `asset/` | install_date: "2020-06-15" | Track equipment age |

---

## Analytics Perspective `What do I trend and analyze?`

Analytics needs historical data and calculated metrics.

```cs
measurement/ → High-frequency process data (100ms samples)
kpi/         → Calculated performance metrics (OEE, efficiency)
event/       → State changes for correlation analysis
history/     → Archived snapshots for post-mortem
log/         → Audit trail for compliance
health/      → Device degradation trends
```

### Analytics Use Cases

| Namespace | Example | Analytics Action |
|-----------|---------|-----------------|
| `measurement/` | temperature_log | Trend analysis |
| `kpi/` | oee_percent: 78.5 | Performance dashboard |
| `event/` | batch_complete | Production correlation |
| `history/` | alarm_archive | Root cause analysis |
| `log/` | operator_actions | Compliance reporting |
| `health/` | degradation_trend | Predictive modeling |

---

## Configuration Perspective `What can I tune?`

Configuration engineers need access to adjustable parameters.

```cs
config/       → Adjustable parameters (thresholds, limits)
control/      → Control loop setpoints (PID tuning)
config/alarm/ → Alarm thresholds (high/low limits)
recipe/       → Product-specific settings
security/     → Access control settings
```

### Configuration Use Cases

| Namespace | Example | Config Action |
|-----------|---------|---------------|
| `config/` | max_speed: 3000 | Set operating limits |
| `control/` | pid_kp: 2.5 | Tune control loops |
| `config/alarm/` | high_temp_threshold: 85 | Adjust alarm points |
| `recipe/` | product_A_setpoints | Load product recipe |
| `security/` | operator_permissions | Manage access levels |

---

## Production/Scheduling Perspective `What's the production status?`

Production managers need batch and scheduling visibility.

```cs
status/   → Current production state
recipe/   → Active product recipe
kpi/      → Production counts and rates
event/    → Batch events (started, completed)
log/      → Production audit trail
control/  → Production setpoints
```

### Production Use Cases

| Namespace | Example | Production Action |
|-----------|---------|-------------------|
| `status/` | active_recipe: "ProductA" | Verify correct product |
| `recipe/` | batch_setpoints | Load recipe for changeover |
| `kpi/` | parts_produced: 1547 | Track production count |
| `event/` | batch_complete | Log batch completion |
| `log/` | recipe_change | Audit product changes |

---

## IT/Infrastructure Perspective `Is the system healthy?`

IT needs communication and system health visibility.

```cs
comm/        → Communication status (timestamps, protocols)
health/      → System health (CPU, memory, connectivity)
diagnostic/  → System errors (comm_errors, timeouts)
meta/        → Schema documentation
security/    → Authentication and access
config/      → Network and communication settings
```

### IT/Infrastructure Use Cases

| Namespace | Example | IT Action |
|-----------|---------|-----------|
| `comm/` | device_timestamp | Verify time sync |
| `health/` | cpu_load: 45% | Monitor system resources |
| `diagnostic/` | comm_error: "TIMEOUT" | Troubleshoot connectivity |
| `meta/` | schema_version: "2.1" | Verify integration compatibility |
| `security/` | active_sessions | Monitor access |
| `config/` | ip_address | Configure networking |

---

## Asset Management Perspective `What equipment do we have?`

Asset managers need equipment identity and lifecycle data.

```cs
asset/       → Physical identity (serial, model, manufacturer)
maintenance/ → Service history and schedules
kpi/         → Utilization and runtime metrics
health/      → Equipment condition scores
history/     → Lifecycle events
```

### Asset Management Use Cases

| Namespace | Example | Asset Action |
|-----------|---------|--------------|
| `asset/` | serial_number: "ABC123" | Equipment registry |
| `asset/` | install_date: "2020-06-15" | Track equipment age |
| `maintenance/` | service_history | Review maintenance records |
| `kpi/` | utilization: 0.85 | Capacity planning |
| `health/` | overall_condition: 0.78 | Replacement planning |

---

## Compliance/Audit Perspective `Can we prove what happened?`

Compliance needs immutable audit trails and documentation.

```cs
log/      → Operator actions (who did what when)
event/    → System events (state changes)
history/  → Archived data (alarms, measurements)
security/ → Access logs (logins, permission changes)
meta/     → System documentation
```

### Compliance Use Cases

| Namespace | Example | Compliance Action |
|-----------|---------|-------------------|
| `log/` | operator_action | Audit trail for FDA |
| `event/` | recipe_loaded | Track product changes |
| `history/` | alarm_archive | Incident investigation |
| `security/` | login_history | Security audit |
| `meta/` | schema_documentation | System documentation |

---

## Perspective-to-Namespace Matrix

| Perspective | Primary Namespaces | Secondary Namespaces |
|-------------|-------------------|----------------------|
| **Operator** | `status/`, `measurement/`, `alarm/`, `command/` | `control/`, `event/` |
| **Maintenance** | `health/`, `maintenance/`, `diagnostic/` | `kpi/`, `event/`, `asset/` |
| **Analytics** | `measurement/`, `kpi/`, `history/` | `event/`, `log/`, `health/` |
| **Configuration** | `config/`, `control/`, `recipe/` | `security/`, `alarm/` |
| **Production** | `status/`, `recipe/`, `kpi/` | `event/`, `log/`, `control/` |
| **IT/Infrastructure** | `comm/`, `health/`, `meta/` | `diagnostic/`, `security/`, `config/` |
| **Asset Management** | `asset/`, `maintenance/` | `kpi/`, `health/`, `history/` |
| **Compliance** | `log/`, `history/`, `security/` | `event/`, `meta/` |

---

## Namespace Coverage by Perspective

| Namespace | Operator | Maint | Analytics | Config | Prod | IT | Asset | Compliance |
|-----------|:--------:|:-----:|:---------:|:------:|:----:|:--:|:-----:|:----------:|
| `measurement/` | ✅ | | ✅ | | | | | |
| `control/` | ✅ | | | ✅ | ✅ | | | |
| `command/` | ✅ | | | | | | | |
| `status/` | ✅ | | | | ✅ | | | |
| `alarm/` | ✅ | ✅ | | | | | | |
| `event/` | ✅ | ✅ | ✅ | | ✅ | | | ✅ |
| `health/` | | ✅ | ✅ | | | ✅ | ✅ | |
| `diagnostic/` | | ✅ | | | | ✅ | | |
| `kpi/` | | ✅ | ✅ | | ✅ | | ✅ | |
| `config/` | | ✅ | | ✅ | | ✅ | | |
| `asset/` | | ✅ | | | | | ✅ | |
| `maintenance/` | | ✅ | | | | | ✅ | |
| `recipe/` | | | | ✅ | ✅ | | | |
| `log/` | | | ✅ | | ✅ | | | ✅ |
| `history/` | | | ✅ | | | | ✅ | ✅ |
| `comm/` | | | | | | ✅ | | |
| `security/` | | | | ✅ | | ✅ | | ✅ |
| `meta/` | | | | | | ✅ | | ✅ |

---

| Perspective | Primary Focus | Key Namespaces |
|-------------|---------------|----------------|
| Operator | Real-time control | status/, measurement/, alarm/, command/, control/ |
| Maintenance | Predictive service | health/, maintenance/, diagnostic/, kpi/, asset/ |
| Analytics | Trending & metrics | measurement/, kpi/, history/, event/, log/ |
| Configuration | Parameter tuning | config/, control/, recipe/, security/ |
| Production | Batch management | status/, recipe/, kpi/, event/, log/ |
| IT/Infrastructure | System health | comm/, health/, meta/, diagnostic/, security/ |
| Asset Management | Equipment lifecycle | asset/, maintenance/, kpi/, health/, history/ |
| Compliance | Audit trail | log/, history/, security/, event/, meta/ |

---

Also added:

Perspective-to-Namespace Matrix - Primary vs secondary namespaces per role
Namespace Coverage Matrix - Shows which perspectives use each namespace (with ✅ checkmarks)