# Measurements and calculations

## Real-time readings
The power and energy meter measures current and voltages and reports in real time the RMS (Root Mean Squared) values for all three phases and neutral.
The voltage and current inputs are continuously monitored at a sampling rate of 64 points per cycle. This amount of resolution helps enable the meter to provide reliable measurements and calculated electrical values for various commercial, buildings and industrial applications.

```json
{
    "Real-time readings": {
        "Voltage L-N": {
            "description": "RMS voltage between line and neutral for each phase (V)",
            "units": "V",
            "phases": ["A", "B", "C", "N"],
            "sampling_rate": "64 points per cycle"
        },
        "Voltage L-L": {
            "description": "RMS voltage between lines for each phase pair (V)",
            "units": "V",
            "phases": ["AB", "BC", "CA"],
            "sampling_rate": "64 points per cycle"
            },
        "Current": {
            "description": "RMS current for each phase and neutral (A)",
            "units": "A",
            "phases": ["A", "B", "C", "N"],
            "sampling_rate": "64 points per cycle"
        },
        "Frequency": "System frequency (Hz)",
        "kW": {
            "description": "Active power (kW) for each phase and total",
            "units": "kW",
            "phases": ["A", "B", "C", "Total"]
        },
        "kVAR": {
            "description": "Reactive power (kVAR) for each phase and total",
            "units": "kVAR",
            "phases": ["A", "B", "C", "Total"]
        },
        "kVA": {
            "description": "Apparent power (kVA) for each phase and total",
            "units": "kVA",
            "phases": ["A", "B", "C", "Total"]
        },
        "TPF": {
            "description": "True power factor (unitless) for each phase and total",
            "units": "unitless",
            "phases": ["A", "B", "C", "Total"]
        },
        "DPF": {
            "description": "Displacement power factor (unitless) for each phase and total",
            "units": "unitless",
            "phases": ["A", "B", "C", "Total"]
        }
    }

}

```

## Energy
The meter provides fully bi-directional, 4-quadrant energy metering.
The meter calculates and stores all accumulated active, reactive and apparent energy measurements in nonvolatile memory:

- Wh, VARh, VAh (delivered and received)
- Wh, VARh, VAh net (delivered - received)
- Wh, VARh, VAh absolute (delivered + received)

All energy parameters represent the total for all three phases. You can view accumulated energy from the display.

```json
{
    "Energy Measurements": {
        "Active Energy (Wh)": {
            "description": "Accumulated active energy in watt-hours",
            "units": "Wh",
            "types": ["delivered", "received", "net", "absolute"],
            "where_used": "Used by: Energy managers, Management, Auditors (ISO 50001)",
            "notes": "Too noisy, Too frequent, Used as inputs, not decisions",
            "where": {
                "delivered": "Energy consumed from the source",
                "received": "Energy supplied back to the source",
                "net": "Difference between delivered and received energy",
                "absolute": "Total energy regardless of direction"
            }
        },
        "Reactive Energy (VARh)": {
            "description": "Accumulated reactive energy in volt-ampere reactive hours",
            "units": "VARh",
            "types": ["delivered", "received", "net", "absolute"],
            "where_used": "Used by: Energy managers, Management, Auditors (ISO 50001)",
            "notes": "Too noisy, Too frequent, Used as inputs, not decisions",
            "where": {
                "delivered": "Reactive energy consumed from the source",
                "received": "Reactive energy supplied back to the source",
                "net": "Difference between delivered and received reactive energy",
                "absolute": "Total reactive energy regardless of direction"
            }
        },
        "Apparent Energy (VAh)": {
            "description": "Accumulated apparent energy in volt-ampere hours",
            "units": "VAh",
            "types": ["delivered", "received", "net", "absolute"],
            "where_used": "Used by: Energy managers, Management, Auditors (ISO 50001)",
            "notes": "Too noisy, Too frequent, Used as inputs, not decisions",
            "where": {
                "delivered": "Apparent energy consumed from the source",
                "received": "Apparent energy supplied back to the source",
                "net": "Difference between delivered and received apparent energy",
                "absolute": "Total apparent energy regardless of direction"
            }
        }
    }
}
```
## Preset energy
NOTE: Not applicable for MID/MIR meter models.
You can input the previous energy values when you replace the meter. Preset energy value cannot be set more than maximum energy overflow value (9.2233 E).

The preset energy values include active energy (Wh), reactive energy (VARh), apparent energy (VAh) (delivered and received).

