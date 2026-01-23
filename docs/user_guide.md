# User Guide: Industrial Register Decoder

> **For:** Field Engineers, Operators, Technicians, Auditors  
> **Reading Time:** 20 minutes  
> **Goal:** Understand how to use the system day-to-day

---

## 1. Problem Context

### What Problem Are We Solving?

**Before this system:**

You're a field engineer installing a new power meter. The device manual says:

```
Register 132: Manufacturing Date
Type: DATETIME
Format: IEC 870-5-4
Address: 132-135 (4 registers)
```

**Your old workflow:**
1. Call IT department: "I need the manufacturing date from register 132"
2. Wait 2 days for custom code to be written
3. IT sends you a script: "Run this on your laptop"
4. You get output: `25 11 1 14 30 0`
5. Call IT again: "What do these numbers mean?"
6. Wait for explanation: "Year=2025, Day=11, Month=1..."

**Total time:** 3-4 days, multiple calls, frustration

**With this system:**

1. Open web interface on your tablet
2. Select device: "PM8000_MAIN_FEEDER"
3. Click "Read Manufacturing Date"
4. See result immediately: **"Manufactured: 2025-01-11"**  
   Status: ✓ Data Valid

**Total time:** 30 seconds, self-service

---

## 2. Why It Matters (Your Daily Work)

### How This Helps You

#### 🔧 **Faster Commissioning**

**Old way:**
```
Day 1: Install device physically
Day 2: Wait for IT to configure system
Day 3: Wait for IT to test integration
Day 4: IT finds bug, debugging
Day 5: Finally operational

Total: 5 days
```

**New way:**
```
Day 1: Install device physically
      Enter device info in simple form
      System auto-configures
      Test reads working
      Device operational

Total: 1 day
```

**Impact:** Get equipment online 4 days faster

#### 🛠️ **Better Troubleshooting**

**Scenario:** Alarm showing on SCADA

**Old way:**
```
1. See alarm code: "0x12340001"
2. Look up in manual (can't find manual)
3. Call vendor support
4. Wait on hold: 30 minutes
5. "That code means high voltage on Phase A"
6. Take action

Total: 45 minutes
```

**New way:**
```
1. Click alarm in system
2. See decoded info immediately:
   "High Voltage Alarm
    Parameter: Voltage
    Phases: Phase A
    Priority: HIGH
    Action: Check circuit breaker"
3. Take action

Total: 30 seconds
```

**Impact:** 90× faster diagnosis

#### 📊 **Trustworthy Data**

Every reading shows health status:

```
Temperature: 23.5°C  ✓ GOOD
Voltage: 243.2V      ✓ GOOD
Current: 15.8A       ⚠ QUESTIONABLE (near limit)
Power: 3.84kW        ✗ BAD (sensor fault)
```

**What this means for you:**
- Green checkmark = Trust the data
- Yellow warning = Double-check it
- Red X = Don't use it, investigate

No more guessing if readings are valid!

#### 📝 **Easier Audits**

**Auditor question:** "Show me the calibration dates for all meters"

**Old way:**
```
1. Manually check each meter display
2. Record in Excel spreadsheet
3. Format for auditor
4. Time: 2 hours for 20 meters
```

**New way:**
```
1. Run report: "Calibration Dates - All Meters"
2. Export to PDF
3. Send to auditor
4. Time: 2 minutes
```

**Impact:** 60× faster compliance reporting

---

## 3. Key Concepts (Simple Explanations)

### The Three Things You Need to Know

#### 1. **Datatypes (The Recipes)**

Think of datatypes like cooking recipes. Once you write the recipe for "chocolate cake," you can bake it many times without rewriting the recipe.

**Example:**
```
DATETIME = Recipe for date and time
- Step 1: Read year from bits 0-6
- Step 2: Add 2000 to year
- Step 3: Read month from bits 24-27
- Step 4: Read day from bits 16-20
... etc.

Use this recipe for:
- Manufacturing date (Register 132)
- Calibration date (Register 200)
- Last service date (Register 300)
- Event timestamp (Register 1000)
```

