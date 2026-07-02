"""
sensors.py - Simulates real-time temperature and moisture data for a virtual greenhouse.

This module provides sensor simulation that mimics realistic diurnal cycles:
- Temperature follows a sinusoidal pattern over 24 hours (cooler at night, warmer during day)
- Moisture decreases over time (evaporation) and increases when water pump activates
- Both sensors include realistic noise to simulate real-world variability
"""

import time
import math
import random
from dataclasses import dataclass
from typing import Optional


@dataclass
class SensorReading:
    """Represents a single sensor reading with timestamp."""
    timestamp: float
    temperature: float  # Celsius
    moisture: float     # Percentage (0-100%)


class GreenhouseSensors:
    """
    Simulates greenhouse environmental sensors with realistic 24-hour cycles.

    Temperature Cycle:
    - Minimum at ~6 AM (dawn): ~15°C
    - Maximum at ~3 PM (mid-afternoon): ~30°C
    - Sinusoidal variation with added noise

    Moisture Cycle:
    - Starts at 70% (optimal)
    - Decreases ~2% per hour due to evaporation/transpiration
    - Increases when water pump activates
    - Includes random noise
    """

    def __init__(
        self,
        base_temp_min: float = 15.0,
        base_temp_max: float = 30.0,
        temp_noise_std: float = 0.5,
        moisture_evaporation_rate: float = 2.0,  # % per hour
        moisture_noise_std: float = 1.0,
        initial_moisture: float = 70.0,
        cycle_period_hours: float = 24.0
    ):
        """
        Initialize the sensor simulation.

        Args:
            base_temp_min: Minimum temperature at night (Celsius)
            base_temp_max: Maximum temperature during day (Celsius)
            temp_noise_std: Standard deviation of temperature noise
            moisture_evaporation_rate: Moisture loss per hour (%)
            moisture_noise_std: Standard deviation of moisture noise
            initial_moisture: Starting moisture level (%)
            cycle_period_hours: Period of the diurnal cycle in hours
        """
        self.base_temp_min = base_temp_min
        self.base_temp_max = base_temp_max
        self.temp_noise_std = temp_noise_std
        self.moisture_evaporation_rate = moisture_evaporation_rate
        self.moisture_noise_std = moisture_noise_std
        self.cycle_period_hours = cycle_period_hours

        # Internal state
        self._current_moisture = initial_moisture
        self._last_update_time = time.time()
        self._water_pump_active = False
        self._heater_active = False

    def _calculate_base_temperature(self, elapsed_hours: float) -> float:
        """
        Calculate base temperature following a sinusoidal 24-hour cycle.

        Peak at 15:00 (3 PM), trough at 06:00 (6 AM)
        Using cosine shifted so peak is at 15 hours (3 PM)
        """
        # Phase shift: cosine peaks at 0, we want peak at 15 hours
        # So we use cos(2π * (t - 15) / 24)
        phase = 2 * math.pi * (elapsed_hours - 15) / self.cycle_period_hours
        temp_range = (self.base_temp_max - self.base_temp_min) / 2
        temp_mid = (self.base_temp_max + self.base_temp_min) / 2
        return temp_mid + temp_range * math.cos(phase)

    def read(self, heater_active: bool = False, water_pump_active: bool = False) -> SensorReading:
        """
        Take a sensor reading at the current time.

        Args:
            heater_active: Whether the heater is currently on (affects temperature)
            water_pump_active: Whether the water pump is currently on (affects moisture)

        Returns:
            SensorReading with current temperature and moisture
        """
        current_time = time.time()
        elapsed_seconds = current_time - self._last_update_time
        elapsed_hours = elapsed_seconds / 3600.0

        # Update moisture based on evaporation and water pump
        if water_pump_active and not self._water_pump_active:
            # Pump just turned on - add water
            self._current_moisture = min(100.0, self._current_moisture + 15.0)
        elif not water_pump_active and self._water_pump_active:
            # Pump just turned off
            pass

        # Continuous evaporation
        self._current_moisture -= self.moisture_evaporation_rate * elapsed_hours
        self._current_moisture = max(0.0, self._current_moisture)

        # Add moisture noise
        moisture_noise = random.gauss(0, self.moisture_noise_std)
        moisture = self._current_moisture + moisture_noise
        moisture = max(0.0, min(100.0, moisture))

        # Calculate temperature with diurnal cycle
        # Total hours since epoch for consistent cycle
        total_hours = current_time / 3600.0
        base_temp = self._calculate_base_temperature(total_hours)

        # Heater effect: adds ~3°C when active
        heater_effect = 3.0 if heater_active else 0.0

        # Add temperature noise
        temp_noise = random.gauss(0, self.temp_noise_std)
        temperature = base_temp + heater_effect + temp_noise

        # Update state
        self._last_update_time = current_time
        self._water_pump_active = water_pump_active
        self._heater_active = heater_active

        return SensorReading(
            timestamp=current_time,
            temperature=round(temperature, 2),
            moisture=round(moisture, 2)
        )

    def get_current_moisture(self) -> float:
        """Get current moisture level without taking a full reading."""
        return self._current_moisture

    def reset_moisture(self, value: float = 70.0):
        """Reset moisture to a specific value (useful for testing)."""
        self._current_moisture = value