```json
{
    "Preset Energy": {
        "Active Energy (Wh)": {
            "description": "Preset accumulated active energy in watt-hours",
            "units": "Wh",
            "types": ["delivered", "received"]
        },
        "Reactive Energy (VARh)": {
            "description": "Preset accumulated reactive energy in volt-ampere reactive hours",
            "units": "VARh",
            "types": ["delivered", "received"]
        },
        "Apparent Energy (VAh)": {
            "description": "Preset accumulated apparent energy in volt-ampere hours",
            "units": "VAh",
            "types": ["delivered", "received"]
        }
    }
}
```

## Min/max values
When the readings reach their lowest or highest value, the meter updates and saves these min/max (minimum and maximum) quantities in non-volatile memory.
The meter’s real-time readings are updated once every 50 cycles for 50 Hz systems, or once every 60 cycles for 60 Hz systems.

```json
{
    "Min/Max Values": {
        "Voltage L-N": {
            "description": "Minimum and maximum RMS voltage between line and neutral for each phase (V)",
            "units": "V",
            "phases": ["A", "B", "C", "N"]
        },
        "Voltage L-L": {
            "description": "Minimum and maximum RMS voltage between lines for each phase pair (V)",
            "units": "V",
            "phases": ["AB", "BC", "CA"]
        },
        "Current": {
            "description": "Minimum and maximum RMS current for each phase and neutral (A)",
            "units": "A",
            "phases": ["A", "B", "C", "N"]
        },
        "Frequency": {
            "description": "Minimum and maximum system frequency (Hz)",
            "units": "Hz"
        },
        "kW": {
            "description": "Minimum and maximum active power (kW) for each phase and total",
            "units": "kW",
            "phases": ["A", "B", "C", "Total"]
        },
        "kVAR": {
            "description": "Minimum and maximum reactive power (kVAR) for each phase and total",
            "units": "kVAR",
            "phases": ["A", "B", "C", "Total"]
        },
        "kVA": {
            "description": "Minimum and maximum apparent power (kVA) for each phase and total",
            "units": "kVA",
            "phases": ["A", "B", "C", "Total"]
        }
    }
}
```

## Demand
The meter can calculate and store power and current demand values over a specified time interval.

### Power demand
Power demand is a measure of average power consumption over a fixed time interval.

NOTE: If not specified, references to demand are assumed to mean power demand.
The meter measures instantaneous consumption and can calculate demand using various methods.

```json
{
    "Demand Measurements": {
        "Power Demand": {
            "description": "Average power consumption over a fixed time interval",
            "units": ["kW", "kVAR", "kVA"],
            "calculation_methods": [
                "Block interval demand",
                "Synchronized demand",
                "Thermal demand"
            ],
            "configurable_parameters": {
                "demand_interval": "1 to 60 minutes in 1 minute increments",
                "calculation_method": "Selectable from display or software"
            }
        },
        "Current Demand": {
            "description": "Average current consumption over a fixed time interval",
            "units": "A",
            "calculation_methods": [
                "Block interval demand",
                "Synchronized demand",
                "Thermal demand"
            ],
            "configurable_parameters": {
                "demand_interval": "1 to 60 minutes in 1 minute increments",
                "calculation_method": "Selectable from display or software"
            }
        }
    }
}
```

### Current demand

The meter calculates current demand using the block interval, synchronized or thermal demand methods.
You can set the demand interval from 1 to 60 minutes in 1 minute increments (for example, 15 minutes).

```json
{
    "Current Demand": {
        "description": "Average current consumption over a fixed time interval",
        "units": "A",
        "calculation_methods": [
            "Block interval demand",
            "Synchronized demand",
            "Thermal demand"
        ],
        "configurable_parameters": {
            "demand_interval": "1 to 60 minutes in 1 minute increments",
            "calculation_method": "Selectable from display or software"
        }
    }
}
```

### Power demand calculation methods
Power demand is calculated by dividing the energy accumulated during a specified period by the length of that period.
How the meter performs this calculation depends on the method and time parameters you select (for example, timed rolling block demand with a 15-minute interval and 5-minute subinterval).

To be compatible with electric utility billing practices, the meter provides the following types of power demand calculations:
- Block interval demand
- Synchronized demand
- Thermal demand

You can configure the power demand calculation method from the display or software.

