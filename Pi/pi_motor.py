import serial
import curses
import time


STOP_TIMEOUT = 0.25   # seconds without key -> STOP
LOOP_DT = 0.05        # loop delay

def controller(stdscr):
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)
    time.sleep(2)  # Arduino reset on serial open
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    stdscr.clear()
    stdscr.nodelay(True)

    stdscr.addstr("These are the following commands to control the motors of the Arduino:\n "
          "- W: FORWARD\n"
          "- S: BACKWARD\n"
          "- A: LEFT\n"
          "- D: RIGHT\n"
          "- Q: STOP SCRIPT\n"
          "Keep pressing the KEY, if u relase the motors will stop.\n")

    stdscr.refresh()

    last_key_time = 0.0
    last_sent = None

    while(True):
        direction = stdscr.getch()
        now = time.time()

        if direction != -1:
            ch = chr(direction).upper()

            if ch == 'Q':
                ser.write(b'Q')
                break

            if ch in ('W', 'A', 'S', 'D'):
                ser.write(ch.encode('ascii'))
                last_sent = ch
                last_key_time = now

        # failsafe: if no recent key press, stop motors
        if now - last_key_time > STOP_TIMEOUT and last_sent != 'Q':
            ser.write(b'Q')
            last_sent = 'Q'

        time.sleep(LOOP_DT)

    ser.close()


if __name__ == "__main__":
    curses.wrapper(controller)
