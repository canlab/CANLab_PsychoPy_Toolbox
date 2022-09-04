# medocControl.py
# Required for Thermode Triggering
from time import time, sleep
from datetime import datetime
import socket
import struct
import binascii

class ThermodeEventListener():
    def wait_for_seconds(self, seconds):
        sleep(seconds)

class ThermodeConfig():
    """
    address: hostName (IP), port: portNum (int), named_program: commandID (string?), other_parameters (optional depending on command) 
    """
    address = '10.64.1.10' # Dartmouth Brain Imaging Center

    port = 20121
    debug = 1
    timedelayformedoc = 0.3


config = ThermodeConfig()   # Create a thermode config object

command_to_id = {
    'GET_STATUS': 0,
    'SELECT_TP': 1,
    'START': 2,
    'PAUSE': 3,
    'TRIGGER': 4,
    'STOP': 5,
    'ABORT': 6,
    'YES': 7, # used to start increasing the temperature
    'NO': 8, # used to start decreasing the temperature
    'COVAS': 9,
    'VAS': 10,
    'SPECIFY_NEXT':11,
    'T_UP': 12,
    'T_DOWN': 13,
    'KEYUP': 14, # used to stop the temperature gradient,
    'UNNAMED': 15
}
# make the same as above but reversed:
id_to_command = {item:key for key, item in command_to_id.items()}
test_states = {
    0 : 'IDLE',                     # Often, waiting for external control
    1 : 'RUNNING',                  # Test Screen is now up. Could mean Waiting for Trigger or Stimulation has been Triggered.
    2 : 'PAUSED',
    3 : 'READY'                     # Is present when Auto-Start is not enabled. This status if prior to the pre-test.
}

states = {
    0 : "IDLE",
    1 : "READY",                    # Machine is Idling, ready to receive commands.
    2 : "TEST IN PROGRESS"          # Test Screen is now up. Could mean Waiting for Trigger or Stimulation has been Triggered.
}

response_codes = { 0 : "OK",
    1 : "FAIL: ILLEGAL PARAMETER",              
    2 : "FAIL: ILLEGAL STATE TO SEND THIS",
    3 : "FAIL: NOT THE PROPER TEST STATE",
    4096: "DEVICE COMMUNICATION ERROR",
    8192: "safety warning, test continues",
    16384: "Safety error, going to IDLE"
}

# converter from bytes to int:
def intToBytes(integer, nbytes):
    return integer.to_bytes(nbytes, byteorder='big')
# converter from int to bytes:
def intFromBytes(xbytes):
    return int.from_bytes(xbytes, 'big')

# packs bytes together
def commandBuilder(command, parameter=None):
    if type(command) is str:
        command = command_to_id[command.upper()]
    if type(parameter) is str:
        # then program code, e.g. '00000001'
        parameter = int(parameter, 2)   # Convert to a binary integer (base 2)
    elif type(parameter) is float:
        parameter = 100*parameter
#    commandbytes = intToBytes(socket.htons(int(time())), 4)
    commandbytes = intToBytes(int(time()), 4)
    commandbytes += intToBytes(int(command), 1)
    if parameter:
        # commandbytes += intToBytes(socket.htonl(int(parameter)), 4) # Append a 4-byte command to the end
        commandbytes += intToBytes(socket.htonl(parameter), 4) # Append a 4-byte command to the end
#        commandbytes += intToBytes(int(parameter), 4)
    return intToBytes(len(commandbytes), 4) + commandbytes # A byte string consisting of 4(length)+
    # prepending the command data with 4-bytes header that indicates the command data length

# command sender:
def sendCommand(command, parameter=None, address=config.address, port=config.port, el=ThermodeEventListener(), verbose=False):
    """
    this functions allows sending commands to the MMS
    e.g. : sendCommand('get_status')
    or sendCommand('select_tp', '01000000')
    """
    # convert command to bytes:
    commandbytes = commandBuilder(command, parameter=parameter)
    # if config.debug:
    #     print(f'Sending the following bytes: {binascii.hexlify(commandbytes)} -- {len(commandbytes)} bytes')
    # now the connection part:
    for attemps in range(50):
        try:
            s = socket.socket()
            s.connect((address, port))
            # s.setblocking(False)    #
            # s.settimeout(20)
            # s.setdefaulttimeout(20) 
            s.send(commandbytes) 
            # sleep(0.01)
            data = msg = s.recv(1024)
            while data:
                # sleep(0.01)
                data = s.recv(17)
#                data = s.recv(34)
                msg += data
                resp = medocResponse(msg)
            if config.debug:
                # print("Received: ")
                # print(resp)
                if (resp.command == 0):
                    print("Polling while " + resp.teststatestr)
                else:
                # if (resp.command != 0):
                    print("Attempting to " + id_to_command[resp.command] + " while status: " + resp.teststatestr + ". " + resp.respstr)
            # if (resp.command == 1 and resp.teststatestr == 'IDLE'):
            #     s.close()
            #     el.wait_for_seconds(config.timedelayformedoc)
            #     pass
            # else:
            s.close()           # 
            return resp         # Replaced this break with a return so I can access the response
        except ConnectionResetError:
            print("==> ConnectionResetError")
            attemps += 1
            s.close()
            sendCommand(0) # This bizarrely wakes it up again for some reason.
            # s.close()
            # el.wait_for_seconds(config.timedelayformedoc)
            # sleep(0.5)
            pass
        el.wait_for_seconds(config.timedelayformedoc)
        # sleep(0.1)         #
        # removed return statement because it is prematurely instantiated.

