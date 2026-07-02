"""
main.py - Main entry point for the virtual greenhouse simulation.

This script initializes and runs the complete greenhouse control system:
1. Creates sensor simulation with 24-hour diurnal cycles
2. Initializes the first-order controller with thresholds
3. Logs all data to system_log.json
4. Runs the simulation loop until interrupted
"""

import time
import signal
import sys
from datetime import datetime

from sensors import GreenhouseSensors
from controller import GreenhouseController
from logger import GreenhouseLogger


# Configuration constants
TEMP_THRESHOLD = 18.0          # Turn on heater below this temperature
MOISTURE_THRESHOLD = 40.0      # Turn on pump below this moisture
CHECK_INTERVAL = 3.0           # Seconds between control cycles
LOG_FILE = "system_log.json"


class GreenhouseSimulation:
    """
    Manages the greenhouse simulation lifecycle.

    Handles initialization, running, graceful shutdown, and reporting.
    """

    def __init__(self):
        """Initialize all greenhouse components."""
        print("=" * 60)
        print("VIRTUAL GREENHOUSE SIMULATION")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Initialize components
        self.sensors = GreenhouseSensors()
        self.controller = GreenhouseController(
            temp_threshold=TEMP_THRESHOLD,
            moisture_threshold=MOISTURE_THRESHOLD,
            check_interval=CHECK_INTERVAL,
            sensors=self.sensors
        )
        self.logger = GreenhouseLogger(LOG_FILE)

        # State
        self.running = False
        self.cycle_count = 0

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle interrupt signals for graceful shutdown."""
        print("\n\nShutdown signal received...")
        self.running = False

    def _print_status(self, reading, state):
        """Print current system status to console."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"Temp: {reading.temperature:.1f}°C | "
              f"Moisture: {reading.moisture:.1f}% | "
              f"Heater: {'ON' if state.heater_on else 'OFF'} | "
              f"Pump: {'ON' if state.water_pump_on else 'OFF'}")

    def run(self):
        """
        Run the main simulation loop.

        Continuously reads sensors, applies control logic, and logs results
        until interrupted by the user.
        """
        self.running = True
        print("System initialized. Press Ctrl+C to stop.\n")
        print("-" * 60)

        try:
            while self.running:
                # Run one control cycle
                reading, state = self.controller.run_cycle()

                # Log the data
                self.logger.log(reading, state)

                # Print status
                self._print_status(reading, state)

                # Increment cycle counter
                self.cycle_count += 1

                # Wait for next cycle
                time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print(f"\nError during simulation: {e}")
            raise

        finally:
            self._shutdown()

    def _shutdown(self):
        """Perform clean shutdown procedures."""
        print("\n" + "-" * 60)
        print("Shutting down...")

        # Save log
        print(f"Saving log to {LOG_FILE}...")

        # Print final statistics
        stats = self.logger.get_log_stats()
        print(f"\nFinal Statistics:")
        print(f"  Total cycles: {self.cycle_count}")
        print(f"  Total entries logged: {stats['total_entries']}")
        print(f"  Heater activations: {stats['heights']}")
        print(f"  Pump activations: {stats['pump_activations']}")
        print(f"  Temperature range: {stats['min_temperature']:.1f}°C - {stats['max_temperature']:.1f}°C")
        print(f"  Moisture range: {stats['min_moisture']:.1f}% - {stats['max_moisture']:.1f}%")

        # Controller stats
        controller_stats = self.controller.get_status()["stats"]
        print(f"\nController Stats:")
        print(f"  Heater cycles: {controller_stats['heater_cycles']}")
        print(f"  Pump cycles: {controller_stats['pump_cycles']}")
        print(f"  Total actions: {controller_stats['total_actions']}")

        print(f"\nSimulation ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)


def main():
    """Main entry point for the greenhouse simulation."""
    simulation = GreenhouseSimulation()
    simulation.run()


if __name__ == "__main__":
    main()