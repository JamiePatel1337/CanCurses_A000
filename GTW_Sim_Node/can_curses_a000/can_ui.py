
import asyncio
from abc import ABC, abstractmethod
from curses import ERR, KEY_RESIZE, curs_set
import _curses

from .can_timers import IntervalTimer

class Display(ABC):

    def __init__(self, stdscr: "_curses._CursesWindow", cycle_time_ms, can_globals, can_dbc) -> None:

        self._maxy = 0
        self._maxx = 0

        self._border_width = 1

        self._header_rows = 3
        self._mid_rows = 2
        self._footer_rows = 3

        self._top_margin = 1
        self._bottom_margin = 0
        self._left_margin = 1
        self._right_margin = -1

        self._value_start_col = 47
        self._start_col_spacing = 16

        self._print_static_header = []
        self._print_static_mid = []
        self._print_static_footer = []

        self._print_dynamic_header = []

        self._tx_rows = 0
        self._rx_rows = 0

        self._available_rows = 0
        self._available_columns = 0

        self._tx_list = []
        #[0x7FF, 'XXX_sig',...]
        self._print_list_tx = []
        #['XXX_sig',...]
        self._print_list_rx = []

        self._globals = can_globals
        self._dbc = can_dbc
        self._stdscr = stdscr
        self._stdscr.nodelay(True)
        self._stdscr.timeout(int(10))
        curs_set(0)

        self._timer = IntervalTimer(interval=(cycle_time_ms / 1000), first_immediately=True, timer_name='Curses_Timer', context={'globals': can_globals}, callback=self.callback)

        self.init_static_data()
        self.get_screen_size()

    @abstractmethod
    def init_static_data(self) -> None:
        pass

    @abstractmethod
    def get_screen_size(self) -> None:
        pass

    @abstractmethod
    def make_display(self) -> None:
        pass

    @abstractmethod
    def handle_char(self, char: int) -> None:
        pass

    async def callback(self, timer_name, context, timer) -> None:

        self.make_display()

        char = self._stdscr.getch()

        if char == ERR:
            await asyncio.sleep(0.01)
        elif char == KEY_RESIZE:
            self.get_screen_size()
        else:
            self.handle_char(char)

