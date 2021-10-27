# this is the last code

from pyModbusTCP.client import ModbusClient
from time import sleep

client = ModbusClient(host = "192.168.1.240", port = 502, auto_open = True, auto_close = True, timeout = 2.2, debug = False)

while(1):
    state = client.read_discrete_inputs(1024, 8)
    print(state)
