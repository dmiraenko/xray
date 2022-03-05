from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter
import serial
import serial.tools.list_ports as port_list

class ISODBF3003:
    port = None

    def make_command(self):
        commandsVar = self.commands.copy()
        text = [x for x in prompt('', completer = self.completer).strip().split(" ") if len(x) != 0]
            
        for i in range(len(text)):
            try:
                if(text[i] not in commandsVar):
                    break
            except:
                break
            commandsVar = commandsVar[text[i]]  

        if(callable(commandsVar)):
            commandsVar(self, text[i:])
        elif(type(commandsVar) is str):
            out = commandsVar + ",".join(text[i:]) + '\r'
            self.port.write(out.encode('ASCII'))

    # Commands
    def set_port(self, empty = []):
        ports = list(port_list.comports())
        if len(ports) == 0:
            print('No ports avalable. Connect your device and press "Enter" to try again.')
            input()
            return None
        print("Available ports:")
        for i in range(len(ports)):
            print(i+1,') ', ports[i], sep='')
        try:
            self.port = serial.Serial(ports[int(prompt("Input port number"))-1])
        except:
            print("Got invalid port number")

    def read_kvma(self, empty = []):
        self.port.write(b'GN\r')
        ans = self.port.read_until(b'\r')[1:-1].split(b':')
        print(f"Setpoint: {int(ans[0])} kV, {int(ans[1])} mA")
        self.port.write(b'GA\r')
        ans = self.port.read_until(b'\r')[1:-1].split(b':')
        print(f"Actual: {int(ans[0])} kV, {int(ans[1])} mA")

    def read_power(self, empty = []):
        self.port.write(b'RP\r')
        print(str(int(self.port.read_until(b'\r')[1:-1])) + " watts")

    def read_timer(self, num : list):
        try:
            int(num[0])
        except:
            raise ValueError("Timer number incorrect.")
        if(len(num) != 1):
            raise ValueError("Timer number incorrect.")
        if(len(num[0]) != 1):
            raise ValueError("Timer number incorrect.")

        self.port.write(b'TN:' + num[0].encode("ASCII") + b'\r')
        ans = int(self.port.read_until(b'\r')[1:-1])
        print(f"Setpoint: {ans // 3600} h, {(ans % 3600) // 60} m, {ans % 60} s")
        self.port.write(b'TA:' + num[0].encode("ASCII") + b'\r')
        ans = self.port.read_until(b'\r')[1:-1]
        print(f"Actual: {ans // 3600} h, {(ans % 3600) // 60} m, {ans % 60} s")

    def read_material(self, empty = []):
        mat = {
                1 : 'Ti',
                2 : 'Cr',
                3 : 'Fe',
                4 : 'Co',
                5 : 'Cu',
                6 : 'Mo',
                7 : 'Ag',
                8 : 'W',
                9 : 'Au'
            }
        
        self.port.write(b'RM\r')
        print(mat[self.port.read_until(b'\r')[1:-1]] + " anode")

    def read_focus(self, empty = []):
        foc = {
            1 : "0.15 x 8 mm",
            2 : "0.4 x 8 mm",
            3 : "0.4 x 12 mm",
            4 : "1.0 x 10 mm",
            5 : "2 x 12 mm",
            6 : "0.04 x 8 mm",
            7 : "0.04 x 12 mm",
            8 : "0.1 x 10 mm",
            9 : "0.2 x 12 mm",
            10 : "0.4 x 0.08 mm",
            11 : "1.4 x 1.2 mm",
            12 : "1 x 1 mm",
            13 : "2 x 1.2 mm"
        }

        self.port.write(b'RF\r')
        print(foc[int(self.port.read_until(b'\r')[1:-1])] + " focus")


    def set_kv(self, data : list):
        try:
            data[0] = str(int(data[0])).zfill(2)
        except:
            raise ValueError("kV given in incorrect format")
        if(len(data) != 1 or len(data[0]) != 2):
            raise ValueError("kV given in incorrect format")
        
        self.port.write(b'SV:' + data[0].encode("ASCII") + b'\r')
        print("kV written to device. Current values are:")
        self.read_kvma()

    def set_ma(self, data : list):
        try:
            data[0] = str(int(data[0])).zfill(2)
        except:
            raise ValueError("mA given in incorrect format")
        if(len(data) != 1 or len(data[0]) != 2):
            raise ValueError("mA given in incorrect format")

        self.port.write(b'SC:' + data[0].encode("ASCII") + b'\r')
        print("mA written to device. Current values are:")
        self.read_kvma()

    def set_kvma(self, data : list):
        try:
            data = [str(int(d)).zfill(2) for d in data]        
        except:
            raise ValueError("Data given in incorrect format")
        if(len(data) != 2 or len(data[0]) != 2 or len(data[1]) != 2):
            raise ValueError("Data given in incorrect format")

        self.port.write(b'SN:' + ",".join(data).encode("ASCII") + b'\r')
        print("kV and mA written to device. Current values are:")
        self.read_kvma()

    def set_power(self, data : list):
        try:
            data[0] = str(int(data[0])).zfill(4)
        except:
            raise ValueError("W given in incorrect format")
        if(len(data) != 1 or len(data[0] != 4)):
            raise ValueError("W given in incorrect format")

        self.port.write(b'SP:' + data[0].encode("ASCII") + b'\r')
        print("W written to device. Current value is:")
        self.read_power()

    def set_timer(self, data : list):
        try:
            data[0] = str(int(data[0])).zfill(1)
            data[1:3] = [str(int(d)).zfill(2) for d in data[1:3]]
        except:
            raise ValueError("Time data given in incorrect format")
        if(len(data) != 4 or [len(d) for d in data] != [1, 2, 2, 2]):
            raise ValueError("Time data given in incorrect format")

        self.port.write(b'TP:' + ",".join(data).encode("ASCII") + b'\r')
        print("Timer " + data[1] + " written to device. Current values are:")
        self.read_timer(data[0:1])

    def set_material(self, data : list):
        mat = {
                'ti': b'1',
                'cr': b'2',
                'fe': b'3',
                'co': b'4',
                'cu': b'5',
                'mo': b'6',
                'ag': b'7',
                'w': b'8',
                'au': b'9'
            }
        if(len(data) != 1 or data[0].lower() not in mat):
            raise ValueError("Material data given in incorrect format")

        self.port.write(b'SM:' + mat[data[0].lower()] + b'\r')
        print("Material selected. Current material is:")
        self.read_material()

    # Manual says to send only one byte, but always specifies to send numbers in decimal format. No idea whether my function should work.
    def set_focus(self, data : list):
        foc = {
            "0.15 x 8 mm" : b'01',
            "0.4 x 8 mm" : b'02',
            "0.4 x 12 mm" : b'03',
            "1.0 x 10 mm" : b'04',
            "2 x 12 mm" : b'05',
            "0.04 x 8 mm" : b'06',
            "0.04 x 12 mm" : b'07',
            "0.1 x 10 mm" : b'08',
            "0.2 x 12 mm" : b'09',
            "0.4 x 0.08 mm" : b'10',
            "0.4 x 1.2 mm" : b'11',
            "1 x 1 mm" : b'12',
            "2 x 1.2 mm" : b'13'
        }
        f = " ".join(data)
        if(f not in foc):
            raise ValueError("Focus data given in incorrect format")
        self.port.write(b'SF:' + foc[f] + b'\r')

        print("Data written to device. Current value is:")
        self.read_focus()

    def toggle_timer(self, num : list):
        try:
            int(num[1])
        except:
            raise ValueError("Timer data given in incorrect format")
        if(len(num) != 2 or num[0].lower() not in {"on", "off"} or len(num[1]) != 1):
            raise ValueError("Timer data given in incorrect format")

        if(num[0].lower() == "on"):
            self.port.write(b'TS:' + num[1].encode("ASCII") + b'\r')            
        elif(num[0].lower() == "off"):
            self.port.write(b'TE:' + num[1].encode("ASCII") + b'\r')            

    def toggle_voltage(self, num : list):
        if(len(num) != 1 or num[0].lower() not in {"on", "off"}):
            print("Error, shutting down voltage for safety:")
            self.port.write(b'HV:0\r')            
            raise ValueError("Shutter data given in incorrect format")

        if(num[0].lower() == "on"):
            self.port.write(b'HV:1\r')            
        elif(num[0].lower() == "off"):
            self.port.write(b'HV:0\r')            

    def toggle_shutter(self, num : list):
        try:
            int(num[1])
        except:
            raise ValueError("Voltage data given in incorrect format")
        if(len(num) != 2 or num[0].lower() not in {"open", "close"} or len(num[1]) != 1):
            raise ValueError("Voltage data given in incorrect format")

        if(num[0].lower() == "close"):
            self.port.write(b'CS:' + num[1].encode("ASCII") + b'\r')            
        elif(num[0].lower() == "open"):
            self.port.write(b'OS:' + num[1].encode("ASCII") + b'\r')            


    def cmdstop(self, empty = []):
        # self.port.close()
        exit(0)

    def generic(self, command : str, data : list):
        self.port.write(command.encode("ASCII") + ",".join(data))

    commands = {
        'set': {
            'ma': set_ma,
            'kv': set_kv,
            'kvma': set_kvma,
            'timer': set_timer,
            'status': 'SW:',
            'power': 'SP:',
            'focus': set_focus,
            'material': set_material,
            'language': 'LS:',
            'date': 'DS',
            'port': set_port
        },
        'read': {
            'kvma': read_kvma,
            'timer': read_timer,
            'msg': 'SR:',
            'power': 'RP',
            'material': read_material
        },
        'timer': toggle_timer,
        'shutter': toggle_shutter,
        'date': 'DR',
        'warm_up': 'WU:',
        'id': 'ID:',
        'voltage': toggle_voltage,
        'tube_worktime': 'RH',
        'stop': cmdstop
    }

    completer = NestedCompleter.from_nested_dict({
        'set': {
            'ma': None,
            'kv': None,
            'kvma': None,
            'timer': None,
            'status': None,
            'power': None,
            'focus': None,
            'material': {
                'Ti': None,
                'Cr': None,
                'Fe': None,
                'Co': None,
                'Cu': None,
                'Mo': None,
                'Ag': None,
                'W': None,
                'Au': None
            },
            'focus':{
                "0.15 x 8 mm" : None,
                "0.4 x 8 mm" : None,
                "0.4 x 12 mm" : None,
                "1.0 x 10 mm" : None,
                "2 x 12 mm" : None,
                "0.04 x 8 mm" : None,
                "0.04 x 12 mm" : None,
                "0.1 x 10 mm" : None,
                "0.2 x 12 mm" : None,
                "0.4 x 0.08 mm" : None,
                "0.4 x 1.2 mm" : None,
                "1 x 1 mm" : None,
                "2 x 1.2 mm" : None
            },
            'language': None,
            'date': None,
            'port': None
        },
        'read': {
            'kvma': None,
            'timer': None,
            'msg': None,
            'power': None,
            'material': None
        },
        'timer':{
            'on': None,
            'off': None
        },
        'shutter':{
            'open': None,
            'close': None
        },
        'date': None,
        'warm_up': None,
        'id': None,
        'voltage': {
            'on' : None,
            'off' : None
        },
        'tube_worktime': None,
        'stop': None
    })

a = ISODBF3003()
try:
    while True:
        a.make_command()
except Exception as e:
    print(repr(e))
