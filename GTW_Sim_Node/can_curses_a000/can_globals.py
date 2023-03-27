
class CanCurses_A000_GTW():

    global_info = {'transport_proto': 'PROTO', 'driver': 'DRIVER', 'dbc': 'DBC', 'channel': 0, 'baud_rate': 500000, 'allow_virt': False}

    com_port = 0
    bus_load = {'value': 0.0, 'min': 0.0, 'max': 0.0}

    #{'XXX_sig': {'frame_id': 0x7FF, 'name': 'XXX_sig', 'value': 0.0, 'min': 0.0, 'max': 0.0},...}
    rx_signal_info = {}

    #{0x7FF: [0xFF,...],...}
    rx_frame_info = {}

    #{0x7FF: {'name': 'XXX_frame', 'frame_id': 0x7FF, 'cycle_time': 0.0, 'is_resolved': False, 'sig_payload': {{'XXX_sig': 0.0},...}, 'byte_payload': [0xFF,...], 'display_frame': True, 'display_sigs': ['XXX_sig',...]},...}
    tx_frame_info = {}

    #{'synch_seq_id': 0},...} - synch_seq_state: 0x0 = complete ok, 0x1 = complete nok, 0x2 = request seq, 0x3 = running
    synch_seq_info = {}

    run_random_sim = False
