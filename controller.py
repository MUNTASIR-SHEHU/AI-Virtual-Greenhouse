"""
controller.py - Automation loop for the virtual greenhouse control system.

This module implements a first-order response controller that:
- Reads sensor data at configurable intervals
- Activates heater when temperature drops below threshold
- Activates water pump when moisture drops below threshold
- Uses hysteresis to prevent rapid cycling
"""

import time
from dataclasses import dataclass
from typing import Optional, Tuple

from sensors import GreenhouseSensors, SensorReading


@dataclass
class ControllerState:
    """Represents the current state of the greenhouse controller."""
    heater_on: bool
    water_pump_on: bool
    last_temp_reading: float
    last_moisture_reading: float
    last_reading_time: float


class GreenhouseController:
    """
    First-order controller for greenhouse automation.

    Control Logic:
    - Heater: Turns ON when temp < threshold, OFF when temp > threshold + hysteresis
    - Water Pump: Turns ON when moisture < threshold, OFF when moisture > threshold + hysteresis

    Hysteresis prevents rapid switching (oscillations) around threshold values.
    """

    def __init__(
        self,
        temp_threshold: float = 18.0,
        moisture_threshold: float = 40.0,
        temp_hysteresis: float = 1.0,
        moisture_hysteresis: float = 3.0,
        check_interval: float = 3.0,
        sensors: Optional[GreenhouseSensors] = None
    ):
        """
        Initialize the greenhouse controller.

        Args:
            temp_threshold: Temperature threshold to trigger heater (Celsius)
            moisture_threshold: Moisture threshold to trigger water pump (%)
            temp_hysteresis: Temperature buffer to prevent rapid cycling (Celsius)
            moisture_hysteresis: Moisture buffer to prevent rapid cycling (%)
            check_interval: Seconds between sensor readings and control actions
            sensors: Sensor instance (creates new one if None)
        """
        self.temp_threshold = temp_threshold
        self.moisture_threshold = moisture_threshold
        self.temp_hysteresis = temp_hysteresis
        self.moisture_hysteresis = moisture_hysteresis
        self.check_interval = check_interval
        self.sensors = sensors or GreenhouseSensors()

        # Controller state
        self.state = ControllerState(
            heater_on=False,
            water_pump_on=False,
            last_temp_reading=20.0,
            last_moisture_reading=50.0,
            last_reading_time=time.time()
        )

        # Statistics
        self.total_actions = 0
        self.heater_cycles = 0
        self.pump_cycles = 0

    def _should_heater_turn_on(self, temp: float) -> bool:
        """
        Determine if heater should turn on.

        Heater turns on when temperature is below threshold.
        It stays on until temperature rises above (threshold + hysteresis).
        """
        if self.state.heater_on:
            # Already on - stay on until temp rises above threshold + hysteresis
            return temp < self.temp_threshold + self.temp_hysteresis
        else:
            # Currently off - turn on when temp drops below threshold
            return temp < self.temp_threshold

    def _should_pump_turn_on(self, moisture: float) -> bool:
        """
        Determine if water pump should turn on.

        Pump turns on when moisture is below threshold.
        It stays on until moisture rises above (threshold + hysteresis).
        """
        if self.state.water_pump_on:
            # Already on - stay on until moisture rises above threshold + hysteresis
            return moisture < self.moisture_threshold + self.moisture_hysteresis
        else:
            # Currently off - turn on when moisture drops below threshold
            return moisture < self.moisture_threshold

    def read_and_control(self) -> Tuple[SensorReading, ControllerState]:
        """
        Read sensors and apply control logic.

        Returns:
            Tuple of (sensor_reading, controller_state)
        """
        # Read current sensor values
        reading = self.sensors.read(
            heater_active=self.state.heater_on,
            water_pump_active=self.state.water_pump_on
        )

        # Determine new control states
        new_heater_state = self._should_heater_turn_on(reading.temperature)
        new_pump_state = self._should_pump_turn_on(reading.moisture)

        # Track state changes for statistics
        if new_heater_state and not self.state.heater_on:
            self.heater_cycles += 1
            self.total_actions += 1
        if new_pump_state and not self.state.water_pump_on:
            self.pump_cycles += 1
            self.total_actions += 1

        # Update state
        self.state = ControllerState(
            heater_on=new_heater_state,
            water_pump_on=new_pump_state,
            last_temp_reading=reading.temperature,
            last_moisture_reading=reading.moisture,
            last_reading_time=time.time()
        )

        return reading, self.state

    def run_cycle(self) -> Tuple[SensorReading, ControllerState]:
        """
        Run a single control cycle and return the results.

        This is the main entry point for each control iteration.

        Returns:
            Tuple of (sensor_reading, controller_state)
        """
        return self.read_and_control()

    def get_status(self) -> dict:
        """Get current controller status as a dictionary."""
        return {
            "heater_on": self.state.heater_on,
            "water_pump_on": self.state.water_pump_on,
            "temperature": self.state.last_temp_reading,
            "moisture": self.state.last_moisture_reading,
            "stats": {
                "total_actions": self.total_actions,
                "heater_cycles": self.heater_cycles,
                "pump_cycles": self.pump_cycles
            }
        }

    def reset_stats(self):
        """Reset controller statistics."""
        self.total_actions = 0
        self.heater_cycles = 0
        self.pump_cycles = 0