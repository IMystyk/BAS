import tkinter as tk
import keyboardlayout as kl
import tkinter.font as tkf
import keyboardlayout.tkinter as klt
from keyboardlayout.tkinter.key import KEY_MAP
import json

GREY = '#bebebe'
DARK_GREY = '#414141'
KEY_SIZE = 100


def normalize_list(input: list) -> list:
    """
    Normalizes values in given list to [0,1] range
    :param input: list to be normalized
    :return: normalized list
    """
    max_value = max(input)
    min_value = min(input)
    normalized_list = []
    for value in input:
        normalized_value = (value - min_value) / (max_value - min_value)
        normalized_list.append(normalized_value)

    return normalized_list


def normalize_dict(input: dict) -> dict:
    """
    Normalizes values in a diven dictionary to [0,1] range
    :param input: dictionary to be normalized
    :return: normalized dictionary
    """
    max_value = max(input.values())
    min_value = min(input.values())
    normalized_dict = dict()
    for key, value in input.items():
        normalized_value = (value - min_value) / (max_value - min_value)
        normalized_dict[key] = normalized_value

    return normalized_dict


def get_blue_red_color(value: float, grey_zero: bool = False) -> tuple:
    """
    Function returns an rgb color between blue and red
    :param value: value to be represented by a color
    :param grey_zero: flag that sets values 0 to color out of the spectrum (107, 107, 107)
    :return: tuple describing a color in an rgb format
    """
    red = 255 * value + 0
    green = 0
    blue = -255 * value + 255

    if bool and value == 0:
        red = green = blue = 107

    return int(red), int(green), int(blue)


def rgb_to_hex(rgb: tuple) -> str:
    """
    Returns string that's hex equivalent of rgb tuple
    :param rgb: RGP tuple
    :return: string representing color in hex
    """
    return '#%02x%02x%02x' % rgb


def apply_heatmap(keyboard: klt.KeyboardLayout, file_name: str):
    """
    Recolors keys on the keyboard according to the heatmap
    :param keyboard:
    :param file_name:
    :return:
    """
    with open(f"./Data/{file_name}", 'r') as presses_file:
        total_presses = presses_file.read()
        total_presses = json.loads(total_presses)

    total_presses = normalize_dict(total_presses)

    for key in total_presses.keys():
        presses = total_presses[key]
        color = get_blue_red_color(presses, True)
        color = rgb_to_hex(color)
        key_info = kl.KeyInfo(
            margin=14,
            color=color,
            txt_color='white',
            txt_font=tkf.Font(family='Arial', size=KEY_SIZE // 4),
            txt_padding=(KEY_SIZE // 6, KEY_SIZE // 10)
        )
        showed_key = KEY_MAP[int(key)]
        keyboard_layout.update_key(showed_key, key_info)


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


if __name__ == '__main__':
    window = tk.Tk()
    window.resizable(False, False)

    key_info = kl.KeyInfo(
        margin=10,
        color=GREY,
        txt_color=DARK_GREY,
        txt_font=tkf.Font(family='Arial', size=KEY_SIZE // 4),
        txt_padding=(KEY_SIZE // 6, KEY_SIZE // 10)
    )

    keyboard_layout = get_keyboard(window, kl.LayoutName.QWERTY, key_info)
    apply_heatmap(keyboard_layout, "total_time_pressed_Mystyk.json")
    window.mainloop()
