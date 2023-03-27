import cantools
import sys

mdf_path = "00000219.MF4"
dbc_path = "/home/mint/Documents/pycangui/Test/VsCode/Model3CAN.dbc"
#dbc_path = "/home/mint/Documents/pycangui/Test/VsCode/tesla_powertrain.dbc"
dbc_path = "./GTW_Sim_Node/tesla_can.dbc"



db = cantools.database.load_file(dbc_path)
#example_message = db.get_message_by_name('ID016DI_bmsRequest')
#example_message = db.get_message_by_frame_id(0x16)
#print(example_message.frame_id)
#print(example_message.name)
#print(example_message.signal_tree[0])
#for message in db.messages:
#    print(f"{hex(message.frame_id)} {message.name}")
#reqmessage = db.get_message_by_frame_id(0x16)
#somesigs = reqmessage.signals
#for i in range (len(somesigs)):
#    print(f"{somesigs[i].name} {somesigs[i].start} {somesigs[i].length} {somesigs[i].scale} {somesigs[i].offset}")
'''
for message in db.messages:
    try:
        cycletime = message.dbc.attributes['GenMsgCycleTime'].value
    except:
        cycletime = 0
    print(f"{hex(message.frame_id)} {message.name} {cycletime} {message.senders} {message.receivers}")
    somesigs = message.signals
    for i in range (len(somesigs)):
        print(f"    {somesigs[i].name} {somesigs[i].start} {somesigs[i].length} {somesigs[i].scale} {somesigs[i].offset} {somesigs[i].minimum} {somesigs[i].maximum} {somesigs[i].unit}")
'''
'''
for message in db.messages:
    print(f"{hex(message.frame_id)} : {message.name}, Tx nodes: {message.senders}, Rx nodes: {message.receivers}")
    j = 0
    for i in message.senders:
        if i == 'GTW':
            print(f"{hex(message.frame_id)} : {message.name}, Tx nodes: {message.senders}, Rx nodes: {message.receivers}", end='')
            j = 1
    for signal in message.signals:
        if signal.is_multiplexer == True:
            print(f" - is muxed!", end='')
            j = 1
    if j > 0:
        print()
'''
        
a = db.get_message_by_name('UI_autopilotControl')
a = db.get_message_by_name('GTW_carState')
a = db.get_message_by_name('MCU_locationStatus2')
#a = db.get_message_by_name('UI_driverAssistRoadSign')

for somesigs in a.signals:
    print(f"{somesigs.name} {somesigs.is_multiplexer} {somesigs.multiplexer_ids} {somesigs.start} {somesigs.length} {somesigs.scale} {somesigs.offset} {somesigs.minimum} {somesigs.maximum} {somesigs.unit}")

sys.exit(0)

#tx/rx nodes
for message in db.messages:
    try:
        cycletime = message.dbc.attributes['GenMsgCycleTime'].value
    except:
        cycletime = 0
    print(f"{hex(message.frame_id)} {message.name} {cycletime} {message.senders} {message.receivers}")
    for rx in message.receivers:
        print(rx)
print()

#multiplexed signals
mux_frame = db.get_message_by_frame_id(0x256)
try:
    cycletime = mux_frame.dbc.attributes['GenMsgCycleTime'].value
except:
    cycletime = 0
print(f"{hex(mux_frame.frame_id)} {mux_frame.name} {cycletime} {mux_frame.senders} {mux_frame.receivers}")
somesigs = mux_frame.signals
for i in range (len(somesigs)):
    print(f"    {somesigs[i].name} {somesigs[i].multiplexer_ids} {somesigs[i].start} {somesigs[i].length} {somesigs[i].scale} {somesigs[i].offset} {somesigs[i].minimum} {somesigs[i].maximum} {somesigs[i].unit}")
mux_frame = db.get_message_by_frame_id(0x2bf)
try:
    cycletime = mux_frame.dbc.attributes['GenMsgCycleTime'].value
except:
    cycletime = 0
print(f"{hex(mux_frame.frame_id)} {mux_frame.name} {mux_frame.length} {cycletime} {mux_frame.senders} {mux_frame.receivers}")
somesigs = mux_frame.signals
for i in range (len(somesigs)):
    print(f"    {somesigs[i].name} {somesigs[i].is_multiplexer} {somesigs[i].multiplexer_ids} {somesigs[i].start} {somesigs[i].length} {somesigs[i].scale} {somesigs[i].offset} {somesigs[i].minimum} {somesigs[i].maximum} {somesigs[i].unit}")
    if i==1:
        print(somesigs[i].choices)
#mux_sig = db.get_message_by_name(mux_frame.signals[0].name)
#mux_sig = db
