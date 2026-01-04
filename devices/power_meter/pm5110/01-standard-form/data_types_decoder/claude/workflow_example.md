# Complete Workflow: Manual → CSV → Everyone Uses It

## The Problem Solved

**Before:** 
- Developer A reads Schneider manual, writes Python parser
- Developer B reads ABB manual, writes different Python parser
- Embedded dev can't understand Python code
- Operator has no reference for alarm codes
- Web UI dev asks "what does alarm code 5 mean?"
- Everyone maintains separate documentation

**After:**
- Developer fills standardized CSV from manual
- **Everyone reads the same CSV file**
- Python dev: reads CSV to know bit positions
- Embedded dev: reads CSV to know enums
- Operator: opens CSV in Excel to look up codes
- Web UI: loads CSV to populate dropdowns
- **Single source of truth**

---

## Real Scenario: Adding Schneider PM5110 Support

### Step 1: Developer Gets Manual

```
📁 PM5110_User_Manual_v2.3.pdf
  - Section 3.2: Communication Registers
  - Page 45: Alarm Attributes Register
  - Page 52: Event Code Register
```

### Step 2: Extract Register Information

**Manual Page 45 shows:**
```
┌─────────────────────────────────────────────┐
│ Register 4000h - Alarm Attributes (32-bit)  │
├──────────┬──────────────┬───────────────────┤
│ Bits     │ Field Name   │ Encoding          │
├──────────┼──────────────┼───────────────────┤
│ 28-31    │ Alarm Type   │ 0 = None          │
│          │              │ 1 = Standard 1s   │
│          │              │ 2 = Custom 1s     │
│          │              │ 5 = Disturbance   │
├──────────┼──────────────┼───────────────────┤
│ 17-20    │ Parameter    │ 0 = None          │
│          │              │ 1 = Voltage       │
│          │              │ 2 = Current       │
│          │              │ 6 = Frequency     │
├──────────┼──────────────┼───────────────────┤
│ 7-10     │ Phases       │ 0 = None          │
│          │              │ 1 = Phase A       │
│          │              │ 7 = ABC           │
├──────────┼──────────────┼───────────────────┤
│ 0        │ Enable       │ 0 = Disabled      │
│          │              │ 1 = Enabled       │
└──────────┴──────────────┴───────────────────┘

Note: When Parameter=1 (Voltage), unit is Volts (V)
```

### Step 3: Fill CSV Template

**Developer opens:** `schneider_pm5110.csv`

```csv
device_model,register_group,field_name,total_bits,bit_offset,bit_width,data_type,enum_value,enum_name,description,unit_code,manual_ref,standard
PM5110,AlarmAttributes,type,32,28,4,enum,0,NONE,No alarm type defined,,p.45,Device specific
PM5110,AlarmAttributes,type,32,28,4,enum,1,STANDARD1S,Standard 1-second alarm for continuous monitoring,,p.45,Device specific
PM5110,AlarmAttributes,type,32,28,4,enum,2,CUSTOM1S,Custom 1-second alarm with user-defined parameters,,p.45,Device specific
PM5110,AlarmAttributes,type,32,28,4,enum,5,DISTURBANCE,Power quality disturbance alarm,,p.45,Device specific
PM5110,AlarmAttributes,parameter,32,17,4,enum,0,NONE,No parameter specified,,p.45,Device specific
PM5110,AlarmAttributes,parameter,32,17,4,enum,1,VOLTAGE,Voltage measurement parameter,8,p.45,Device specific
PM5110,AlarmAttributes,parameter,32,17,4,enum,2,CURRENT,Current measurement parameter,6,p.45,Device specific
PM5110,AlarmAttributes,parameter,32,17,4,enum,6,FREQUENCY,Frequency (Hz) parameter,5,p.45,Device specific
PM5110,AlarmAttributes,phases,32,7,4,enum,0,NONE,No phase specified,,p.45,Device specific
PM5110,AlarmAttributes,phases,32,7,4,enum,1,A,Phase A only,,p.45,Device specific
PM5110,AlarmAttributes,phases,32,7,4,enum,7,ABC,All three phases (A-B-C),,p.45,Device specific
PM5110,AlarmAttributes,enable,32,0,1,flag,0,DISABLED,Alarm disabled (not active),,p.45,Device specific
PM5110,AlarmAttributes,enable,32,0,1,flag,1,ENABLED,Alarm enabled (active),,p.45,Device specific
```

