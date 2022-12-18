import serial
import time
import tools


# Establish RS232 serial connection to device
def connect_serial(serial_port, baudrate=9600):
    tools.print_title("### SERIAL CONNECTION ###")
    try:
        ser = serial.Serial(port=serial_port, baudrate=baudrate, bytesize=8, timeout=2, parity='N', xonxoff=0,
                            stopbits=1)
        print("[Port]   {0}\n[Status] connected".format(ser.name))
        return ser

    except serial.SerialException:
        print("[Port]   {0}\n[Status] error".format(serial_port))
        return None


# Read serial input buffer (including timeout of 1s)
def receive(ser):
    response_incoming = 0           # flag for data incoming
    output = ''                     # prepare response buffer
    start_time = time.time()
    curr_time = time.time()

    while curr_time-start_time < 1:                 # wait timeout (in s)
        if ser.in_waiting > 0:                      # check for data on serial port
            response_incoming = 1
            ser_string = ser.readline()
            readbuf = ser_string.decode("Ascii")
            output += readbuf                       # add read line to response buffer
        curr_time = time.time()

    if response_incoming == 0:      # if no answer has been received within timeout
        output = 'No answer.'

    tools.print_robot_receive('>>> ' + output)      # final print

    return output


# Send message to device and listen for automatic answer
def send(ser, msg, ask=0):
    if ask:
        input('-> Ready to continue ? (press enter)')
    tools.print_robot_send('<<< ' + msg)
    msg_to_send = msg + '\r'
    msg_bytes = msg_to_send.encode('ASCII')
    ser.write(msg_bytes)
    answer = receive(ser)
    return answer
