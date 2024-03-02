import tkinter as tk
from tkinter import ttk, scrolledtext
import serial
import serial.tools.list_ports
import threading
import queue
import time
import re

# Define a fixed width for buttons and labels
button_width = 5
label_width = 20  # Adjust this based on your content

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def refresh_ports():
    port_menu['menu'].delete(0, 'end')
    new_ports = list_serial_ports()
    for port in new_ports:
        port_menu['menu'].add_command(label=port, command=tk._setit(port_var, port))
    port_var.set(new_ports[0] if new_ports else 'No Ports Available')

def update_text():
    while not data_queue.empty():
        data = data_queue.get()

        matches = re.finditer(r"s(\d+)=(-?\d+\.\d+)", data)
        for match in matches:
            motor_id = int(match.group(1))
            motor_value = match.group(2)
            labels[motor_id - 1].config(text=f"s{motor_id}: {motor_value}")

        text_box.configure(state='normal')
        text_box.insert(tk.END, data + '\n')
        text_box.configure(state='disabled')
        text_box.see(tk.END)

    root.after(100, update_text)

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

def connect_serial():
    global serial_thread, ser
    port = port_var.get()
    ser = serial.Serial(port, 9600, timeout=1)
    serial_thread = threading.Thread(target=read_from_port, args=(ser, data_queue), daemon=True)
    serial_thread.start()
    connect_button.config(state='disabled')

def send_continuous(char):
    while continue_sending.get(char, False):
        if ser and ser.isOpen():
            ser.write(char.encode())
        time.sleep(0.1)

def on_press(char):
    print("char is ",char)
    continue_sending[char] = True
    motor_id = int(char)
    motor_group = (motor_id - 1) // 2 + 1
    direction = 'A' if motor_id % 2 == 1 else 'C'
    #send_continuous(f'{direction}{motor_group}F')
    send_once(f'{direction}{motor_group}F')


def on_release(char):
    continue_sending[char] = False
    motor_id = int(char)
    motor_group = (motor_id - 1) // 2 + 1
    #send_continuous(f'S{motor_group}F')
    send_once(f'S{motor_group}F')

def send_once(char):
    if ser and ser.isOpen():
        ser.write(char.encode())

def toggle_text_box():
    if text_box.winfo_viewable():
        text_box.pack_forget()
        toggle_button.config(text='Show Debug Box')
    else:
        text_box.pack(pady=5)
        toggle_button.config(text='Hide Debug Box')

# Creating the main window
root = tk.Tk()
root.title("Serial Communication App")
root.configure(bg='light gray')

data_queue = queue.Queue()
ser = None
continue_sending = {}

# Styling for the buttons
button_style = {'font': ('Helvetica', 12, 'bold'), 'bg': '#0052cc', 'fg': 'white'}
toggle_button_style = {'font': ('Helvetica', 10), 'bg': 'gray', 'fg': 'black'}

# Frame for port selection and refresh button
port_frame = tk.Frame(root, bg='light gray')
port_frame.pack(side=tk.LEFT, padx=10, pady=5)

# Dropdown for serial ports
port_label = tk.Label(port_frame, text="Select Port:", bg='light gray')
port_var = tk.StringVar(root)
ports = list_serial_ports()
port_menu = ttk.OptionMenu(port_frame, port_var, ports[0] if ports else 'No Ports Available', *ports)
port_label.pack()
port_menu.pack()

# Refresh button for COM ports
refresh_button = tk.Button(port_frame, text="Refresh Ports", command=refresh_ports, **button_style)
refresh_button.pack(pady=5)

# Connect button
connect_button = tk.Button(port_frame, text="Connect", command=connect_serial, **button_style)
connect_button.pack(pady=5)

# Canvas for scrollable motors
canvas = tk.Canvas(root, bg='light gray')
canvas.pack(side=tk.LEFT, fill=tk.Y)

# Scrollbar for canvas
scrollbar = tk.Scrollbar(root, command=canvas.yview)
scrollbar.pack(side=tk.LEFT, fill=tk.Y)
canvas.configure(scrollregion=canvas.bbox("all"))
canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

# Frames for arrow buttons and labels
motor_frames = [tk.Frame(canvas, bg='light gray') for _ in range(30)]
labels = []

