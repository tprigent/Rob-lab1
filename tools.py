import serial


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
