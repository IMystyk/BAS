import argparse
import threading
import tkinter as tk
import tkinter.font as tkf
from pynput.keyboard import Key, Listener
import keyboardlayout as kl
import keyboardlayout.tkinter as klt
from keymap import VIRTUAL_KEY_MAP
from keyboardlayout.tkinter.key import KEY_MAP

grey = '#bebebe'
dark_grey = '#414141'
key_size = 60


def on_press(key, keyboard_layout):
    pressed_key_info = kl.KeyInfo(
        margin=14,
        color='red',
        txt_color='white',
        txt_font=tkf.Font(family='Arial', size=key_size // 4),
        txt_padding=(key_size // 6, key_size // 10)
    )
    try:
        key = key.vk
    except AttributeError:
        key = key.value.vk
    key = VIRTUAL_KEY_MAP.get(key)
    if key is not None:
        key = KEY_MAP[key]
        keyboard_layout.update_key(key, pressed_key_info)


def on_release(key, keyboard_layout):
    released_key_info = kl.KeyInfo(
        margin=10,
        color=grey,
        txt_color=dark_grey,
        txt_font=tkf.Font(family='Arial', size=key_size // 4),
        txt_padding=(key_size // 6, key_size // 10)
    )
    try:
        key = key.vk
    except AttributeError:
        key = key.value.vk
    key = VIRTUAL_KEY_MAP.get(key)
    if key is not None:
        key = KEY_MAP[key]
        keyboard_layout.update_key(key, released_key_info)


def _check_esc_pressed(keyboard_layout):
    with Listener(on_press=lambda event: on_press(event, keyboard_layout),
                  on_release=lambda event: on_release(event, keyboard_layout)) as listener:
        listener.join()


def get_keyboard(
        window: tk.Tk,
        layout_name: kl.LayoutName,
        key_info: kl.KeyInfo
) -> klt.KeyboardLayout:
    keyboard_info = kl.KeyboardInfo(
        position=(0, 0),
        padding=2,
        color=dark_grey
    )
    letter_key_size = (key_size, key_size)  # width, height
    keyboard_layout = klt.KeyboardLayout(
        layout_name,
        keyboard_info,
        letter_key_size,
        key_info,
        master=window
    )
    return keyboard_layout


def main_loop_tmp(keyboard_layout):
    kb_input_thread = threading.Thread(target=_check_esc_pressed, args=(keyboard_layout,))
    kb_input_thread.daemon = True
    kb_input_thread.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'layout_name',
        nargs='?',
        type=kl.LayoutName,
        default=kl.LayoutName.QWERTY,
        help='the layout_name to use'
    )
    args = parser.parse_args()

    window = tk.Tk()
    window.resizable(False, False)

    key_info = kl.KeyInfo(
        margin=10,
        color=grey,
        txt_color=dark_grey,
        txt_font=tkf.Font(family='Arial', size=key_size // 4),
        txt_padding=(key_size // 6, key_size // 10)
    )
    keyboard_layout = get_keyboard(window, args.layout_name, key_info)

    main_loop_thread = threading.Thread(target=main_loop_tmp, args=(keyboard_layout,))
    main_loop_thread.daemon = True
    main_loop_thread.start()
    window.mainloop()
