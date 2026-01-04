# Expert-Level Configuration Design Guide

## Trade-off Analysis: Human vs Machine Readability

### Current CSV Approach
**Strengths:**
- ✅ Universal tool support (Excel, databases, Python pandas)
- ✅ Flat structure easy to query with SQL/grep
- ✅ Simple diff tools work out-of-box

**Weaknesses:**
- ❌ Massive repetition (32 bits stored 100+ times)
- ❌ No type reuse or composition
- ❌ Poor schema evolution (adding column breaks everything)
- ❌ Relationships implicit, not explicit
- ❌ No validation rules or constraints

---

## Recommended Layered Architecture

### Layer 1: Base Types (types.yaml)
**Purpose:** Reusable primitives shared across all devices

**Benefits:**
- Define `phases` enum once, use 1000 times
- Standard types (IEC 61850, IEEE) as authoritative source
- Units dictionary prevents typos ("Volts" vs "V" vs "volts")

**Machine Readability:** ⭐⭐⭐⭐⭐  
**Human Readability:** ⭐⭐⭐⭐

---

### Layer 2: Device Schema (pm5110.yaml)
**Purpose:** Device-specific register maps

**Benefits:**
- References base types via `inherits`
- Validation rules as data (not code)
- Changelog tracks evolution
- Metadata (addresses, access rights) separate from structure

**Machine Readability:** ⭐⭐⭐⭐⭐  
**Human Readability:** ⭐⭐⭐⭐⭐

---

### Layer 3: Generated Artifacts
**Purpose:** Optimized for specific consumers

```
┌──────────────┐
│  Base Types  │
│  Device Schema│
└──────┬───────┘
       │
       ├─→ Python dataclasses (for parsing)
       ├─→ TypeScript interfaces (for web UI)
       ├─→ HTML docs (for operators)
       ├─→ GraphQL schema (for APIs)
       └─→ Protobuf (for embedded systems)
```

---

## Alternative Format Comparison

### Option A: YAML/JSON (Recommended for New Projects)

**YAML Example:**
```yaml
AlarmAttributes:
  type: {offset: 28, width: 4, enum: AlarmType}
  priority: {offset: 3, width: 2, enum: Priority}
```

**Pros:**
- Hierarchical (group related fields)
- Comments inline
- Human-editable with validation (JSON Schema)

**Cons:**
- Whitespace-sensitive (YAML)
- Not tabular (harder to bulk-edit in Excel)

**Best For:** Configuration that changes infrequently, needs version control

---

### Option B: Protocol Buffers (.proto)

```protobuf
message AlarmAttributes {
  enum Type {
    NONE = 0;
    STANDARD1S = 1;
    // ...
  }
  Type type = 1 [(offset) = 28, (width) = 4];
  Priority priority = 2 [(offset) = 3, (width) = 2];
}
```

**Pros:**
- Code generation for 20+ languages
- Binary encoding (efficient over network)
- Schema evolution built-in (field numbers)

**Cons:**
- Less human-readable than YAML
- Requires toolchain (protoc compiler)

**Best For:** Cross-platform SDKs, high-performance systems

---

### Option C: Domain-Specific Language (DSL)

```
register AlarmAttributes at 0x1000 (32 bits, read-write) {
  field type: AlarmType at bits[28:31]
  field priority: Priority at bits[3:4]
  
  rule "Logic alarms require logic subtype"
    when type == LOGIC
    then subtype in [AND, OR, NAND, NOR]
}
```

**Pros:**
- Optimized for domain (no extra syntax)
- Can embed business rules
- Generate parsers, docs, validators from single source

**Cons:**
- Custom tooling required
- Learning curve for new team members

**Best For:** Large projects with dedicated infrastructure team

---

### Option D: Hybrid CSV + Metadata (Compromise)

Keep CSV for bulk data, add sidecar files:

```
registers/
  ├── alarm_attributes.csv     (flat data)
  ├── alarm_attributes.meta    (validation rules)
  ├── types/
  │   ├── enums.csv
  │   └── units.csv
  └── schema.json              (relationships)
```

**Pros:**
- Backward compatible with existing tools
- Progressive enhancement (add metadata incrementally)

**Cons:**
- Multiple files to keep in sync
- Still has CSV limitations

**Best For:** Migration from legacy systems

---

## Versioning Strategies

### Semantic Versioning for Schemas

```yaml
meta:
  schema_version: "2.1.0"  # MAJOR.MINOR.PATCH
```

**Rules:**
- **MAJOR:** Breaking changes (remove field, change type)
- **MINOR:** Additions (new optional field, new enum value)
- **PATCH:** Documentation/metadata only

### Field Deprecation Pattern

