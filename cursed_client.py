import socket
import threading
import curses
import random
from time import sleep
from math import ceil


IP_ADRESS = '51.15.41.219'
PORT = 10010


MESSAGE_HISTORY = []
PRINTABLE = ''' 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~абвгдеёжзийклмнопрстуфхцчшщьъэыюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЪЭЫЮЯ'''
COLORS = [curses.COLOR_BLACK, curses.COLOR_RED, curses.COLOR_GREEN, curses.COLOR_YELLOW, curses.COLOR_BLUE, curses.COLOR_MAGENTA, curses.COLOR_CYAN]


SCREEN = None
CURSTR = []
CURSOR_INDEX = 0
KEY = 0
KEY_BACKSPACE = 8
KEY_ENTER = 10


def hear():
    while True:
        #MESSAGE_HISTORY.append((chr(random.randint(ord('a'), ord('z'))) * 270, 0))
        #sleep(2)
        MESSAGE_HISTORY.append((sock.recv(60 * 5).decode("utf-8"), 0))

sock = socket.socket()
sock.connect((IP_ADRESS, PORT))
thr1 = threading.Thread(target=hear)
thr1.start()


def cut_string(s, size):
    ret = []
    l = len(s)
    for i in range(0, ceil(l / size)):
        ret.append(s[i * size:(i + 1) * size])
    return ret


def handle_input():
    global CURSTR
    global CURSOR_INDEX
    global KEY
    while True:
        if SCREEN:
            key = SCREEN.getch()
        else:
            continue
        KEY = key
        if key == curses.KEY_LEFT:
            CURSOR_INDEX = max(CURSOR_INDEX - 1, 0)
        elif key == curses.KEY_RIGHT:
            CURSOR_INDEX = min(CURSOR_INDEX + 1, len(CURSTR))
        elif key == KEY_BACKSPACE:
            if CURSTR and CURSOR_INDEX:
                CURSTR = CURSTR[:CURSOR_INDEX - 1] + CURSTR[CURSOR_INDEX:]
                CURSOR_INDEX -= 1
        elif key == KEY_ENTER and CURSTR:
            message = ''.join(CURSTR)
            MESSAGE_HISTORY.append((message, 1))
            sock.send(message.encode("utf-8"))
            CURSTR = []
        elif chr(key) in PRINTABLE:
            CURSTR = CURSTR[:CURSOR_INDEX] + [chr(key)] + CURSTR[CURSOR_INDEX:]
            CURSOR_INDEX += 1
        CURSOR_INDEX = min(max(0, CURSOR_INDEX), len(CURSTR))


def client(screen):
    global SCREEN
    SCREEN = screen

    curses.start_color()
    curses.init_pair(1, random.choice(COLORS), curses.COLOR_WHITE)

    thr2 = threading.Thread(target=handle_input)
    thr2.start()

    while True:
        key = KEY
        curstr = CURSTR
        screen.clear()

        height, width = screen.getmaxyx()
        try:
            screen.addstr(height - 1, 0, '=' * width)
        except Exception:
            pass
        height_left = height - 2

        cuted_curstr = cut_string('> ' + ''.join(curstr), width)
        for i in range(0, len(cuted_curstr)):
            screen.addstr(height - 2 - i, 0, cuted_curstr[-1 - i])
        height_left -= len(cuted_curstr)

        screen.addstr(height_left, 0, '=' * width)
        height_left -= 1

        msg_history = ['']
        for i in range(-1, -len(MESSAGE_HISTORY) - 1, -1):
            message, own_message = MESSAGE_HISTORY[i]
            cuted_message = cut_string(message, width - 2)
            cuted_message[0] = ('> ' if own_message else '') + cuted_message[0]
            for i in range(1, len(cuted_message)):
                cuted_message[i] = '  ' + cuted_message[i]
            cuted_message = cuted_message[::-1] + ['']
            msg_history += cuted_message
            if len(msg_history) > height_left:
                break
        for i in range(min(height_left, len(msg_history))):
            screen.addstr(height_left - i, 0, msg_history[i])

        status_bar = 'Anchated | made by KingCake | trust'.format(width, height)
        screen.addstr(0, 0, status_bar + ' ' * (width - len(status_bar)), curses.color_pair(1))
        cursor_index = CURSOR_INDEX + 2
        cursor_y = height - 2 - len(cuted_curstr) + ceil((cursor_index + 1) / width)
        cursor_x = cursor_index % width
        cursor_y = min(max(0, cursor_y), height - 1)
        cursor_x = min(max(0, cursor_x), width - 1)
        screen.move(cursor_y, cursor_x)
        screen.refresh()


def main():
    curses.wrapper(client)


if __name__ == "__main__":
    main()