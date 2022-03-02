import serial.tools.list_ports

def set_port():
    ports = list(serial.tools.list_ports.comports())
    if len(ports) == 0:
        print('No ports available. Connect yor device and press "Enter" to try again.')
        input()
        return None
    else:
        print("Input number one of available ports:")
        for i in range(len(ports)):
            print(i+1,') ', ports[i], sep='')
        return ports[int(input())-1]

comm = ['set port', 'stop']
while True:
    s = input().lower()
    if s not in comm:
        print('Unknown command!')
    if s == comm[0]:
        port = set_port()
    