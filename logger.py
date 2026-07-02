"""
logger.py - System logging for the virtual greenhouse control system.

This module handles logging all sensor data and controller actions to a JSON file,
creating a complete record of the greenhouse simulation for analysis and debugging.
"""

import json
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from pathlib import Path

from sensors import SensorReading
from controller import ControllerState


@dataclass
class LogEntry:
    """
    Represents a single log entry for the greenhouse system.

    Each entry contains both sensor data and controller state at a specific moment,
    allowing complete reconstruction of system behavior over time.
    """

    timestamp: float  # Unix epoch time
    sensor_reading: Dict[str, Any]  # Serialized SensorReading data
    controller_state: Dict[str, Any]  # Serialized ControllerState data
    action_taken: str  # Description of control action (if any)
    temperature: float  # Celsius
    moisture: float     # Percentage
    heater_on: bool     # Current heater status
    pump_on: bool       # Current water pump status


class GreenhouseLogger:
    """
    Handles logging of greenhouse sensor data and controller actions to JSON.

    This logger records every cycle of the greenhouse control system, creating
    a permanent record for analysis, monitoring, and debugging.
    """

    def __init__(self, log_file_path: str = "system_log.json"):
        """
        Initialize the logger.

        Args:
            log_file_path: Path to the JSON log file
        """
        self.log_file = Path(log_file_path)
        self.log_file.parent.mkdir(exist_ok=True)

        # Load existing log if file exists
        self.log_entries: List[LogEntry] = []
        self._load_existing_log()

    def _load_existing_log(self):
        """Load existing log entries from the JSON file."""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    # Convert back to LogEntry objects
                    self.log_entries = [
                        LogEntry(
                            timestamp=entry["timestamp"],
                            sensor_reading=entry["sensor_reading"],
                            controller_state=entry["controller_state"],
                            action_taken=entry["action_taken"],
                            temperature=entry["temperature"],
                            moisture=entry["moisture"],
                            heater_on=entry["heater_on"],
                            pump_on=entry["pump_on"]
                        )
                        for entry in data
                    ]
            except json.JSONDecodeError:
                self.log_entries = []

    def _save_to_file(self):
        """Save all log entries to the JSON file."""
        with open(self.log_file, 'w') as f:
            json.dump(
                [asdict(entry) for entry in self.log_entries],
                f,
                indent=2
            )

    def log(self, sensor_reading: SensorReading, controller_state: ControllerState):
        """
        Log the current sensor reading and controller state.

        Args:
            sensor_reading: The latest sensor reading
            controller_state: The current controller state
        """
        # Determine what action was taken
        action_taken = ""
        if controller_state.heater_on != controller_state.heater_on:  # Change detection
            action_taken = "HEATER_TURNED_ON" if controller_state.heater_on else "HEATER_TURNED_OFF"
        if controller_state.water_pump_on != controller_state.water_pump_on:  # Change detection
            if action_taken:
                action_taken += " & WATER_PUMP_TURNED_" + ("ON" if controller_state.water_pump_on else "OFF")
            else:
                action_taken = "WATER_PUMP_TURNED_" + ("ON" if controller_state.water_pump_on else "OFF")

        # Create log entry
        log_entry = LogEntry(
            timestamp=time.time(),
            sensor_reading=asdict(sensor_reading),
            controller_state=asdict(controller_state),
            action_taken=action_taken,
            temperature=sensor_reading.temperature,
            moisture=sensor_reading.moisture,
            heater_on=controller_state.heater_on,
            pump_on=controller_state.water_pump_on
        )

        self.log_entries.append(log_entry)

    def get_log_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the logged data.

        Returns:
            Dictionary containing log statistics
        """
        if not self.log_entries:
            return {
                "total_entries": 0,
                "heights": 0,
                "pump_activations": 0,
                "min_temperature": None,
                "max_temperature": None,
                "min_moisture": None,
                "max_moisture": None
            }

        temperatures = [entry.temperature for entry in self.log_entries]
        moistures = [entry.moisture for entry in self.log_entries]

        return {
            "total_entries": len(self.log_entries),
            "heights": len([e for e in self.log_entries if e.heater_on]),
            "pump_activations": len([e for e in self.log_entries if e.pump_on]),
            "min_temperature": min(temperatures),
            "max_temperature": max(temperatures),
            "min_moisture": min(moistures),
            "max_moisture": max(moistures)
        }

    def export_csv(self, csv_path: str = "system_log.csv"):
        """
        Export log data as CSV for spreadsheet analysis.

        Args:
            csv_path: Path for the CSV file
        """
        try:
            import csv

            with open(csv_path, 'w', newline='') as f:
                fieldnames = [
                    'timestamp', 'temperature', 'moisture', 'heater_on',
                    'pump_on', 'action_taken'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for entry in self.log_entries:
                    writer.writerow({
                        'timestamp': entry.timestamp,
                        'temperature': entry.temperature,
                        'moisture': entry.moisture,
                        'heater_on': entry.heater_on,
                        'pump_on': entry.pump_on,
                        'action_taken': entry.action_taken
                    })
        except ImportError:
            print("CSV export not available (csv module not available)")

    def get_latest_entry(self) -> Optional[LogEntry]:
        """
        Get the most recent log entry.

        Returns:
            Latest LogEntry or None if no entries exist
        """
        return self.log_entries[-1] if self.log_entries else None

    def get_entries_by_time_range(
        self,
        start_time: float,
        end_time: float
    ) -> List[LogEntry]:
        """
        Get log entries within a specific time range.

        Args:
            start_time: Unix epoch timestamp for start of range
            end_time: Unix epoch timestamp for end of range

        Returns:
            List of LogEntry objects within the time range
        """
        return [
            entry for entry in self.log_entries
            if start_time <= entry.timestamp <= end_time
        ]