for i, motor_frame in enumerate(motor_frames):
    canvas.create_window((0, i * 40), window=motor_frame, anchor='nw')

    # Labels for motors
    motor_labels = tk.Label(motor_frame, text=f"MOTOR-{i+1}", bg='light gray')
    motor_labels.pack()

    labels.append(tk.Label(motor_frame, text=f"s{i+1}: Not Received", bg='light gray'))
    labels[i].pack()

    # Updating the button mapping
    buttons = {f'Left Arrow {i+1}': str(i*2+1) for i in range(30)}
    buttons.update({f'Right Arrow {i+1}': str(i*2+2) for i in range(30)})

    arrow_symbols = {f'Left Arrow {i+1}': '←' for i in range(30)}
    arrow_symbols.update({f'Right Arrow {i+1}': '→' for i in range(30)})
    
    # Frames for arrow buttons and labels
motor_frames = [tk.Frame(canvas, bg='light gray') for _ in range(30)]
labels = []

for i, motor_frame in enumerate(motor_frames):
    canvas.create_window((0, i * 40), window=motor_frame, anchor='nw')

    # Labels for motors
    motor_labels = tk.Label(motor_frame, text=f"MOTOR-{i+1}", bg='light gray')
    motor_labels.pack()

    labels.append(tk.Label(motor_frame, text=f"s{i+1}: Not Received", bg='light gray'))
    labels[i].pack()

    # Updating the button mapping
    buttons = {f'Left Arrow {i+1}': str(i*2+1), f'Right Arrow {i+1}': str(i*2+2)}

    arrow_symbols = {f'Left Arrow {i+1}': '←', f'Right Arrow {i+1}': '→'}

    # Frames for arrow buttons and labels
motor_frames = [tk.Frame(canvas, bg='light gray') for _ in range(30)]
labels = []

for i, motor_frame in enumerate(motor_frames):
    canvas.create_window((0, i * 40), window=motor_frame, anchor='nw')

    # Labels for motors
    motor_labels = tk.Label(motor_frame, text=f"MOTOR-{i+1}", bg='light gray')
    motor_labels.pack(side=tk.LEFT)

    labels.append(tk.Label(motor_frame, text=f"s{i+1}: Not Received", bg='light gray'))
    labels[i].pack(side=tk.LEFT, padx=10)

    # Updating the button mapping
    buttons = {f'Left Arrow {i+1}': str(i*2+1), f'Right Arrow {i+1}': str(i*2+2)}

    arrow_symbols = {f'Left Arrow {i+1}': '←', f'Right Arrow {i+1}': '→'}

    # Frame for arrow buttons
    button_frame = tk.Frame(motor_frame, bg='light gray')
    button_frame.pack(side=tk.LEFT, padx=10)

    button_left = tk.Button(button_frame, text=arrow_symbols[f'Left Arrow {i+1}'], height=2, width=5, **button_style)
    button_left.bind("<ButtonPress>", lambda event, ch=buttons[f'Left Arrow {i+1}']: on_press(ch))
    button_left.bind("<ButtonRelease>", lambda event, ch=buttons[f'Left Arrow {i+1}']: on_release(ch))
    button_left.pack(side=tk.LEFT)

    button_right = tk.Button(button_frame, text=arrow_symbols[f'Right Arrow {i+1}'], height=2, width=5, **button_style)
    button_right.bind("<ButtonPress>", lambda event, ch=buttons[f'Right Arrow {i+1}']: on_press(ch))
    button_right.bind("<ButtonRelease>", lambda event, ch=buttons[f'Right Arrow {i+1}']: on_release(ch))
    button_right.pack(side=tk.LEFT)


#.

# Text box for displaying received data
text_box = scrolledtext.ScrolledText(root, state='disabled', height=10)
text_box.pack(pady=5)

# Toggle button for showing/hiding the text box
toggle_button = tk.Button(root, text="Show Debug Box", command=toggle_text_box, **toggle_button_style)
toggle_button.pack(pady=5)

# Initially hiding the text box
text_box.pack_forget()

# Update text box with received data
root.after(100, update_text)

# Running the GUI application
root.mainloop()

# Closing the serial port when the window is closed
if ser and ser.isOpen():
    ser.close()
