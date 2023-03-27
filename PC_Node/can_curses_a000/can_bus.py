
from canlib import canlib

class TransportBus():

    def __init__(self, can_globals) -> None:

        if can_globals.global_info['allow_virt'] == True:
            can_globals.com_port = canlib.openChannel(channel=can_globals.global_info['channel'], flags=canlib.canOPEN_ACCEPT_VIRTUAL)
        else:
            can_globals.com_port = canlib.openChannel(channel=can_globals.global_info['channel'])
        
        if can_globals.global_info['baud_rate'] == 1000000:
            can_globals.com_port.setBusParams(canlib.canBITRATE_1M)
        elif can_globals.global_info['baud_rate'] == 250000:
            can_globals.com_port.setBusParams(canlib.canBITRATE_250K)
        elif can_globals.global_info['baud_rate'] == 125000:
            can_globals.com_port.setBusParams(canlib.canBITRATE_125K)
        elif can_globals.global_info['baud_rate'] == 100000:
            can_globals.com_port.setBusParams(canlib.canBITRATE_100K)
        elif can_globals.global_info['baud_rate'] == 83000:
            can_globals.com_port.setBusParams(canlib.canBITRATE_83K)
        elif can_globals.global_info['baud_rate'] == 62000:
            can_globals.com_port.setBusParams(canlib.canBITRATE_62K)
        elif can_globals.global_info['baud_rate'] == 50000:
            can_globals.com_port.setBusParams(canlib.canBITRATE_50K)
        elif can_globals.global_info['baud_rate'] == 10000:
            can_globals.com_port.setBusParams(canlib.canBITRATE_10K)
        else:
            can_globals.com_port.setBusParams(canlib.canBITRATE_500K)
            can_globals.global_info['baud_rate'] = 500000
        
        if can_globals.global_info['channel'] < canlib.getNumberOfChannels():
            can_globals.com_port.busOn()