**Time taken:** ~30 minutes to extract and format

**Commit message:** `Add Schneider PM5110 AlarmAttributes register (Manual v2.3, p.45)`

---

## Step 4: How Each Team Uses This CSV

### Python Developer (Data Processing)

```python
import csv
import struct

class PM5110Decoder:
    def __init__(self, config_file='schneider_pm5110.csv'):
        """Load config once at startup"""
        self.config = self._load_config(config_file)
    
    def _load_config(self, filepath):
        """Build lookup dictionaries from CSV"""
        fields = {}
        enums = {}
        
        with open(filepath) as f:
            for row in csv.DictReader(f):
                if row['device_model'] != 'PM5110':
                    continue
                
                # Store field info
                key = (row['register_group'], row['field_name'])
                if key not in fields:
                    fields[key] = {
                        'offset': int(row['bit_offset']),
                        'width': int(row['bit_width']),
                        'type': row['data_type']
                    }
                
                # Store enum mappings
                if row['enum_value']:
                    enum_key = (*key, int(row['enum_value']))
                    enums[enum_key] = {
                        'name': row['enum_name'],
                        'description': row['description']
                    }
        
        return {'fields': fields, 'enums': enums}
    
    def decode_alarm_attributes(self, raw_value):
        """Decode 32-bit alarm register"""
        result = {}
        
        # Extract each field based on CSV config
        for (group, field), info in self.config['fields'].items():
            if group != 'AlarmAttributes':
                continue
            
            # Extract bits
            mask = (1 << info['width']) - 1
            value = (raw_value >> info['offset']) & mask
            
            # Look up enum meaning if available
            enum_key = (group, field, value)
            if enum_key in self.config['enums']:
                result[field] = {
                    'value': value,
                    'name': self.config['enums'][enum_key]['name'],
                    'description': self.config['enums'][enum_key]['description']
                }
            else:
                result[field] = {'value': value}
        
        return result

# Usage
decoder = PM5110Decoder()
alarm_data = decoder.decode_alarm_attributes(0x12003401)

print(f"Alarm Type: {alarm_data['type']['name']}")
print(f"Description: {alarm_data['type']['description']}")
print(f"Enabled: {alarm_data['enable']['name']}")
```

---

### Embedded C Developer (Firmware)

```c
/* 
 * PM5110 Alarm Decoder
 * Register definitions from: schneider_pm5110.csv
 * Last updated: 2025-12-29
 */

#include <stdint.h>

// Enum definitions from CSV (device_model=PM5110, register_group=AlarmAttributes)
typedef enum {
    ALARM_TYPE_NONE = 0,          // CSV: No alarm type defined
    ALARM_TYPE_STANDARD1S = 1,    // CSV: Standard 1-second alarm
    ALARM_TYPE_CUSTOM1S = 2,      // CSV: Custom 1-second alarm
    ALARM_TYPE_DISTURBANCE = 5    // CSV: Power quality disturbance
} AlarmType_t;

typedef enum {
    PARAM_NONE = 0,               // CSV: No parameter specified
    PARAM_VOLTAGE = 1,            // CSV: Voltage measurement (unit_code=8, Volts)
    PARAM_CURRENT = 2,            // CSV: Current measurement (unit_code=6, Amperes)
    PARAM_FREQUENCY = 6           // CSV: Frequency (unit_code=5, Hertz)
} AlarmParameter_t;

typedef enum {
    PHASE_NONE = 0,               // CSV: No phase specified
    PHASE_A = 1,                  // CSV: Phase A only
    PHASE_ABC = 7                 // CSV: All three phases
} PhaseSelection_t;

// Bit positions from CSV (bit_offset, bit_width)
#define ALARM_TYPE_OFFSET       28  // CSV: offset=28, width=4
#define ALARM_TYPE_MASK         0xF
#define ALARM_PARAM_OFFSET      17  // CSV: offset=17, width=4
#define ALARM_PARAM_MASK        0xF
#define ALARM_PHASES_OFFSET     7   // CSV: offset=7, width=4
#define ALARM_PHASES_MASK       0xF
#define ALARM_ENABLE_OFFSET     0   // CSV: offset=0, width=1
#define ALARM_ENABLE_MASK       0x1

// Decode function based on CSV structure
void decode_alarm_attributes(uint32_t raw_value) {
    AlarmType_t type = (raw_value >> ALARM_TYPE_OFFSET) & ALARM_TYPE_MASK;
    AlarmParameter_t param = (raw_value >> ALARM_PARAM_OFFSET) & ALARM_PARAM_MASK;
    PhaseSelection_t phases = (raw_value >> ALARM_PHASES_OFFSET) & ALARM_PHASES_MASK;
    uint8_t enabled = (raw_value >> ALARM_ENABLE_OFFSET) & ALARM_ENABLE_MASK;
    
    // Take action based on decoded values
    if (enabled && type == ALARM_TYPE_DISTURBANCE) {
        if (param == PARAM_VOLTAGE && phases == PHASE_ABC) {
            // Handle 3-phase voltage disturbance
            trigger_disturbance_response();
        }
    }
}
```

