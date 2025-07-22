# FS25 Engine and Transmission Config Tool

A standalone Python desktop application for generating engine and transmission configurations for Farming Simulator 25. Built with Tkinter/CustomTkinter and designed for export to portable .exe using PyInstaller.

## Features

- **Modern Dark Mode GUI**: Beautiful dark theme with CustomTkinter (with Tkinter fallback)
- **Engine Configuration**: Complete engine setup with auto-generated torque curves
- **Transmission Configuration**: Support for Manual, Automatic, CVT, and PowerShift transmissions
- **Preset System**: Built-in engine and transmission presets with save/load functionality
- **FS25 XML Generation**: Generate properly formatted XML matching FS25 game files
- **XML Syntax Highlighting**: Color-coded XML preview with line numbers
- **Compact Interface**: Streamlined button layout for efficient workflow
- **Save/Load System**: Save and load custom configurations as JSON files
- **Copy to Clipboard**: Easy copying of generated XML
- **Tooltips**: Helpful tooltips for all input fields and buttons
- **Portable**: Designed to run as a standalone executable

## Engine Presets

- **7.3 Powerstroke**: 275 HP, 600 minRPM, turbocharged
- **6.0 Powerstroke**: 325 HP, 650 minRPM, turbocharged
- **6.7 Powerstroke**: 475 HP, 650 minRPM, turbocharged
- **5.9 Cummins**: 325 HP, 700 minRPM, turbocharged
- **6.7 Cummins**: 400 HP, 700 minRPM, turbocharged

## Transmission Presets

- **10-speed Allison Automatic**: Automatic transmission with 10 forward gears
- **13-speed Eaton Fuller**: Manual transmission with 13 forward gears
- **4-speed with Granny Gear**: Manual transmission with low gearing enabled
- **18-speed Eaton Fuller**: Manual transmission with 18 forward gears

## Installation

### Option 1: Portable EXE (Recommended for Windows Users)

1. Download the latest `FS25_Config_Tool.exe` from releases
2. Run the executable directly - no installation required
3. The application is completely portable and can be run from any location

### Option 2: Python Source Code

#### Prerequisites

- Python 3.7 or higher
- CustomTkinter (optional, falls back to standard Tkinter)

#### Running the Application

1. Clone or download this repository
2. Install dependencies (optional):
   ```bash
   pip install customtkinter
   ```
3. Run the application:
   ```bash
   python fs25_config_tool.py
   ```

## Usage

### Engine Configuration

1. **Engine Settings Tab**: Configure engine parameters
   - Engine Name: Name of the engine
   - Engine Cost: Cost in dollars
   - Horsepower: Rated horsepower (used for torque calculation)
   - Minimum/Maximum RPM: Engine RPM range (default max: 3500)
   - Fuel Usage Scale: Fuel consumption multiplier (default: 1.0)
   - Turbocharged: Check for turbocharged engines

2. **Presets**: Use the dropdown to load predefined engine configurations

### Transmission Configuration

1. **Transmission Settings Tab**: Configure transmission parameters
   - Transmission Name: Name of the transmission
   - Transmission Cost: Cost in dollars
   - Transmission Type: Manual, Automatic, CVT, or PowerShift
   - Top Speed: Maximum speed in km/h
   - Forward/Reverse Gears: Number of gears
   - Low Gearing: Enable for enhanced torque output in low gears
   - Low Gear Boost %: Percentage boost for first 25% of forward gears

2. **Presets**: Use the dropdown to load predefined transmission configurations

### Output Generation

1. **Output Tab**: Generate and manage XML output
   - **Engine Actions**: Generate, Copy, Save engine XML
   - **Transmission Actions**: Generate, Copy, Save transmission XML
   - **Presets**: Save, Load, Add custom configurations
   - **Combined Actions**: Generate and save complete FS25 XML

2. **XML Preview**: View formatted XML with syntax highlighting and line numbers

## Torque Curve Generation

The application automatically generates torque curves based on:
- **Formula**: Torque = (HP × 9549) / Peak RPM
- **Peak RPM**: Approximately 65% of maximum RPM
- **Turbocharged Engines**: Generate flatter, higher mid-range curves
- **Naturally Aspirated**: Traditional torque curves with steeper decline
- **10 RPM Points**: Evenly spaced from minimum to maximum RPM

