import serial
import time

import tools


def connect_serial(serial_port, baudrate=9600):
    tools.print_title("\n### SERIAL CONNECTION ###")
    try:
        ser = serial.Serial(port=serial_port, baudrate=baudrate, bytesize=8, timeout=2, parity='N', xonxoff=0,
                            stopbits=1)
        print("[Port]   {0}\n[Status] connected".format(ser.name))
        return ser

    except serial.SerialException:
        print("[Port]   {0}\n[Status] error".format(serial_port))
        return None


def receive(ser):
    output = "No answer."
    start_time = time.time()
    curr_time = time.time()

    while curr_time-start_time < 1:                 # wait timeout (in s)
        if ser.in_waiting > 0:                      # check for data on serial port
            ser_string = ser.readline()
            output = ser_string.decode("Ascii")

        curr_time = time.time()

    tools.print_robot_receive('>>> ' + output)
    return output


def send(ser, msg, ask=0):
    if ask:
        input('-> Ready to continue ? (press enter)')
    tools.print_robot_send('<<< ' + msg)
    msg_to_send = msg + '\b'
    msg_bytes = bytes(msg_to_send, 'utf-8')
    ser.write(msg_bytes)
    answer = receive(ser)
    return answer