```yaml
AlarmAttributes:
  old_field:
    offset: 10
    deprecated: true
    deprecated_in: "2.0.0"
    removed_in: "3.0.0"
    replacement: "new_field"
    migration: |
      new_field = old_field * 1000  # Convert units
```

### Firmware Compatibility Matrix

```yaml
firmware_support:
  "1.x": ["schema_v1.0"]
  "2.0-2.5": ["schema_v1.0", "schema_v2.0"]
  "2.6+": ["schema_v2.0", "schema_v2.1"]
```

---

## Evolution Best Practices

### 1. Never Break Existing Parsers

**Bad:**
```yaml
# v1.0
priority: {offset: 3, width: 2}

# v2.0 - BREAKING!
priority: {offset: 5, width: 3}  # Moved offset
```

**Good:**
```yaml
# v2.0 - Additive
priority: {offset: 3, width: 2, deprecated: true}
priority_v2: {offset: 5, width: 3}
```

### 2. Use Reserved Ranges

```yaml
AlarmAttributes:
  reserved_fields:
    - {offset: 20, width: 2, purpose: "Future expansion"}
```

### 3. Default Values

```yaml
fields:
  new_feature:
    offset: 15
    width: 1
    added_in: "2.1.0"
    default: 0  # Safe for older firmware
```

---

## Multi-Consumer Generation

### Example: Generate Python Decoder

```python
# Generated from pm5110.yaml v1.0.0
from enum import Enum

class AlarmType(Enum):
    NONE = 0
    STANDARD1S = 1
    CUSTOM1S = 2

class AlarmAttributes:
    def __init__(self, raw_value: int):
        self.type = AlarmType((raw_value >> 28) & 0xF)
        self.priority = Priority((raw_value >> 3) & 0x3)
        self.enable = bool(raw_value & 0x1)
```

### Example: Generate HTML Documentation

```html
<!-- Generated from pm5110.yaml v1.0.0 -->
<h2>AlarmAttributes Register</h2>
<table>
  <tr><th>Field</th><th>Bits</th><th>Type</th></tr>
  <tr><td>type</td><td>28-31</td><td>AlarmType enum</td></tr>
  <tr><td>priority</td><td>3-4</td><td>Priority enum</td></tr>
</table>
```

---

## Recommended Tools

### For Validation
- **JSON Schema:** Validate YAML structure
- **Pydantic:** Python models with runtime validation
- **Zod:** TypeScript schema validation

### For Code Generation
- **datamodel-code-generator:** YAML → Python dataclasses
- **quicktype:** JSON → Multiple languages
- **jq/yq:** Query/transform YAML/JSON

### For Documentation
- **MkDocs:** Markdown → static site
- **Sphinx:** reStructuredText → docs
- **Docusaurus:** React-based doc site

---

## Migration Path

### Phase 1: Keep CSV, Add Schema Layer
1. Create `types.yaml` with reusable enums
2. Create `pm5110.yaml` that references CSV data
3. Build validator: CSV ↔ YAML consistency check

### Phase 2: Canonical Source Switch
1. YAML becomes source of truth
2. Generate CSV for backward compatibility
3. Scripts: `yaml2csv.py`, `csv2yaml.py`

### Phase 3: Full Generation
1. Generate parsers (Python, C++, TypeScript)
2. Generate docs (HTML, PDF, Markdown)
3. CI/CD: Validate on every commit

---

## Real-World Examples

### Google Protocol Buffers
- **Structure:** `.proto` files with field numbers
- **Evolution:** Add fields with new numbers, never reuse
- **Tooling:** `protoc` generates code for 20+ languages

### Kubernetes
- **Structure:** YAML manifests with OpenAPI schemas
- **Evolution:** `apiVersion` field tracks changes
- **Validation:** Built-in schema validation

### AWS CloudFormation
- **Structure:** JSON/YAML templates
- **Evolution:** Versioned resource types
- **Tooling:** `cfn-lint` validates before deployment

### Terraform
- **Structure:** HCL (HashiCorp Configuration Language)
- **Evolution:** Provider versioning + state migration
- **Tooling:** `terraform validate`, `terraform fmt`

---

## Summary Recommendations

| Aspect | Recommendation |
|--------|----------------|
| **Format** | YAML for source, generate everything else |
| **Structure** | 3-layer: Base types → Device schemas → Generated |
| **Versioning** | Semantic versioning with deprecation warnings |
| **Evolution** | Always additive, never break existing parsers |
| **Validation** | JSON Schema + runtime checks |
| **Documentation** | Generate from schema (single source of truth) |
| **Tools** | Version control (Git) + CI/CD validation |

The key insight: **Optimize for change, not just current state.** Your schema will evolve as devices add features, so design for evolution from day one.
