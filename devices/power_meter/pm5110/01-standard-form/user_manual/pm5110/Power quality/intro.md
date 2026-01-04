# Power quality

## Power quality measurements
The meter measures voltage and current harmonics up to the 15th individual harmonic, and calculates Total Harmonic Distortion (THD, thd) and Total Demand Distortion (TDD) based on 31st harmonics.

## Harmonics overview
Harmonics are integer multiples of the fundamental frequency of the power system.

Harmonics information is valuable for power quality analysis, determining properly rated transformers, maintenance and troubleshooting. Evaluation of harmonics is required for compliance to system power quality standards such as EN50160 and meter power quality standards such as IEC 61000-4-30.

Harmonics measurements include per-phase magnitudes and angles (relative to the fundamental frequency of the phase A voltage) for the fundamental and higher order harmonics relative to the fundamental frequency. The meter’s power system setting defines which phases are present and determines how line-to-line or line-to-neutral voltage harmonics and current harmonics are calculated.

Harmonics are used to identify whether the supplied system power meets required power quality standards, or if non-linear loads are affecting your power system. Power system harmonics can cause current flow on the neutral conductor, and damage to equipment such as increased heating in electric motors. Power conditioners or harmonic filters can be used to minimize unwanted harmonics.

### Total harmonic distortion %
Total harmonic distortion (THD%) is a measure of the total per-phase voltage or current harmonic distortion present in the power system.
THD% provides a general indication of the quality of a waveform. THD% is calculated for each phase of both voltage and current.

### Total demand distortion
Total demand distortion (TDD) is the per-phase harmonic current distortion against the full load demand of the electrical system.

TDD indicates the impact of harmonic distortion in the system. For example, if your system is showing high THD values but a low demand, the impact of harmonic distortion on your system might be insignificant. However at full load, the THD value for the current harmonics is equal to TDD, so this could negatively impact your system.

### Harmonic content calculations
Harmonic content (HC) is equal to the RMS value of all the non-fundamental harmonic components in one phase of the power system.

```formula
HC = √(H2² + H3² + H4² + ... + Hn²)
```

Where:
- Hn = RMS value of the nth harmonic component


### THD% calculations
THD% is a quick measure of the total distortion present in a waveform and is the ratio of harmonic content (HC) to the fundamental harmonic (H1).

```formula
THD% = (HC / H1) × 100
```

Where:
- HC = Harmonic content
- H1 = RMS value of the fundamental harmonic component

### thd calculations
thd is an alternate method for calculating total harmonic distortion that uses the RMS value for the total harmonic content rather than the fundamental content.

```formula
thd = (HC / √(H1² + HC²)) × 100
```

Where:
- HC = Harmonic content
- H1 = RMS value of the fundamental harmonic component
- Total RMS = √(H1² + HC²)
- HC = Harmonic content

### TDD calculations
TDD (total demand distortion) evaluates the harmonic currents between an end user and a power source.
The harmonic values are based on a point of common coupling (PCC), which is a common point where each user receives power from the power source.

The meter uses the following equation to calculate TDD:

```formula
TDD = (√(HC×IA)² + (HC×IB) + (HC×IC)²) / ILoad × 100
```

Where:
- HC = Harmonic content.
- IA, IB, IC = RMS current for phases A, B, and C
- ILoad is equal to the maximum demand load on the power system.

### Viewing harmonics using the display
You can view harmonics data using the display.

voltage or current harmonics you want to view.

IEEE mode	IEC mode	Description
V L-L	U	Line-to-line voltage harmonics data
V L-N	V	Line-to-neutral voltage harmonics data
Amps	I	Current harmonics data
TDD	TDD	Total demand distortion data
The fundamental (1st) harmonics numeric magnitudes and angles for all phases are displayed.

```json
{
    "Power Quality": {
        "Harmonics": [
            {
                "description": "Fundamental harmonic (1st harmonic) voltage and current magnitudes and angles for all phases.",
                "Harmonics": "Fundamental (1st)",
                "IEE mode": "V L-L",
                "IEC mode": "U",
                "units": "%"
            },
            {
                "description": "Fundamental harmonic (1st harmonic) voltage and current magnitudes and angles for all phases.",
                "Harmonics": "Fundamental (1st)",
                "IEE mode": "V L-N",
                "IEC mode": "V",
                "units": "%"
            },
            {
                "description": "Fundamental harmonic (1st harmonic) voltage and current magnitudes and angles for all phases.",
                "Harmonics": "Fundamental (1st)",
                "IEE mode": "Amps",
                "IEC mode": "I",
                "units": "%"
            },
            {
                "description": "Total Harmonic Distortion percentage for voltage and current for all phases.",
                "Harmonics": "Fundamental (1st)",
                "IEE mode": "TDD",
                "IEC mode": "TDD",
                "units": "%"
            }
        ],
        }
}
```

The vertical axis of the harmonics graph indicates the harmonic’s magnitude as a percentage of the fundamental harmonic, and is scaled based on the largest harmonic displayed. At the top of each vertical bar is a marker that shows the maximum value of the harmonic. If the harmonic is greater than the fundamental harmonic, this marker is triangular-shaped to show that the value is out of range.

### Viewing TDD using the display
The meter display provides screens that show TDD values.

### Viewing THD/thd using the display
You can view THD/thd data using the display.
NOTE: Your meter’s Modbus map includes registers for total harmonic distortion data for integration into your power or energy management system.
Navigate to THD to view the THD/thd Select screen.
Press THD to display values that use the calculation method based on the fundamental harmonic or thd to display values that use the calculation method based on the RMS value of all harmonics in that phase (including the fundamental).
IEEE mode	IEC mode	Description
Amps	I	Total harmonic distortion data for per phase and neutral currents.
V L-L	U	Total harmonic distortion data line-to-line voltage.
V L-N	V	Total harmonic distortion data line-to-neutral voltage.
Press the current or voltage THD or thd values you want to view.
The total harmonic distortion percentage values are displayed.

Press the up arrow to return to the main display screens.

```json
{
    "Power Quality": {
        : [
            {
                "description": "Total harmonic distortion percentage for per phase and neutral currents.",
                "Harmonics":"THD/thd",
                "IEE mode": "Amps",
                "IEC mode": "I",
                "units": "%"
            },
            {
                "description": "Total harmonic distortion percentage for line-to-line voltage.",
                "Harmonics":"THD/thd",
                "IEE mode": "V L-L",
                "IEC mode": "U",
                "units": "%"
            },
            {
                "description": "Total harmonic distortion percentage for line-to-neutral voltage.",
                "Harmonics":"THD/thd",
                "IEE mode": "V L-N",
                "IEC mode": "V",
                "units": "%"
            }
        ]
    }
}
```