
import os
import sys
import asyncio

from curses import wrapper

from can_curses_a000 import CanCurses_A000_GTW, CanConfig, TransportBus, CanDbcParser, CanTransmitFrame, CanReceiveSignals, SynchronousSequence, CursesDisplay

cc = CanCurses_A000_GTW()

cg = CanConfig(cc, sys, os)

can = TransportBus(cc)

cd = CanDbcParser(cc.global_info['dbc'])


async def async_init_rx():
    sig_dict = {}
    sig_dict.update({'MCU_elevation': {'frame_id': 0x68, 'name': 'MCU_elevation', 'value': 0, 'min': 0, 'max': 0}})
    sig_dict.update({'MCU_navigonExpectedSpeed': {'frame_id': 0x68, 'name': 'MCU_navigonExpectedSpeed', 'value': 0, 'min': 0, 'max': 0}})
    frame_list = []
    frame_list.append(0x3)
    frame_list.append(0x6D)
    cr = CanReceiveSignals(sig_dict, frame_list, 10, cc, cd, sys)
    await asyncio.sleep(0.001)


async def async_init_tx():
    frame_dict = {}
    frame_dict.update({0x318: {'name': 'GTW_carState', 'cycle_time_ms': 2500, 'display_frame': True, 'display_sigs': ['GTW_updateInProgress','MCU_factoryMode','MCU_transportModeOn','BC_headLightLStatus']}})
    frame_dict.update({0x238: {'name': 'UI_driverAssistRoadSign', 'cycle_time_ms': 1000, 'display_frame': True, 'display_sigs': ['UI_roadSign','UI_roadSignCounter','UI_splineLocConfidence','UI_stopSignStopLineDist','UI_trafficLightStopLineDist','UI_topQrtlFleetSpeedMPS','UI_meanFleetSplineSpeedMPS','UI_currSplineIdFull']}})
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