```json
{
    "Power Demand Calculation Methods": {
        "Block Interval Demand": {
            "description": "Calculates demand over fixed, non-overlapping time intervals",
            "use_case": "Commonly used for billing purposes",
            "example": "15-minute intervals starting at the top of the hour"
        },
        "Synchronized Demand": {
            "description": "Calculates demand over fixed intervals synchronized to a specific time",
            "use_case": "Useful for comparing demand across multiple meters",
            "example": "30-minute intervals starting at 00:00 and 00:30"
        },
        "Thermal Demand": {
            "description": "Calculates demand based on thermal characteristics of the load",
            "use_case": "Ideal for applications where load changes gradually",
            "example": "Demand calculated using a rolling average over a specified time"
        }
    }
}
```
#### Block interval demand
For block interval demand method types, you specify a period of time interval (or block) that the meter uses for the demand calculation.
Select/configure how the meter handles that interval from one of these different methods:

##### Type Description
Timed Sliding Block	Select an interval from 1 to 60 minutes (in 1-minute increments). If the interval is between 1 and 15 minutes, the demand calculation updates every 15 seconds. If the interval is between 16 and 60 minutes, the demand calculation updates every 60 seconds. The meter displays the demand value for the last completed interval.
Timed Block	Select an interval from 1 to 60 minutes (in 1-minute increments). The meter calculates and updates the demand at the end of each interval.
Timed Rolling Block	Select an interval and a subinterval. The subinterval must divide evenly into the interval (for example, three 5-minute subintervals for a 15-minute interval). Demand is updated at the end of each subinterval. The meter displays the demand value for the last completed interval.
Block interval demand example
The following illustration shows the different ways power demand is calculated using the block interval method. In this example, the interval is set to 15 minutes.

Timed Sliding Block

```json
{
    "Block Interval Demand Methods": {
        "Timed Sliding Block": {
            "description": "Demand calculation updates every 15 or 60 seconds based on interval length",
            "interval_range": "1 to 60 minutes",
            "update_frequency": {
                "1-15 minutes": "every 15 seconds",
                "16-60 minutes": "every 60 seconds"
            },
            "displayed_value": "Last completed interval"
        },
        "Timed Block": {
            "description": "Demand calculation updates at the end of each interval",
            "interval_range": "1 to 60 minutes",
            "update_frequency": "At the end of each interval",
            "displayed_value": "Last completed interval"
        },
        "Timed Rolling Block": {
            "description": "Demand calculation updates at the end of each subinterval",
            "interval_and_subinterval": "Subinterval must divide evenly into the interval",
            "update_frequency": "At the end of each subinterval",
            "displayed_value": "Last completed interval"
        }
    }
}
```
#### Synchronized demand
You can configure the demand calculations to be synchronized using a command sent over communications, or the device’s internal real-time clock.

##### Command synchronized demand
This method allows you to synchronize the demand intervals of multiple meters on a communications network. For example, if a programmable logic controller (PLC) input is monitoring a pulse at the end of a demand interval on a utility revenue meter, you can program the PLC to issue a command to multiple meters whenever the utility meter starts a new demand interval. Each time the command is issued, the demand readings of each meter are calculated for the same interval.

##### Clock synchronized demand
This method allows you to synchronize the demand interval to the meter’s internal real-time clock. This helps you synchronize the demand to a particular time, typically on the hour (for example, at 12:00 am). If you select another time of day when the demand intervals are to be synchronized, the time must be specified in minutes from midnight. For example, to synchronize at 8:00 am, select 480 minutes.

NOTE: For these demand types, you can choose block or rolling block options. If you select a rolling block demand option, you need to specify a subinterval.

```json
{
    "Synchronized Demand Methods": {
        "Command Synchronized Demand": {
            "description": "Synchronizes demand intervals across multiple meters via communication commands",
            "use_case": "Ideal for networked meters requiring simultaneous demand updates",
            "example": "PLC issues command to start new demand interval"
        },
        "Clock Synchronized Demand": {
            "description": "Synchronizes demand intervals based on the meter's internal real-time clock",
            "use_case": "Useful for aligning demand calculations with specific times of day",
            "example": "Synchronize at 8:00 am (480 minutes from midnight)"
        }
    }
}
```
#### Thermal demand
Thermal demand calculates the demand based on a thermal response, which imitates the function of thermal demand meters.
The demand calculation updates at the end of each interval. You can set the demand interval from 1 to 60 minutes (in 1-minute increments).

