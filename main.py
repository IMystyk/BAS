import argparse
import os
import threading
import tkinter as tk
import tkinter.font as tkf

import pynput.keyboard
from pynput.keyboard import Key, Listener
import keyboardlayout as kl
import keyboardlayout.tkinter as klt
from keymap import VIRTUAL_KEY_MAP
from keyboardlayout.tkinter.key import KEY_MAP
from datetime import datetime
import json

GREY = '#bebebe'
DARK_GREY = '#414141'
KEY_SIZE = 100

ALREADY_PRESSED = list()
TOTAL_TIMES_PRESSED = dict()
TOTAL_TIME_PRESSED = dict()
LAST_TIME_PRESSED = dict()


def on_press(key: pynput.keyboard.Key, keyboard_layout: klt.KeyboardLayout):
    """
    Function called when the key is pressed
    :param key: pressed key
    :param keyboard_layout: keyboard layout that is showed in the GUI
    :return:
    """
    if key not in ALREADY_PRESSED:
        ALREADY_PRESSED.append(key)
    else:
        return
    pressed_key_info = kl.KeyInfo(
        margin=14,
        color='red',
        txt_color='white',
        txt_font=tkf.Font(family='Arial', size=KEY_SIZE // 4),
        txt_padding=(KEY_SIZE // 6, KEY_SIZE // 10)
    )
    try:
        key = key.vk
    except AttributeError:
        key = key.value.vk
    key = VIRTUAL_KEY_MAP.get(key)
    if key is not None:
        try:
            TOTAL_TIMES_PRESSED[key] += 1
        except KeyError:
            TOTAL_TIMES_PRESSED[key] = 1
        LAST_TIME_PRESSED[key] = datetime.now()
        key = KEY_MAP[key]
        keyboard_layout.update_key(key, pressed_key_info)


def on_release(key: pynput.keyboard.Key, keyboard_layout: klt.KeyboardLayout):
    """
    Function called when the key is released
    :param key: released key
    :param keyboard_layout: keyboard layout that is showed in the GUI
    :return:
    """
    try:
        ALREADY_PRESSED.remove(key)
    except ValueError:
        pass
    released_key_info = kl.KeyInfo(
        margin=10,
        color=GREY,
        txt_color=DARK_GREY,
        txt_font=tkf.Font(family='Arial', size=KEY_SIZE // 4),
        txt_padding=(KEY_SIZE // 6, KEY_SIZE // 10)
    )
    try:
        key = key.vk
    except AttributeError:
        key = key.value.vk
    key = VIRTUAL_KEY_MAP.get(key)
    if key is not None:
        try:
            TOTAL_TIME_PRESSED[key] += datetime.now() - LAST_TIME_PRESSED[key]
        except KeyError:
            TOTAL_TIME_PRESSED[key] = datetime.now() - LAST_TIME_PRESSED[key]
        key = KEY_MAP[key]
        keyboard_layout.update_key(key, released_key_info)


def check_key_pressed(keyboard_layout: klt.KeyboardLayout):
    """
    Function setting listeners for key_press and key_release events
    :param keyboard_layout:
    :return:
    """
    with Listener(on_press=lambda event: on_press(event, keyboard_layout),
                  on_release=lambda event: on_release(event, keyboard_layout)) as listener:
        listener.join()


def get_keyboard(
        window: tk.Tk,
        layout_name: kl.LayoutName,
        key_info: kl.KeyInfo
) -> klt.KeyboardLayout:
    """
    Returns a keyboard layout that is displayed in the main window
    :param window: main application window
    :param layout_name: type of layout used in tk window
    :param key_info: parameters for keys in keyboard layout
    :return: KeyboardLayout used in the main application window
    """

    keyboard_info = kl.KeyboardInfo(
        position=(0, 0),
        padding=2,
        color=DARK_GREY
    )
    letter_key_size = (KEY_SIZE, KEY_SIZE)  # width, height
    keyboard_layout = klt.KeyboardLayout(
        layout_name,
        keyboard_info,
        letter_key_size,
        key_info,
        master=window
    )
    return keyboard_layout


def main_loop_tmp(keyboard_layout: klt.KeyboardLayout):
    """
    Function responsible for running key events listeners in a separate thread
    :param keyboard_layout: keyboard layout displayed in the main window
    :return:
    """
    kb_input_thread = threading.Thread(target=check_key_pressed, args=(keyboard_layout,))
    kb_input_thread.daemon = True
    kb_input_thread.start()


def on_closing(window: tk.Tk):
    """
    Function called when main window is being closed. Here gathered data is saved to the files before closing the app.
    :param window: main application window
    :return:
    """
    timestamp = datetime.now()
    date = f'{timestamp.year}{timestamp.month}{timestamp.day}{timestamp.hour}{timestamp.minute}{timestamp.second}'
    if not os.path.exists("./Data"):
        os.makedirs("./Data")
    for key in VIRTUAL_KEY_MAP.values():
        if TOTAL_TIMES_PRESSED.get(key) is None:
            TOTAL_TIMES_PRESSED[key] = 0
        if TOTAL_TIME_PRESSED.get(key) is None:
            TOTAL_TIME_PRESSED[key] = 0
        else:
            TOTAL_TIME_PRESSED[key] = TOTAL_TIME_PRESSED[key].total_seconds() * 10 ** 6
    with open(f"./Data/total_times_pressed{date}.json", 'w') as file:
        file.write(json.dumps(TOTAL_TIMES_PRESSED))
    with open(f"./Data/total_time_pressed{date}.json", 'w') as file:
        file.write(json.dumps(TOTAL_TIME_PRESSED))
    window.destroy()


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     'layout_name',
    #     nargs='?',
    #     type=kl.LayoutName,
    #     default=kl.LayoutName.QWERTY,
    #     help='the layout_name to use'
    # )
    # args = parser.parse_args()

    window = tk.Tk()
    window.protocol("WM_DELETE_WINDOW", lambda arg=window: on_closing(arg))
    window.resizable(False, False)

    key_info = kl.KeyInfo(
        margin=10,
        color=GREY,
        txt_color=DARK_GREY,
        txt_font=tkf.Font(family='Arial', size=KEY_SIZE // 4),
        txt_padding=(KEY_SIZE // 6, KEY_SIZE // 10)
    )
    keyboard_layout = get_keyboard(window, kl.LayoutName.QWERTY, key_info)

    main_loop_thread = threading.Thread(target=main_loop_tmp, args=(keyboard_layout,))
    main_loop_thread.daemon = True
    main_loop_thread.start()
    window.mainloop()
