❌ **`alarm/high_temp/setpoint`** → Breaks semantics  
The question is "must a human act?" — setpoints don't require action, **alarms** do.

❌ **`control/alarm/`** → Wrong domain  
`control/` is for *process control* (PID setpoints, valve positions). Alarm thresholds aren't controlling the process.

❌ **`asset/alarm_config/`** → Could work, but...  
This is operational config that changes semi-frequently. `asset/` should be static metadata (serial numbers, model, location).

❌ **`measurement/setpoint`** → Category error  
Measurements are observed values. Setpoints are configured limits.