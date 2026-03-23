# Polaris-Calc Unit Conversion System

## Overview
The **Unit Conversion System** is a robust, dimension-aware utility for converting between simple and complex unit expressions. It supports standard SI prefixes, compound mathematical expressions, and dimensional mapping.

## Key Features
- **SI Prefixes**: Automatically recognizes prefixes from Yotta ($10^{24}$) to Yocto ($10^{-24}$).
- **Compound Expressions**: Supports units like `kg*m/s^2`, `J/(kg*K)`, `km/h`, and `m^3`.
- **Dimensional Analysis**: Every unit is mapped to a 7-element dimensional vector: $[L, M, T, I, \Theta, N, J]$.
- **Physical Category Detection**: Can identify the physical quantity of a unit (e.g., `kg*m/s^2` is Force).
- **Ambiguity Handling**: Recognizes when multiple physical quantities share the same dimensions (e.g., $s^{-1}$ could be frequency, angular velocity, or radioactivity).
- **Temperature Scales**: Correctly handles absolute temperatures ($20\ ^\circ C = 293.15\ K$) vs. temperature differences ($1\ K = 1\ ^\circ C$ increase).
- **Currencies**: Supports basic currency conversion (but prevents mixing currencies in physical expressions like `kg*USD`).

## Mathematical Support
- **Operators**: `*`, `/`, `^`, `( )`.
- **Implied Multiplication**: `kg m` is interpreted as `kg * m`.
- **Unicode Support**: Supports characters like `·`, `²`, `³`, `µ`.

## Internal Architecture

### Base Dimensions
System-wide consistency is maintained by normalizing all units to an internal SI-based coordinate system (kilogram, meter, second, etc.).
- **Mass Base**: Kilogram (kg).
- **Length Base**: Meter (m).
- **Time Base**: Second (s).

### Core Components
1. **`default_units.py`**: The unit database. Every entry contains a conversion factor to the base unit and flags for prefix support.
2. **`unit_conversor.py`**: The logic module. It parses expressions into dimensional vectors and calculates cumulative conversion factors.
3. **`test_unit_conversor.py`**: A comprehensive test suite for verifying correctness.

## Usage Examples

### 1. Simple Conversion
```python
from unit_conversor import convert

# 1 km to meters -> 1000.0
res = convert(1.0, "km", "m")
```

### 2. Compound Expressions
```python
# Convert Joule/(kg·K) to calorie/(g·K)
res = convert(1.0, "J/(kg*K)", "cal/(g*K)")
```

### 3. Dimensional Querying
```python
from unit_conversor import get_unit_type

# Returns "Force"
category = get_unit_type("kg*m/s^2")

# Returns "Hz, rad/s, Bq" (ambiguous case)
category = get_unit_type("s^-1")
```

## Running Tests
Run the standalone test script to ensure system integrity:
```bash
python test_unit_conversor.py
```

## Extending the Library
To add a new unit, simply add an entry to the appropriate category in `default_units.py`:
```python
# Example: Adding a new unit to "Length"
"Length": {
    "m": {"factor": 1.0, "use_prefixes": True},
    "my_unit": {"factor": 5.0, "use_prefixes": False},
}
```
If the new unit introduces a new dimension key or an ambiguous symbol, update `base_dimensions` and `_DIM_KEY_OVERRIDES` in `unit_conversor.py`.
