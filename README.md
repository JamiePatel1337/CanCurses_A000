# CanCurses_A000

Simple Python (>3.7) CAN Tx/Rx with Curses UI. Tested with Kvaser Virtual CAN channels only.

python packages needed:
 >python3.7
 venv
 canlib
 cantools
 asyncio


apt install python3-pip python3-venv -y
python3 -m venv .venv --prompt venv_user
source .venv/bin/activate
deactivate

https://www.kvaser.com/developer-blog/kvaser-canlib-and-python-part-1-initial-setup/#/!

pip3 install cantools
pip3 install asyncio


pip3 install pyinstaller
pyinstaller -F -D -n elf_out -c ./main.py