##### Thermal demand example
The following illustration shows the thermal demand calculation. In this example, the interval is set to 15 minutes. The interval is a window of time that moves across the timeline. The calculation updates at the end of each interval.

```json
{
    "Thermal Demand": {
        "description": "Calculates demand based on thermal response characteristics",
        "interval_range": "1 to 60 minutes",
        "update_frequency": "At the end of each interval",
        "example": "15-minute interval with moving time window"
    }
}
```


### Peak demand
The meter records the peak (or maximum) values for kWD, kVARD, and kVAD power (or peak demand).
The peak for each value is the highest average reading since the meter was last reset. These values are maintained in the meter’s non-volatile memory.

The meter also stores the date and time when the peak demand occurred. In addition to the peak demand, the meter also stores the coinciding average 3-phase power factor. The average 3-phase power factor is defined as “demand kW/demand kVA” for the peak demand interval.

```json
{
    "Peak Demand": {
        "description": "Records the maximum average power demand values",
        "units": ["kW", "kVAR", "kVA"],
        "recorded_values": {
            "kWD": "Peak active power demand",
            "kVARD": "Peak reactive power demand",
            "kVAD": "Peak apparent power demand"
        },
        "additional_info": {
            "timestamp": "Date and time when peak demand occurred",
            "average_power_factor": "Demand kW / Demand kVA during peak interval"
        }
    }
}
```

### Predicted demand
The meter calculates predicted demand for the end of the present interval for kW, kVAR, and kVA demand, taking into account the energy consumption so far within the present (partial) interval and the present rate of consumption.
Predicated demand is updated according to the update rate of your meter.

The following illustration shows how a change in load can affect predicted demand for the interval. In this example, the interval is set to 15 minutes.


```json
{
    "Predicted Demand": {
        "description": "Estimates demand for the end of the current interval based on current consumption",
        "units": ["kW", "kVAR", "kVA"],
        "calculation_basis": "Based on energy consumption so far and current rate of consumption",
        "recorded_values": {
            "kW": "Predicted active power demand",
            "kVAR": "Predicted reactive power demand",
            "kVA": "Predicted apparent power demand"
        },
        "update_rate": "According to meter's update frequency",
        "influencing_factors": {
            "energy_consumed_so_far": "Total energy used in the current interval",
            "current_rate_of_consumption": "Present load affecting predicted demand"
        },
        "example_scenario": {
            "initial_demand": "Demand at the start of the interval",
            "load_change": "Impact of load changes during the interval on predicted demand",
            "final_prediction": "Estimated demand at the end of the interval"
        },
        "parameters": {
            "A": "Beginning of interval",
            "B": "Demand for last completed interval",
            "C": "15-minute interval",
            "D": "Partial interval",
            "E": "Change in load",
            "F": "Predicted demand if load is added during interval; predicted demand increases to reflect increased demand",
            "G": "Predicted demand if no load is added",
            "H": "Time"
        }
    }
}
```

### Setting up demand calculations
Use the Demand setup screens to define power or current demand.

Power Demand or Current Demand

Values	Description
Method
Timed Sliding Block

Timed Block

Timed Rolling Block

Cmd Sync Block

Cmd Sync Roll Block

Clock Sync Block

Clock Sync Roll Block

Thermal

Select the appropriate demand calculation method for your needs
Interval
0 - 60	Set the demand interval, in minutes.
Subinterval
0 - 60	
Applies only to rolling block methods.

Define how many subintervals the demand interval should be equally divided into.

Clock Sync Time	 
0 - 2359	
Applies only to clock sync methods (these synchronize the demand interval to the meter’s internal clock).

Define what time of day you want to synchronize the demand, from the start of the day. For example, set this setting to 0730 to synchronize demand at 7:30 AM.