---

### Operator (Direct CSV Usage)

**Scenario:** Alarm code 0x51003401 appears on display

**Steps:**
1. Open `schneider_pm5110.csv` in Excel
2. Filter: `device_model = PM5110`, `register_group = AlarmAttributes`
3. Calculate field values:
   - Type field (bits 28-31): `(0x51003401 >> 28) & 0xF = 5`
4. Search CSV for: `field_name = type`, `enum_value = 5`
5. **Result:** `DISTURBANCE - Power quality disturbance alarm`

**No programming needed** - operator reads CSV directly

---

### Web UI Developer (JavaScript)

```javascript
// Load CSV and build user interface
class PM5110ConfigUI {
    constructor() {
        this.config = null;
    }
    
    async loadConfig() {
        const response = await fetch('schneider_pm5110.csv');
        const csvText = await response.text();
        this.config = this.parseCSV(csvText);
    }
    
    parseCSV(text) {
        const lines = text.split('\n');
        const headers = lines[0].split(',');
        const data = [];
        
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',');
            const row = {};
            headers.forEach((h, idx) => row[h] = values[idx]);
            if (row.device_model === 'PM5110') {
                data.push(row);
            }
        }
        
        return data;
    }
    
    buildAlarmTypeDropdown() {
        // Get all alarm type enum values from CSV
        const alarmTypes = this.config
            .filter(row => 
                row.register_group === 'AlarmAttributes' && 
                row.field_name === 'type'
            )
            .map(row => ({
                value: row.enum_value,
                label: row.enum_name,
                tooltip: row.description
            }));
        
        // Build HTML dropdown
        const select = document.getElementById('alarm-type-select');
        alarmTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type.value;
            option.textContent = type.label;
            option.title = type.tooltip;  // Shows on hover
            select.appendChild(option);
        });
    }
    
    decodeAlarmDisplay(rawValue) {
        // Decode and show human-readable values
        const type = (rawValue >> 28) & 0xF;
        const enabled = rawValue & 0x1;
        
        // Look up meanings from CSV
        const typeRow = this.config.find(r =>
            r.register_group === 'AlarmAttributes' &&
            r.field_name === 'type' &&
            parseInt(r.enum_value) === type
        );
        
        const enableRow = this.config.find(r =>
            r.register_group === 'AlarmAttributes' &&
            r.field_name === 'enable' &&
            parseInt(r.enum_value) === enabled
        );
        
        return {
            type: typeRow?.enum_name || 'UNKNOWN',
            typeDesc: typeRow?.description || '',
            status: enableRow?.enum_name || 'UNKNOWN'
        };
    }
}

// Usage
const ui = new PM5110ConfigUI();
await ui.loadConfig();
ui.buildAlarmTypeDropdown();

const decoded = ui.decodeAlarmDisplay(0x51003401);
console.log(`Alarm: ${decoded.type} (${decoded.status})`);
console.log(`Info: ${decoded.typeDesc}`);
```

