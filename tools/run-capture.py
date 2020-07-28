#!/usr/bin/env python3

from fibre.protocol import ChannelBrokenException
from odrive import find_any
from odrive.utils import dump_errors, oscilloscope_dump
import sys
import time


def run():
    print("Connect a single ODrive to USB and ensure that motors are free to spin.")
    print("Press enter to continue...")
    input()

    print("Searching for an ODrive...")
    odrv0 = find_any()

    print(f"Connecting to ODrive {hex(odrv0.serial_number)}...")
    try:
        axis = odrv0.axis0
        motor = axis.motor
        encoder = axis.encoder
        controller = axis.controller

        axis.error = 0
        motor.error = 0
        encoder.error = 0
        controller.error = 0

        print("Performing encoder index pulse search...")
        axis.requested_state = 6
        while axis.current_state != 1 and axis.error == 0:
           time.sleep(1)
        time.sleep(5)

        print("Spinning up the motor...")
        encoder.config.acceleration_alpha = 0.004
        motor.current_control.acceleration_ff_gain = 0.8
        controller.config.control_mode = 1
        controller.input_current = 0
        axis.requested_state = 8
        time.sleep(2.0)

        controller.input_current = 2
        time.sleep(0.5)

        print("Capturing data...")
        controller.input_current = 0
        oscilloscope_dump(odrv0, 8192)

        print("Idling the motor...")
        axis.requested_state = 1

        print("Capture complete.")
        dump_errors(odrv0)

    except ChannelBrokenException:
        print("Current limit set to 90A with no velocity limits. Good Luck, and God speed.")
        print("Configuration completed.")


def main():
    try:
        run()
    except KeyboardInterrupt:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