**Your job:** Just point to the recipe. Don't rewrite it.

#### 2. **Register Map (The Directory)**

Like a phone directory. It tells you which "recipe" to use for each register.

```
Device: PM8000_MAIN_FEEDER
├─ Register 132 → Use DATETIME recipe
├─ Register 500 → Use TEMPERATURE recipe
├─ Register 8000 → Use ALARM recipe
└─ Register 8002 → Use ALARM recipe (same recipe, different alarm)
```

**Your job:** Add entries when installing new devices.

#### 3. **Health Status (The Quality Check)**

Every reading gets automatically checked:

```
Reading: Temperature = 85°C

Health Check:
1. Is it a number? ✓ Yes
2. Is it in valid range (-40 to 125°C)? ✓ Yes
3. Is sensor working? ✓ Yes

Result: Health = GOOD ✓
```

If any check fails → Health = BAD ✗

**Your job:** Trust green, investigate red.

### How Data Flows (Visual)

```
┌──────────────┐
│ Power Meter  │  "Register 132 has data"
└──────┬───────┘
       │
       ↓ (Read via Modbus)
┌──────────────┐
│ Raw Numbers  │  [0x19, 0x0B04, 0x0E1E, 0x007B]
└──────┬───────┘
       │
       ↓ (Lookup: Register 132 → DATETIME)
┌──────────────┐
│ Decoder      │  "Use DATETIME recipe"
└──────┬───────┘
       │
       ↓ (Extract + Transform)
┌──────────────┐
│ Decoded Data │  Year=2025, Month=1, Day=11
└──────┬───────┘
       │
       ↓ (Validate)
┌──────────────┐
│ Health Check │  ✓ All values valid
└──────┬───────┘
       │
       ↓ (Display)
┌──────────────┐
│ Your Screen  │  "Manufactured: 2025-01-11 ✓"
└──────────────┘
```

---

## 4. Standard Procedures

### Procedure 1: Reading Device Data

**When:** Commissioning, troubleshooting, auditing

**Steps:**

1. **Access the interface**
   - Open web browser
   - Navigate to: `http://scada-server/decoder`
   - Login with your credentials

2. **Select device**
   - From dropdown: Choose device (e.g., "PM8000_MAIN_FEEDER")
   - Or: Search by location/tag number

3. **Choose what to read**
   - Click category: Manufacturing Data, Measurements, Alarms, etc.
   - Or: Enter specific register number

4. **Read and interpret**
   ```
   Manufacturing Date
   ├─ Value: 2025-01-11
   ├─ Health: ✓ GOOD
   ├─ Quality: Valid data, synchronized time
   └─ Source: Register 132-135
   ```

5. **Take action based on health**
   - ✓ Green: Data is good, use it
   - ⚠ Yellow: Data questionable, verify manually
   - ✗ Red: Data bad, don't use, investigate

### Procedure 2: Adding New Device

**When:** Installing new equipment

**Prerequisites:**
- Device installed and powered
- Network connection verified
- Device manual available

**Steps:**

1. **Gather device information**
   ```
   Device Model: PM8000
   Serial Number: PM8K-2024-0157
   IP Address: 192.168.1.100
   Modbus Slave ID: 1
   Firmware Version: v3.2.1
   ```

2. **Check if device model exists**
   - Look in dropdown: "Supported Devices"
   - If "PM8000" exists → Skip to step 4
   - If not → Continue to step 3

3. **Request device model support** (if new)
   - Fill form: "Request New Device Model"
   - Upload: Device manual PDF
   - IT will add templates (usually 1-2 days)

4. **Add device instance**
   - Click: "Add New Device"
   - Fill form:
     ```
     Device Model: PM8000
     Tag Name: PM8000_MAIN_FEEDER
     Location: Building A, Panel 3
     IP Address: 192.168.1.100
     Modbus ID: 1
     ```
   - Click: "Test Connection"
   - If test passes → Click: "Save"