```json
{
    "used_for": ["Power Demand", "Current Demand"],
    "Demand Setup Parameters": {
        "calculation_method": {
            "description": "Select the appropriate demand calculation method",
            "options": {
                "Timed Sliding Block": "Demand calculation updates every 15 or 60 seconds based on interval length",
                "Timed Block": "Demand calculation updates at the end of each interval",
                "Timed Rolling Block": "Demand calculation updates at the end of each subinterval",
                "Cmd Sync Block": "Command Synchronized Demand",
                "Cmd Sync Roll Block": "Command Synchronized Rolling Demand",
                "Clock Sync Block": "Clock Synchronized Demand",
                "Clock Sync Roll Block": "Clock Synchronized Rolling Demand",
                "Thermal": "Calculates demand based on thermal response characteristics"
            }
        },
        "Interval": {
            "description": "Set the demand interval in minutes",
            "range": [0, 60],
            "units": "minutes",
            "demand_interval": "1 to 60 minutes in 1 minute increments",
            "data_type": "integer"
        },
        "Subinterval": {
            "description": "Define how many subintervals the demand interval should be equally divided into.",
            "range": [0, 60],
            "units": "minutes",
            "data_type": "integer",
            "demand_interval": "1 to 60 minutes in 1 minute increments",
            "applicability": "Applies only to rolling block methods"
        },
        "Clock Sync Time": {
            "description": "Define what time of day you want to synchronize the demand, from the start of the day. For example, set this setting to 0730 to synchronize demand at 7:30 AM.",
            "range": "0 - 2359",
            "applicability": "Applies only to clock sync methods"
        }
    }
}
```

## Power factor (PF)
Power factor (PF) is the ratio of real power (P) to apparent power (S).

PF is provided as a number between -1 and 1 or as a percentage from -100% to 100%, where the sign is determined by the convention.

A purely resistive load has no reactive components, so its power factor is 1 (PF = 1, or unity power factor). Inductive or capacitive loads introduce a reactive power (Q) component to the circuit which causes the PF to become closer to zero.

### True PF and displacement PF
The meter supports true power factor and displacement power factor values:
- True power factor includes harmonic content.
- Displacement power factor only considers the fundamental frequency.

NOTE: Unless specified, the power factor displayed by the meter is true power factor.

```json
{
    "Power Factor (PF)": {
        "description": "Ratio of real power to apparent power",
        "units": "unitless",
        "types": {
            "True Power Factor (TPF)": "Accounts for both displacement and distortion components",
            "Displacement Power Factor (DPF)": "Accounts only for the phase difference between voltage and current"
        },
        "phases": ["A", "B", "C", "Total"]
    }
}
```

#### Real, reactive and apparent power (PQS)
A typical AC electrical system load has both resistive and reactive (inductive or capacitive) components.
Real power, also known as active power (P) is consumed by resistive loads. Reactive power (Q) is either consumed by inductive loads or generated by capacitive loads.

Apparent power (S) is the capacity of your measured power system to provide real and reactive power.

The units for power are watts (W or kW) for real power P, vars (VAR or kVAR) for reactive power Q, and volt-amps (VA or kVA) for apparent power S.


##### Power flow
Positive real power P(+) flows from the power source to the load. Negative real power P(-) flows from the load to the power source.

Power factor sign convention
Power factor sign (PF sign) can be positive or negative, and is defined by the conventions used by the IEEE or IEC standards.
You can set the power factor sign (PF sign) convention that is used on the display to either IEC or IEEE.

PF sign convention: IEC
PF sign correlates with the direction of real power (kW) flow.

Quadrant 1 and 4: Positive real power (+kW), the PF sign is positive (+).

Quadrant 2 and 3: Negative real power (-kW), the PF sign is negative (-).

PF sign convention: IEEE
PF sign is correlates with the PF lead/lag convention, in other words, the effective load type (inductive or capacitive):

For a capacitive load (PF leading, quadrant 2 and 4), the PF sign is positive (+).

For an inductive load (PF lagging, quadrant 1 and 3), the PF sign is negative (-).
```json
{
    "Power Flow and PF Sign Conventions": {
        "Real Power (P)": {
            "description": "Power consumed by resistive loads",
            "units": "W or kW",
            "flow_directions": {
                "Positive Real Power (+kW)": "Flows from power source to load",
                "Negative Real Power (-kW)": "Flows from load to power source"
            }
        },
        "Reactive Power (Q)": {
            "description": "Power consumed or generated by inductive or capacitive loads",
            "units": "VAR or kVAR"
        },
        "Apparent Power (S)": {
            "description": "Capacity of the power system to provide real and reactive power",
            "units": "VA or kVA"
        },
        "PF Sign Conventions": {
            "IEC": {
                "Quadrants 1 and 4": "Positive real power (+kW), PF sign is positive (+)",
                "Quadrants 2 and 3": "Negative real power (-kW), PF sign is negative (-)"
            },
            "IEEE": {
                "Capacitive Load (PF leading, quadrants 2 and 4)": "PF sign is positive (+)",
                "Inductive Load (PF lagging, quadrants 1 and 3)": "PF sign is negative (-)"
            }
        }
    }
}
```
Power factor register format
The meter provides power factor values in a variety of formats to suit your energy management software.
Power factor in IEC and lead/lag (IEEE) formats: Float32 and Int16U registers
The meter provides total power factor in IEC and lead/lag (IEEE) formats in both Float32 and Int16U data types. You can use these registers to bring power factor information into third-party software. These registers are interpreted using the standard IEC and IEEE sign conventions.

