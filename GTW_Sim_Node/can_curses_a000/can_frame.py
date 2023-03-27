
import asyncio
from canlib import canlib, Frame

from .can_timers import IntervalTimer

class CanTransmitFrame:

    _frame_info = {}

    def __init__(self, frame_dict, can_globals, can_dbc) -> None:

        #
        self._mux_lim = {}
        #
        if len(frame_dict) != 0:
            #
            for key in frame_dict:
                #
                self._frame_info.update({key: {}})
                #
                self._frame_info[key].update({'name': frame_dict[key]['name']})
                self._frame_info[key].update({'frame_id': key})
                self._frame_info[key].update({'cycle_time': 0.0})
                self._frame_info[key].update({'is_resolved': False})
                self._frame_info[key].update({'sig_payload': {}})
                self._frame_info[key].update({'byte_payload': []})
                self._frame_info[key].update({'display_frame': frame_dict[key]['display_frame']})
                self._frame_info[key].update({'display_sigs': []})
                #
                #
                #
                self._frame_info[key]['is_resolved'] = can_dbc.CheckDbcForFrame(key, frame_dict[key]['name'])

                if self._frame_info[key]['is_resolved'] == True:

                    self._frame_info[key].update({'display_sigs': frame_dict[key]['display_sigs']})
        
                    self._mux_lim.update({key: can_dbc.GetFrameMuxLimit(key)})

                    if can_dbc.GetFrameCycleTimeMs(key) == 0:
                        self._frame_info[key]['cycle_time'] = (frame_dict[key]['cycle_time_ms'] / 1000)
                    else:
                        self.frame_info[key]['cycle_time'] = (can_dbc.GetFrameCycleTimeMs(key) / 1000)


                    for i in range(len(can_dbc.ListSignalsByFrame(key))):
                        self._frame_info[key]['sig_payload'].update({can_dbc.ListSignalsByFrame(key)[i]: 0})

                else:
                    self._frame_info[key]['cycle_time'] = (frame_dict[key]['cycle_time_ms'] / 1000)
                    for i in range(8):
                        self._frame_info[key]['byte_payload'].append(0x0)
                #
            #
            #push to globals
            for key in self._frame_info:
                can_globals.tx_frame_info.update({key: self._frame_info[key]})
            #
        #
        #timers
        self._timer_238h = IntervalTimer(interval=self._frame_info[0x238]['cycle_time'], first_immediately=True, timer_name="Can_Tx_Object_Timer_0x238", context={'globals': can_globals, 'dbc': can_dbc}, callback=self.callback_238h)
        self._timer_318h = IntervalTimer(interval=self._frame_info[0x318]['cycle_time'], first_immediately=True, timer_name="Can_Tx_Object_Timer_0x318", context={'globals': can_globals, 'dbc': can_dbc}, callback=self.callback_318h)
        #


    def update_238h(self, can_globals, can_dbc) -> None:

        self._frame_info[0x238].update({'sig_payload': can_globals.tx_frame_info[0x238]['sig_payload']})
        self._frame_info[0x238].update({'byte_payload': can_globals.tx_frame_info[0x238]['byte_payload']})

        if self._frame_info[0x238]['is_resolved'] == True and can_dbc.GetFrameIsMuxed(0x238) == True:
            mux_sig = 'UI_roadSign'
            mux_val = self._frame_info[0x238]['sig_payload'][mux_sig]
            mux_val += 1
            if mux_val > self._mux_lim[0x238]:
                mux_val = 0
            cnt_sig = 'UI_roadSignCounter'
            cnt_val = self._frame_info[0x238]['sig_payload'][cnt_sig]
            cnt_val += 1
            if cnt_val > (pow(2, can_dbc.GetSignalLength(cnt_sig)) - 1):
                cnt_val = 0
            self._frame_info[0x238]['sig_payload'].update({mux_sig: mux_val})
            self._frame_info[0x238]['sig_payload'].update({cnt_sig: cnt_val})

        for signal in can_dbc.ListSignalsByFrame(0x238):

            if self._frame_info[0x238]['sig_payload'][signal] > can_dbc.GetSignalMaximum(signal):
                self._frame_info[0x238]['sig_payload'].update({signal: can_dbc.GetSignalMaximum(signal)})

            if self._frame_info[0x238]['sig_payload'][signal] < can_dbc.GetSignalMinimum(signal):
                self._frame_info[0x238]['sig_payload'].update({signal: can_dbc.GetSignalMinimum(signal)})

        can_globals.tx_frame_info.update({0x238: self._frame_info[0x238]})

    def update_318h(self, can_globals, can_dbc) -> None:

        self._frame_info[0x318].update({'sig_payload': can_globals.tx_frame_info[0x318]['sig_payload']})
        self._frame_info[0x318].update({'byte_payload': can_globals.tx_frame_info[0x318]['byte_payload']})

        for signal in can_dbc.ListSignalsByFrame(0x318):

            if self._frame_info[0x318]['sig_payload'][signal] > can_dbc.GetSignalMaximum(signal):
                self._frame_info[0x318]['sig_payload'].update({signal: can_dbc.GetSignalMaximum(signal)})

            if self._frame_info[0x318]['sig_payload'][signal] < can_dbc.GetSignalMinimum(signal):
                self._frame_info[0x318]['sig_payload'].update({signal: can_dbc.GetSignalMinimum(signal)})

        can_globals.tx_frame_info.update({0x318: self._frame_info[0x318]})


    def send_238h(self, can_globals, can_dbc) -> None:

        if self._frame_info[0x238]['is_resolved'] == True:

            #
            this_sig_name = can_dbc.GetMuxSignalName(0x238)
            mux_val = self._frame_info[0x238]['sig_payload'][this_sig_name]
            #
            payload = {}
            payload.update({this_sig_name: mux_val})
            #
            if mux_val == 0:
                this_sig_name = 'UI_dummyData'
                payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
            if mux_val == 1:
                this_sig_name = 'UI_stopSignStopLineDist'
                payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
                this_sig_name = 'UI_stopSignStopLineConf'
                payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
            if mux_val == 2:
                this_sig_name = 'UI_trafficLightStopLineDist'
                payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
                this_sig_name = 'UI_trafficLightStopLineConf'
                payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
            if mux_val == 3:
                this_sig_name = 'UI_baseMapSpeedLimitMPS'
                payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
                this_sig_name = 'UI_bottomQrtlFleetSpeedMPS'
                payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
                this_sig_name = 'UI_topQrtlFleetSpeedMPS'
                payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
            if mux_val == 4:
                this_sig_name = 'UI_meanFleetSplineSpeedMPS'
                payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
                this_sig_name = 'UI_medianFleetSpeedMPS'
                payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
                this_sig_name = 'UI_meanFleetSplineAccelMPS2'
                payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
                this_sig_name = 'UI_rampType'
                payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
            if mux_val == 5:
                this_sig_name = 'UI_currSplineIdFull'
                payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
            
            #
            this_sig_name = 'UI_splineLocConfidence'
            payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
            this_sig_name = 'UI_splineID'
            payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
            this_sig_name = 'UI_roadSignCounter'
            payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
            this_sig_name = 'UI_roadSignChecksum'
            payload.update({this_sig_name: self._frame_info[0x238]['sig_payload'][this_sig_name]})
            #
            #
            #
            #
            #
            #

            encoded_tx_payload = can_dbc._db.encode_message(0x238, payload, strict=False)

        else:

            encoded_tx_payload = bytearray(self._frame_info[0x238]['byte_payload'])

        tx_frame = Frame(id_=0x238, data=encoded_tx_payload, flags=canlib.MessageFlag.STD)

        can_globals.com_port.write(tx_frame)

    def send_318h(self, can_globals, can_dbc) -> None:

        if self._frame_info[0x318]['is_resolved'] == True:

            encoded_tx_payload = can_dbc._db.encode_message(0x318, self._frame_info[0x318]['sig_payload'], strict=False)

        else:

            encoded_tx_payload = bytearray(self._frame_info[0x318]['byte_payload'])

        tx_frame = Frame(id_=0x318, data=encoded_tx_payload, flags=canlib.MessageFlag.STD)

        can_globals.com_port.write(tx_frame)


    async def callback_238h(self, timer_name, context, timer) -> None:
        await asyncio.sleep(0.001)
        self.update_238h(context['globals'], context['dbc'])
        self.send_238h(context['globals'], context['dbc'])

    async def callback_318h(self, timer_name, context, timer) -> None:
        await asyncio.sleep(0.001)
        self.update_318h(context['globals'], context['dbc'])
        self.send_318h(context['globals'], context['dbc'])


