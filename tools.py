import serial
import time


def connect_serial(serial_port, baudrate=9600):
    print("### SERIAL CONNECTION ###")
    try:
        ser = serial.Serial(port=serial_port, baudrate=baudrate, bytesize=8, timeout=2, parity='N', xonxoff=0,
                            stopbits=1)
        print("[Port]:   {0}\n[Status] connected".format(ser.name))
        return ser

    except serial.SerialException:
        print("[Port]   {0}\n[Status] error".format(serial_port))
        return None


def receive(ser, timeout):
    output = ""
    flag = True
    start_time = time.time()
    while flag:
        # Wait until there is data waiting in the serial buffer
        if ser.in_waiting > 0:
            # Read data out of the buffer until a carriage return / new line is found
            ser_string = ser.readline()
            # Print the contents of the serial data
            try:
                output = ser_string.decode("Ascii")
                print('>>> ' + ser_string.decode("Ascii"))
            except:
                pass
            else:
                deltat = time.time() - start_time
                if deltat > timeout:
                    flag = False
    return output


def send(ser, msg):
    print('<<< ' + msg)
    msg_to_send = msg + '\b'
    msg_bytes = bytes(msg_to_send, 'utf-8')
    ser.write(msg_bytes)
    return receive(ser, 2)
