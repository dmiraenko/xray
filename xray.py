from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter
import serial
import serial.tools.list_ports as port_list

class DBF3003:
    port = None

    def make_command(self):
        commandsVar = self.commands.copy()
        text = [x for x in prompt('', completer = self.completer).strip().split(" ") if len(x) != 0]
            
        try:
            for i in range(len(text)+1):
                commandsVar = commandsVar[text[i]]  
        except:
            pass
        # print(i, text, text[i:])
        if(callable(commandsVar)):
            commandsVar(self, text[i:])
        elif(type(commandsVar) is str):
            out = commandsVar + ",".join(text[i+1:]) + '\r'
            self.port.write(out.encode('ASCII'))

    # Commands
    def set_port(self, empty = []):
        if(len(empty) != 0):
            print(empty)
            raise ValueError("Command given in incorrect format")
        ports = list(port_list.comports())
        if len(ports) == 0:
            print('No ports avalable. Connect your device and press "Enter" to try again.')
            input()
            return None
        print("Available ports:")
        for i in range(len(ports)):
            print(i+1,') ', ports[i], sep='')
        try:
            self.port = serial.Serial(ports[int(prompt("Input port number\n"))-1].device)
        except:
            print("Got invalid port number")

    def read_kvma(self, empty = []):
        if(len(empty) != 0):
            raise ValueError("Command given in incorrect format")
        self.port.write(b'GN\r')
        ans = self.port.read_until(b'\r')[1:-1].split(b':')
        print(f"Setpoint: {int(ans[0])} kV, {int(ans[1])} mA")
        self.port.write(b'GA\r')
        ans = self.port.read_until(b'\r')[1:-1].split(b':')
        print(f"Actual: {int(ans[0])} kV, {int(ans[1])} mA")

    def read_power(self, empty = []):
        if(len(empty) != 0):
            raise ValueError("Command given in incorrect format")
        self.port.write(b'RP\r')
        print(str(int(self.port.read_until(b'\r')[1:-1])) + " watts")

    def read_timer(self, num : list):
        try:
            int(num[0])
        except:
            raise ValueError("Timer number incorrect.")
        if(len(num) != 1 or len(num[0]) != 1):
            raise ValueError("Timer number incorrect.")

        self.port.write(b'TN:' + num[0].encode("ASCII") + b'\r')
        ans = int(self.port.read_until(b'\r')[1:-1])
        print(f"Setpoint: {ans // 3600} h, {(ans % 3600) // 60} m, {ans % 60} s")
        self.port.write(b'TA:' + num[0].encode("ASCII") + b'\r')
        ans = int(self.port.read_until(b'\r')[1:-1])
        print(f"Actual: {ans // 3600} h, {(ans % 3600) // 60} m, {ans % 60} s")

    def read_material(self, empty = []):
        if(len(empty) != 0):
            raise ValueError("Command given in incorrect format")
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
        print(mat[int(self.port.read_until(b'\r')[1:-1])] + " anode")

    def read_focus(self, empty = []):
        if(len(empty) != 0):
            raise ValueError("Command given in incorrect format")
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

    def read_tube(self, empty = []):
        if(len(empty) != 0):
            raise ValueError("Command given in incorrect format")
        self.port.write(b'XC:\r')
        num = int(self.port.read_until(b'\r')[1:-1])
        self.port.write(b'WT:\r')
        warmup = int(self.port.read_until(b'\r')[1:-1])
        self.port.write(b'RH\r')
        time = self.port.read_until(b'\r')[1:-1]

        print(f"Selected tube: {num}")
        # Is remaining warm-up time given in seconds or what?
        print(f"Warm-up time left: {warmup}")
        print(f"Elapsed operating hours of current tube: {int(time[:-2])} h {int(int(time[-2:]) * 0.6)} m {int(int(time[-2:]) * 36) % 60} s")

    def read_waterflow(self, empty = []):
        if(len(empty) != 0):
            raise ValueError("Command given in incorrect format")
        self.port.write(b'SR:14\r')
        minflow = int(self.port.read_until(b'\r')[-4:-1])
        self.port.write(b'SR:15\r')
        flow = int(self.port.read_until(b'\r')[-4:-1])

        print(f"Minimum water flow rate: {minflow} Hz")
        print(f"Current water flow rate: {flow} Hz")

    def read_date(self, empty = []):
        if(len(empty) != 0):
            raise ValueError("Command given in incorrect format")
        
        self.port.write("DR\r")
        ans = self.port.read_until(b'\r')[1:-1].decode()
        print("No idea how to interpret this, something must be missing in the manual. The answer is:\n" + ans)

    def read_message(self, empty = []):
        if(len(empty) != 0):
            raise ValueError("Command given in incorrect format")
        
        self.port.write(b'ER\r')
        print(self.port.read_until(b'\r')[1:-1].decode())

    def read_id(self, empty = []):
        if(len(empty) != 0):
            raise ValueError("Command given in incorrect format")
        
        self.port.write(b'ID:\r')
        print(self.port.read_until(b'\r')[1:-1].decode())

    def read_status(self, empty = []):
        if(len(empty) != 0):
            raise ValueError("Command given in incorrect format")
        st = {"01" : {
                0 : ["External control disabled", "External control enabled"],
                1 : ["High voltage OFF", "High voltage ON"],
                2 : ["Cooling circuit OK", "Cooling circuit NOT OK"],
                3 : ["Buffer battery OK", "Buffer battery EMPTY"],
                4 : ["mA setpoint = actual", "mA setpoint =/= actual"],
                5 : ["kV setpoint = actual", "kV setpoint =/= actual"],
                6 : ["Shutter OK", "Shutter NOT OK"]
            },
            "03" : {
                0 : ["Timer 1 OFF", "Timer 1 ON"],
                1 : ["Timer 2 OFF", "Timer 2 ON"],
                2 : ["Timer 3 OFF", "Timer 3 ON"],
                3 : ["Timer 4 OFF", "Timer 4 ON"],
                4 : ["Shutter 1 MANUAL control", "Shutter 1 COMPUTER control"],
                5 : ["Shutter 2 MANUAL control", "Shutter 2 COMPUTER control"],
                6 : ["Shutter 3 MANUAL control", "Shutter 3 COMPUTER control"],
                7 : ["Shutter 4 MANUAL control", "Shutter 4 COMPUTER control"]
            },
            "04" : {
                0 : ["Shutter 1 command CLOSE", "Shutter 1 command OPEN"],
                1 : ["Shutter 1 CLOSED", "Shutter 1 OPEN"],
                2 : ["Shutter 1 NOT closed non-systematically", "Shutter 1 closed non-systematically"],
                3 : ["Shutter 1 CONNECTED", "Shutter 1 NOT CONNECTED"],
                4 : ["Shutter 2 command CLOSE", "Shutter 2 command OPEN"],
                5 : ["Shutter 2 CLOSED", "Shutter 2 OPEN"],
                6 : ["Shutter 2 NOT closed non-systematically", "Shutter 2 closed non-systematically"],
                7 : ["Shutter 2 CONNECTED", "Shutter 2 NOT CONNECTED"]
            },
            # No documentation for status word "05". Presumably, it is like "04", but for shutters 3 & 4. I provide this here.
            "05" : {
                0 : ["Shutter 3 command CLOSE", "Shutter 3 command OPEN"],
                1 : ["Shutter 3 CLOSED", "Shutter 3 OPEN"],
                2 : ["Shutter 3 NOT closed non-systematically", "Shutter 3 closed non-systematically"],
                3 : ["Shutter 3 CONNECTED", "Shutter 3 NOT CONNECTED"],
                4 : ["Shutter 4 command CLOSE", "Shutter 4 command OPEN"],
                5 : ["Shutter 4 CLOSED", "Shutter 4 OPEN"],
                6 : ["Shutter 4 NOT closed non-systematically", "Shutter 4 closed non-systematically"],
                7 : ["Shutter 4 CONNECTED", "Shutter 4 NOT CONNECTED"]
            },
            "06" : {
                4 : ["Warm-up program NOT ACTIVE", "Warm-up program ACTIVE"],
                5 : ["Warm-up NOT ABORTED", "Warm-up ABORTED"],
                6 : ["Warm-up NOT via external computer", "Warm-up via external computer"],
                7 : ["Warm-up NOT via keyboard", "Warm-up via keyboard"]
            }
        }
        sw12 = {
            33 : "Cooling system failed",
            37 : "Absolute undervoltage monitoring",
            38 : "Absolute overvoltage monitoring",
            39 : "Absolute undercurrent monitoring",
            43 : "Extern Stop",
            46 : "EMERGENCY-STOP",
            49 : "Preselection exceeding rated power",
            50 : "Tube overpower",
            51 : "Preselection out of range",
            52 : "Presel. exceeding rated generator current",
            53 : "High voltage lamp defective",
            55 : "Relative overcurrent monitoring",
            56 : "Relative undervoltage monitoring",
            60 : "Relative undercurrent monitoring",
            63 : "Door contact 1 and 2 open",
            64 : "Door contact 1 open",
            65 : "Door contact 2 open",
            67 : "Temp. supervision cooling system",
            70 : "Tube to be warmed up?",
            72 : "Preselection out of range.",
            76 : "—— Stand-by ——-",
            80 : "Temperature supervision power module",
            86 : "HV contactor faulty",
            90 : "Fault in filament circuit",
            91 : "Buffer battery emptyr",
            96 : "Shutter non-systematically closed",
            97 : "Shutter not connected",
            98 : "Shutter not opened",
            99 : "Shutter not closed",
            104 : "External warning lamp failed",
            105 : "Temperature supervision generator",
            106 : "Warm-up necessary",
            108 : "Power fail (low voltage)",
            109 : "Warm-up! 0=No",
            112 : "Shutter safety circuit open",
            113 : "Absolute overcurrent monitoring",
            114 : "Relative overvoltage monitoring",
            116 : "Warm-up terminated after 3 attempts",
            117 : "Warm-up aborted. Try again",
            118 : "Push START Button"
        }

        for s in st:
            self.port.write(b'SR:' + s.encode("ASCII") + b'\r')
            ans = bin(int(self.port.read_until(b'\r')[-4:-1]))[2:].zfill(8)
            for n in st[s]:
                print(st[s][n][int(ans[n])])
        
        self.port.write(b'SR:12\r')
        print(sw12[int(self.port.read_until(b'\r')[-4:-1])])

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
        # print(data)
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
        if(len(data) != 1 or len(data[0]) != 4):
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

    def set_tube(self, num : list):
        try:
            int(num[0])
        except:
            raise ValueError("Tube number given in incorrect format")
        if(len(num) != 1 or len(num[0]) != 1):
            raise ValueError("Tube number given in incorrect format")

        self.port.write(b'CT:' + num[0].encode("ASCII") + b'\r')
        print("Tube number selected. Current values are:")
        self.read_tube()

    def set_warmup(self, data : list):
        wu = {
            "none" : "0",
            "24h" : "1",
            "48h" : "2",
            "week" : "3",
            "rtc" : "4"
        }
        try:
            data[1] = str(int(data[1])).zfill(2)
        except:
            raise ValueError("Warmup data given in incorrect format")
        if(len(data) != 2 or data[0].lower() not in wu or len(data[1]) != 2):
            raise ValueError("Warmup data given in incorrect format")

        data[0] = wu[data[0].lower()]
        self.port.write(b'WU:' + ",".join(data).encode("ASCII") + b'\r')
        print("Warm-up time written to device. Current values are:")
        self.read_tube()

    def set_waterflow(self, num : list):
        try:
            num[0] = str(int(num[0])).zfill(3)
        except:
            raise ValueError("Water flow data given in incorrect format")
        if(len(num) != 1 or len(num[0]) != 3):
            raise ValueError("Water flow data given in incorrect format")

        self.port.write(b'SW:14,' + num[0].encode('ASCII') + b'\r')
        print("Water flow data written to device. Updated values are:")
        self.read_waterflow()

    def set_date(self, data : list):
        try:
            data = [str(int(d)).zfill(2).encode("ASCII") for d in data]
        except:
            raise ValueError("Date values given in incorrect format")
        if(len(data) != 6 or [len(d) for d in data] != [2, 2, 2, 2, 2, 2]):
            raise ValueError("Date values given in incorrect format")

        print("Manual doesn't make sense here, need to investigate")
        self.port.write(b'DS:' + b','.join(data[:3]) + b';' + b','.join(data[3:]) + b'\r')
        
    def set_language(self, data : list):
        lang = {
            'deutsch' : b"1",
            'english' : b"2",
            'francais' : b"3",
            'espanol' : b"4"
        }
        if(len(data) != 1 or data[0] not in lang):
            raise ValueError("Incorrect language")

        self.port.write(b'LS:' + lang[data[0]] + b'\r')

    def toggle_timer(self, num : list):
        sw03 = {
            "1" : ["Timer 1 OFF", "Timer 1 ON"],
            "2" : ["Timer 2 OFF", "Timer 2 ON"],
            "3" : ["Timer 3 OFF", "Timer 3 ON"],
            "4" : ["Timer 4 OFF", "Timer 4 ON"]
        }
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

        self.port.write(b'SR:03\r')
        ans = bin(int(self.port.read_until(b'\r')[-4:-1]))[2:].zfill(8)
        print(sw03[num[1]][int(ans[int(num[1])-1])])

    def toggle_voltage(self, num : list):
        stv = ["High voltage OFF", "High voltage ON"]
        if(len(num) != 1 or num[0].lower() not in {"on", "off"}):
            print("Error, shutting down voltage for safety:")
            self.port.write(b'HV:0\r')            
            raise ValueError("Voltage data given in incorrect format")

        if(num[0].lower() == "on"):
            self.port.write(b'HV:1\r')            
        elif(num[0].lower() == "off"):
            self.port.write(b'HV:0\r')

        self.port.write(b'SR:01\r')
        print(stv[int(bin(int(self.port.read_until(b'\r')[1:-1]))[2:].zfill(8)[1])])

    def toggle_shutter(self, num : list):
        try:
            int(num[1])
        except:
            raise ValueError("Shutter data given in incorrect format")
        if(len(num) != 2 or num[0].lower() not in {"open", "close"} or len(num[1]) != 1):
            raise ValueError("Shutter data given in incorrect format")

        if(num[0].lower() == "close"):
            self.port.write(b'CS:' + num[1].encode("ASCII") + b'\r')            
        elif(num[0].lower() == "open"):
            self.port.write(b'OS:' + num[1].encode("ASCII") + b'\r')            


    def cmdstop(self, empty = []):
        if(len(empty) != 0):
            raise ValueError("Command given in incorrect format")
        # self.port.close()
        exit(0)

    def generic(self, command : str, data : list):
        self.port.write(command.encode("ASCII") + ",".join(data))

    commands = {
        'set': {
            'kv': set_kv,
            'ma': set_ma,
            'kvma': set_kvma,
            'timer': set_timer,
            'power': set_power,
            'focus': set_focus,
            'material': set_material,
            'language': set_language,
            'date' : set_date,
            'port': set_port,
            'tube' : set_tube,
            'warmup' : set_warmup,
            'waterflow' : set_waterflow
        },
        'read': {
            'kvma': read_kvma,
            'timer': read_timer,
            'msg': read_message,
            'power': read_power,
            'material': read_material,
            'tube' : read_tube,
            'focus' : read_focus,
            'waterflow' : read_waterflow,
            'id' : read_id,
            'date': read_date
        },
        'timer': toggle_timer,
        'shutter': toggle_shutter,
        'voltage': toggle_voltage,
        'status' : read_status,
        'stop': cmdstop
    }

    completer = NestedCompleter.from_nested_dict({
        'set': {
            'ma': None,
            'kv': None,
            'kvma': None,
            'timer': None,
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
            'warmup' : {
                'none' : None,
                '24h' : None,
                '48h' : None,
                'week' : None,
                'RTC' : None
            },
            'language': {
                'english' : None,
                'deutsch' : None,
                'francais' : None,
                'espanol' : None,
            },
            'waterflow' : None,
            'tube' : None,
            'date': None,
            'port': None
        },
        'read': {
            'kvma': None,
            'timer': None,
            'msg': None,
            'power': None,
            'focus' : None,
            'material': None,
            'waterflow' : None
        },
        'timer':{
            'on': None,
            'off': None
        },
        'shutter':{
            'open': None,
            'close': None
        },
        'voltage': {
            'on' : None,
            'off' : None
        },
        'status' : None,
        'date': None,
        'warm_up': None,
        'id': None,
        'stop': None
    })

a = DBF3003()
while True:
    try:
        a.make_command()
    except Exception as e:
        print(repr(e))
