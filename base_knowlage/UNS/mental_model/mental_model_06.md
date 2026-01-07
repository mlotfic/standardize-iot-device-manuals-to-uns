# 06. The Real Expert Move: Namespace Documentation

Complete Branch Descriptions - JSON structure with description, update_rate, retention, permissions, consumers, and example_topics for each namespace
Quick Reference Table - All 18 namespaces with Update Rate, Retention, Permissions, Primary Consumer
Example Complete Meta Definition - Full JSON including device info, contact, documentation, integration details
Why Meta Matters - Table showing what questions meta/ answers
Template: Minimum Viable meta/ - Starter template for new devices


Expert architects **always** populate `meta/` to make namespaces self-documenting.

---

## The Complete `meta/` Structure

```cs
meta/
├─ schema_version: "2.1"
├─ last_updated: "2025-01-01"
├─ contact: "controls-team@company.com"
├─ documentation_url: "https://docs.../device-xyz"
├─ device_type: "power_meter"
├─ manufacturer: "Schneider Electric"
├─ model: "PM5110"
└─ branch_descriptions: {...}
```

---

## Complete Branch Descriptions for All 18 Namespaces

```json
{
  "branch_descriptions": {
    "measurement": {
      "description": "Real-time process values from sensors",
      "update_rate": "100ms",
      "retention": "streaming",
      "consumers": ["historian", "operator"],
      "example_topics": ["temperature", "pressure", "voltage", "current"]
    },
    "control": {
      "description": "Declarative setpoints - maintain these values",
      "update_rate": "on_change",
      "permissions": "operator",
      "consumers": ["control_system", "operator"],
      "example_topics": ["target_speed", "target_temperature", "pid_setpoint"]
    },
    "command": {
      "description": "Imperative actions - do this NOW",
      "update_rate": "on_action",
      "permissions": "operator",
      "consumers": ["hmi", "scada"],
      "example_topics": ["start", "stop", "reset", "acknowledge_alarm"]
    },
    "status": {
      "description": "Current device state - read only",
      "update_rate": "on_change",
      "retention": "current_only",
      "consumers": ["operator", "dashboard"],
      "example_topics": ["running", "mode", "connected", "active_recipe"]
    },
    "alarm": {
      "description": "Active alarms requiring operator action",
      "update_rate": "on_change",
      "retention": "active_only",
      "consumers": ["operator", "notification_system"],
      "severity_levels": [1, 2, 3, 4],
      "example_topics": ["high_pressure", "overcurrent", "comm_failure"]
    },
    "event": {
      "description": "Discrete occurrences - something happened",
      "update_rate": "on_occurrence",
      "retention": "recent_100",
      "consumers": ["analytics", "correlation"],
      "example_topics": ["batch_started", "batch_complete", "mode_changed"]
    },
    "health": {
      "description": "Device self-diagnostics - how the device feels",
      "update_rate": "1s",
      "retention": "trending",
      "consumers": ["maintenance", "predictive_analytics"],
      "example_topics": ["bearing_condition", "winding_temp", "cpu_load"]
    },
    "diagnostic": {
      "description": "Troubleshooting data - for engineers",
      "update_rate": "on_error",
      "retention": "last_100_errors",
      "consumers": ["engineer", "support"],
      "example_topics": ["last_error_code", "error_stack", "comm_errors"]
    },
    "kpi": {
      "description": "Calculated/accumulated business metrics",
      "update_rate": "varies",
      "retention": "persistent",
      "consumers": ["analytics", "business_intelligence"],
      "example_topics": ["runtime_hours", "energy_kwh", "oee_percent"]
    },
    "config": {
      "description": "Tunable parameters - keyboard to change",
      "update_rate": "on_change",
      "permissions": "supervisor",
      "consumers": ["engineer", "commissioning"],
      "example_topics": ["alarm_thresholds", "display_units", "ip_address"]
    },
    "asset": {
      "description": "Physical identity - wrench to change",
      "update_rate": "static",
      "retention": "persistent",
      "consumers": ["asset_management", "cmms"],
      "example_topics": ["serial_number", "model", "install_date", "manufacturer"]
    },
    "maintenance": {
      "description": "Service records and schedules",
      "update_rate": "on_service",
      "permissions": "maintenance",
      "consumers": ["maintenance", "cmms"],
      "example_topics": ["last_service", "next_service", "service_interval"]
    },
    "recipe": {
      "description": "Product-specific process definitions",
      "update_rate": "on_product_change",
      "permissions": "production",
      "consumers": ["production", "batch_control"],
      "sub_branches": ["batch_setpoints", "sequence_steps", "quality_targets"],
      "example_topics": ["product_A/setpoints", "product_B/sequence_steps"]
    },
    "log": {
      "description": "Audit trail - who did what when",
      "update_rate": "on_action",
      "retention": "90_days",
      "immutable": true,
      "consumers": ["compliance", "audit"],
      "example_topics": ["operator_action", "recipe_change", "alarm_ack"]
    },
    "history": {
      "description": "Archived data for post-mortem analysis",
      "update_rate": "on_archive",
      "retention": "1_year",
      "consumers": ["analyst", "investigation"],
      "example_topics": ["alarm_archive", "measurement_snapshots", "event_log"]
    },
    "comm": {
      "description": "Communication infrastructure metadata",
      "update_rate": "1s",
      "retention": "current_only",
      "consumers": ["it", "system_admin"],
      "example_topics": ["device_timestamp", "protocol", "address", "last_message"]
    },
    "security": {
      "description": "Authentication and access control",
      "update_rate": "on_auth_event",
      "permissions": "admin",
      "consumers": ["admin", "audit"],
      "example_topics": ["current_user", "access_level", "session_expires"]
    },
    "meta": {
      "description": "Namespace documentation - self-describing",
      "update_rate": "on_schema_change",
      "consumers": ["developers", "integrators"],
      "example_topics": ["schema_version", "branch_descriptions", "contact"]
    }
  }
}
```

