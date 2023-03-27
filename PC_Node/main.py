
import os
import sys
import asyncio

from curses import wrapper

from can_curses_a000 import CanCurses_A000_PC, CanConfig, TransportBus, CanDbcParser, CanTransmitFrame, CanReceiveSignals, SynchronousSequence, CursesDisplay

cc = CanCurses_A000_PC()

cg = CanConfig(cc, sys, os)

can = TransportBus(cc)

cd = CanDbcParser(cc.global_info['dbc'])


async def async_init_rx():
    sig_dict = {}
    sig_dict.update({'UI_roadSign': {'frame_id': 0x238, 'name': 'UI_roadSign', 'value': 0, 'min': 0, 'max': 0}})
    sig_dict.update({'UI_roadSignCounter': {'frame_id': 0x238, 'name': 'UI_roadSignCounter', 'value': 0, 'min': 0, 'max': 0}})
    sig_dict.update({'UI_splineLocConfidence': {'frame_id': 0x238, 'name': 'UI_splineLocConfidence', 'value': 0, 'min': 0, 'max': 0}})
    sig_dict.update({'UI_stopSignStopLineDist': {'frame_id': 0x238, 'name': 'UI_stopSignStopLineDist', 'value': 0, 'min': 0, 'max': 0}})
    sig_dict.update({'UI_trafficLightStopLineDist': {'frame_id': 0x238, 'name': 'UI_trafficLightStopLineDist', 'value': 0, 'min': 0, 'max': 0}})
    sig_dict.update({'UI_trafficLightStopLineDist': {'frame_id': 0x238, 'name': 'UI_trafficLightStopLineDist', 'value': 0, 'min': 0, 'max': 0}})
    sig_dict.update({'UI_topQrtlFleetSpeedMPS': {'frame_id': 0x238, 'name': 'UI_topQrtlFleetSpeedMPS', 'value': 0, 'min': 0, 'max': 0}})
    sig_dict.update({'UI_meanFleetSplineSpeedMPS': {'frame_id': 0x238, 'name': 'UI_meanFleetSplineSpeedMPS', 'value': 0, 'min': 0, 'max': 0}})
    sig_dict.update({'UI_currSplineIdFull': {'frame_id': 0x238, 'name': 'UI_currSplineIdFull', 'value': 0, 'min': 0, 'max': 0}})
    sig_dict.update({'GTW_updateInProgress': {'frame_id': 0x318, 'name': 'GTW_updateInProgress', 'value': 0, 'min': 0, 'max': 0}})
    sig_dict.update({'MCU_factoryMode': {'frame_id': 0x318, 'name': 'MCU_factoryMode', 'value': 0, 'min': 0, 'max': 0}})
    sig_dict.update({'MCU_transportModeOn': {'frame_id': 0x318, 'name': 'MCU_transportModeOn', 'value': 0, 'min': 0, 'max': 0}})
    sig_dict.update({'BC_headLightLStatus': {'frame_id': 0x318, 'name': 'BC_headLightLStatus', 'value': 0, 'min': 0, 'max': 0}})
    frame_list = []
    cr = CanReceiveSignals(sig_dict, frame_list, 10, cc, cd, sys)
    await asyncio.sleep(0.001)


async def async_init_tx():
    frame_dict = {}
    frame_dict.update({0x3: {'name': 'NEO_noExist1', 'cycle_time_ms': 1000, 'display_frame': True, 'display_sigs': []}})
    frame_dict.update({0x6D: {'name': 'NEO_noExist2', 'cycle_time_ms': 1000, 'display_frame': True, 'display_sigs': []}})
    frame_dict.update({0x68: {'name': 'MCU_locationStatus2', 'cycle_time_ms': 1000, 'display_frame': True, 'display_sigs': ['MCU_elevation','MCU_navigonExpectedSpeed']}})
    ct = CanTransmitFrame(frame_dict, cc, cd)
    await asyncio.sleep(0.001)


async def async_init_synch_seq_0():
    cs_s = SynchronousSequence(50, 0, cc, cd, 0)
    await asyncio.sleep(0.001)

async def async_init_synch_seq_1():
    cs_d = SynchronousSequence(50, 0, cc, cd, 1)
    await asyncio.sleep(0.001)

async def async_init_synch_seq_2():
    cs_d = SynchronousSequence(0, 50, cc, cd, 1)
    await asyncio.sleep(0.001)


async def async_init_display(stdscr):
    cu = CursesDisplay(stdscr, 17, cc, cd)
    await asyncio.sleep(0.001)


def main(stdscr) -> None:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(async_init_rx())
        loop.create_task(async_init_tx())
        loop.create_task(async_init_synch_seq_0())
        loop.create_task(async_init_synch_seq_1())
        loop.create_task(async_init_synch_seq_2())
        loop.create_task(async_init_display(stdscr))
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(loop.shutdown_asyncgens())
        print(" SIGINT! Exiting...")

if __name__ == "__main__":
    wrapper(main)


