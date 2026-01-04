# The Expert's Mental Model: UNS Namespace Design

When an expert stares at a device datasheet with 200+ parameters, they're not just sorting data — they're building a **semantic layer** that will survive the next 10 years of operational evolution. Here's the internal dialogue:

---

## The Decision Tree (What's Actually Happening In Their Head)

### First Pass: The Nature Question `What IS this data fundamentally?`

```css
Parameter: "Motor_Temperature_Deg_C"

🧠 Internal dialogue:
├─ Is this ABOUT the device or FROM the device?
│  └─ FROM the device → Continue...
│
├─ Does it change, or is it fixed?
│  └─ Changes → Continue...
│
├─ Is it observed or commanded?
│  └─ Observed → measurement/ or health/
│
└─ Is it about the PROCESS or the DEVICE itself?
   ├─ Process → measurement/temperature
   └─ Device → health/winding_temperature
```

**The key insight**:

`measurement/` is for *what the device monitors*.
`health/` is for *the device monitoring itself*.

---

### Second Pass: The Consumer Question `Who/what needs this data, and why?`

```css
Parameter: "Total_Runtime_Hours"

🧠 Thinking through use cases:
├─ Operator dashboard? → status/ (current state)
├─ Maintenance scheduling? → Could be maintenance/
├─ OEE calculation? → kpi/ (it's derived/accumulated)
├─ Historian trending? → measurement/ if it's a counter
└─ Asset registry? → asset/ if it's static metadata

Decision: It ACCUMULATES over time → kpi/runtime_hours
NOT measurement/ (not an instantaneous sensor value)
NOT asset/ (changes continuously)
```

**The trap they're avoiding**: "Runtime" *feels* like status, but it's
**calculated state**, not instantaneous state.

---

### Third Pass: The Lifecycle Question `When/why does this value change?`

```css
Parameter: "Operating_Mode"

🧠 Change triggers:
├─ Changes due to command? → status/ (commanded mode)
├─ Changes due to process? → status/ (automatic mode)
├─ Changes due to alarm? → status/ (safe mode)
└─ Never changes (firmware)? → asset/firmware_mode

If it can be SET:
├─ command/set_mode ← The intent
└─ status/mode ← The reality

Rule: status/ is READ-ONLY from external systems
      command/ is WRITE (intent to change)
```

**Critical distinction**: `status/mode` ≠ `command/set_mode`  
One is *what is*, one is *what was requested*. 
The gap between them is **control loop feedback**.

---