---

### Documentation Generator (Automated Docs)

```python
import csv

def generate_markdown_docs(csv_file, output_file):
    """Generate user documentation from CSV"""
    
    with open(csv_file) as f:
        rows = list(csv.DictReader(f))
    
    # Group by register
    registers = {}
    for row in rows:
        if row['device_model'] != 'PM5110':
            continue
        
        reg = row['register_group']
        if reg not in registers:
            registers[reg] = {}
        
        field = row['field_name']
        if field not in registers[reg]:
            registers[reg][field] = []
        
        registers[reg][field].append(row)
    
    # Generate markdown
    with open(output_file, 'w') as f:
        f.write("# Schneider PM5110 Register Reference\n\n")
        f.write("*Auto-generated from device configuration CSV*\n\n")
        
        for reg_name, fields in registers.items():
            f.write(f"## {reg_name} Register\n\n")
            
            for field_name, rows in fields.items():
                f.write(f"### {field_name}\n\n")
                f.write(f"- **Bits:** {rows[0]['bit_offset']}")
                f.write(f"-{int(rows[0]['bit_offset']) + int(rows[0]['bit_width']) - 1}\n")
                f.write(f"- **Width:** {rows[0]['bit_width']} bits\n")
                f.write(f"- **Reference:** Manual {rows[0]['manual_ref']}\n\n")
                
                if rows[0]['data_type'] == 'enum':
                    f.write("**Values:**\n\n")
                    for row in rows:
                        if row['enum_value']:
                            f.write(f"- `{row['enum_value']}` = **{row['enum_name']}** - ")
                            f.write(f"{row['description']}\n")
                    f.write("\n")
                elif rows[0]['data_type'] == 'number':
                    f.write(f"**Description:** {rows[0]['description']}\n\n")

# Generate docs
generate_markdown_docs('schneider_pm5110.csv', 'PM5110_Reference.md')
```

---

## The Key Benefit

### One CSV File Serves Everyone:

```
schneider_pm5110.csv (Single Source of Truth)
         │
         ├─→ Python dev reads it: knows bit positions
         ├─→ C dev reads it: generates enums
         ├─→ Operator reads it: looks up alarm meanings
         ├─→ Web UI reads it: populates dropdowns
         ├─→ Doc generator reads it: creates PDF manual
         └─→ QA reads it: validates device responses
```

### No Translation Needed:

- ❌ No "Python parser" vs "C parser" differences
- ❌ No outdated documentation
- ❌ No asking "what does code 5 mean?"
- ✅ Everyone reads **the same file**
- ✅ Update CSV once, everyone sees changes
- ✅ Git tracks all changes with history

---

## Adding Another Device (ABB M2M)

**Same process, same CSV format:**

```csv
device_model,register_group,field_name,total_bits,bit_offset,bit_width,data_type,enum_value,enum_name,description,unit_code,manual_ref,standard
M2M,AlarmConfig,alarm_type,32,28,4,enum,0,NO_ALARM,No alarm configured,,p.23,Device specific
M2M,AlarmConfig,alarm_type,32,28,4,enum,1,STANDARD,Standard alarm type,,p.23,Device specific
M2M,AlarmConfig,priority,32,3,2,enum,0,LOW,Low priority alarm,,p.23,Device specific
M2M,AlarmConfig,priority,32,3,2,enum,1,MEDIUM,Medium priority alarm,,p.23,Device specific
```

**Notice:** Even though ABB calls it "AlarmConfig" not "AlarmAttributes", and uses "NO_ALARM" not "NONE", the CSV structure is identical. Everyone can still parse it the same way.

---

## Summary: The Complete Flow

```
1. Manual (PDF) 
   ↓ [Developer extracts]
2. CSV File (standardized format)
   ↓ [Everyone uses directly]
3. ├─→ Python code reads CSV
   ├─→ C code reads CSV  
   ├─→ Operator reads CSV in Excel
   ├─→ Web UI loads CSV
   └─→ Docs generated from CSV

Result: Single source of truth, no format conversion, everyone speaks the same language
```

**This is what "standardized transformation" means** - not fancy architecture, just a simple CSV format that everyone can use directly.