class CursesDisplay(Display):

    def init_static_data(self) -> None:

        self._stdscr.erase()
        self._stdscr.box()

        self._tx_rows = 0
        if len(self._globals.tx_frame_info) > 0:
            for key in self._globals.tx_frame_info:
                if self._globals.tx_frame_info[key]['display_frame'] == True:
                    if self._globals.tx_frame_info[key]['is_resolved'] == True:
                        for i in self._globals.tx_frame_info[key]['display_sigs']:
                            self._tx_list.append(i)
                            self._tx_rows += 1
                    else:
                        self._tx_list.append(key)
                        self._tx_rows += 1


        self._rx_rows = len(self._globals.rx_signal_info) + len(self._globals.rx_frame_info)

        #header rows
        self._print_static_header.append(f"________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________")
        #mid-page rows
        self._print_static_mid.append(f"________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________")
        self._print_static_mid.append("")
        #footer rows
        self._print_static_footer.append(f"________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________")
        self._print_static_footer.append(f"Start [s]                                                         Stop [d]")
        self._print_static_footer.append('')

    def get_screen_size(self) -> None:

        self._maxy, self._maxx = self._stdscr.getmaxyx()
        self._maxy -= 1
        self._maxx -= 2

        self._available_rows = self._maxy - (self._header_rows + self._top_margin + self._bottom_margin + (self._footer_rows - 1) + self._border_width)

        self._available_columns = self._maxx - (self._left_margin + self._right_margin + (self._border_width * 2))

        #
        #[0x7FF, 'XXX_sig',...]
        del self._print_list_tx [:]
        #['XXX_sig',...]
        del self._print_list_rx [:]
        #
        #if available rows > 0
        if self._available_rows > 0:
            #
            #if tx rows >= available rows
            if(self._tx_rows >= self._available_rows):
                #
                #if tx rows > 0
                if(self._tx_rows > 0):
                    #
                    #print all tx rows, up to max available rows
                    for i in self._tx_list[0:min(self._tx_rows, self._available_rows)]:
                        self._print_list_tx.append(i)
                    #
                #
            #
            #else tx rows < available rows
            else:
                #
                #if tx rows > 0
                if(self._tx_rows > 0):
                    #
                    #print all tx rows
                    for i in self._tx_list[0:self._tx_rows]:
                        self._print_list_tx.append(i)
                    #
                    #if tx rows + mid_rows <= available rows
                    if (self._tx_rows + self._mid_rows) <= self._available_rows:
                        #
                        #if tx rows + mid_rows + rx rows <= available rows
                        if (self._tx_rows + self._mid_rows + self._rx_rows) <= self._available_rows:
                            #
                            #print all rx rows
                            rx_rows = self._rx_rows
                            #
                        #else
                        else:
                            #
                            #print rx rows upto avail
                            rx_rows = min(self._rx_rows, self._available_rows - (self._tx_rows + self._mid_rows))
                            #
                        #
                        #get rows
                        for key in self._globals.rx_signal_info:
                            if rx_rows > 0:
                                self._print_list_rx.append(key)
                                rx_rows -= 1
                        for key in self._globals.rx_frame_info:
                            if rx_rows > 0:
                                self._print_list_rx.append(key)
                                rx_rows -= 1
                        #
                    #
                #
                #else tx rows = 0
                else:
                    #
                    #if rx rows > 0
                    if(self._rx_rows > 0):
                        #
                        #print rx rows upto avail
                        rx_rows = min(self._rx_rows, self._available_rows)
                        for key in self._globals.rx_signal_info:
                            if rx_rows > 0:
                                self._print_list_rx.append(key)
                                rx_rows -= 1
                        for key in self._globals.rx_frame_info:
                            if rx_rows > 0:
                                self._print_list_rx.append(key)
                                rx_rows -= 1
                            #
                        #
                    #
                #
            #
        #

    def print_row(self, y, x, fstr, flist, col) -> int:
        #helper fct - if reach end of available columns, stop printing and return 1
        #
        #if fstr is string
        if type(fstr).__name__ == 'str':
            #
            for char in fstr:
                #
                if col > 0:
                    #
                    self._stdscr.addstr(y, x, char)
                    #
                    x += 1
                    #
                    col -= 1
                    #
                else:
                    return 1
            #
            #
            #if flist is nonzero list
            if type(flist).__name__ == 'list' and len(flist) > 0:
                #
                for byte in flist:
                    #
                    self.print_row(y, x, f"0x{format(byte, '02X')}", [], col)
                    #
                    x += 5
                    #
                    col -= 5
                    #
                #
            #
        #
        return 0
        #

    def make_display(self) -> None:

        #
        loc_y = self._border_width
        loc_x = self._border_width + self._left_margin
        rows = self._available_rows
        cols = self._available_columns
        #erase, box
        self._stdscr.erase()
        self._stdscr.box()
        #
        #if available rows > 0
        if rows > 0:
            #
            #print dynamic header
            if self.print_row(loc_y, loc_x, f"{type(self._globals).__name__} - {self._globals.global_info['driver']} Ch.{self._globals.global_info['channel']}", [], cols) == 0:
                #
                loc_x = self._value_start_col
                cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                #
                if self.print_row(loc_y, loc_x, 'Val.', [], cols) == 0:
                    #
                    loc_x = self._value_start_col + self._start_col_spacing
                    cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                    #
                    if self.print_row(loc_y, loc_x, 'Max.', [], cols) == 0:
                        #
                        loc_x = self._value_start_col + (self._start_col_spacing * 2)
                        cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                        #
                        self.print_row(loc_y, loc_x, 'Min.', [], cols)
                    #
                #
            loc_x = self._border_width + self._left_margin
            cols = self._available_columns
            loc_y += 1
            if self.print_row(loc_y, loc_x, f"{self._globals.global_info['transport_proto']} @ {(self._globals.com_port.getBusParams()[0]/1000000):1.1f} Mbps - Bus Load:", [], cols) == 0:
                #
                loc_x = self._value_start_col
                cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                #
                if self.print_row(loc_y, loc_x, f"{self._globals.bus_load['value']:3.1f}", [], cols) == 0:
                    #
                    loc_x = self._value_start_col + self._start_col_spacing
                    cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                    #
                    if self.print_row(loc_y, loc_x, f"{self._globals.bus_load['max']:3.1f}", [], cols) == 0:
                        #
                        loc_x = self._value_start_col + (self._start_col_spacing * 2)
                        cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                        #
                        self.print_row(loc_y, loc_x, f"{self._globals.bus_load['min']:3.1f}", [], cols)
                    #
                #
            loc_x = self._border_width + self._left_margin
            cols = self._available_columns
            loc_y += 1
            #
            #print static header
            for i in range(len(self._print_static_header)):
                self.print_row(loc_y, loc_x, self._print_static_header[i], [], cols)
                loc_x = self._border_width + self._left_margin
                cols = self._available_columns
                loc_y += 1
            #
            #skip top margin
            loc_y += self._top_margin
            #
            #
            #
            #if tx rows >= available rows
            if(self._tx_rows >= rows):
                #
                #if tx rows > 0
                if(self._tx_rows > 0):
                    #
                    #print tx list
                    for id in self._print_list_tx:
                        #
                        #if type is str
                        if type(id).__name__ == 'str':
                            #
                            #print signals
                            frame_id = self._dbc.GetFrameIdFromSignalName(id)
                            if self.print_row(loc_y, loc_x, f"0x{format(frame_id, '02X')} : Tx : {id}", [], cols) == 0:
                                #
                                loc_x = self._value_start_col
                                cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                                #
                                #if float
                                if type(self._globals.tx_frame_info[frame_id]['sig_payload'][id]).__name__ == 'float':
                                    #
                                    #write value 1.3f
                                    self.print_row(loc_y, loc_x, f"{self._globals.tx_frame_info[frame_id]['sig_payload'][id]:1.3f}", [], cols)
                                #else if int
                                elif type(self._globals.tx_frame_info[frame_id]['sig_payload'][id]).__name__ == 'int':
                                    #write value
                                    self.print_row(loc_y, loc_x, f"{self._globals.tx_frame_info[frame_id]['sig_payload'][id]}", [], cols)
                                #
                                #
                                loc_x = self._border_width + self._left_margin
                                cols = self._available_columns
                                #
                                loc_y += 1
                                rows -= 1
                                #
                            #
                        #
                        #else if type is int
                        elif type(id).__name__ == 'int':
                            #
                            #print frame + bytes
                            self.print_row(loc_y, loc_x, f"0x{format(id, '02X')} : Tx : ", self._globals.tx_frame_info[id]['byte_payload'], cols)
                            #
                            loc_x = self._border_width + self._left_margin
                            cols = self._available_columns
                            #
                            loc_y += 1
                            rows -= 1
                            #
                        #
                    #
                #
            #
            #else tx rows < available rows
            else:
                #
                #if tx rows > 0
                if(self._tx_rows > 0):
                    #
                    #print tx list
                    for id in self._print_list_tx:
                        #
                        #if type is str
                        if type(id).__name__ == 'str':
                            #
                            #print signals
                            frame_id = self._dbc.GetFrameIdFromSignalName(id)
                            if self.print_row(loc_y, loc_x, f"0x{format(frame_id, '02X')} : Tx : {id}", [], cols) == 0:
                                #
                                loc_x = self._value_start_col
                                cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                                #
                                #if float
                                if type(self._globals.tx_frame_info[frame_id]['sig_payload'][id]).__name__ == 'float':
                                    #
                                    #write value 1.3f
                                    self.print_row(loc_y, loc_x, f"{self._globals.tx_frame_info[frame_id]['sig_payload'][id]:1.3f}", [], cols)
                                #else if int
                                elif type(self._globals.tx_frame_info[frame_id]['sig_payload'][id]).__name__ == 'int':
                                    #write value
                                    self.print_row(loc_y, loc_x, f"{self._globals.tx_frame_info[frame_id]['sig_payload'][id]}", [], cols)
                                #
                                #
                                loc_x = self._border_width + self._left_margin
                                cols = self._available_columns
                                #
                                loc_y += 1
                                rows -= 1
                                #
                            #
                        #
                        #else if type is int
                        elif type(id).__name__ == 'int':
                            #
                            #print frame + bytes
                            self.print_row(loc_y, loc_x, f"0x{format(id, '02X')} : Tx : ", self._globals.tx_frame_info[id]['byte_payload'], cols)
                            #
                            loc_x = self._border_width + self._left_margin
                            cols = self._available_columns
                            #
                            loc_y += 1
                            rows -= 1
                            #
                        #
                    #
                    #if rx rows + mid_rows <= available rows
                    if self._mid_rows <= rows:
                        #
                        #if rx rows exist print mid
                        if self._rx_rows > 0:
                            for i in range(self._mid_rows):
                                if rows > 0:
                                    self.print_row(loc_y, loc_x, self._print_static_mid[i], [], cols)
                                    loc_x = self._border_width + self._left_margin
                                    cols = self._available_columns
                                    loc_y += 1
                                    rows -= 1
                        #
                        if self._rx_rows > 0:
                            #print rx rows
                            for signal in self._print_list_rx:
                                #
                                if rows > 0:
                                    #
                                    if type(signal).__name__ == 'str':
                                        #print signal
                                        #write line
                                        if self.print_row(loc_y, loc_x, f"0x{format(self._globals.rx_signal_info[signal]['frame_id'], '03X')} : Rx : {signal}", [], cols) == 0:
                                            #
                                            loc_x = self._value_start_col
                                            cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                                            #
                                            #if float
                                            if type(self._globals.rx_signal_info[signal]['value']).__name__ is float:
                                                #write value 1.3f
                                                if self.print_row(loc_y, loc_x, f"{self._globals.rx_signal_info[signal]['value']:1.3f}", [], cols) == 0:
                                                    loc_x = self._value_start_col + self._start_col_spacing
                                                    cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                                                    if self.print_row(loc_y, loc_x, f"{self._globals.rx_signal_info[signal]['max']:1.3f}", [], cols) == 0:
                                                        loc_x = self._value_start_col + (self._start_col_spacing * 2)
                                                        cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                                                        self.print_row(loc_y, loc_x, f"{self._globals.rx_signal_info[signal]['min']:1.3f}", [], cols)
                                            #else
                                            else:
                                                #write value
                                                if self.print_row(loc_y, loc_x, f"{self._globals.rx_signal_info[signal]['value']}", [], cols) == 0:
                                                    loc_x = self._value_start_col + self._start_col_spacing
                                                    cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                                                    if self.print_row(loc_y, loc_x, f"{self._globals.rx_signal_info[signal]['max']}", [], cols) == 0:
                                                        loc_x = self._value_start_col + (self._start_col_spacing * 2)
                                                        cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                                                        self.print_row(loc_y, loc_x, f"{self._globals.rx_signal_info[signal]['min']}", [], cols)
                                            #
                                            loc_x = self._border_width + self._left_margin
                                            cols = self._available_columns
                                            #
                                            loc_y += 1
                                            rows -= 1
                                            #
                                    elif type(signal).__name__ == 'int':
                                        #print id + bytes
                                        #print frame + bytes
                                        self.print_row(loc_y, loc_x, f"0x{format(signal, '03X')} : Rx : ", self._globals.rx_frame_info[signal], cols)
                                        #
                                        loc_x = self._border_width + self._left_margin
                                        cols = self._available_columns
                                        #
                                        loc_y += 1
                                        rows -= 1
                                        #
                                    #
                                #
                            #
                        #
                    #
                #
                #else tx rows = 0
                else:
                    #
                    #if rx rows > 0
                    if self._rx_rows > 0:
                        #
                            #print rx rows
                            for signal in self._print_list_rx:
                                #
                                if rows > 0:
                                    #
                                    if type(signal).__name__ == 'str':
                                        #print signal
                                        #write line
                                        if self.print_row(loc_y, loc_x, f"0x{format(self._globals.rx_signal_info[signal]['frame_id'], '03X')} : Rx : {signal}", [], cols) == 0:
                                            #
                                            loc_x = self._value_start_col
                                            cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                                            #
                                            #if float
                                            if type(self._globals.rx_signal_info[signal]['value']).__name__ is float:
                                                #write value 1.3f
                                                if self.print_row(loc_y, loc_x, f"{self._globals.rx_signal_info[signal]['value']:1.3f}", [], cols) == 0:
                                                    loc_x = self._value_start_col + self._start_col_spacing
                                                    cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                                                    if self.print_row(loc_y, loc_x, f"{self._globals.rx_signal_info[signal]['max']:1.3f}", [], cols) == 0:
                                                        loc_x = self._value_start_col + (self._start_col_spacing * 2)
                                                        cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                                                        self.print_row(loc_y, loc_x, f"{self._globals.rx_signal_info[signal]['min']:1.3f}", [], cols)
                                            #else
                                            else:
                                                #write value
                                                if self.print_row(loc_y, loc_x, f"{self._globals.rx_signal_info[signal]['value']}", [], cols) == 0:
                                                    loc_x = self._value_start_col + self._start_col_spacing
                                                    cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                                                    if self.print_row(loc_y, loc_x, f"{self._globals.rx_signal_info[signal]['max']}", [], cols) == 0:
                                                        loc_x = self._value_start_col + (self._start_col_spacing * 2)
                                                        cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                                                        self.print_row(loc_y, loc_x, f"{self._globals.rx_signal_info[signal]['min']}", [], cols)
                                            #
                                            loc_x = self._border_width + self._left_margin
                                            cols = self._available_columns
                                            #
                                            loc_y += 1
                                            rows -= 1
                                            #
                                    elif type(signal).__name__ == 'int':
                                        #print id + bytes
                                        #print frame + bytes
                                        #
                                        self.print_row(loc_y, loc_x, f"0x{format(signal, '03X')} : Rx : ", self._globals.rx_frame_info[signal], cols)
                                        #
                                        loc_x = self._border_width + self._left_margin
                                        cols = self._available_columns
                                        #
                                        loc_y += 1
                                        rows -= 1
                                        #
                                    #
                                #
                            #
                    #
                #
            #
            #
            #
            #print static footer
            loc_y = self._maxy - (self._footer_rows - self._border_width)
            for i in range(self._footer_rows - 1):
                self.print_row(loc_y, loc_x, self._print_static_footer[i], [], cols)
                loc_x = self._border_width + self._left_margin
                cols = self._available_columns
                loc_y += 1
            #
        #
        #else available rows <= 0
        else:
            #
            #handle header/footer/margins only
            if self._maxy > self._header_rows:
                #
                #print header
                #print dynamic header
                if self.print_row(loc_y, loc_x, f"{type(self._globals).__name__} - {self._globals.global_info['driver']} Ch.{self._globals.global_info['channel']}", [], cols) == 0:
                    #
                    loc_x = self._value_start_col
                    cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                    #
                    if self.print_row(loc_y, loc_x, 'Val.', [], cols) == 0:
                        #
                        loc_x = self._value_start_col + self._start_col_spacing
                        cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                        #
                        if self.print_row(loc_y, loc_x, 'Max.', [], cols) == 0:
                            #
                            loc_x = self._value_start_col + (self._start_col_spacing * 2)
                            cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                            #
                            self.print_row(loc_y, loc_x, 'Min.', [], cols)
                        #
                    #
                #
                loc_x = self._border_width + self._left_margin
                cols = self._available_columns
                loc_y += 1
                if self.print_row(loc_y, loc_x, f"{self._globals.global_info['transport_proto']} @ {(self._globals.com_port.getBusParams()[0]/1000000):1.1f} Mbps - Bus Load:", [], cols) == 0:
                    #
                    loc_x = self._value_start_col
                    cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                    #
                    if self.print_row(loc_y, loc_x, f"{self._globals.bus_load['value']:3.1f}", [], cols) == 0:
                        #
                        loc_x = self._value_start_col + self._start_col_spacing
                        cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                        #
                        if self.print_row(loc_y, loc_x, f"{self._globals.bus_load['max']:3.1f}", [], cols) == 0:
                            #
                            loc_x = self._value_start_col + (self._start_col_spacing * 2)
                            cols = (self._border_width + self._left_margin + self._available_columns) - loc_x
                            #
                            self.print_row(loc_y, loc_x, f"{self._globals.bus_load['min']:3.1f}", [], cols)
                        #
                    #
                loc_x = self._border_width + self._left_margin
                cols = self._available_columns
                loc_y += 1
                #
                #print static header
                for i in range(len(self._print_static_header)):
                    self.print_row(loc_y, loc_x, self._print_static_header[i], [], cols)
                    loc_x = self._border_width + self._left_margin
                    cols = self._available_columns
                    loc_y += 1
                #
            #
        #
        #refresh
        self._stdscr.refresh()
        #

    def handle_char(self, char: int) -> None:
        if chr(char) == "d" and self._globals.synch_seq_info['synch_seq_standby_state_on_key_d'] < 2:
            self._globals.synch_seq_info.update({'synch_seq_standby_state_on_key_d': 2})
        elif chr(char) == "s" and self._globals.synch_seq_info['synch_seq_enable_state_on_key_s'] < 2:
            self._globals.synch_seq_info.update({'synch_seq_enable_state_on_key_s': 2})

