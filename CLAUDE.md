# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
A simulated autonomous IoT greenhouse control system in Python. The system models real-world greenhouse conditions with diurnal temperature and moisture cycles, and implements automated control logic for heating and irrigation.

## Project Structure
```
virtual-greenhouse/
├── main.py          # Entry point - runs the simulation loop
├── sensors.py       # Sensor simulation with 24-hour diurnal cycles
├── controller.py    # First-order control logic for heater/water pump
├── logger.py        # JSON logging of all sensor data and actions
├── system_log.json  # Generated log file (created at runtime)
└── CLAUDE.md        # This file
```

## Development Commands
```bash
# Run the simulation
python main.py

# Run a single test cycle (for quick verification)
python -c "from sensors import GreenhouseSensors; from controller import GreenhouseController; s = GreenhouseSensors(); c = GreenhouseController(sensors=s); r, state = c.run_cycle(); print(f'Temp: {r.temperature}°C, Moisture: {r.moisture}%')"
```

## Architecture

### sensors.py
- `SensorReading`: Dataclass holding timestamp, temperature, and moisture
- `GreenhouseSensors`: Simulates environmental sensors
  - Temperature: Sinusoidal 24-hour cycle (min 15°C at 6AM, max 30°C at 3PM)
  - Moisture: Decreases ~2%/hour due to evaporation, increases when pump activates
  - Both include realistic Gaussian noise

### controller.py
- `ControllerState`: Dataclass tracking current heater/pump status
- `GreenhouseController`: First-order control system
  - Heater turns ON when temp < 18°C, OFF when temp > 19°C (hysteresis)
  - Water pump turns ON when moisture < 40%, OFF when moisture > 43%
  - Tracks statistics (cycles, total actions)

### logger.py
- `LogEntry`: Dataclass for individual log entries
- `GreenhouseLogger`: JSON file logging
  - Logs every sensor reading and controller state
  - Supports CSV export for analysis
  - Tracks activation counts and min/max values

### main.py
- `GreenhouseSimulation`: Orchestrates the entire system
  - Initializes all components
  - Runs the main control loop (3-second intervals)
  - Handles graceful shutdown (Ctrl+C)
  - Prints real-time status and final statistics

## Control Logic
The controller uses hysteresis-based control to prevent rapid switching:
- **Heater**: Activates below 18°C, deactivates above 19°C
- **Water Pump**: Activates below 40% moisture, deactivates above 43%

This ensures stable operation and prevents oscillation around threshold values.