## Gear Ratio Calculation

Gear ratios are calculated based on:
- **Transmission Type**: Different ratio patterns for each type
- **Low Gearing**: Enhanced ratios for first 25% of forward gears
- **Speed Requirements**: Optimized for specified top speed
- **Realistic Ratios**: Based on actual transmission characteristics

## FS25 XML Format

The application generates XML that matches the exact format used by Farming Simulator 25:

```xml
<motorConfigurations>
    <motorConfiguration name="Engine Name" hp="400" price="15000">
        <motor torqueScale="0.8" minRpm="700" maxRpm="3500" maxForwardSpeed="120" maxBackwardSpeed="22" brakeForce="2" lowBrakeForceScale="0.1" dampingRateScale="0.2">
            <torque rpm="700" torque="0.9"/>
            <torque rpm="2275" torque="1.0"/>
            <!-- ... more torque points ... -->
        </motor>
        <transmission autoGearChangeTime="1" gearChangeTime="0.3" name="Transmission Name" axleRatio="25" startGearThreshold="0.3">
            <directionChange useGear="true"/>
            <backwardGear gearRatio="4.066" name="R"/>
            <forwardGear gearRatio="4.784"/>
            <!-- ... more gear ratios ... -->
        </transmission>
    </motorConfiguration>
</motorConfigurations>
```

## Creating Portable EXE

### Using PyInstaller

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Create the portable executable:
```bash
pyinstaller --onefile --windowed --name "FS25 Engine and Transmission Config Tool" --add-data "LICENSE;." fs25_config_tool.py
```

3. The executable will be created in the `dist` folder

### Using the Build Script

1. Run the provided build script:
```bash
build_exe.bat
```

2. The portable release will be created in the "FS25 Engine and Transmission Config Tool Portable Release" folder

### PyInstaller Options

- `--onefile`: Create a single portable executable file
- `--windowed`: Run without console window
- `--name`: Specify the output filename
- `--add-data`: Include additional files (optional)
- `--icon`: Add custom icon (optional)

## Distribution

The portable release is located in the **"FS25 Engine and Transmission Config Tool Portable Release"** folder and contains:

- **FS25 Engine and Transmission Config Tool.exe** - The complete portable application
- **PORTABLE_README.txt** - Simple usage instructions

This folder can be distributed as-is - users simply need to run the EXE file.

## File Structure

```
FS25-Engine-and-Transmission-Config-Tool/
├── fs25_config_tool.py    # Main application file
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── LICENSE                # License file
├── build_exe.bat          # Windows build script
├── PORTABLE_README.txt    # Portable version instructions
└── FS25 Engine and Transmission Config Tool Portable Release/
    ├── FS25 Engine and Transmission Config Tool.exe  # Portable executable
    └── PORTABLE_README.txt                           # Usage instructions
```

## Code Architecture

The application is built with a modular architecture:

- **Tooltip**: Simple tooltip system for help text
- **TorqueCurveGenerator**: Handles automatic torque curve generation
- **GearRatioCalculator**: Calculates transmission gear ratios
- **XMLGenerator**: Generates FS25-compatible XML with syntax highlighting
- **PresetManager**: Manages engine and transmission presets
- **FS25ConfigTool**: Main application class with GUI (CustomTkinter/Tkinter)

## Requirements

- **Python**: 3.7+ (for source code)
- **Dependencies**: 
  - `customtkinter>=5.2.0` (optional, falls back to tkinter)
  - `pyinstaller` (for creating EXE)
- **GUI**: tkinter (included with Python) or CustomTkinter
- **File I/O**: json, os (standard library)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues or questions:
1. Check the tooltips in the application
2. Review the preset configurations
3. Ensure all input values are valid numbers
4. Check that file paths are accessible for saving
5. For EXE issues, try running as administrator

## Future Enhancements

- Additional engine and transmission presets
- More sophisticated torque curve algorithms
- Integration with FS25 modding tools
- Export to additional file formats
- Advanced gear ratio optimization
- Custom themes and styling options 