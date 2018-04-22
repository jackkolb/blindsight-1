# Manages the Snapdragon board: GPIO input/output, processing, response

from gpiozero import LED
import RPi.GPIO as GPIO
import time


# ## Pin Numbers ## #

# Motor Controller Pins
motor_pin_1 = 6
motor_pin_2 = 13
motor_pin_3 = 19
motor_pin_4 = 26

# Ultrasonic Pins
sonic_trig_pin = 3
sonic_echo_pin = 4

# Vibrator Pins
vibrator_pins = {
    "1": 21,
    "2": 20,
    "3": 16,
    "4": 12,
    "5": 7,
    "6": 8,
    "7": 25,
    "8": 24,
    "9": 23,
    "10": 18
}


# ## Setup Pins ## #

# Setup Board
try:
    GPIO.setmode(GPIO.BOARD)
except:
    pass

# Setup Motor Pins
GPIO.setup(motor_pin_1, GPIO.OUT)
GPIO.setup(motor_pin_2, GPIO.OUT)
GPIO.setup(motor_pin_3, GPIO.OUT)
GPIO.setup(motor_pin_4, GPIO.OUT)


# Setup Ultrasonic Pins
GPIO.setup(sonic_trig_pin, GPIO.OUT)
GPIO.setup(sonic_echo_pin, GPIO.IN)


# Setup Vibrator Pins
GPIO.setup(vibrator_pins["1"], GPIO.OUT)
GPIO.setup(vibrator_pins["2"], GPIO.OUT)
GPIO.setup(vibrator_pins["3"], GPIO.OUT)
GPIO.setup(vibrator_pins["4"], GPIO.OUT)
GPIO.setup(vibrator_pins["5"], GPIO.OUT)
GPIO.setup(vibrator_pins["6"], GPIO.OUT)
GPIO.setup(vibrator_pins["7"], GPIO.OUT)
GPIO.setup(vibrator_pins["8"], GPIO.OUT)
GPIO.setup(vibrator_pins["9"], GPIO.OUT)
GPIO.setup(vibrator_pins["10"], GPIO.OUT)


def setStep(w1, w2, w3, w4):
    GPIO.output(motor_pin_1, w1)
    GPIO.output(motor_pin_2, w2)
    GPIO.output(motor_pin_3, w3)
    GPIO.output(motor_pin_4, w4)


# moves the stepper one step
def move_stepper(direction="none"):
    delay = .003
    if direction == "forward":
        setStep(1, 0, 0, 1)
        time.sleep(delay)
        setStep(1, 0, 0, 0)
        time.sleep(delay)
        setStep(1, 1, 0, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 0)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(0, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 0, 1, 1)
        time.sleep(delay)
        setStep(0, 0, 0, 1)
        time.sleep(delay)
#        setStep(1, 0, 0, 1)

    if direction == "backward":
        setStep(1, 0, 0, 1)
        time.sleep(delay)
        setStep(0, 0, 0, 1)
        time.sleep(delay)
        setStep(0, 0, 1, 1)
        time.sleep(delay)
        setStep(0, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 0)
        time.sleep(delay)
        setStep(1, 1, 0, 0)
        time.sleep(delay)
        setStep(1, 0, 0, 0)
        time.sleep(delay)
#        setStep(1, 0, 0, 1)

    return


# sends a sonar pulse and gets the distance reading
def get_sonar():
    # get input from sensor
    print("IN")
    GPIO.output(sonic_trig_pin, True)
    time.sleep(0.00001)
    GPIO.output(sonic_trig_pin, False)

    pulse_start = 0
    pulse_end = 0

    while GPIO.input(sonic_echo_pin) == 0:
        pulse_start = time.time()

    while GPIO.input(sonic_echo_pin) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * 17150
    distance = round(distance, 2)
    print("OUT")
    return distance


# turns on a vibrator pin to a given current
def set_vibrator_current(pin, current):
    # set gpio pin current
    print("current: " + str(current))
    if current < 0:
        GPIO.output(pin, 0)
    else:
        GPIO.output(pin, current / 8)
        

    return


# the primary control loop
def primary_control():
    # 1. move stepper
    # 2. get sonar
    # 3. update vibrations
    GPIO.output(sonic_trig_pin, False)
    time.sleep(2)

    point = 1  # direction indicator (-5 to 5), also corresponds to the vibrator. Starts at 0
    direction = "forward"

    steps_per_vibrator = 10
    
    print("in primary control")
    while True:
        print("LOOP")
        for step in range(0, steps_per_vibrator):
            move_stepper(direction=direction)  # move stepper

        # update point value
        if direction == "forward":
            point += 1
        elif direction == "backward":
            point -= 1

        if point == 10:
            time.sleep(.1)
            direction = "backward"
        if point == 1:
            time.sleep(.1)
            direction = "forward"

        print("Point: " + str(point))

        distance_cm = get_sonar()  # get the distance from the sonar
        print("  Distance read (cm): " + str(distance_cm))

        distance_ft = distance_cm / 2.54  # converts the distance from centimeters to feet
        inverse_distance_ft = 30 - distance_ft  # gets the inverse_distance (30ft = 0ft, 20ft = 10ft, 10ft = 20ft)

        # gets the inverse distance as a proportion of the max (30ft), multiplies by 8 to get the vibration intensity
        current = (inverse_distance_ft / 30) * 8

        set_vibrator_current(vibrator_pins[str(point)], current)  # turns on the vibrator to the current


if __name__ == "__main__":
    print("HI")
    primary_control()