5. **Verify readings**
   - Click: "Read Manufacturing Date"
   - Verify matches label on device
   - If mismatch → Check Modbus settings

**Troubleshooting:**

| Problem | Solution |
|---------|----------|
| Connection failed | Check IP, verify cable, ping device |
| Wrong data | Check Modbus slave ID, verify byte order |
| Health shows BAD | Normal for first read, clear cache and retry |

### Procedure 3: Troubleshooting Bad Data

**When:** Health status shows red ✗

**Steps:**

1. **Check error message**
   ```
   Temperature: 150°C ✗ BAD
   Error: Value 150 exceeds maximum 125
   ```

2. **Determine cause**
   - **Out of range:** Sensor fault or wrong configuration
   - **Communication error:** Network/cable issue
   - **Wrong datatype:** Configuration mistake

3. **Quick fixes to try**
   ```
   ☐ Refresh reading (might be transient)
   ☐ Check device display (compare to our reading)
   ☐ Verify network connection
   ☐ Check Modbus settings (ID, baud rate, parity)
   ```

4. **If still bad:**
   - Log ticket with details
   - Include screenshot of error
   - Note when problem started
   - IT will investigate configuration

### Procedure 4: Monthly Audit Report

**When:** Monthly compliance check

**Steps:**

1. **Generate report**
   - Navigate to: "Reports" → "Compliance"
   - Select: "Monthly Audit Report"
   - Date range: Last month
   - Click: "Generate"

2. **Review report sections**
   ```
   ✓ All Devices Online (25/25)
   ✓ Calibration Dates Valid (25/25)
   ⚠ Warning: 2 devices approaching calibration due date
   ✗ Error: 1 device has communication issues
   ```

3. **Export for auditor**
   - Format: PDF or Excel
   - Click: "Export"
   - Send to compliance team

4. **Follow up on issues**
   - Schedule calibration for devices with warnings
   - Fix communication errors before next audit

---

## 5. Practical Examples

### Example 1: Commissioning New Power Meter

**Scenario:** Installing PM8000 power meter in Building A

**Task list:**

1. **Physical installation** ✓
   - Mounted in panel
   - Wiring completed
   - Powered on

2. **Network setup** ✓
   - IP configured: 192.168.1.101
   - Ping successful
   - Firewall port opened

3. **Add to system**
   - Open decoder interface
   - Add New Device:
     ```
     Model: PM8000
     Name: PM8000_BUILDING_A
     IP: 192.168.1.101
     Modbus ID: 1
     Location: Building A, MDP
     ```
   - Test connection: ✓ Success

4. **Verify basic readings**
   ```
   Manufacturing Date: 2024-12-15 ✓ GOOD
   Firmware Version: v3.2.1 ✓ GOOD
   Serial Number: PM8K-2024-0245 ✓ GOOD
   
   Voltage L1: 242.5V ✓ GOOD
   Voltage L2: 241.8V ✓ GOOD
   Voltage L3: 243.1V ✓ GOOD
   
   Current L1: 12.4A ✓ GOOD
   Current L2: 11.9A ✓ GOOD
   Current L3: 12.1A ✓ GOOD
   ```

5. **Configure alarms**
   - Set high voltage alarm: 250V
   - Set high current alarm: 50A
   - Set low voltage alarm: 210V
   - Test alarm by simulation

6. **Final verification**
   - Check SCADA display shows meter
   - Verify historical data logging
   - Document in commissioning sheet

**Time:** 30 minutes (vs. 2 days old way)

### Example 2: Troubleshooting Alarm

**Scenario:** SCADA shows alarm on main feeder

**What you see:**
```
ALARM: PM8000_MAIN_FEEDER
Code: 0x12340001
Time: 2025-01-11 14:30:45
```

**What you do:**

1. **Click alarm for details**
   ```
   Alarm Attributes:
   ├─ Type: STANDARD1S (1-second monitoring)
   ├─ Subtype: OVER_SIGNED (exceeds upper limit)
   ├─ Parameter: VOLTAGE
   ├─ Phases: PHASE_A
   ├─ Priority: HIGH
   ├─ Enable: ENABLED ✓
   └─ Action: CHECK CIRCUIT BREAKER
   ```