---

## Quick Reference: Branch Properties

| Namespace | Update Rate | Retention | Permissions | Primary Consumer |
|-----------|-------------|-----------|-------------|------------------|
| `measurement/` | 100ms | Streaming | Read-only | Historian |
| `control/` | On change | Current | Operator | Control System |
| `command/` | On action | Transient | Operator | HMI |
| `status/` | On change | Current | Read-only | Dashboard |
| `alarm/` | On change | Active | Read-only | Notification |
| `event/` | On occurrence | Recent 100 | Read-only | Analytics |
| `health/` | 1s | Trending | Read-only | Maintenance |
| `diagnostic/` | On error | Last 100 | Read-only | Engineer |
| `kpi/` | Varies | Persistent | Read-only | BI |
| `config/` | On change | Persistent | Supervisor | Engineer |
| `asset/` | Static | Persistent | Read-only | CMMS |
| `maintenance/` | On service | Persistent | Maintenance | CMMS |
| `recipe/` | Per product | Persistent | Production | Batch Control |
| `log/` | On action | 90 days | Read-only | Compliance |
| `history/` | On archive | 1 year | Read-only | Analyst |
| `comm/` | 1s | Current | Read-only | IT |
| `security/` | On auth | Session | Admin | Admin |
| `meta/` | On schema | Persistent | Read-only | Developer |

---

## Example Complete Meta Definition

```json
{
  "meta": {
    "schema_version": "2.1",
    "schema_date": "2025-01-01",
    "device": {
      "type": "power_meter",
      "manufacturer": "Schneider Electric",
      "model": "PM5110",
      "firmware": "1.2.3"
    },
    "contact": {
      "team": "controls-team@company.com",
      "owner": "john.smith@company.com"
    },
    "documentation": {
      "url": "https://docs.company.com/uns/pm5110",
      "datasheet": "https://www.se.com/pm5110"
    },
    "integration": {
      "protocol": "Modbus TCP",
      "poll_rate_ms": 100,
      "address_map": "https://docs.company.com/modbus/pm5110"
    },
    "topic_pattern": "uns/{site}/{area}/{line}/{device}/{branch}/{topic}",
    "branches": {
      "active": ["measurement", "status", "alarm", "kpi", "config", "asset", "health", "comm", "meta"],
      "optional": ["control", "command", "event", "diagnostic", "maintenance", "recipe", "log", "history", "security"]
    }
  }
}
```

---

## Why Meta Matters

> **In 3 years, no one will remember why `health/` exists or what goes there.**
> 
> Self-documenting namespaces survive turnover.

### What meta/ prevents:

| Without meta/ | With meta/ |
|---------------|-----------|
| "What does this topic mean?" | Check branch_descriptions |
| "Who owns this integration?" | Check contact |
| "How fast does this update?" | Check update_rate |
| "Can I write to this?" | Check permissions |
| "Where's the documentation?" | Check documentation_url |
| "What version is this schema?" | Check schema_version |

---

## Template: Minimum Viable meta/

```json
{
  "meta": {
    "schema_version": "1.0",
    "last_updated": "2025-01-01",
    "contact": "team@company.com",
    "branch_descriptions": {
      "measurement": "Process values",
      "status": "Device state",
      "alarm": "Active alarms",
      "config": "Tunable parameters",
      "asset": "Device identity"
    }
  }
}
```

Start with this minimum and expand as the namespace grows.

---
