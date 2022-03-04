from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter
import serial as sr
import serial.tools.list_ports as port_list

class Xray:
    port = None

    @staticmethod
    def __commands_to_comlpeter(commands):
        completer = commands.copy()
        for c in completer:
            if(type(completer[c]) is dict):
                completer[c] = Xray.commands_to_comlpeter(completer[c])
            else:
                completer[c] = None
        return completer

    def make_command(self):
        commandsVar = self.commands.copy()
        text = [x for x in prompt('', completer = self.compl).strip().split(" ") if len(x) != 0]
        
        for i in range(len(text)):
            if(text[i] not in commandsVar):
                break
            commandsVar = commandsVar[text[i]]  

        if(callable(commandsVar)):
            commandsVar(self.port)
        elif(type(commandsVar) is str):
            out = commandsVar + ",".join(text[i:]) + '\r'
            self.port.write(out.encode('ASCII'))
        if text[0] == 'stop':   
            print('Programm stopped!')

    # Commands
    def set_port(self):
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

    def parse_kvma(self):
        self.port.write(b'GN\r')
        ans = self.port.read_until(b'\r').split(b':')
        print(f"kV setpoint: {int(ans[0])}\nmA setpoint: {int(ans[1])}")
        self.port.write(b'GA\r')
        ans = self.port.read_until(b'\r').split(b':')
        print(f"kV actual: {int(ans[0])}\nmA actual: {int(ans[1])}")

    def cmdstop(self):
        self.port.close()
        exit(0)

    commands = {
        'set': {
            'ma': 'SC:',
            'kv': 'SV:',
            'kvma': 'SN:',
            'timer': 'TP:',
            'status': 'SW:',
            'power': 'SP:',
            'focus': 'SF:',
            'material': {
                'Ti': 'SM:1',
                'Cr': 'SM:2',
                'Fe': 'SM:3',
                'Co': 'SM:4',
                'Cu': 'SM:5',
                'Mo': 'SM:6',
                'Ag': 'SM:7',
                'W': 'SM:8',
                'Au': 'SM:9'
            },
            'language': 'LS:',
            'date': 'DS',
            'port': set_port
        },
        'read': {
            'kvma': parse_kvma,
            'timer':{
                's': 'TN:',
                'a': 'TA:'
            },
            'msg': 'SR:',
            'power': 'RP',
            'material': 'RM'
        },
        'timer':{
            'on': 'TS:',
            'off': 'TE:'
        },
        'shutter':{
            'open': 'OS:',
            'close': 'CS:'
        },
        'date': 'DR',
        'warm_up': 'WU:',
        'id': 'ID:',
        'voltage': 'HV:',
        'tube_worktime': 'RH',
        'stop': cmdstop
    }
    compl = NestedCompleter.from_nested_dict(__commands_to_comlpeter(commands))

a = Xray()
try:
    while True:
        a.make_command()
except Exception as e:
    print(repr(e))
