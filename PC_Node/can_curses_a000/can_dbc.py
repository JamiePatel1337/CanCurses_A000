
import cantools

class CanDbcParser:

    #{{0x7FF: {'name': 'XXX_frame', 'frame_id': 0x7FF, 'dlc': 8, 'cycle_time_ms': 0, 'is_muxed': False, 'transmitter': 'ECU_XXX', 'receivers': [], 'sig_info': {{'XXX_sig': {'name': 'XXX_sig', 'startbit': 0, 'length': 1, 'factor': 0.1, 'offset': 0.0, 'minimum': 0.0, 'maximum': 0.1, 'unit': '[1]', 'is_mux': False, 'mux_id': 0}},...}}},...}
    dbc_info = {}

    def __init__(self, dbc_path) -> None:
        
        self._db = cantools.database.load_file(dbc_path)
        self._frame_is_muxed = 0
        self._sig_frames = {}

        for message in self._db.messages:

            frame_info = {}
            sig_info = {}

            #{'name': 'XXX_sig', 'startbit': 0, 'length': 1, 'factor': 0.1, 'offset': 0.0, 'minimum': 0.0, 'maximum': 0.1, 'unit': '[1]', 'is_mux': False, 'mux_id': 0, 'receiver': 'ECU_XXX'}
            signals = message.signals
            for signal in signals:

                sig_attr = {}

                sig_attr.update({'name': signal.name})

                sig_attr.update({'startbit': signal.start})
                sig_attr.update({'length': signal.length})

                sig_attr.update({'factor': signal.scale})
                sig_attr.update({'offset': signal.offset})

                if signal.minimum is not None:
                    sig_attr.update({'minimum': signal.minimum})
                else:
                    sig_attr.update({'minimum': signal.offset})
                if signal.maximum is not None:
                    sig_attr.update({'maximum': signal.maximum})
                else:
                    sig_attr.update({'maximum': (((pow(2, signal.length) - 1) * signal.scale) + signal.offset)})

                if signal.unit is not None:
                    sig_attr.update({'unit': signal.unit})
                else:
                    sig_attr.update({'unit': '[1]'})

                sig_attr.update({'is_mux': signal.is_multiplexer})
                if signal.is_multiplexer == True:
                    self._frame_is_muxed += 1
                if signal.multiplexer_ids is not None:
                    sig_attr.update({'mux_id': signal.multiplexer_ids[0]})
                else:
                    sig_attr.update({'mux_id': 0})

                sig_info.update({sig_attr['name']: sig_attr})

                self._sig_frames.update({signal.name: message.frame_id})


            #{{'name': 'XXX_frame', 'frame_id': 0x7FF, 'dlc': 8, 'cycle_time_ms': 0, 'is_muxed': False, 'transmitter': 'ECU_XXX', 'receivers': [], 'sig_info': {}},...}
            frame_info.update({'name': message.name})
            frame_info.update({'frame_id': message.frame_id})

            frame_info.update({'dlc': message.length})

            try:
                cycletime = message.dbc.attributes['GenMsgCycleTime'].value
            except:
                cycletime = 0
            frame_info.update({'cycle_time_ms': cycletime})

            if self._frame_is_muxed == 1:
                frame_info.update({'is_muxed': True})
            else:
                frame_info.update({'is_muxed': False})
            self._frame_is_muxed = 0

            frame_info.update({'transmitter': message.senders[0]})
            frame_info.update({'receivers': message.receivers})

            frame_info.update({'sig_info': sig_info})

            self.dbc_info.update({message.frame_id: frame_info})


    def CheckDbcForFrame(self, frame_id, name) -> bool:
        try:
            if name == self.dbc_info[frame_id]['name']:
                return True
            else:
                return False
        except:
            return False

    def GetFrameDlc(self, frame_id) -> int:
        return self.dbc_info[frame_id]['dlc']

    def GetFrameCycleTimeMs(self, frame_id) -> int:
        return self.dbc_info[frame_id]['cycle_time_ms']

    def GetFrameIsMuxed(self, frame_id) -> bool:
        return self.dbc_info[frame_id]['is_muxed']

    def GetFrameMuxLimit(self, frame_id) -> int:
        ret = 0
        if self.dbc_info[frame_id]['is_muxed'] == False:
            return 0
        for key in self.dbc_info[frame_id]['sig_info']:
            if self.dbc_info[frame_id]['sig_info'][key]['is_mux'] == False:
                if self.dbc_info[frame_id]['sig_info'][key]['mux_id'] > ret:
                    ret = self.dbc_info[frame_id]['sig_info'][key]['mux_id']
        return ret
    
    def GetMuxSignalName(self, frame_id) -> str:
        ret = ''
        if self.dbc_info[frame_id]['is_muxed'] == False:
            return ''
        for key, value in self.dbc_info[frame_id]['sig_info'].items():
            if value['is_mux'] == True:
                ret = value['name']
        return ret

    def ListSignalsByFrame(self, frame_id) -> list:
        ret = []
        for key, value in self.dbc_info[frame_id]['sig_info'].items():
            ret.append(key)
        return ret

    def GetFrameIdFromSignalName(self, name) -> int:
        ret = 0x800
        try:
            ret = self._sig_frames[name]
        except:
            pass
        return ret

    def CheckDbcForSignal(self, frame_id, name) -> bool:
        for key, value in self.dbc_info[frame_id]['sig_info'].items():
            if name == key:
                return True
        return False

    def GetSignalLength(self, name) -> int:
        for key, value in self.dbc_info.items():
            for skey, svalue in value['sig_info'].items():
                if name == skey:
                    return svalue['length']

    def GetSignalFactor(self, name) -> float:
        for key, value in self.dbc_info.items():
            for skey, svalue in value['sig_info'].items():
                if name == skey:
                    return svalue['factor']

    def GetSignalOffset(self, name) -> float:
        for key, value in self.dbc_info.items():
            for skey, svalue in value['sig_info'].items():
                if name == skey:
                    return svalue['offset']

    def GetSignalMinimum(self, name) -> float:
        for key, value in self.dbc_info.items():
            for skey, svalue in value['sig_info'].items():
                if name == skey:
                    return svalue['minimum']

    def GetSignalMaximum(self, name) -> float:
        for key, value in self.dbc_info.items():
            for skey, svalue in value['sig_info'].items():
                if name == skey:
                    return svalue['maximum']

    def GetSignalUnit(self, name) -> str:
        for key, value in self.dbc_info.items():
            for skey, svalue in value['sig_info'].items():
                if name == skey:
                    return svalue['unit']


