# Unified Namespace

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

## 01-diagnostic <where do I put error codes? - what is wrong?>

- `diagnostic` solves the "where do I put error codes?" problem that haunts every implementation.

path: `uns/diagnostic/`

examples:

```css
uns/diagnostic/error_code: "0x01"
uns/diagnostic/error_description: "Overcurrent"
uns/diagnostic/error_timestamp: "2024-01-01T14:30:00Z"
```

---

## 02-maintenance <where do I put maintenance data? - what is maintenance?>

- `maintenance/` is essential because predictive maintenance data **isn't operational** — mixing it with `measurement/` makes noise.

path: `uns/maintenance/`

examples:

```css
uns/maintenance/last_service_date: "2024-01-01"
uns/maintenance/next_service_date: "2024-01-01"
uns/maintenance/service_interval: "30 days"
uns/maintenance/service_required: true
```

---

## 03-measurement <where do I put measurements? - What we have?>

- `measurement/` is for **observed values**.

path: `uns/measurement/`

examples:

```css
uns/measurement/temperature: 25.0
uns/measurement/humidity: 50.0
uns/measurement/pressure: 101.3
```

---

## 04-control <where do I put setpoints?- what we want?>

- `control/` is for **setpoints**.

path: `uns/control/`

examples:

```css
uns/control/target_temperature: 25.0
uns/control/target_humidity: 50.0
uns/control/target_pressure: 101.3
```

---

## 05-event <where do I put events? - what happened?>

- `event/` is for **discrete occurrences**.

path: `uns/event/`

examples:

```css
uns/event/temperature_too_high: true
uns/event/humidity_too_low: true
uns/event/pressure_too_high: true
```

---

## 06-alarm <where do I put alarms? - info needs action?>

- `alarm/` is for **alarms**.

path: `uns/alarm/`

examples:

### alarm state

```css
uns/alarm/temperature_too_high: true
uns/alarm/humidity_too_low: true
uns/alarm/pressure_too_high: true
```

**Multi-level alarms** (high-high, high, low, low-low):

```css
config/alarm/
            ├─ temp_high_high: {setpoint: 90, priority: 1, delay: 0}
            ├─ temp_high: {setpoint: 80, priority: 2, delay: 5}
            ├─ temp_low: {setpoint: 60, priority: 2, delay: 5}
            └─ temp_low_low: {setpoint: 50, priority: 1, delay: 0}
```

---

## 07-status <where do I put status? - information?>

- `status/` is for **information**.

path: `uns/status/`

examples:

```css
uns/status/temp_warning: true
uns/status/humidity_warning: true
uns/status/pressure_warning: true
```

## 08-config <where do I put config?>

- `config/` is for **configuration**.

path: `uns/config/`

examples:

### alarm config

```css
uns/config/alarm/temperature_too_high/
            ├─ setpoint: 80.0
            ├─ deadband: 2.0
            ├─ delay: 5.0
            ├─ priority: 1
            ├─ enabled: true
            └─ notification_group: "ops"
```

---

## 09-recipe <where do I put recipe?>

Because in batch/discrete manufacturing, **recipe data** doesn't fit cleanly anywhere:

- Not `control/` (that's live setpoints)
- Not `kpi/` (it's prescriptive, not calculated)
- Not `asset/` (it changes per product)

But maybe that's just `control/recipe/`? The question would be: "*What should happen?*" vs. control's "*What am I commanding right now?*"

path: `uns/recipe/`

examples:

```css
uns/recipe/ → What's the process definition?
    ├─ batch_setpoints: {
        ├─ target_temperature: 25.0
        ├─ target_humidity: 50.0
        ├─ target_pressure: 101.3
    }
    ├─ sequence_steps: {
        ├─ step_1: {
            ├─ duration: 60
            ├─ target_temperature: 25.0
            ├─ target_humidity: 50.0
            ├─ target_pressure: 101.3
        }
        ├─ step_2: {
            ├─ duration: 60
            ├─ target_temperature: 25.0
            ├─ target_humidity: 50.0
            ├─ target_pressure: 101.3
        }
        └─ step_3: {
            ├─ duration: 60
            ├─ target_temperature: 25.0
            ├─ target_humidity: 50.0
            ├─ target_pressure: 101.3
        }
    }
    └─ quality_targets: {
        ├─ target_temperature: 25.0
        ├─ target_humidity: 50.0
        ├─ target_pressure: 101.3
    }
```

---

## 10-history <where do I put history?>

Because **history data** doesn't fit cleanly anywhere:

- Not `measurement/` (that's live values)
- Not `event/` (it's prescriptive, not calculated)

But maybe that's just `measurement/history/`? The question would be: "*What should happen?*" vs. measurement's "*What am I measuring right now?*"

path: `uns/history/`

examples:

```css
uns/history/alarm/temperature_too_high/
                                    ├─ triggered_at: "2024-01-01T14:30:00Z"
                                    ├─ acknowledged: false
                                    └─ current_value: 85.2
```

03. The Final Expert Test

Before committing, they ask:

1. **"Can I explain this to a new hire in 30 seconds?"**
   - If not, the placement is too clever.

2. **"Will this break if we add 50 more devices?"**
   - Tests scalability of the pattern.

3. **"Can I write one Spark/SQL query to get all measurements across all devices?"**
   - Tests query predictability: `SELECT * WHERE topic LIKE '%/measurement/%'`

4. **"If this value is missing, which dashboard breaks?"**
   - Tests if criticality matches branch placement.