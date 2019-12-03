import odrive
from odrive.enums import *

import time
import math

def readYesNo(promptStr):
    while True:
        try:
            val = input(promptStr+" (Y/N):\t").lower()
            assert(val == 'y' or val == 'n')
            return val == 'y'
        except:
            print("Invalid reponse\n")

def readFloat(promptStr, min, max, unit):
    while True:
        try:
            val = float(input(promptStr + " ["+str(min)+', '+str(max)+'] ['+unit+']:\t'))
            assert(val >= 0 and val <= max)
            return val
        except AssertionError:
            print("Value out of range\n")
        except ValueError:
            print("Value not convertible to float\n")

def readSelection(promptStr, min, max):
    while True:
        try:
            val = int(input(promptStr))
            assert(val >= min and val <= max)
            return val
        except AssertionError:
                print("Value out of range\n")
        except ValueError:
                print("Value not convertible to int\n")

def readInt(promptStr, min, max, unit):
    while True:
        try:
            val = int(input(promptStr + " ["+str(min)+', '+str(max)+'] ['+unit+']:\t'))
            assert(val >= min and val <= max)
            return val
        except AssertionError:
                print("Value out of range")
        except ValueError:
                print("Value not convertible to int\n")


# Start of wizard
print("Welcome to the ODrive Startup Wizard!")
print("Website: https://odriverobotics.com/")
print("Documentation: https://docs.odriverobotics.com/")
print("Forums: https://discourse.odriverobotics.com/")
print("Discord: https://discord.gg/k3ZZ3mS")
print("Github: https://github.com/madcowswe/ODrive/")

print()
print('Finding an ODrive...')
odrv = odrive.find_any()
print('ODrive '+str(hex(odrv.serial_number))+' found')

print()
axisNum = readSelection("Which Axis do you want to configure? ", 0, 1)
if(axisNum == 0):
    axis = odrv.axis0
else:
    axis = odrv.axis1

print()
print("Setting parameters for axis" + str(axisNum))
axis.requested_state = AXIS_STATE_IDLE
axis.error = 0
axis.motor.error = 0
axis.encoder.error = 0
axis.controller.error = 0
axis.sensorless_estimator.error = 0

# val = readSelection("Select motor type:\n0 - High Current\n1 - Gimbal Motor\n: ", 0, 1)
# if(val == 1):
#     print("Gimbal motors are not yet supported by this wizard, sorry!")
#     quit()
# print()

# Motor parameters
if readYesNo("Calibrate motor now?"):
    if odrv.vbus_voltage < 8:
        print("Please turn on your power supply")
    time.sleep(0.1)
    while odrv.vbus_voltage < 8:
        time.sleep(0.1)

    print("Bus Voltage: " + str(odrv.vbus_voltage))

    print()
    print("Calibrating motor... ")
    axis.requested_state = AXIS_STATE_MOTOR_CALIBRATION
    time.sleep(0.1)
    while axis.current_state != AXIS_STATE_IDLE:
        time.sleep(0.1)
    
    if axis.motor.error > 0:
        print(MotorStatus(int(axis.motor.error)).name)
        print("Oops, you have a motor error!  Check your wiring, make sure you're using the right axis, and if all else fails, see https://docs.odriverobotics.com/troubleshooting#common-motor-errors")
        quit()
    else:
        print("Phase Resistance: " + str(axis.motor.config.phase_resistance))
        print("Phase Inductance: " + str(axis.motor.config.phase_inductance))

axis.motor.config.pole_pairs = readInt("Motor Pole Pairs", 0, 2**31 - 1, '')
val = readFloat("Max safe motor current", 0, math.inf, 'A')
axis.motor.config.current_lim = val
axis.motor.config.requested_current_range = val
axis.controller.config.vel_limit = readFloat("Max safe motor speed", 0, math.inf, 'counts/s')

print()
axis.encoder.config.cpr = readInt("Encoder counts per revolution", 0, 2**31 - 1, 'counts')
axis.encoder.config.use_index = readYesNo("Use Encoder Index Pin?")

print()
if readYesNo("Enable step/direction interface?"):
    axis.config.enable_step_dir = True
    axis.config.counts_per_step = readInt("Counts per step", 0, math.inf, 'counts')
    axis.config.step_gpio_pin = readSelection("Step GPIO Pin:\t", 0, 8)
    axis.config.dir_gpio_pin = readSelection("Dir GPIO Pin:\t", 0, 8)
else:
    axis.config.enable_step_dir = False

if readYesNo("Enter closed loop control at startup?"):
    axis.config.startup_motor_calibration = True
    axis.config.startup_encoder_offset_calibration = True
    axis.config.startup_closed_loop_control = True
    axis.config.startup_encoder_index_search = True
else:
    axis.config.startup_motor_calibration = False
    axis.config.startup_encoder_offset_calibration = False
    axis.config.startup_closed_loop_control = False
    axis.config.startup_encoder_index_search = False

if readYesNo("Use brake resistor?"):
    odrv.config.brake_resistance = readFloat("Brake resistance", 0, math.inf, 'ohm')
else:
    odrv.config.brake_resistance = 0.0

print()
if readYesNo("Setup Trapezoidal Trajectory Planning?"):
    axis.trap_traj.config.vel_limit = readFloat("Desired speed during move", 0, math.inf, "counts/s")
    axis.trap_traj.config.accel_limit = readFloat("Desired acceleration at beginning of move", 0, math.inf, 'counts/s^2')
    axis.trap_traj.config.decel_limit = readFloat("Desired deceleration at end of move", 0, math.inf, 'counts/s^2')
    axis.trap_traj.config.A_per_css = readFloat("Amps per unit of acceleration", 0, math.inf, 'A/(count/s^2)')
else:
    axis.trap_traj.config.vel_limit = 0
    axis.trap_traj.config.accel_limit = 0
    axis.trap_traj.config.decel_limit = 0
    axis.trap_traj.config.A_per_css = 0

print()
if readYesNo("ODrive will reboot.  Save Configuration?"):
    odrv.save_configuration()
odrv.reboot()
print()
quit()