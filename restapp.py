from flask import Flask, request, jsonify,send_from_directory
import serial
import serial.tools.list_ports
import threading
import queue
import time
import re

app = Flask(__name__)

data_queue = queue.Queue()
ser = None
#continue_sending = {}

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def send_once(char):
    if ser and ser.isOpen():
        ser.write(char.encode())

def send_continuous(char):
    while continue_sending.get(char, False):
        if ser and ser.isOpen():
            ser.write(char.encode())
        time.sleep(0.1)

def read_from_port(ser, queue):
    while ser.isOpen():
        try:
            data = ser.readline()
            decoded_data = data.decode('utf-8').rstrip()
            if decoded_data:
                queue.put(decoded_data)
        except UnicodeDecodeError as e:
            print(f"UnicodeDecodeError: {e}")
            print(f"Received bytes: {data}")
            try:
                decoded_data = data.decode('latin-1', errors='replace').rstrip()
                print(f"Decoded with latin-1: {decoded_data}")
                queue.put(decoded_data)
            except UnicodeDecodeError as e:
                print(f"Failed to decode with latin-1 as well. Discarding the data.")
        except serial.SerialException:
            break

@app.route('/')
def send_frontend():
    return send_from_directory('frontend', "index.html")

@app.route("/ports")
def get_ports():
    ports = list_serial_ports()
    print(ports)
    return jsonify({"ports": ports})

@app.route("/connect", methods=["POST"])
def connect_serial():
    global serial_thread, ser
    port = request.json.get("port")
    ser = serial.Serial(port, 9600, timeout=1)
    serial_thread = threading.Thread(target=read_from_port, args=(ser, data_queue), daemon=True)
    serial_thread.start()
    return jsonify({"message": "Connected to serial port successfully"})

@app.route("/send", methods=["POST"])
def send_command():
    command = request.json.get("command")
    if ser and ser.isOpen():
        ser.write(command.encode())
        return jsonify({"message": "Command sent successfully"})
    else:
        return jsonify({"error": "Serial port not open"})

@app.route("/disconnect")
def disconnect_serial():
    if ser and ser.isOpen():
        ser.close()
        return jsonify({"message": "Serial port disconnected successfully"})
    else:
        return jsonify({"error": "Serial port not open"})

@app.route("/getValues")
def get_values():
    if not data_queue.empty():
        data = data_queue.get()
        matches = re.finditer(r"s(\d+)=(-?\d+\.\d+)", data)
        for match in matches:
            motor_id = int(match.group(1))
            motor_value = match.group(2)
            return jsonify({"motorId": motor_id, "motorValue":motor_value})

@app.route("/rotate", methods=["POST"])
def rotate_motor():
    direction = request.json.get("direction")
    motor_group = request.json.get("motor_group")
    if direction == 'clockwise':
        direction_command = 'C'
    elif direction == 'anti-clockwise':
        direction_command = 'A'
    if ser and ser.isOpen():
        send_once(f'{direction_command}{motor_group}F')
        return jsonify({"message": "Command sent successfully"})
    else: 
        return jsonify({"message": "Serial Port Not Open"})


@app.route("/stop", methods=["POST"])
def stop_motor():
    motor_group = request.json.get("motor_group")
    if ser and ser.isOpen():
        send_once(f'S{motor_group}F')
        return jsonify({"message": "Command sent successfully"})
    else: 
        return jsonify({"message": "Serial Port Not Open"})


if __name__ == "__main__":
    app.run(debug=True)
