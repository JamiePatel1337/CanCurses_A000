
import asyncio
import random

from .can_timers import OneShotTimer, IntervalTimer

class SynchronousSequence():

    #{{'synch_seq_id': 'XXX_id', 'synch_seq_state': 0},...}
    #synch_seq_state: 0x0 = complete ok, 0x1 = complete nok, 0x2 = request seq, 0x3 = running
    _seq_info = {}

    _global_callbacks = ['synch_seq_enable_state_on_key_s', 'synch_seq_standby_state_on_key_d']

    def __init__(self, cycle_time_ms, start_delay_ms, can_globals, can_dbc, index) -> None:

        self._index = int(index)
        self._seq_info.update({self._global_callbacks[self._index]: 0})

        can_globals.synch_seq_info.update({self._global_callbacks[self._index]: self._seq_info[self._global_callbacks[self._index]]})

        if start_delay_ms != 0:
            self._wait = OneShotTimer(timeout=(start_delay_ms / 1000), context={'globals': can_globals, 'dbc': can_dbc}, callback=self.start)
        else:
            self._wait = 0

        if cycle_time_ms != 0:
            self._timer = IntervalTimer(interval=(cycle_time_ms / 1000), first_immediately=True, timer_name='Synch_Seq_Timer', context={'globals': can_globals, 'dbc': can_dbc}, callback=self.callback)
        else:
            self._timer = 0

        random.seed()

    async def start(self, context) -> None:

        while True:
            #
            if context['globals'].run_random_sim == True:
                #
                for id in context['globals'].tx_frame_info:
                    if context['globals'].tx_frame_info[id]['is_resolved'] == True:
                        for signal in context['globals'].tx_frame_info[id]['display_sigs']:
                            if signal == 'MCU_elevation':
                                rd = int((random.randrange(pow(2, 30)))/10)
                            else:
                                rd = ((random.randrange(pow(2, context['dbc'].GetSignalLength(signal)))) * context['dbc'].GetSignalFactor(signal)) + context['dbc'].GetSignalOffset(signal)
                            if rd > context['dbc'].GetSignalMaximum(signal):
                                rd = context['dbc'].GetSignalMaximum(signal)
                            if rd < context['dbc'].GetSignalMinimum(signal):
                                rd = context['dbc'].GetSignalMinimum(signal)
                            context['globals'].tx_frame_info[id]['sig_payload'][signal] = rd
                    else:
                        for byte in range(8):
                            context['globals'].tx_frame_info[id]['byte_payload'][byte] = random.randrange(255)
                #
            #
            sleep_time = 10
            for key in context['globals'].tx_frame_info:
                cycle_time = context['globals'].tx_frame_info[key]['cycle_time']
                if cycle_time < sleep_time:
                    sleep_time = cycle_time
            await asyncio.sleep(sleep_time)

    async def synch_seq_enable_state_on_key_s(self, context) -> None:

        context['globals'].run_random_sim = True

        context['globals'].synch_seq_info.update({self._global_callbacks[0]: 0})

    async def synch_seq_standby_state_on_key_d(self, context) -> None:

        context['globals'].run_random_sim = False

        for id in context['globals'].tx_frame_info:
            for signal in context['globals'].tx_frame_info[id]['display_sigs']:
                if signal != 'UI_roadSignCounter' and signal != 'UI_roadSign':
                    rd = context['dbc'].GetSignalOffset(signal)
                    context['globals'].tx_frame_info[id]['sig_payload'][signal] = rd

        context['globals'].synch_seq_info.update({self._global_callbacks[1]: 0})

    async def callback(self, timer_name, context, timer) -> None:

        for key in context['globals'].synch_seq_info:
            self._seq_info.update({key: context['globals'].synch_seq_info[key]})

        if self._index == 0:
            if self._seq_info[self._global_callbacks[self._index]] == 2:
                self._seq_info.update({self._global_callbacks[self._index]: 3})
                for key, value in self._seq_info.items():
                    context['globals'].synch_seq_info.update({key: value})
                await self.synch_seq_enable_state_on_key_s(context)
        elif self._index == 1:
            if self._seq_info[self._global_callbacks[self._index]] == 2:
                self._seq_info.update({self._global_callbacks[self._index]: 3})
                for key, value in self._seq_info.items():
                    context['globals'].synch_seq_info.update({key: value})
                await self.synch_seq_standby_state_on_key_d(context)


