from pynput import mouse
import json
import pyautogui
import time
import os

def on_click(x, y, button, pressed):
    global clicked_position
    if pressed:  
        clicked_position = (x, y)
        return False

def load_coords_json(path):
    with open(path, 'r') as file:
        return json.load(file)


def write_coords_dict(path, coords_dict):
    with open(os.path.join(path, 'coordinates.json'), 'w') as file:
        json.dump(coords_dict, file, indent=4)


def clean_dict(path):
    coords_dict = load_coords_json(os.path.join(path, 'coordinates.json'))
    for index, page in enumerate(coords_dict):
        for coord in list(page.keys()):
            coords_dict[index][coord] = ""
    write_coords_dict(coords_dict)


def read_data(data_path):
    with open(data_path, 'r', encoding='utf8') as file:
        return json.load(file)
    
def get_single_coord():
    global clicked_position
    clicked_position = None
    pyautogui.hotkey(["alt", "tab"])
    pyautogui.hotkey(["enter"])
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
        return clicked_position

def setup_coords(path):
    global clicked_position
    coords_dict = load_coords_json(os.path.join(path, 'coordinates.json'))
    clicked_position = None
    pyautogui.hotkey(["alt", "tab"])
    pyautogui.hotkey(["enter"])
    for key, value in coords_dict.items():
        for coord in coords_dict[key].keys():
            if value[coord] == "":
                print(coord)
                with mouse.Listener(on_click=on_click) as listener:
                    listener.join()
                coords_dict[key][coord] = clicked_position
                if '*' in coord:
                    with mouse.Listener(on_click=on_click) as listener:
                        listener.join()
                    print('Chiudi')
        write_coords_dict(path, coords_dict)
        coords_dict[key] = ({k.strip('*'): v for k, v in coords_dict[key].items()})
    return coords_dict

def get_coord(path):
    coords_new = setup_coords(path)
    write_coords_dict(path, coords_new)
    time.sleep(5)