2. **Understand the alarm**
   - It's a voltage alarm
   - Phase A is over limit
   - High priority = urgent
   - Suggested action: Check breaker

3. **Verify with live data**
   ```
   Current Voltage:
   ├─ Phase A: 253.4V ⚠ (limit: 250V)
   ├─ Phase B: 242.1V ✓
   └─ Phase C: 241.8V ✓
   ```

4. **Take action**
   - Check physical breaker
   - Measure voltage with meter
   - If confirmed high: Adjust tap changer
   - If normal: False alarm, check sensor

5. **Document**
   - Log action taken
   - Note resolution time
   - Attach photos if needed

**Resolution time:** 5 minutes (vs. 45 minutes old way)

### Example 3: Calibration Due Check

**Scenario:** Monthly check for calibration due dates

**Steps:**

1. **Run calibration report**
   - Reports → "Calibration Status"
   - All Devices

2. **Review results**
   ```
   Devices Requiring Calibration (next 30 days):
   
   1. PM8000_BUILDING_A
      Last Calibration: 2024-01-15
      Due Date: 2025-01-15
      Days Remaining: 4 days
      Status: ⚠ URGENT
   
   2. PM8000_BUILDING_C
      Last Calibration: 2024-02-10
      Due Date: 2025-02-10
      Days Remaining: 30 days
      Status: ⚠ WARNING
   ```

3. **Schedule maintenance**
   - Create work orders for both devices
   - Coordinate with calibration vendor
   - Schedule before due dates

4. **Track completion**
   - After calibration, tech updates system
   - New date automatically recorded
   - Report shows ✓ GOOD

**Time saved:** 2 hours vs manual checking

---

## 6. Conclusion

### Your Responsibilities

As a field engineer using this system:

#### ✓ **Do This:**
- Add new devices when installing
- Verify readings make sense
- Report bad data immediately
- Keep device information current
- Review health status regularly
- Document issues in tickets

#### ✗ **Don't Do This:**
- Ignore red health status
- Use bad data for decisions
- Skip connection testing
- Forget to update after changes
- Override safety alarms

### Getting Help

#### **Issue Level 1: Normal Operation**
- Question: "How do I read a specific register?"
- Solution: Check this guide or video tutorials
- Contact: Your supervisor

#### **Issue Level 2: Device Problems**
- Question: "Why is this reading showing BAD?"
- Solution: Follow troubleshooting procedure
- Contact: Maintenance team or IT support

#### **Issue Level 3: System Issues**
- Question: "System not responding"
- Solution: Check network, restart browser
- Contact: IT helpdesk (x1234)

#### **Issue Level 4: Emergencies**
- Question: "Safety alarm not working!"
- Solution: Follow emergency procedures
- Contact: Emergency hotline (x911)

### Training Resources

**Available training:**
- [ ] Online video tutorials (15 min each)
- [ ] Hands-on workshop (4 hours)
- [ ] Quick reference cards (printed)
- [ ] Knowledge base articles

**Recommended path:**
1. Watch "Introduction" video (15 min)
2. Try commissioning test device (30 min)
3. Attend hands-on workshop (4 hours)
4. Practice with real devices (1 week)
5. Get certified (optional, for lead engineers)

### Success Criteria

You're ready to use the system when you can:

- [ ] Add a new device independently
- [ ] Read and interpret any register
- [ ] Understand health status colors
- [ ] Troubleshoot basic connection issues
- [ ] Generate monthly reports
- [ ] Explain to a colleague how it works

### Feedback

**Help us improve:**
- Found a bug? Report it
- Have an idea? Suggest it
- Process unclear? Let us know
- Training not helpful? Tell us

**Contact:** field-engineer-support@example.com

---

**Remember:** This system is here to make your job easier. If it's not, we want to know!

**Version:** 1.0.0  
**For Users:** v1  
**Last Updated:** 2025-01-11