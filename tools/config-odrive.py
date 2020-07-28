#!/usr/bin/env python3

from fibre.protocol import ChannelBrokenException
from odrive import find_any
from odrive.utils import dump_errors
import sys
import time


def usage():
    print(f"usage: {sys.argv[0]} <left|right|single>")


def configure_axis(axis, can_id):
    print(f"Calibrating axis ID {can_id}...")

    motor = axis.motor
    encoder = axis.encoder
    controller = axis.controller

    axis.error = 0
    motor.error = 0
    encoder.error = 0
    controller.error = 0

    axis.config.can_node_id = can_id
    axis.config.can_heartbeat_rate_ms = 1

    motor.config.pole_pairs = 16
    motor.config.calibration_current = 2
    axis.requested_state = 4
    while axis.current_state != 1 and axis.error == 0:
        print("Waiting for motor calibration to complete...")
        time.sleep(1)
    if axis.error != 0:
        return False

    motor.config.pre_calibrated = 1
    motor.config.calibration_current = 10

    encoder.config.use_index = 1
    encoder.config.cpr = 16384 # CPR for US Digital Encoders
    axis.requested_state = 6
    while axis.current_state != 1 and axis.error == 0:
        time.sleep(0.5)
    if axis.error != 0:
        return False
    axis.requested_state = 7
    while axis.current_state != 1 and axis.error == 0:
        time.sleep(0.5)
    if axis.error != 0:
        return False
    encoder.config.pre_calibrated = 1

    controller.config.control_mode = 1

    controller.config.enable_current_mode_vel_limit = 0 # disables the velocity limit in current mode
    controller.config.enable_overspeed_error = 0 # disables overspeed errors

    motor.config.requested_current_range = 90 #Changes the current range 
    motor.config.current_lim = 90 # setting current limit 
    
    return True


def run(axis0, axis1=None):
    print("Connect a single ODrive to USB and ensure that motors are free to spin.")
    print("Press enter to continue...")
    input()

    print("Searching for an ODrive...")
    odrv0 = find_any()
    print(f"Configuring ODrive {hex(odrv0.serial_number)}...")
    if not configure_axis(odrv0.axis0, axis0):
        dump_errors(odrv0)
        sys.exit(3)
    if axis1 is not None:
        if not configure_axis(odrv0.axis1, axis1):
            dump_errors(odrv0)
            sys.exit(3)
    else:
        odrv0.axis1.config.can_node_id = axis0 + 1

    odrv0.can.can_protocol = 1
    odrv0.can.set_baud_rate(1000000)
    odrv0.save_configuration()

    try:
        odrv0.reboot()
    except ChannelBrokenException:
        print("Current limit set to 90A with no velocity limits. Good Luck, and God speed.")
        print("Configuration completed.")


def main():
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    side = sys.argv[1].strip().lower()
    if side not in ["left", "right", "single"]:
        usage()
        sys.exit(2)

    try:
        if side == "left":
            run(2, 1)
        elif side == "right":
            run(3, 4)
        elif side == "single":
            run(1)
    except KeyboardInterrupt:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()