NOTE: For information on how to calculate actual power factor values from the values in Int16U registers, see your meter’s Modbus register list, available from www.se.com .
Four quadrant power factor information: floating point registers
The meter also provides PF information (including sign and quadrant) in single floating point registers for each of the PF values (for example, per-phase and total values for true and displacement PF, and associated minimums and maximums). The meter performs a simple algorithm to the PF value then stores it in the appropriate PF register.

The meter and software (such as Power Monitoring Expert or ION Setup ) interpret these PF registers for reporting or data entry fields according to the following diagram:

The PF value is calculated from the PF register value using the following formulas:

Quadrant	PF range	PF register range	PF formula
Quadrant 1

0 to +1

0 to +1

PF value = PF register value

Quadrant 2

-1 to 0

-2 to -1

PF value = (-2) - (PF register value)

Quadrant 3

0 to -1

-1 to 0

PF value = PF register value

Quadrant 4

+1 to 0

+1 to +2

PF value = (+2) - (PF register value)


```json
{
    "Power Factor Register Format": {
        "IEC and Lead/Lag (IEEE) Formats": {
            "data_types": ["Float32", "Int16U"],
            "description": "Total power factor in IEC and lead/lag formats",
            "usage": "For integration with third-party software"
        },
        "Four Quadrant Power Factor Information": {
            "data_type": "Single floating point registers",
            "description": "PF information including sign and quadrant for per-phase and total values",
            "calculation_formulas": {
                "Quadrant 1": {
                    "PF_range": "0 to +1",
                    "PF_register_range": "0 to +1",
                    "PF_formula": "PF value = PF register value"
                },
                "Quadrant 2": {
                    "PF_range": "-1 to 0",
                    "PF_register_range": "-2 to -1",
                    "PF_formula": "PF value = (-2) - (PF register value)"
                },
                "Quadrant 3": {
                    "PF_range": "0 to -1",
                    "PF_register_range": "-1 to 0",
                    "PF_formula": "PF value = PF register value"
                },
                "Quadrant 4": {
                    "PF_range": "+1 to 0",
                    "PF_register_range": "+1 to +2",
                    "PF_formula": "PF value = (+2) - (PF register value)"
                }
            }
        }
    }
}
```

## Timers
The meter supports operating timer and load timer.

### Operating timer
The operating timer ( Timer > Oper ) keeps track of how long the meter has been powered up.

Load timer
The load timer ( Timer > Load ) keeps track of how much time the input current exceeds the specified load timer setpoint current.
```json
{
    "Timers": {
        "Operating Timer": {
            "description": "Tracks total time the meter has been powered on",
            "units": "hours",
            "use_case": "Maintenance scheduling, warranty tracking"
        },
        "Load Timer": {
            "description": "Tracks total time the load has been applied",
            "units": "hours",
            "use_case": "Equipment usage monitoring, performance analysis"
        }
    }
}
```
## Predicted Demand vs. Calculated Demand
In the context of power metering (e.g., for devices like the PM5110), demand refers to the average power or current consumption over a specified time interval. The key distinction between predicted demand and calculated demand lies in their timing and purpose:

### Calculated Demand:

This is the actual, historical demand value computed for a completed interval (e.g., a full 15-minute block).
It uses methods like block interval, synchronized, or thermal demand to average energy consumption over the past period.
Examples include peak demand (maximum recorded value) or min/max values stored in non-volatile memory.
Used for billing, auditing, and retrospective analysis (e.g., ISO 50001 compliance).

### Predicted Demand:

This is an estimate or forecast of the demand at the end of the current (ongoing) interval, based on partial data.
It factors in energy consumed so far and the current rate of consumption to project the final value.
Updated frequently (e.g., every 15-60 seconds depending on interval length) and not stored as historical data.
Useful for real-time monitoring, load management, and anticipating peaks before the interval ends.
In summary, calculated demand provides confirmed past performance, while predicted demand offers a proactive insight into future consumption within the active interval. This helps in decision-making for energy management without waiting for the interval to complete.

---




