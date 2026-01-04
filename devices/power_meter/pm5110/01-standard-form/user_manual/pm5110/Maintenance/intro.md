# Maintenance

## Maintenance overview
The meter does not contain any user-serviceable parts. If the meter requires service, contact your local Schneider Electric Technical Support representative.

### Power meter memory
The meter uses its nonvolatile memory to retain data and metering configuration values.

Under the operating temperature range specified for the power meter this nonvolatile memory has an expected life of at least 45 years.

NOTE: Life expectancy is a function of operating conditions and does not constitute any expressed or implied warranty.

### Firmware version, model and serial number
You can view the meter model, serial number, date of manufacture, firmware version (including OS - Operating System and RS - Reset System), language version, and OS CRC (Cyclic Redundancy Check) from the display panel. The OS CRC value is a number (Hexadecimal format) that identifies the uniqueness between different OS firmware versions.

Using the display panel: Navigate to Maint > Diag > Info.

#### Firmware upgrades
The power meter supports the downloading of new firmware and language files over the communications link.
This requires the free DLF3000 software, which is available at www.se.com . The DLF3000 offers an extensive Help file with information on operating the software. The most recent firmware and language files are also available on the website.

downloading new firmware to PM5110 power meter through Modbus is not supported.


### Diagnostics information
The diagnostics screen provides meter information, status and event data for troubleshooting.


### Control power (auxiliary power) interruption event
For MID/MIR compliant models.

### Troubleshooting

```json
{
    "Maintenance": {
        "Power meter memory": {
            "description": "The meter uses its nonvolatile memory to retain data and metering configuration values. Under the operating temperature range specified for the power meter this nonvolatile memory has an expected life of at least 45 years."
        },
        "Firmware version, model and serial number": {
            "description": "You can view the meter model, serial number, date of manufacture, firmware version (including OS - Operating System and RS - Reset System), language version, and OS CRC (Cyclic Redundancy Check) from the display panel. The OS CRC value is a number (Hexadecimal format) that identifies the uniqueness between different OS firmware versions."
        },
        "Diagnostics information": {
            "description": "The diagnostics screen provides meter information, status and event data for troubleshooting."
        },
        "Control power (auxiliary power) interruption event": {
            "description": "For MID/MIR compliant models."
        },
        "Troubleshooting": {
            "description": "LED indicators: Abnormal heartbeat / serial communications LED behavior could mean potential problems with the meter."
        }
    }
}
```

### LED indicators
Abnormal heartbeat / serial communications LED behavior could mean potential problems with the meter.
Problem	Probable causes	Possible solutions
LED flash rate does not change when data is sent from the host computer.	Communications wiring	If using a serial-to-RS-485 converter, trace and check that all wiring from the computer to the meter is properly terminated.
Internal hardware problem	Perform a hard reset: turn off control power to the meter, then re-apply power. If the problem persists, contact Technical Support .
Heartbeat / serial communications LED remains lit and does not flash ON and OFF	Internal hardware problem	Perform a hard reset: turn off control power to the meter, then re-apply power. If the problem persists, contact Technical Support .
Heartbeat / serial communications LED flashes, but the display is blank.	Display setup parameters incorrectly set	Review display parameter setup.
If the problem is not fixed after troubleshooting, contact Technical Support for help. Make sure you have your meter’s firmware version, model and serial number information available.

```json
{
    "Maintenance": {
        "LED indicators": {
            "description": "Abnormal heartbeat / serial communications LED behavior could mean potential problems with the meter.",
            "troubleshooting_steps": [
                {
                    "problem": "LED flash rate does not change when data is sent from the host computer.",
                    "probable_causes": [
                        "Communications wiring",
                        "Internal hardware problem"
                    ],
                    "possible_solutions": [
                        "If using a serial-to-RS-485 converter, trace and check that all wiring from the computer to the meter is properly terminated.",
                        "Perform a hard reset: turn off control power to the meter, then re-apply power. If the problem persists, contact Technical Support."
                    ]
                },
                {
                    "problem": "Heartbeat / serial communications LED remains lit and does not flash ON and OFF",
                    "probable_causes": [
                        "Internal hardware problem"
                    ],
                    "possible_solutions": [
                        "Perform a hard reset: turn off control power to the meter, then re-apply power. If the problem persists, contact Technical Support."
                    ]
                },
                {
                    "problem": "Heartbeat / serial communications LED flashes, but the display is blank.",
                    "probable_causes": [
                        "Display setup parameters incorrectly set"
                    ],
                    "possible_solutions": [
                        "Review display parameter setup."
                    ]
                }
            ]
        }
    }
}
```
Troubleshooting checks
There are some checks you can perform to try to identify potential issues with the meter’s operation.
The following table describes potential problems, their possible causes, checks you can perform or possible solutions for each. After referring to this table, if you cannot resolve the problem, contact your local Schneider Electric sales representative for assistance.

