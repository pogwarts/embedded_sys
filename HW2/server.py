import socket
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Define server IP and PORT
SERVER_IP = "0.0.0.0"  # Listen on all available interfaces
SERVER_PORT = 49152    # Port number (must match the STM32 client's port)

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the server address and port
server_socket.bind((SERVER_IP, SERVER_PORT))

# Start listening for incoming connections
server_socket.listen(1)  # Allows 1 client connection at a time (can be increased if needed)
print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

# Accept a connection from a client
client_socket, client_address = server_socket.accept()
print(f"Connection established with {client_address}")

# Initialize lists to store received data
x_data, y_data, z_data = [], [], []

# Set up the plot with three subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))

# Initialize line plots for x, y, and z data
line_x, = ax1.plot([], [], 'r-', label='X Data')
line_y, = ax2.plot([], [], 'g-', label='Y Data')
line_z, = ax3.plot([], [], 'b-', label='Z Data')

# Set the limits of the axes
ax1.set_xlim(0, 1000)
ax1.set_ylim(-100, 100)
ax2.set_xlim(0, 1000)
ax2.set_ylim(-100, 100)
ax3.set_xlim(0, 1000)
ax3.set_ylim(-100, 100)

# Set labels and titles
ax1.set_title('X Data')
ax1.set_xlabel('Time')
ax1.set_ylabel('X Value')
ax1.legend()

ax2.set_title('Y Data')
ax2.set_xlabel('Time')
ax2.set_ylabel('Y Value')
ax2.legend()

ax3.set_title('Z Data')
ax3.set_xlabel('Time')
ax3.set_ylabel('Z Value')
ax3.legend()

def update_plot(frame):
    data = client_socket.recv(50)  # Buffer size of 50 bytes
    if not data:
        # If no data is received, the client has disconnected
        print("Client disconnected")
        return

    # Decode and print the received data
    received_message = data.decode('utf-8').strip().replace('\x00', '')
    print(f"Received from STM32: {received_message}")

    # Parse the received data (assuming it's in the format "X: 0, Y: 0, Z: 1012")
    try:
        parts = received_message.split(',')
        x = int(parts[0].split(':')[1].strip())
        y = int(parts[1].split(':')[1].strip())
        z = int(parts[2].split(':')[1].strip())
        x = x*9.81/1000
        y = y*9.81/1000
        z = z*9.81/1000
        x_data.append(x)
        y_data.append(y)
        z_data.append(z)
    except (ValueError, IndexError) as e:
        print(f"Error parsing data: {e}")
        return

    # Update the line plots
    line_x.set_data(range(len(x_data)), x_data)
    line_y.set_data(range(len(y_data)), y_data)
    line_z.set_data(range(len(z_data)), z_data)

    # Rescale the x-axis to fit the data
    ax1.set_xlim(0, len(x_data))
    ax2.set_xlim(0, len(y_data))
    ax3.set_xlim(0, len(z_data))

    ax1.relim()
    ax1.autoscale_view()
    ax2.relim()
    ax2.autoscale_view()
    ax3.relim()
    ax3.autoscale_view()

# Use FuncAnimation to update the plot dynamically
ani = FuncAnimation(fig, update_plot, interval=100)

plt.tight_layout()
plt.show()

# Close the connection
client_socket.close()
server_socket.close()