class CanReceiveSignals:

    #{'XXX_sig': {'frame_id': 0x7FF, 'name': 'XXX_sig', 'value': 0.0, 'min': 0.0, 'max': 0.0},...}
    _signal_info = {}

    #{0x7FF: [0xFF,...],...}
    _frame_info = {}

    def __init__(self, signal_dict, frame_list, cycle_time_ms, can_globals, can_dbc, sys) -> None:

        try:

            for key, value in signal_dict.items():

                if can_dbc.CheckDbcForSignal(value['frame_id'], value['name']) == True:

                    self._signal_info.update({key: value})

                    if value['value'] > can_dbc.GetSignalMaximum(key):
                        self._signal_info[key].update({'value': can_dbc.GetSignalMaximum(key)})

                    if value['value'] < can_dbc.GetSignalMinimum(key):
                        self._signal_info[key].update({'value': can_dbc.GetSignalMinimum(key)})

                else:
                    print("invalid rx signal! exiting...")
                    sys.exit(1)

        except:
            print("invalid rx signal! exiting...")
            sys.exit(1)

        for key, value in self._signal_info.items():
            can_globals.rx_signal_info.update({key: value})
        
        for key in frame_list:
            self._frame_info.update({key: []})
            for i in range(8):
                self._frame_info[key].append(0xFF)

        for key, value in self._frame_info.items():
            can_globals.rx_frame_info.update({key: value})

        self._timer = IntervalTimer(interval=(cycle_time_ms / 1000), first_immediately=True, timer_name="Can_Rx_Object_Timer", context={'globals': can_globals, 'dbc': can_dbc}, callback=self.callback)

    def update(self, can_globals, can_dbc) -> None:

        can_globals.bus_load.update({'value': (can_globals.com_port.get_bus_statistics().busLoad / 100)})
        if can_globals.bus_load['value'] > can_globals.bus_load['max']:
            can_globals.bus_load.update({'max': can_globals.bus_load['value']})
        if can_globals.bus_load['value'] < can_globals.bus_load['min']:
            can_globals.bus_load.update({'min': can_globals.bus_load['value']})

        try:

            rx_can = can_globals.com_port.read(timeout=int(1))
            rx_id = rx_can.id
            rx_data = rx_can.data

            #for id in global.frame_info
            for key in can_globals.rx_frame_info:
                #
                #if rx_can.id matches
                if key == rx_id:
                    #
                    #save payload to globals
                    for i in range(8):
                        can_globals.rx_frame_info[key][i] = rx_can.data[i]
                    #
                #
            #

            try:

                rx_data = can_dbc._db.decode_message(rx_can.id, rx_can.data, decode_choices=False)

                for key, value in rx_data.items():
                    found = False
                    for signal in self._signal_info:
                        if found == False:
                            if key == signal:
                                self._signal_info[key].update({'value': value})
                                found = True

                for key, value in self._signal_info.items():
                    if value['value'] > can_dbc.GetSignalMaximum(key):
                        value['value'] = can_dbc.GetSignalMaximum(key)
                    if value['value'] < can_dbc.GetSignalMinimum(key):
                        value['value'] = can_dbc.GetSignalMinimum(key)
                    if value['value'] > value['max']:
                        value['max'] = value['value']
                    if value['value'] < value['min']:
                        value['min'] = value['value']

            except Exception:
                return

        except Exception as e:
            return

        for key, value in self._signal_info.items():
            can_globals.rx_signal_info.update({key: value})

    async def callback(self, timer_name, context, timer) -> None:
        await asyncio.sleep(0.001)
        self.update(context['globals'], context['dbc'])