Potential problem	Possible cause	Possible solution
The maintenance (wrench) icon is illuminated on the power meter display.

When the maintenance (wrench) icon is illuminated, it indicates an event has occurred which may require attention.

Go to Maint > Diag . Event messages display to indicate the reason the icon is illuminated. Note these event messages and call the Technical Support or contact your local sales representative for assistance.

The display is blank after applying control power to the power meter.

The power meter may not be receiving the necessary power.

The display may have timed out. Verify that the power meter line and terminals are receiving the necessary power. Verify that the heartbeat LED is blinking. Press a button to see if the display timed out.

The data being displayed is inaccurate or not what you expect.

Incorrect setup values.

Incorrect voltage inputs.

Power meter is wired improperly

Check that the correct values have been entered for power meter setup parameters (CT and VT ratings, Nominal Frequency, and so on).

Check power meter voltage input terminals (1, 2, 3, 4) to verify that adequate voltage is present.

Check that all CTs and VTs are connected correctly (proper polarity is observed) and that they are energized. Check shorting terminals. See the recommended torque in the Wiring section of the installation manual.

Cannot communicate with power meter from a remote personal computer.

Power meter address is incorrect.

Power meter baud rate is incorrect.

Communications lines are improperly connected.

Communications lines are improperly terminated.

Incorrect route statement to power meter.

Check to see that the power meter is correctly addressed.

Verify that the baud rate of the power meter matches the baud rate of all other devices on its communications link.

Verify the power meter communications connections.

Check to see that a multi-point communications terminator is properly installed.

Check the route statement. Contact Global Technical Support for assistance.

Energy/Alarm LED not working.

May have been disabled by user.

Confirm that the energy / alarm LED is configured correctly.

```json
{
    "Maintenance": {
        "Troubleshooting checks": {
            "description": "There are some checks you can perform to try to identify potential issues with the meter’s operation.",
            "potential_problems": [
                {
                    "problem": "The maintenance (wrench) icon is illuminated on the power meter display.",
                    "possible_cause": "When the maintenance (wrench) icon is illuminated, it indicates an event has occurred which may require attention.",
                    "possible_solution": "Go to Maint > Diag . Event messages display to indicate the reason the icon is illuminated. Note these event messages and call the Technical Support or contact your local sales representative for assistance."
                },
                {
                    "problem": "The display is blank after applying control power to the power meter.",
                    "possible_cause": "The power meter may not be receiving the necessary power.",
                    "possible_solution": "The display may have timed out. Verify that the power meter line and terminals are receiving the necessary power. Verify that the heartbeat LED is blinking. Press a button to see if the display timed out."
                },
                {
                    "problem": "The data being displayed is inaccurate or not what you expect.",
                    "possible_cause": "Incorrect setup values. Incorrect voltage inputs. Power meter is wired improperly",
                    "possible_solution": "Check that the correct values have been entered for power meter setup parameters (CT and VT ratings, Nominal Frequency, and so on). Check power meter voltage input terminals (1, 2, 3, 4) to verify that adequate voltage is present. Check that all CTs and VTs are connected correctly (proper polarity is observed) and that they are energized. Check shorting terminals. See the recommended torque in the Wiring section of the installation manual."
                },
                {
                    "problem": "Cannot communicate with power meter from a remote personal computer.",
                    "possible_cause": "Power meter address is incorrect. Power meter baud rate is incorrect. Communications lines are improperly connected. Communications lines are improperly terminated. Incorrect route statement to power meter.",
                    "possible_solution": "Check to see that the power meter is correctly addressed. Verify that the baud rate of the power meter matches the baud rate of all other devices on its communications link. Verify the power meter communications connections. Check to see that a multi-point communications terminator is properly installed. Check the route statement. Contact Global Technical Support for assistance."
                },
                {
                    "problem": "Energy/Alarm LED not working.",
                    "possible_cause": "May have been disabled by user.",
                    "possible_solution": "Confirm that the energy / alarm LED is configured correctly."
                }
            ]
        }
    }
}
```

### Technical assistance