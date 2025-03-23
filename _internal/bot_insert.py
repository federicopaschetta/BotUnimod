import os
import pyautogui
import time
import json
import read_pdf
from pynput.mouse import Listener
import sys
import setup.get_coord as get_coord

def on_click(x, y, button, pressed):
    global clicked
    if pressed:
        return False  # Stoppa il listener
def load_coords_json(path):
    with open(path, 'r') as file:
        return json.load(file)
    
def read_data(data_path):
    with open(data_path, 'r', encoding='utf8') as file:
        return json.load(file)
    
def delete_cell():
    pyautogui.doubleClick() 
    time.sleep(0.1)
    pyautogui.press("backspace") 
    
def change_page(buttons_dict, page, button):
    return buttons_dict[page][button]

def switch_tab():
    pyautogui.hotkey("alt", "tab")
    time.sleep(0.5)
    pyautogui.press("enter")
    
def actions_on_page(info_dict, coords_json, types, act_page):
    for field, value in info_dict[act_page].items():
        if value is not None:
            x, y = coords_json[act_page][field]
            pyautogui.moveTo(x, y, duration=0.1)
            pyautogui.click()
            if field in types['Buttons'][act_page]:
                if types['Buttons'][act_page][field] != act_page:
                    act_page = change_page(types['Buttons'], act_page, field)
                    actions_on_page(info_dict, coords_json, types, act_page)
                    break
            elif field in types['Select'][act_page]:
                action = types['Select'][act_page][field][value]
                for i in range((action[0])):
                    pyautogui.press(action[1])
                pyautogui.press("enter")
            elif field in types['Radio'][act_page]:
                x, y = coords_json[act_page][value]
                pyautogui.moveTo(x, y, duration=0.1)
                pyautogui.click()
            elif field in types['Checkbox'][act_page]:
                if value == "No":
                    pyautogui.click()
            else:
                if field not in types['Select Input'][act_page]:
                    delete_cell()
                pyautogui.write(''.join(value.split(' ')), interval=0.01)
                if field in types['Select Input'][act_page]:
                    pyautogui.press("enter")
        
def load_immobili_dict(pdf_path, sections_path, prov_dict, com_dict):
    tot_dict = {'Fabbricato': {}, 'Terreno': {}}
    for elem in pdf_path:
        key = elem.replace('.pdf', '')
        pdf_dict = read_pdf.get_info_from_pdf(elem, sections_path, prov_dict, com_dict)
        tot_dict[pdf_dict['Tipo']][key] = ({k: v for k, v in pdf_dict.items() if k != 'Tipo'})
    return tot_dict
        
def insert_immobili(immobili_dict, coords_json, types, type_estate):
    switch_tab()
    immobili = immobili_dict[type_estate]
    act_page = type_estate
    for key, immobile in immobili.items():
        immobile["Salva"] = ""
        if type_estate=='Terreno':
            pass
            # immobile["No"] = ""
        actions_on_page({type_estate: immobile}, coords_json, types, act_page)
        with Listener(on_click=on_click) as listener:
            listener.join()
        time.sleep(2)
    return

        
def main(pdf_list, type): 
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    get_coord.get_coord(os.path.join(base_path, 'setup'))
    coords_json = load_coords_json(os.path.join(base_path, 'setup', 'coordinates.json'))
    types = read_data(os.path.join(base_path, 'setup', 'types.json'))
    sections_path = os.path.join(base_path, 'data', 'sections.txt')
    prov_dict, com_dict = read_pdf.load_prov_com(os.path.join(base_path, 'data'))
    immobili_dict = load_immobili_dict(pdf_list, sections_path, prov_dict, com_dict)
    insert_immobili(immobili_dict, coords_json, types, type)
        
