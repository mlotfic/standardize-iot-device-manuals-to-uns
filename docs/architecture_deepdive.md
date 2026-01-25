# System Architecture: Deep-Dive Documentation

> **Comprehensive technical architecture for system designers and senior developers**

---

## 📑 Table of Contents

1. [System Overview](#system-overview)
2. [Core Architecture Patterns](#core-architecture-patterns)
3. [Pipeline A: Decoder Architecture](#pipeline-a-decoder-architecture)
4. [Pipeline B: Router Architecture](#pipeline-b-router-architecture)
5. [Data Structures & Algorithms](#data-structures--algorithms)
6. [Template Processing Engine](#template-processing-engine)
7. [Runtime Engine Design](#runtime-engine-design)
8. [Integration Patterns](#integration-patterns)
9. [Performance & Scalability](#performance--scalability)
10. [Deployment Architectures](#deployment-architectures)

---

## 1. System Overview

### 1.1 Architectural Philosophy

**Core Principle:** Data-driven configuration over code generation

```
Traditional Approach:
Templates → Code Generator → Compiled Code → Runtime Execution
  ↑                ↑              ↑            ↑
  Static        Compile-time   Deploy-time   Runtime
  
Our Approach:
Templates → Runtime Interpreter → Execution
  ↑                 ↑              ↑
  Static         Runtime        Runtime
  
Benefits:
- No build step
- Instant template updates
- Lower complexity
- Easier debugging
```

### 1.2 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Configuration Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Templates (CSV)  │  Validation Rules  │  UNS Mappings      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Processing Layer                         │
├─────────────────────────────────────────────────────────────┤
│  Template Loader  │  Decoder Engine  │  UNS Router          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Integration Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Protocol Adapters  │  Publishers  │  Export Generators     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Target Systems                           │
├─────────────────────────────────────────────────────────────┤
│  SCADA  │  Historian  │  MQTT  │  OPC-UA  │  Analytics      │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Technology Stack

**Core Runtime:**
- Python 3.8+ (interpreter)
- CSV (configuration format)
- JSON (runtime cache format)

**Protocol Libraries:**
- pymodbus (Modbus RTU/TCP)
- opcua (OPC-UA client/server)
- paho-mqtt (MQTT client)

**Data Processing:**
- pandas (CSV processing, optional)
- numpy (numeric operations, optional)

**Integration:**
- Jinja2 (template generation for exports)
- SQLAlchemy (database integration, optional)

---

## 2. Core Architecture Patterns

### 2.1 Two-Pipeline Architecture

**Design Decision:** Separation of concerns between semantics and routing

```
┌────────────────────────────────────────────────────────────┐
│  PIPELINE A: Semantic Decoder                               │
│  Responsibility: "What does this data mean?"                │
├────────────────────────────────────────────────────────────┤
│  Input:  Raw bytes from device                             │
│  Process: Bit extraction → Transformation → Validation     │
│  Output: Decoded values with health status                 │
│                                                            │
│  Example:                                                  │
│  [0x19, 0x0B04] → {year: 2025, month: 1, health: GOOD}   │
└────────────────────────────────────────────────────────────┘
                          ↓
                  Decoded Data Stream
                          ↓
┌────────────────────────────────────────────────────────────┐
│  PIPELINE B: Namespace Router                              │
│  Responsibility: "Where should this data go?"              │
├────────────────────────────────────────────────────────────┤
│  Input:  Decoded values + metadata                        │
│  Process: Decision tree → Path generation → Publishing    │
│  Output: Data routed to correct namespace/target          │
│                                                            │
│  Example:                                                  │
│  {year: 2025, ...} → asset/PM8000/metadata/mfg_date      │
└────────────────────────────────────────────────────────────┘
```

**Why Two Pipelines?**

1. **Independence:** Decoding logic doesn't depend on routing
2. **Reusability:** Same decoder works for any routing strategy
3. **Testability:** Each pipeline tested independently
4. **Flexibility:** Mix and match components

### 2.2 Template-Driven Design Pattern

**Pattern:** Strategy Pattern + Registry Pattern + Interpreter Pattern

```python
# Strategy Pattern: Different field types, same interface
class FieldDecoder(ABC):
    @abstractmethod
    def decode(self, raw_value: int) -> Any:
        pass

class NumberField(FieldDecoder):
    def decode(self, raw_value: int) -> float:
        return raw_value * self.scale + self.offset

class EnumField(FieldDecoder):
    def decode(self, raw_value: int) -> str:
        return self.enum_map.get(raw_value, "UNKNOWN")

# Registry Pattern: DataTypes registered at load time
class DataTypeRegistry:
    def __init__(self):
        self._registry = {}
    
    def register(self, name: str, datatype: DataType):
        self._registry[name] = datatype
    
    def get(self, name: str) -> DataType:
        return self._registry[name]

# Interpreter Pattern: Templates interpreted at runtime
class TemplateInterpreter:
    def interpret(self, template_row: dict) -> Field:
        field_type = template_row['value_type']
        if field_type == 'number':
            return NumberField(...)
        elif field_type == 'enum':
            return EnumField(...)
        # ...
```

### 2.3 Immutable Data Structures

**Design Decision:** Templates are immutable after loading

```python
from dataclasses import dataclass, field
from typing import FrozenSet

@dataclass(frozen=True)  # Immutable
class DataType:
    name: str
    total_bits: int
    fields: FrozenSet[Field]  # Immutable set
    
    def __hash__(self):
        return hash((self.name, self.total_bits))
```

**Benefits:**
- Thread-safe (no locks needed)
- Cacheable (hash-based lookup)
- Predictable (no side effects)
- Memory efficient (shared references)

### 2.4 Health-First Design

**Pattern:** Result Object Pattern with health metadata

```python
@dataclass
class DecodedValue:
    """Every decoded value includes health status"""
    value: Any
    health: bool
    quality: str  # GOOD, QUESTIONABLE, BAD
    errors: List[str]
    warnings: List[str]
    metadata: dict
    
# Usage
result = decoder.decode(...)
if result.health:
    # Use value confidently
    publish(result.value)
else:
    # Handle error
    log_error(result.errors)
    alert_operator()
```

---

## 3. Pipeline A: Decoder Architecture

### 3.1 Decoder Data Flow

```
┌──────────────┐
│ Modbus Words │  [0x1234, 0x5678]
└──────┬───────┘
       │
       ↓ (1) Lookup Register
┌──────────────┐
│ Register Map │  (PM8000, 132) → DATETIME
└──────┬───────┘
       │
       ↓ (2) Get DataType
┌──────────────┐
│ DataType Lib │  DATETIME definition
└──────┬───────┘
       │
       ↓ (3) Word Combining
┌──────────────┐
│ 64-bit Value │  0x1234567890ABCDEF
└──────┬───────┘
       │
       ↓ (4) Field Extraction (for each field)
┌──────────────┐
│ Bit Masking  │  (value >> offset) & mask
└──────┬───────┘
       │
       ↓ (5) Transformation
┌──────────────┐
│ Offset/Scale │  raw * scale + offset
└──────┬───────┘
       │
       ↓ (6) Validation
┌──────────────┐
│ Health Check │  min ≤ value ≤ max?
└──────┬───────┘
       │
       ↓ (7) Enum Lookup
┌──────────────┐
│ Decoded Data │  {year: 2025, health: True, ...}
└──────────────┘
```

### 3.2 Bit Extraction Algorithm

**Core algorithm:** Efficient bit masking

```python
def extract_field(value: int, offset: int, width: int) -> int:
    """
    Extract width bits starting at offset from value.
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    
    Example:
    value  = 0b0001001000110100  (0x1234)
    offset = 4
    width  = 4
    
    Step 1: Create mask
    mask = (1 << 4) - 1 = 0b1111
    
    Step 2: Shift and mask
    (0x1234 >> 4) & 0xF = 0x123 & 0xF = 0x3
    
    Result: 3
    """
    mask = (1 << width) - 1
    return (value >> offset) & mask
```

**Optimization:** Precompute masks at load time

```python
@dataclass
class Field:
    name: str
    offset: int
    width: int
    _mask: int = field(init=False, repr=False)
    
    def __post_init__(self):
        # Precompute mask (done once at load)
        self._mask = (1 << self.width) - 1
    
    def extract(self, value: int) -> int:
        # Fast extraction (no mask calculation)
        return (value >> self.offset) & self._mask
```

### 3.3 Word Combining Strategies

**Strategy 1: Big-Endian (Most Significant Word First)**

```python
def combine_words_big_endian(words: List[int]) -> int:
    """
    words = [0x1234, 0x5678]
    
    Step 1: 0x1234 << 16 = 0x12340000
    Step 2: 0x12340000 | 0x5678 = 0x12345678
    """
    result = 0
    for word in words:
        result = (result << 16) | (word & 0xFFFF)
    return result
```

**Strategy 2: Little-Endian (Least Significant Word First)**

```python
def combine_words_little_endian(words: List[int]) -> int:
    """
    words = [0x5678, 0x1234]  # LSW first
    
    Step 1: Reverse words
    reversed_words = [0x1234, 0x5678]
    
    Step 2: Combine as big-endian
    """
    return combine_words_big_endian(list(reversed(words)))
```

**Strategy 3: Byte-Level Endianness**

```python
def combine_words_byte_swap(words: List[int]) -> int:
    """
    Handle byte-swapped words (Siemens PLCs)
    
    words = [0x1234, 0x5678]
    
    Step 1: Swap bytes in each word
    swapped = [0x3412, 0x7856]
    
    Step 2: Combine
    """
    swapped_words = [swap_bytes(w) for w in words]
    return combine_words_big_endian(swapped_words)
```

### 3.4 Validation Engine

**Multi-Layer Validation:**

```python
class ValidationEngine:
    def validate(self, field: Field, value: Any) -> ValidationResult:
        """
        Layer 1: Type validation
        Layer 2: Range validation
        Layer 3: Enum validation
        Layer 4: Cross-field validation
        """
        errors = []
        warnings = []
        
        # Layer 1: Type check
        if not isinstance(value, field.expected_type):
            errors.append(f"Type mismatch: expected {field.expected_type}")
            return ValidationResult(health=False, errors=errors)
        
        # Layer 2: Range check
        if field.min_value is not None:
            if value < field.min_value:
                errors.append(f"Value {value} < min {field.min_value}")
        
        if field.max_value is not None:
            if value > field.max_value:
                errors.append(f"Value {value} > max {field.max_value}")
        
        # Layer 3: Enum check
        if field.type == 'enum':
            if value not in field.enum_values:
                errors.append(f"Value {value} not in enum table")
        
        # Layer 4: Warning thresholds
        if field.warning_threshold is not None:
            if value > field.warning_threshold:
                warnings.append(f"Approaching limit: {value}")
        
        health = len(errors) == 0
        quality = 'GOOD' if health else 'BAD'
        if warnings:
            quality = 'QUESTIONABLE'
        
        return ValidationResult(
            health=health,
            quality=quality,
            errors=errors,
            warnings=warnings
        )
```

### 3.5 Caching Strategy

**Two-Level Cache:**

```python
class DecoderCache:
    """
    L1: Template cache (in-memory, immutable)
    L2: Decode result cache (LRU, size-limited)
    """
    
    def __init__(self, max_results=1000):
        # L1: Templates (never evicted)
        self.datatypes: Dict[str, DataType] = {}
        self.register_map: Dict[Tuple[str, int], RegisterDef] = {}
        
        # L2: Recent decodes (LRU cache)
        from functools import lru_cache
        self._decode_cached = lru_cache(maxsize=max_results)(
            self._decode_uncached
        )
    
    def decode(self, device: str, address: int, words: List[int]):
        # Convert words to hashable type for cache key
        words_tuple = tuple(words)
        
        # L1: Lookup template (fast, O(1))
        register_def = self.register_map[(device, address)]
        datatype = self.datatypes[register_def.datatype]
        
        # L2: Cached decode (if same data seen recently)
        return self._decode_cached(datatype, words_tuple)
```

---

## 4. Pipeline B: Router Architecture

### 4.1 UNS Decision Tree

**Decision Matrix Implementation:**

```python
class UNSDecisionTree:
    """
    Implements decision tree for namespace routing.
    
    Questions → Answers → Namespace
    """
    
    RULES = [
        # Rule 1: Fixed metadata about device
        {
            'conditions': {
                'Q1': 'ABOUT',
                'Q2': 'FIXED',
                'Q4': 'AUDIT'
            },
            'namespace': 'asset',
            'path_template': 'asset/{device_id}/metadata/{field_name}'
        },
        
        # Rule 2: Live process measurements
        {
            'conditions': {
                'Q1': 'FROM',
                'Q2': 'CONTINUOUS',
                'Q4': 'PROCESS'
            },
            'namespace': 'measurement',
            'path_template': 'measurement/{device_id}/{field_name}'
        },
        
        # Rule 3: Event-driven alarms
        {
            'conditions': {
                'Q1': 'FROM',
                'Q2': 'EVENT',
                'Q4': 'EXCEPTION'
            },
            'namespace': 'alarm',
            'path_template': 'alarm/{device_id}/{alarm_type}'
        },
        
        # ... more rules
    ]
    
    def route(self, register_meta: dict) -> str:
        """Find matching rule and generate path"""
        for rule in self.RULES:
            if self._matches(rule['conditions'], register_meta):
                return self._generate_path(
                    rule['path_template'],
                    register_meta
                )
        
        # Default fallback
        return f"unknown/{register_meta['device_id']}/{register_meta['name']}"
    
    def _matches(self, conditions: dict, meta: dict) -> bool:
        """Check if all conditions match"""
        return all(
            meta.get(key) == value
            for key, value in conditions.items()
        )
```

### 4.2 Path Generation

**Template Engine for Paths:**

```python
from jinja2 import Template

class PathGenerator:
    def __init__(self):
        self.templates = {}
    
    def register_template(self, namespace: str, template: str):
        """
        Register path template for namespace.
        
        Example:
        register_template(
            'measurement',
            'measurement/{{site}}/{{area}}/{{device_id}}/{{field_name}}'
        )
        """
        self.templates[namespace] = Template(template)
    
    def generate(self, namespace: str, context: dict) -> str:
        """
        Generate path from template and context.
        
        context = {
            'site': 'FactoryA',
            'area': 'Line1',
            'device_id': 'PM8000_001',
            'field_name': 'voltage_l1'
        }
        
        →  'measurement/FactoryA/Line1/PM8000_001/voltage_l1'
        """
        template = self.templates.get(namespace)
        if not template:
            raise ValueError(f"No template for namespace: {namespace}")
        
        return template.render(context)
```

### 4.3 Multi-Target Publishing

**Publisher Pattern with Fan-Out:**

```python
class PublisherManager:
    """Manages multiple publishers with fan-out pattern"""
    
    def __init__(self):
        self.publishers: List[Publisher] = []
    
    def add_publisher(self, publisher: Publisher):
        """Add a publisher to the fan-out list"""
        self.publishers.append(publisher)
    
    async def publish_all(self, path: str, data: dict):
        """Publish to all publishers concurrently"""
        tasks = [
            pub.publish(path, data)
            for pub in self.publishers
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle failures
        for pub, result in zip(self.publishers, results):
            if isinstance(result, Exception):
                logger.error(f"Publish failed for {pub}: {result}")
```

**Example Publishers:**

```python
class MQTTPublisher(Publisher):
    async def publish(self, path: str, data: dict):
        topic = f"uns/{path}"
        payload = json.dumps(data)
        await self.client.publish(topic, payload)

class OPCUAPublisher(Publisher):
    async def publish(self, path: str, data: dict):
        node_id = self.path_to_nodeid(path)
        await self.server.write_value(node_id, data['value'])

class InfluxDBPublisher(Publisher):
    async def publish(self, path: str, data: dict):
        point = {
            'measurement': path.split('/')[0],
            'tags': {'path': path},
            'fields': data,
            'time': datetime.utcnow()
        }
        await self.client.write(point)
```

---

## 5. Data Structures & Algorithms

### 5.1 Core Data Structures

**DataType Registry (Trie-based):**

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.datatype = None

class DataTypeRegistry:
    """
    Trie for efficient prefix matching of datatypes.
    
    Allows patterns like:
    - DATETIME → Exact match
    - DATETIME_* → Prefix match
    """
    
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, name: str, datatype: DataType):
        node = self.root
        for char in name:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.datatype = datatype
    
    def get(self, name: str) -> Optional[DataType]:
        node = self.root
        for char in name:
            if char not in node.children:
                return None
            node = node.children[char]
        return node.datatype
    
    def get_prefix(self, prefix: str) -> List[DataType]:
        """Get all datatypes matching prefix"""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return self._collect_all(node)
```

### 5.2 Register Map (Hash Map + Spatial Index)

```python
class RegisterMap:
    """
    Dual-index structure for fast lookup:
    1. Hash map: (device, address) → RegisterDef
    2. Interval tree: device → address ranges
    """
    
    def __init__(self):
        # Primary index: exact lookups
        self._exact: Dict[Tuple[str, int], RegisterDef] = {}
        
        # Secondary index: range queries
        self._ranges: Dict[str, IntervalTree] = {}
    
    def add(self, device: str, address: int, reg_def: RegisterDef):
        # Add to exact lookup
        key = (device, address)
        self._exact[key] = reg_def
        
        # Add to range index
        if device not in self._ranges:
            self._ranges[device] = IntervalTree()
        
        end_address = address + reg_def.word_count - 1
        self._ranges[device].add(Interval(address, end_address, reg_def))
    
    def get_exact(self, device: str, address: int) -> Optional[RegisterDef]:
        """O(1) exact lookup"""
        return self._exact.get((device, address))
    
    def get_range(self, device: str, start: int, end: int) -> List[RegisterDef]:
        """O(log n + k) range query"""
        if device not in self._ranges:
            return []
        return [i.data for i in self._ranges[device].overlap(start, end)]
```

### 5.3 Validation Cache (Bloom Filter + LRU)

```python
class ValidationCache:
    """
    Two-stage cache for validation results:
    1. Bloom filter: Quick negative checks (not seen before)
    2. LRU cache: Store recent validation results
    """
    
    def __init__(self, capacity=10000):
        from pybloom_live import BloomFilter
        
        # Stage 1: Bloom filter (probabilistic)
        self.bloom = BloomFilter(capacity=capacity, error_rate=0.001)
        
        # Stage 2: LRU cache (definitive)
        from functools import lru_cache
        self._cache = {}
        self.capacity = capacity
    
    def check(self, field_id: str, value: Any) -> Optional[bool]:
        """
        Check if we've validated this exact value before.
        
        Returns:
        - True: Valid (cached result)
        - False: Invalid (cached result)
        - None: Not in cache
        """
        key = (field_id, value)
        
        # Quick check: definitely not in cache
        if key not in self.bloom:
            return None
        
        # Definitive check: lookup in LRU
        return self._cache.get(key)
    
    def store(self, field_id: str, value: Any, is_valid: bool):
        """Store validation result"""
        key = (field_id, value)
        
        self.bloom.add(key)
        self._cache[key] = is_valid
        
        # LRU eviction if full
        if len(self._cache) > self.capacity:
            # Remove oldest entry
            oldest = next(iter(self._cache))
            del self._cache[oldest]
```

---

## 6. Template Processing Engine

### 6.1 CSV Parser with Validation

```python
class TemplateParser:
    """
    Parse and validate CSV templates.
    
    Validation levels:
    1. Syntax: Valid CSV format
    2. Schema: Required columns present
    3. Semantics: Values make sense
    4. Integrity: Cross-template consistency
    """
    
    REQUIRED_COLUMNS = {
        'structure': ['datatype', 'field_name', 'bit_start', 'bit_end', 'value_type'],
        'validation': ['datatype', 'field_name', 'min_value', 'max_value'],
        'enums': ['datatype', 'field_name', 'value', 'label'],
        'register_map': ['device_model', 'register_address', 'datatype'],
    }
    
    def parse(self, template_type: str, filepath: str) -> List[dict]:
        """Parse CSV with full validation"""
        # Level 1: Syntax
        rows = self._parse_csv(filepath)
        
        # Level 2: Schema
        self._validate_schema(template_type, rows)
        
        # Level 3: Semantics
        self._validate_semantics(template_type, rows)
        
        return rows
    
    def _validate_schema(self, template_type: str, rows: List[dict]):
        """Check required columns present"""
        required = self.REQUIRED_COLUMNS[template_type]
        first_row = rows[0]
        
        missing = [col for col in required if col not in first_row]
        if missing:
            raise SchemaError(f"Missing columns: {missing}")
    
    def _validate_semantics(self, template_type: str, rows: List[dict]):
        """Check values make sense"""
        for row in rows:
            if template_type == 'structure':
                # Check bit positions
                start = int(row['bit_start'])
                end = int(row['bit_end'])
                if start > end:
                    raise SemanticError(
                        f"bit_start {start} > bit_end {end}"
                    )
                
                # Check value type is valid
                if row['value_type'] not in ['number', 'enum', 'flag', 'reserved']:
                    raise SemanticError(
                        f"Invalid value_type: {row['value_type']}"
                    )
```

### 6.2 Template Merger

```python
class TemplateMerger:
    """
    Merge multiple CSV files (default + custom overlays).
    
    Strategy:
    - Default templates: Base definitions
    - Custom templates: Override or extend
    """
    
    def merge(self, default_files: List[str], custom_files: List[str]) -> dict:
        """
        Merge templates with custom overriding default.
        
        Returns merged datatype library.
        """
        # Load defaults
        datatypes = self._load_datatypes(default_files)
        
        # Apply custom overlays
        for custom_file in custom_files:
            custom_types = self._load_datatypes([custom_file])
            
            for name, custom_dt in custom_types.items():
                if name in datatypes:
                    # Merge: custom overrides default
                    datatypes[name] = self._merge_datatype(
                        datatypes[name],
                        custom_dt
                    )
                else:
                    # New datatype
                    datatypes[name] = custom_dt
        
        return datatypes
    
    def _merge_datatype(self, default: DataType, custom: DataType) -> DataType:
        """Merge two datatype definitions"""
        # Start with default fields
        merged_fields = {f.name: f for f in default.fields}
        
        # Override/add custom fields
        for field in custom.fields:
            merged_fields[field.name] = field
        
        return DataType(
            name=custom.name or default.name,
            total_bits=custom.total_bits or default.total_bits,
            fields=list(merged_fields.values())
        )
```

---

## 7. Runtime Engine Design

### 7.1 Event-Driven Architecture

```python
class DecoderEngine:
    """
    Event-driven decoder with async I/O.
    
    Events:
    - register_read: New data from device
    - decode_complete: Decoding finished
    - validation_failed: Bad data detected
    - publish_success: Data published
    """
    
    def __init__(self):
        self.event_bus = EventBus()
        self.decoder = Decoder()
        self.router = Router()
        self.publishers = []
    
    async def run(self):
        """Main event loop"""
        # Subscribe to events
        self.event_bus.subscribe('register_read', self.on_register_read)
        self.event_bus.subscribe('decode_complete', self.on_decode_complete)
        
        # Start polling devices
        await self.poll_devices()
    
    async def on_register_read(self, event: Event):
        """Handle new register data"""
        device = event.data['device']
        address = event.data['address']
        words = event.data['words']
        
        # Decode
        result = await self.decoder.decode_async(device, address, words)
        
        # Emit decode complete event
        await self.event_bus.emit('decode_complete', {
            'device': device,
            'address': address,
            'result': result
        })
    
    async def on_decode_complete(self, event: Event):
        """Handle decoded data"""
        result = event.data['result']
        
        if not result.health:
            # Emit validation failed
            await self.event_bus.emit('validation_failed', event.data)
            return
        
        # Route and publish
        path = self.router.route(result)
        await self.publish_all(path, result.data)
```

### 7.2 Async I/O for Device Communication

```python
class AsyncModbusPoller:
    """
    Async Modbus poller with connection pooling.
    
    Features:
    - Connection pool (reuse connections)
    - Retry logic (handle transient failures)
    - Circuit breaker (avoid hammering failed devices)
    """
    
    def __init__(self, max_connections=10):
        self.pool = ConnectionPool(max_connections)
        self.circuit_breakers = {}
    
    async def poll_register(self, device: Device, register: Register):
        """Poll single register with retry logic"""
        circuit_breaker = self.circuit_breakers.get(device.id)
        
        if circuit_breaker and circuit_breaker.is_open:
            # Skip if circuit breaker open
            return None
        
        retries = 3
        for attempt in range(retries):
            try:
                # Get connection from pool
                async with self.pool.get_connection(device) as conn:
                    # Read register
                    words = await conn.read_holding_registers(
                        register.address,
                        register.word_count
                    )
                    
                    # Success: reset circuit breaker
                    if circuit_breaker:
                        circuit_breaker.reset()
                    
                    return words
            
            except ModbusError as e:
                if attempt < retries - 1:
                    # Retry with backoff
                    await asyncio.sleep(2 ** attempt)
                else:
                    # Final failure: open circuit breaker
                    if circuit_breaker:
                        circuit_breaker.open()
                    raise
```

---

## 8. Integration Patterns

### 8.1 Adapter Pattern for Protocols

```python
class ProtocolAdapter(ABC):
    """Base adapter for all protocols"""
    
    @abstractmethod
    async def connect(self, config: dict):
        pass
    
    @abstractmethod
    async def read(self, address: int, count: int) -> List[int]:
        pass
    
    @abstractmethod
    async def write(self, address: int, values: List[int]):
        pass

class ModbusAdapter(ProtocolAdapter):
    """Modbus RTU/TCP adapter"""
    
    async def read(self, address: int, count: int) -> List[int]:
        return await self.client.read_holding_registers(address, count)

class OPCUAAdapter(ProtocolAdapter):
    """OPC-UA adapter"""
    
    async def read(self, address: int, count: int) -> List[int]:
        # OPC-UA uses node IDs, not addresses
        node_id = self.address_to_nodeid(address)
        values = await self.client.read_values([node_id])
        return self.pack_to_words(values)
```

### 8.2 Export Generator Pattern

```python
class ExportGenerator:
    """Generate target-specific configuration files"""
    
    def generate_ignition_csv(self, register_map: dict, output_file: str):
        """Generate Ignition Gateway CSV import file"""
        with open(output_file, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Tag Name', 'Tag Path', 'Address', 'Data Type', 'Scan Class'])
            
            for reg in register_map.values():
                writer.writerow([
                    reg.name,
                    f"Devices/{reg.device}/{reg.category}",
                    f"{reg.address}:{reg.word_count}",
                    self.modbus_to_ignition_type(reg.datatype),
                    '1s'  # Scan rate
                ])
    
    def generate_opcua_nodes(self, register_map: dict) -> List[dict]:
        """Generate OPC-UA node definitions"""
        nodes = []
        for reg in register_map.values():
            nodes.append({
                'nodeId': f"ns=2;s={reg.device}.{reg.name}",
                'browseName': reg.name,
                'displayName': reg.description,
                'dataType': self.to_opcua_type(reg.datatype),
                'accessLevel': 'CurrentRead' if reg.access == 'R' else 'CurrentReadWrite'
            })
        return nodes
```

---

## 9. Performance & Scalability

### 9.1 Performance Characteristics

**Decode Performance:**

| Operation | Complexity | Typical Time |
|-----------|-----------|--------------|
| Template load | O(n) | 85ms (1000 registers) |
| Register lookup | O(1) | <1μs (hash map) |
| Word combining | O(k) | <1μs (k = word count) |
| Bit extraction | O(1) | <1μs (bit mask) |
| Validation | O(m) | <100μs (m = validation rules) |
| Full decode | O(n+m) | 0.8ms average |

**Memory Footprint:**

```
Template cache: ~2KB per datatype
Register map: ~100 bytes per register
Decode result cache: ~500 bytes per cached result

For 1000 registers:
- Templates: 100 datatypes × 2KB = 200KB
- Register map: 1000 × 100B = 100KB
- Results cache: 1000 × 500B = 500KB
Total: ~800KB
```

### 9.2 Scaling Strategies

**Horizontal Scaling:**

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Decoder  │  │ Decoder  │  │ Decoder  │
│ Instance │  │ Instance │  │ Instance │
│    1     │  │    2     │  │    3     │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┴─────────────┘
                   │
            ┌──────▼──────┐
            │ Load        │
            │ Balancer    │
            └──────┬──────┘
                   │
            ┌──────▼──────┐
            │ MQTT Broker │
            └─────────────┘
```

**Vertical Scaling:**

```python
class ParallelDecoder:
    """Use multiprocessing for CPU-bound decoding"""
    
    def __init__(self, workers=4):
        self.pool = ProcessPoolExecutor(max_workers=workers)
    
    async def decode_batch(self, registers: List[Tuple]) -> List[dict]:
        """Decode multiple registers in parallel"""
        loop = asyncio.get_event_loop()
        
        # Distribute work across processes
        tasks = [
            loop.run_in_executor(self.pool, self.decode_one, reg)
            for reg in registers
        ]
        
        return await asyncio.gather(*tasks)
```

---

## 10. Deployment Architectures

### 10.1 Edge Deployment

```
┌────────────────────────────────────────┐
│         Edge Device (RPi, Gateway)      │
├────────────────────────────────────────┤
│  ┌──────────────────────────────────┐ │
│  │ Decoder Engine                    │ │
│  │  - Template cache (local)         │ │
│  │  - Modbus client                  │ │
│  │  - MQTT publisher                 │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
             ↓ MQTT
┌────────────────────────────────────────┐
│         MQTT Broker (Cloud)            │
└────────────────────────────────────────┘
             ↓ Subscribe
┌────────────────────────────────────────┐
│      SCADA / Analytics (Cloud)         │
└────────────────────────────────────────┘
```

### 10.2 Centralized Deployment

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Device 1 │  │ Device 2 │  │ Device N │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │ Modbus      │ Modbus      │ Modbus
     └─────────────┴─────────────┘
                   │
        ┌──────────▼──────────┐
        │  Central Decoder    │
        │  - All templates    │
        │  - All devices      │
        │  - Publish to UNS   │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  UNS Infrastructure │
        │  - MQTT / OPC-UA    │
        │  - Historian        │
        │  - Analytics        │
        └─────────────────────┘
```

### 10.3 Hybrid Deployment

```
Site A:                  Site B:
┌──────────┐            ┌──────────┐
│Edge Node │            │Edge Node │
│ Decoder  │            │ Decoder  │
└────┬─────┘            └────┬─────┘
     │ MQTT                  │ MQTT
     └───────────┬───────────┘
                 │
        ┌────────▼────────┐
        │ Cloud Broker    │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ Cloud Services  │
        │ - Historian     │
        │ - Analytics     │
        │ - SCADA         │
        └─────────────────┘
```

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-11  
**For:** System Architects & Senior Developers