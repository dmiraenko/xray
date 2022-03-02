from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter
import serial as sr
import serial.tools.list_ports as port_list

def set_port():
    ports = list(port_list.comports())
    if len(ports) == 0:
        print('No ports avalable. Connect yore device and press "Enter" to try again.')
        input()
        return None
    else:
        print("Input number one of available ports:")
        for i in range(len(ports)):
            print(i+1,') ', ports[i], sep='')
        return ports[int(input())-1]

def commands_to_comlpeter(commands):
    completer = commands.copy()
    for c in completer:
        if(type(completer[c]) is dict):
            completer[c] = commands_to_comlpeter(completer[c])
        else:
            completer[c] = None
    return completer

def parse_kvma(port : sr.Serial):
    port.write(b'GN\r')
    ans = port.read_until(b'\r').split(b':')
    print(f"kV setpoint: {int(ans[0])}\nmA setpoint: {int(ans[1])}")
    port.write(b'GA\r')
    ans = port.read_until(b'\r').split(b':')
    print(f"kV actual: {int(ans[0])}\nmA actual: {int(ans[1])}")


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
        'port': 'SET_PORT'
    },
    'read': {
        'kvma':parse_kvma,
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
    'stop': None
}

compl = commands_to_comlpeter(commands)
port = sr.Serial(port = '/dev/pts/8')


while True:
    commandsVar = commands.copy()
    completer = NestedCompleter.from_nested_dict(compl)
    text = [x for x in prompt('', completer = completer).strip().split(" ") if len(x) != 0]
    
    for i in range(len(text)):
        if(text[i] not in commandsVar):
            break
        commandsVar = commandsVar[text[i]]  

    if(callable(commandsVar)):
        commandsVar(port)
    elif(type(commandsVar) is str):
        out = commandsVar + ",".join(text[i:]) + '\r'
        port.write(out.encode('ASCII'))
    if text[0] == 'stop':   
        print('Programm stopped!')
        break



