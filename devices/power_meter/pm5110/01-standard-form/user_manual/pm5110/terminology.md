Straight extraction → structured, no guessing, no cleanup beyond column mapping.

I’m mapping the table like this (because that’s how engineers actually consume it):

* `alarm_label` → human-readable alarm name
* `ion_setup` → ION Setup name
* `display` → HMI / Display name
* `valid_range` → engineering range **as written**
* `resolution_range` → display resolution range **as written**
* `units` → units (or `null` if none)

https://www.productinfo.schneider-electric.com/pm5100/pm5100-user-manual/PM5100%20User%20Manual/English/BM_PM5100UserManual_EAV15105_0000425845.ditamap/$/R_Hardware_DirectConnectVoltageLimits_PM5300_0000087309

terminology