# 03. The Real Expert Thinking: Edge Cases

Edge cases where naive placement leads to confusion. Learn from these patterns.

---

## Case 1: Alarm Acknowledgement

```cs
Parameter: "Alarm_Ack_Button_Pressed"

🧠 Naive placement: event/ (something happened)
🧠 Expert placement: command/acknowledge_alarm

Why? Because it's INTENT from operator, not device reporting.

The complete flow:
├─ alarm/high_pressure: true           ← Device reports
├─ command/ack_alarm: {user: "john"}   ← Operator acts
├─ log/alarm_acknowledged: {...}       ← Audit trail
└─ alarm/high_pressure_acked: true     ← Device confirms
```

**Namespaces involved**: `alarm/`, `command/`, `log/`

---

## Case 2: Setpoint Echo (The Three-Layer Reality)

```cs
Parameters:
- "Speed_Setpoint_Commanded" 
- "Speed_Setpoint_Active"
- "Speed_Actual"

🧠 The trap: These sound like the same thing

Expert placement:
├─ control/target_speed: 1500      ← What we WANT (intent)
├─ status/active_setpoint: 1450    ← What device ACCEPTED (validated)
└─ measurement/actual_speed: 1447  ← What's HAPPENING (reality)

The gap between them = control loop feedback
```

**Namespaces involved**: `control/`, `status/`, `measurement/`

---

## Case 3: Error Codes

```cs
Parameter: "Last_Error_Code"

🧠 Decision points:
├─ Is it CURRENTLY in error?  → alarm/active_fault
├─ Is it historical?          → event/fault_occurred  
├─ Is it for debugging?       → diagnostic/last_error
├─ Is it about device health? → health/fault_count
└─ Is it for compliance?      → log/error_log

Expert choice often:
├─ alarm/active_fault: true
├─ diagnostic/last_error_code: "E0423"
├─ diagnostic/last_error_desc: "COMM_TIMEOUT"
├─ health/error_count_total: 15 (for MTBF)
├─ history/error_archive: [...]
└─ log/error_occurred: {timestamp, code, context}
```

**Why `diagnostic/` is critical**: It's for *troubleshooting*, not *operating*.

**Namespaces involved**: `alarm/`, `diagnostic/`, `health/`, `history/`, `log/`, `event/`

---

## Case 4: Timestamps

```cs
Parameter: "Device_Clock"

🧠 What's it used for?

If it's event correlation:
└─ comm/device_timestamp (trust/sync issue)

If it's just health:
└─ health/clock_drift

If it's embedded in events:
└─ event/batch_complete: {timestamp: "...", id: "..."}

If it's for audit:
└─ log/{action}: {timestamp: "...", user: "..."}

Never standalone in measurement/ unless it's a process variable
```

**Namespaces involved**: `comm/`, `health/`, `event/`, `log/`

---

## Case 5: Recipe Management

```cs
Parameters:
- "Recipe_Name"
- "Recipe_Setpoints"
- "Active_Recipe"

🧠 The trap: Mixing recipe definition with execution

Expert placement:
├─ recipe/chocolate_cake/setpoints: {...}     ← Recipe definition
├─ recipe/chocolate_cake/sequence_steps: [...] ← Process steps
├─ recipe/chocolate_cake/quality_targets: {...} ← Quality specs
├─ status/active_recipe: "chocolate_cake"      ← Currently loaded
├─ command/load_recipe: "chocolate_cake"       ← Intent to load
├─ event/recipe_loaded: {name, timestamp}      ← Confirmation
└─ log/recipe_change: {from, to, user}         ← Audit
```

**Namespaces involved**: `recipe/`, `status/`, `command/`, `event/`, `log/`

---

## Case 6: Maintenance Tracking

```cs
Parameters:
- "Oil_Change_Due"
- "Hours_Since_Service"
- "Next_Service_Date"

🧠 The trap: Mixing maintenance data with health metrics

Expert placement:
├─ maintenance/last_service_date: "2025-01-01"
├─ maintenance/next_service_date: "2025-04-01"
├─ maintenance/service_type: "oil_change"
├─ kpi/hours_since_service: 847
├─ health/oil_condition: 0.72 (degradation score)
├─ alarm/service_overdue: true (if critical)
├─ event/service_completed: {date, tech, notes}
└─ config/service_interval_hours: 1000
```

**Namespaces involved**: `maintenance/`, `kpi/`, `health/`, `alarm/`, `event/`, `config/`

---

## Case 7: Configuration vs Asset

```cs
Parameter: "Motor_Rated_Power"

🧠 The test: Does it require a WRENCH or a KEYBOARD to change?

Wrench to change (physical):
├─ asset/rated_power: 5.5         ← Motor nameplate
├─ asset/serial_number: "ABC123"
├─ asset/install_date: "2024-06-15"
└─ asset/manufacturer: "ABB"

Keyboard to change (configurable):
├─ config/max_power_limit: 5.0    ← Software limit
├─ config/alarm_threshold: 4.5
├─ config/display_units: "kW"
└─ config/ip_address: "192.168.1.100"
```

**Namespaces involved**: `asset/`, `config/`

---

## Case 8: Security and Access