def poll_for_change(desired_value,poll_interval=config.timedelayformedoc,poll_max=20,verbose=False,server_lag=1.,reuse_socket=False):
    """
    Poll system for a value change. Useful for waiting until the Medoc system has transitioned to a specific state in order to issue another command, but the transition length is unknowable.

    Args:
        to_watch (str): the response field we should be monitoring; most often 'test_state' or 'pathway_state'
        desired_value (str): the desired value of the field to wait on, i.e. keep checking until response_field has this value
        poll_interval (float): how often to poll; default .5s
        poll_max (int): upper limit on polling attempts; default -1 (unlimited)
        verbose (bool): print poll attempt number and current state
        server_lag (float): sometimes if the socket connection is pinged too quickly after a value change the subsequent command after this method is called can get missed. This adds an additional layer of timing delay before returning from this method to prevent this; default 1s
        reuse_socket (bool): try to reuse the last created socket connection; *NOT CURRENTLY FUNCTIONAL*

    Returns:
        status (bool): whether desired_value was achieved

    """
    val = ''
    count = 1
    while val != desired_value:
        if verbose:
            print(("Poll: {}".format(str(count))))
        response = sendCommand('GET_STATUS')
        if response.teststatestr:
            val = response.teststatestr
        else:
            val = 'RESPONSE_FORMAT_ERROR'
        if verbose:
            print(("Current value: {}".format(val)))
        sleep(poll_interval)
        count += 1
        if poll_max > 0 and count > poll_max:
            print("Polling limit exceeded")
            return False
    sleep(server_lag)
    return True

# printout:
class medocResponse():
    """
    A container to interpret and store the output response.
    """
    # decoding the bytes we receive:
    def __init__(self, response):
        self.length = struct.unpack_from('H', response[0:4])[0]
        self.timestamp = intFromBytes(response[4:8])
        self.datetime = datetime.fromtimestamp(self.timestamp)
        self.strtime = self.datetime.strftime("%Y-%m-%d %H:%M:%S")
        self.command = intFromBytes(response[8:9])
        self.state = intFromBytes(response[9:10])
        self.teststate = intFromBytes(response[10:11])
        # see if we have a documented state for this response:
        if self.state in states:
            self.statestr = states[self.state]
        else:
            self.statestr = 'unknown state code'
            self.teststate = intFromBytes(response[10:11])
            # see if we have a documented test state for this response:
        if self.teststate in test_states:
            self.teststatestr = test_states[self.teststate]
        else:
            self.teststatestr = 'unknown test state code'
        
        self.respcode = struct.unpack_from('H', response[11:13])[0]
        if self.respcode in response_codes:
            self.respstr = response_codes[self.respcode]
        else:
            self.respstr = "unknown response code"
        
        # the test time is in seconds once divided by 1000:
        self.testtime = struct.unpack_from('I', response[13:17])[0] / 1000.
        # the temperature is in °C once divided by 100:
        self.temp = struct.unpack_from('h', response[17:19])[0] / 100.
        self.CoVAS = intFromBytes(response[19:20])
        self.yes = intFromBytes(response[20:21])
        self.no = intFromBytes(response[21:22])
        self.message = response[22:self.length]
        # store the whole response
        self.response = response
    def __repr__(self):
        msg = ""
        msg += f"timestamp : {self.strtime}\n"
        msg += f"command : {id_to_command[self.command]}\n"
        msg += f"state : {self.statestr}\n"
        msg += f"test state : {self.teststatestr}\n"
        msg += f"response code : {self.respstr}\n"
        msg += f"temperature : {self.temp}°C\n"
        if self.statestr == "TEST IN PROGRESS":
            msg += f"test time : {self.testtime} seconds\n"
        elif self.respstr != "OK":
            msg += f"sup. message : {self.message}\n"
        if self.yes:
            msg += "~~ also: yes was pressed! ~~\n"
        if self.no:
            msg += "~~ also: no was pressed! ~~\n"
        return msg
    def __str__(self):
        return self.__repr__()
    def __getitem__(self, s):
        return self.response[s]


if __name__ == "__main__":
    sendCommand('select_tp', config.vas_search_program)
    sleep(15)
    sendCommand('vas', 4) # Set pain rating 4
    sleep(3)
    sendCommand('t_down', 500) # Step 5 degrees down
    sleep(10)
    sendCommand('vas', 7) # Set pain rating 7
    sleep(3)
    sendCommand('t_up', 500) # Step 5 degrees up
    sleep(10)
    sendCommand('vas', 10) # Set pain rating 10
    sleep(3)
    sendCommand('stop')

    # Aggressive Methods
    # def send_and_poll(command="", parameter=""):
    #     if command in {}:
    #         poll_for_change(desired_value, poll_max=3)
    #         response = sendCommand(command)
    #         if response.teststatestr == ''
