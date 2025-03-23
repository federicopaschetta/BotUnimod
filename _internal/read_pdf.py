import json
import PyPDF2
import re
import os


def load_prov_com(path):
    with open(os.path.join(path, 'province.json'), 'rb') as file_prov:
        dict_prov = json.load(file_prov)
    with open(os.path.join(path, 'comuni.json'), 'rb') as file_com:
        dict_com = json.load(file_com)
    return dict_prov, dict_com

def get_sections_markers(path):
    with open(path, 'r') as f:
        return [line.strip() for line in f.readlines()]
    
def divide_pdf_on_sections(path, text):
    markers = get_sections_markers(path)
    sections = []
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.startswith(markers[0]):
            index_split = i
            break
    sections.append('\n'.join(lines[:index_split]))
    for marker in markers[1:]:
        new_i = lines.index(marker)
        sections.append('\n'.join(lines[index_split:new_i]))
        index_split = new_i
    sections.append('\n'.join(lines[index_split:]))
    return sections[0], sections[1], sections[2]

def read_str(list, starting, re_search, num_groups):
    for riga in list:
        if riga.startswith(starting):
            match = re.search(re_search, riga, re.IGNORECASE)
            return [match.group(i) for i in range(1, num_groups+1)]

def read_nums(list, starting, add_none=False):
    for riga in list:
        if riga.strip().startswith(starting):
            match = re.findall(r"\d+", riga.replace(".", ""))
            if len(match)<3 and add_none:
                    match.extend([None] * (3 - len(match)))
            return match

        
def get_cat_classe(line):
    match = re.search(r"Categoria\s+([A-Z])\/(\d+)", line[0])
    cat = match.group(1) + match.group(2)
    classe = re.search(r"Classe\s+(\d+)", line[1])
    if classe:
        classe = classe.group(1)
    else:
        classe = ''
    consistenza = re.search(r"Consistenza\s+([\d,]+)", line[2]).group(1)
    return cat, classe, consistenza

        
def get_info_from_pdf(pdf_path, sections_path, prov_dict, com_dict):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = '\n'.join(page.extract_text() for page in reader.pages)
    immobile = {}
    intro, info, intestati = [part.split('\n') for part in divide_pdf_on_sections(sections_path, text)]
    comune, provincia = read_str(info, "Dati identificativi:", r"Comune di ([A-Za-zÀ-ÿ\s]+) \(\w+\) \((\w+)\)", 2)
    foglio, particella, subalterno = read_nums(info, 'Foglio', add_none=True)
    cat_line = [line for line in info if line.startswith('Categoria')]
    
    # area_tot, tot_no_aree_scop = (sorted([int(elem) for elem in read_nums(info, "Dati di superficie: ")], reverse=True)[:2])

    immobile['Tipo'] = (read_str(intro, "Immobile di catasto", r"catasto (\w+)", 1)[0].capitalize()[:-1]+'o')
    immobile['Provincia'] = prov_dict[provincia]
    immobile['Comune Amministrativo'] = comune
    if immobile['Tipo'] == 'Terreno':
        immobile['Provincia Catastale'] = prov_dict[provincia]
        immobile['Comune Catastale'] = comune
        sezione = read_str(info, "Sezione", r"Sezione ([A-Za-zÀ-ÿ\s]+)", 1)
        immobile['Sezione Censuaria'] = sezione if sezione is not None else comune
        area_tot = read_nums(info, "Superficie: ")[0]
        immobile['Reddito Dominicale'] = ','.join(read_nums(info, 'Redditi')[:2])
        immobile['Reddito Agrario'] = ','.join(read_nums(info, 'agrario')[:2])
        immobile['Natura'] = 'Terreno'
        
    else:
        com_cat, provincia_cat = read_str(info, "Comune di", r"Comune di ([A-Za-zÀ-ÿ\s]+) \(\w+\) \((\w+)\)", 2)
        immobile['Provincia Catastale'] = prov_dict[provincia_cat]
        immobile['Comune Catastale'] = com_cat
        area_tot = read_nums(info, "Dati di superficie: ")[0]
        categoria, classe, consistenza = get_cat_classe(cat_line[0].strip().split(', '))    
        immobile['Categoria'] = categoria.replace('/', '')
        immobile['Rendita'] = ','.join(read_nums(info, 'Rendita'))
        immobile['Classe'] = classe
        unita = 'Metri Quadrati' if 'C' in categoria else 'Vani'
        immobile[unita] = consistenza
        
    immobile['Foglio'] = foglio
    immobile['Particella Uno'] = particella
    immobile['Subalterno Uno'] = subalterno
    zona_censuaria = read_nums(info, 'Zona censuaria')
    immobile['Zona Censuaria'] = zona_censuaria[0] if zona_censuaria is not None else None
    immobile['Superficie Catastale'] = str(area_tot)
    # immobile['Indirizzo'] = read_str(info, 'Indirizzo: ', r"Indirizzo:\s*(.+)", 1)[0]
    # immobile['superficie_totale_no_scoperte'] = tot_no_aree_scop
    
    return immobile