```cs
Parameters:
- "User_Logged_In"
- "Access_Level"
- "Login_Attempt_Failed"

🧠 The trap: Mixing security state with events

Expert placement:
├─ security/current_user: "operator_1"
├─ security/access_level: 2
├─ security/session_timeout: 3600
├─ status/logged_in: true
├─ event/login_successful: {user, timestamp}
├─ alarm/intrusion_detected: false
├─ log/login_attempt: {user, success, ip}
└─ config/max_login_attempts: 3
```

**Namespaces involved**: `security/`, `status/`, `event/`, `alarm/`, `log/`, `config/`

---

## Case 9: KPI Calculations

```cs
Parameters:
- "Total_Energy_kWh"
- "Energy_This_Month"
- "OEE_Percent"

🧠 The trap: Confusing totalizers with calculated KPIs

Expert placement:
├─ kpi/energy_total_kwh: 1547892     ← Lifetime accumulator
├─ kpi/energy_this_month: 8456       ← Period calculation
├─ kpi/oee_percent: 78.5             ← Derived metric
├─ kpi/availability: 0.92
├─ kpi/performance: 0.88
├─ kpi/quality: 0.97
├─ measurement/power_kw: 28.7        ← Instantaneous (NOT kpi)
├─ history/energy_daily: [...]       ← Historical snapshots
└─ event/meter_reset: {timestamp}    ← If totalizer resets
```

**Namespaces involved**: `kpi/`, `measurement/`, `history/`, `event/`

---

## Case 10: Communication Health

```cs
Parameters:
- "Last_Message_Time"
- "Messages_Lost"
- "Connection_Status"

🧠 The trap: Mixing comm infrastructure with device health

Expert placement:
├─ comm/device_timestamp: "2025-01-04T10:30:00Z"
├─ comm/last_message_received: "2025-01-04T10:29:55Z"
├─ comm/protocol: "Modbus TCP"
├─ comm/address: "192.168.1.50:502"
├─ status/connected: true
├─ health/messages_lost_count: 3
├─ health/comm_quality: 0.998
├─ alarm/connection_lost: false
└─ diagnostic/last_comm_error: "TIMEOUT"
```

**Namespaces involved**: `comm/`, `status/`, `health/`, `alarm/`, `diagnostic/`

---

## Case 11: Meta/Documentation

```cs
Parameter: "Schema Version"

🧠 When to use meta/

Expert placement:
├─ meta/schema_version: "2.1"
├─ meta/last_updated: "2025-01-01"
├─ meta/contact: "controls-team@company.com"
├─ meta/documentation_url: "https://docs.../device-xyz"
└─ meta/branch_descriptions: {
│     "measurement": "Process values sampled at 100ms",
│     "alarm": "Active alarms requiring operator action",
│     "config": "Tunable parameters, requires supervisor role"
│   }
```

**Why meta/ matters**: Self-documenting namespaces survive turnover.

**Namespaces involved**: `meta/`

---

## Edge Case Decision Matrix

| Scenario | Naive Choice | Expert Choice | Key Insight |
|----------|--------------|---------------|-------------|
| Alarm acknowledgement | `event/` | `command/` | It's operator intent, not device report |
| Active setpoint | `control/` | `status/` | Device validates before accepting |
| Last error code | `status/` | `diagnostic/` | Troubleshooting ≠ operating |
| Device clock | `measurement/` | `comm/` | Infrastructure, not process |
| Recipe definition | `config/` | `recipe/` | Changes per product |
| Oil condition score | `measurement/` | `health/` | Diagnostic, not process |
| Hours since service | `health/` | `kpi/` | Calculated accumulation |
| Motor nameplate power | `config/` | `asset/` | Wrench vs keyboard |
| Login user | `status/` | `security/` | Access control domain |
| Energy totalizer | `measurement/` | `kpi/` | Accumulated, not instant |
| Message loss count | `status/` | `health/` | Device self-monitoring |
| Schema version | `asset/` | `meta/` | Namespace docs, not device |

---

## The Expert's Quick Rules

1. **Intent vs Report**: Operator actions → `command/`, device reports → `status/` or `event/`
2. **Wrench vs Keyboard**: Physical changes → `asset/`, software changes → `config/`
3. **Process vs Device**: Monitoring external → `measurement/`, monitoring self → `health/`
4. **Instant vs Accumulated**: Real-time values → `measurement/`, totals → `kpi/`
5. **Operating vs Troubleshooting**: Day-to-day → `status/`, debugging → `diagnostic/`
6. **Current vs Historical**: Active state → `alarm/`, past records → `history/`
7. **Compliance vs Analytics**: Audit trail → `log/`, analysis → `history/`

---

|Case	|Topic	|Key |Namespaces|
|---|---|---|---|
|1	|Alarm Acknowledgement	|alarm/, command/, log/
|2	|Setpoint Echo	|control/, status/, measurement/
|3	|Error Codes	|alarm/, diagnostic/, health/, history/, log/, event/
|4	|Timestamps	|comm/, health/, event/, log/
|5	|Recipe Management	|recipe/, status/, command/, event/, log/
|6	|Maintenance Tracking	|maintenance/, kpi/, health/, alarm/, event/, config/
|7	|Config vs Asset	|asset/, config/
|8	|Security & Access	|security/, status/, event/, alarm/, log/, config/
|9	|KPI Calculations	|kpi/, measurement/, history/, event/
|10	|Communication Health	|comm/, status/, health/, alarm/, diagnostic/
|11	|Meta/Documentation	|meta/



Edge Case Decision Matrix - naive vs expert choices
Expert's Quick Rules - 7 quick decision rules
