# Resets

## Meter resets
Resets allow you to clear various accumulated parameters stored on your meter or reinitialize the meter or meter accessories.
Meter resets clear your meter’s onboard data logs and other related information. Resets are typically performed after you make changes to the meter’s basic setup parameters (such as frequency, VT/PT or CT settings) to clear invalid or obsolete data in preparation for putting the meter into active service

### Meter Initialization
Meter Initialization is a special command that clears the meter’s logged data, counters and timers.
It is common practice to initialize the meter after its configuration is completed, before adding it to an energy management system.

After configuring all the meter setup parameters, navigate through the different meter display screens and make sure the displayed data is valid then perform meter initialization.

```json
{
    "Resets": {
        "Meter Initialization": {
            "description": "Clears all logged data, counters and timers in the meter.",
            "command_type": "Global Reset",
            "applicable_devices": [
                "PM5110",
                "PM5210",
                "PM5310"
            ]
        }
    }
}
```

## Performing global resets using the display
Global resets allow you to clear all data of a particular type, such as all energy values or all minimum/maximum values.

Option	Description
Meter Initialization	Clears all data listed in this table (energy, demand, min/max values, counters, logs and timers).
Energies	Clears all accumulated energy values (kWh, kVARh, kVAh).
Demands	Clears all the demand registers.
Min/Max	Clears all the minimum and maximum registers.
Alarm Counts & Logs	Clears all the alarm counters and alarm logs.

```json
{
    "Resets": {
        "Meter Initialization": {
            "description": "Clears all data listed in this table (energy, demand, min/max values, counters, logs and timers).",
            "command_type": "Global Reset"
        },
        "Energies": {
            "description": "Clears all accumulated energy values (kWh, kVARh, kVAh).",
            "command_type": "Global Reset"
        },
        "Demands": {
            "description": "Clears all the demand registers.",
            "command_type": "Global Reset"
        },
        "Min/Max": {
            "description": "Clears all the minimum and maximum registers.",
            "command_type": "Global Reset"
        },
        "Alarm Counts & Logs": {
            "description": "Clears all the alarm counters and alarm logs.",
            "command_type": "Global Reset"
        }
    }
}
```

To perform resets using ION Setup , see the “PM5100 ” topic in the ION Setup online help or in the ION Setup device configuration guide.


## Performing single resets using the display
Single resets allow you clear data only in a specific register or register type.
Single resets are often combined to allow you to clear all data of a similar type, for example, a kWh, kVAR and kVA reset may be combined into an energy reset that clears all of the meter’s energy logs.


Available single resets using the display
Parameter	Option	Description
Energy	Accumulated	Clears all accumulated energy values (kWh, kVARh, kVAh).
Demand	Power, Current	Select which demand registers to clear (power demand or current demand).
Alarms	Event Queue	Clears the alarm event queue register (active alarms list).
History Log	Clears the alarm history log.
Counters	Select Counters and then select which alarm counter to clear. See the Alarm counter reset options table.
Active Load Timer	—	Clears and restarts the load operation timer.
To perform resets using ION Setup , see the “PM5100 ” topic in the ION Setup online help or in the ION Setup device configuration guide

```json
{
    "Resets": {
        "Energy": {
            "Accumulated": {
                    "description": "Clears all accumulated energy values (kWh, kVARh, kVAh).",
                    "command_type": "Single Reset"
                }
            },
            "Demand": {
                "Power": {
                    "description": "Select which demand registers to clear (power demand or current demand).",
                    "command_type": "Single Reset"
                },
                "Current": {
                    "description": "Select which demand registers to clear (power demand or current demand).",
                    "command_type": "Single Reset"
                }
            },
            "Alarms": {
                "Event Queue": {
                    "description": "Clears the alarm event queue register (active alarms list).",
                    "command_type": "Single Reset"
                },
                "History Log": {
                    "description": "Clears the alarm history log.",
                    "command_type": "Single Reset"
                }
            },
            "Counters": {
                "Select Counters": {
                    "description": "Select which alarm counter to clear.",
                    "command_type": "Single Reset"
                }
            },
            "Active Load Timer": {
                "---": {
                    "description": "Clears and restarts the load operation timer.",
                    "command_type": "Single Reset"
                }
            }
        }
    }
```