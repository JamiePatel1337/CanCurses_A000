
import json

class CanConfig():

    def __init__(self, can_globals, sys, os) -> None:
        #
        #parse args, if nok exit(1)
        if len(sys.argv) != 2 or type(sys.argv[1]).__name__ != 'str':
            print(f"Usage: CanCurses.py /path/to/cc_cfg.json")
            sys.exit(1)
        #
        #if config file exists and is json type
        if os.path.exists(sys.argv[1]) == False:
            print('config file does not exist!')
            sys.exit(1)
        name, ext =  os.path.splitext(sys.argv[1])
        if ext != '.json':
            print("invalid config file! exiting...")
            sys.exit(1)
        #
        #open cfg
        with open(sys.argv[1], 'r') as cfg_file:
            cfg = json.load(cfg_file)
            #
            #only CAN supported in a000
            if type(cfg['TRANSPORT']).__name__ != 'str' or cfg['TRANSPORT'] != 'CAN':
                print("invalid configuration! exiting...")
                sys.exit(1)
            #
            #only Kvaser supported in a000
            if type(cfg['CAN_DRIVER']).__name__ != 'str' or cfg['CAN_DRIVER'] != 'Kvaser':
                print("invalid configuration! exiting...")
                sys.exit(1)
            #
            #if dbc valid
            if type(cfg['DBC_FILE']).__name__ != 'str':
                print("invalid configuration! exiting...")
                sys.exit(1)
            if os.path.exists(cfg['DBC_FILE']) == False:
                print('dbc file does not exist!')
                sys.exit(1)
            name, ext =  os.path.splitext(cfg['DBC_FILE'])
            if ext != '.dbc':
                print("invalid dbc file! exiting...")
                sys.exit(1)
            #
            #if channel valid
            if type(cfg['CHANNEL']).__name__ != 'int':
                print("invalid configuration! exiting...")
                sys.exit(1)
            #
            #if baud rate valid
            if type(cfg['BITRATE']).__name__ != 'int':
                print("invalid configuration! exiting...")
                sys.exit(1)
            #
            #if allow_virtual valid
            if type(cfg['ACCEPT_VIRTUAL']).__name__ != 'bool':
                print("invalid configuration! exiting...")
                sys.exit(1)
            #
            #save all to globals
            can_globals.global_info.update({'transport_proto': cfg['TRANSPORT']})
            can_globals.global_info.update({'driver': cfg['CAN_DRIVER']})
            can_globals.global_info.update({'dbc': cfg['DBC_FILE']})
            can_globals.global_info.update({'channel': cfg['CHANNEL']})
            can_globals.global_info.update({'baud_rate': cfg['BITRATE']})
            can_globals.global_info.update({'allow_virt': cfg['ACCEPT_VIRTUAL']})
            #
        #
    #


