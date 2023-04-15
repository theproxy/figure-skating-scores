from bs4 import BeautifulSoup
import json
import os

def str2num(input):
    # print(f"{input} // {[c for c in input]}")
    if input == '-':
        return '-'
    if input == []:
        return None

    if input == "":
        return None

    return float(input)


def parse_html_competition(filename,detailed=False):
    fp = open(filename,'r')
    soup = BeautifulSoup(fp, features='html.parser')
    fp.close()
    competition = dict()
    competition['name'] = soup.title.text
    competition['date'] = soup.find_all('h3',{"class":"date"})[0].text
    competition['venue'] = soup.find_all('div')[1].find_all('h3')[1].text
    competition['location'] = soup.find_all('div')[1].find_all('h3')[2].text
    competition['events'] = list()
    event_list = soup.find_all('table')[2].find_all('tr')
    for count, event in enumerate(event_list):
        if count == 0:
            continue # header
        event_info = dict()
        event_info['name'] = event.find_all('td',{'class':'event'})[0].text.strip()
        event_info['datetime'] = event.find_all('td',{'class':'event'})[1].text.strip()
        event_info['state'] = event.find_all('td',{'class':'stat'})[0].text.strip()
        event_info['file'] = event.find_all('td', {'class': 'stat'})[0].find('a')['href']
        competition['events'].append(event_info)

    return competition


def parse_html_program(filename, detailed=True):
    fp= open(filename,'r')
    soup = BeautifulSoup(fp, features='html.parser')
    fp.close()
    program = dict()
    program['competition'] = soup.find_all('title')[-1].text
    program['program'] = soup.find_all('div',{'class': 'catTitle'})[0].text.strip()
    program['file'] = filename
    start_order = soup.find_all('tr', {'class': 'parent'})
    program['start_order'] = dict()
    for item in start_order:
        key = item.find_all('td',{'class': 'start'})[0].text
        program['start_order'][key] = item.find_all('td',{'class': 'name'})[0].text
    officials = soup.find_all('table',{'class': 'officials'})[0].find_all('tr')
    program['officials'] = dict()
    for count, official in enumerate(officials):
        if count == 0: #header
            continue
        key = official.find_all('td')[0].text
        program['officials'][key] = official.find_all('td')[1].text
    program['detailed'] = soup.find_all('li',{'class':'judgeDetailRef'})[0].find('a')['href']

    if detailed == True:
        # get path
        head, tail = os.path.split(filename)
        detailed_file = os.path.join(head,program['detailed'])
        print(f"{head} and {detailed_file}")
        detailed_results = parse_html_detailed_scores(detailed_file)
        program['detailed_resuilts'] = detailed_results

    return program

def parse_html_detailed_scores(filename):
    fp = open(filename, 'r')
    soup = BeautifulSoup(fp, features='html.parser')
    fp.close()
    tables = soup.find_all('table')

    n_skaters = len(tables) // 4  #

    n_skaters = len(tables) // 4  # each skater has 4 tables
    event_sheet = dict()
    performances = list()

    for i in range(n_skaters):
        skater_info = dict()
        skater_info['sum'] = tables[4 * i]
        for item in skater_info['sum'].find_all('td'):
            skater_info[item['class'][0]] = item.get_text()
        skater_info['elm'] = tables[(4 * i) + 1]

        # get number of all elements:
        elem_nums = skater_info['elm'].find_all('td', {'class': 'num'})
        n_elements = 0
        for element_num in elem_nums:
            if int(element_num.text) > n_elements:
                n_elements = int(element_num.text)
        # print(f"Detected {n_elements} elements")

        elements = list()
        components = list()
        for count,row in enumerate(skater_info['elm'].find_all('tr'),start=0):
            if count == 0:
                continue
            if count >= 1 and count <= n_elements:
                current_elem = dict()
                current_elem["base_value"] = float(row.find_all('td', {"class": "bv"})[0].text)
                current_elem["credit_flag"] = row.find_all('td', {"class": "num"})[0].text
                current_elem["element_desc"] = row.find_all('td', {"class": "elem"})[0].text
                current_elem["element_num"] = row.find_all('td', {"class": "num"})[0].text
                current_elem["goe"] = float(row.find_all('td', {"class": "goe"})[0].text)
                current_elem["info_flag"] = row.find_all('td', {"class": "info"})[0].text
                current_elem["ref"] = row.find_all('td', {"class": "ref"})[0].text
                current_elem["scores_of_panel"] = float(row.find_all('td', {"class": "psv"})[0].text)
                for judge_count, judge in enumerate(row.find_all('td', {"class": "jud"}), start=0):
                    current_judge_score = judge.text.strip()
                    # print(f"count: {judge_count}, Current Score: {judge.text}")
                    current_elem[f"J{judge_count+1}"] = str2num(current_judge_score)
                # print(current_elem)
                elements.append(current_elem)
            if count == n_elements+1:
                #total BV and total elem score
                # total_bv_score = str2num(row.find_all('td',{'class': 'tbvv'})[0].text)
                total_element_score = str2num(row.find_all('td',{'class': 'tps'})[0].text)
            if count == (n_elements + 2):
                pass # header
            if count == (n_elements + 3):
                #composition
                current_component = dict()
                current_component['component_desc'] = "Composition"
                current_component['factor'] = str2num(row.find_all('td',{'class': 'cf'})[0].text)
                current_component['scores_of_panel'] = str2num(row.find_all('td', {'class': 'panel'})[0].text)
                current_component['ref'] = None # IDK?
                current_component["J1"] = str2num(row.find_all('td', {"class": "cjud"})[0].text.strip())
                current_component["J2"] = str2num(row.find_all('td', {"class": "cjud"})[1].text.strip())
                current_component["J3"] = str2num(row.find_all('td', {"class": "cjud"})[2].text.strip())
                current_component["J4"] = str2num(row.find_all('td', {"class": "cjud"})[3].text.strip())
                current_component["J5"] = str2num(row.find_all('td', {"class": "cjud"})[4].text.strip())
                current_component["J6"] = str2num(row.find_all('td', {"class": "cjud"})[5].text.strip())
                current_component["J7"] = str2num(row.find_all('td', {"class": "cjud"})[6].text.strip())
                current_component["J8"] = str2num(row.find_all('td', {"class": "cjud"})[7].text.strip())
                current_component["J9"] = str2num(row.find_all('td', {"class": "cjud"})[8].text.strip())
                current_component["J9"] = str2num(row.find_all('td', {"class": "cjud"})[8].text.strip())
                components.append(current_component)
            if count == (n_elements + 4):
                # presentation
                current_component = dict()
                current_component['component_desc'] = "Presentation"
                current_component['factor'] = str2num(row.find_all('td',{'class': 'cf'})[0].text)
                current_component['scores_of_panel']  = str2num(row.find_all('td', {'class': 'panel'})[0].text)
                current_component['ref'] = None # IDK?
                current_component["J1"] = str2num(row.find_all('td', {"class": "cjud"})[0].text.strip())
                current_component["J2"] = str2num(row.find_all('td', {"class": "cjud"})[1].text.strip())
                current_component["J3"] = str2num(row.find_all('td', {"class": "cjud"})[2].text.strip())
                current_component["J4"] = str2num(row.find_all('td', {"class": "cjud"})[3].text.strip())
                current_component["J5"] = str2num(row.find_all('td', {"class": "cjud"})[4].text.strip())
                current_component["J6"] = str2num(row.find_all('td', {"class": "cjud"})[5].text.strip())
                current_component["J7"] = str2num(row.find_all('td', {"class": "cjud"})[6].text.strip())
                current_component["J8"] = str2num(row.find_all('td', {"class": "cjud"})[7].text.strip())
                current_component["J9"] = str2num(row.find_all('td', {"class": "cjud"})[8].text.strip())
                components.append(current_component)
            if count == (n_elements + 5):
                # skating skills
                current_component = dict()
                current_component['component_desc'] = "Skating Skills"
                current_component['factor']  = str2num(row.find_all('td',{'class': 'cf'})[0].text)
                current_component['scores_of_panel']  = str2num(row.find_all('td', {'class': 'panel'})[0].text)
                current_component['ref'] = None # IDK?
                current_component["J1"] = str2num(row.find_all('td', {"class": "cjud"})[0].text.strip())
                current_component["J2"] = str2num(row.find_all('td', {"class": "cjud"})[1].text.strip())
                current_component["J3"] = str2num(row.find_all('td', {"class": "cjud"})[2].text.strip())
                current_component["J4"] = str2num(row.find_all('td', {"class": "cjud"})[3].text.strip())
                current_component["J5"] = str2num(row.find_all('td', {"class": "cjud"})[4].text.strip())
                current_component["J6"] = str2num(row.find_all('td', {"class": "cjud"})[5].text.strip())
                current_component["J7"] = str2num(row.find_all('td', {"class": "cjud"})[6].text.strip())
                current_component["J8"] = str2num(row.find_all('td', {"class": "cjud"})[7].text.strip())
                current_component["J9"] = str2num(row.find_all('td', {"class": "cjud"})[8].text.strip())
                components.append(current_component)
            if count == (n_elements + 13):
                # General Component Factor
                general_component_factor = str2num(row.find_all('td', {"class": "gcfv"})[0].text.strip())
                total_factored_score = str2num(row.find_all('td', {"class": "score"})[0].text.strip())

        skater_info['ded'] = tables[(4 * i) + 2]
        # print(f"{skater_info['ded']}")
        skater_info['total_ded'] = str2num(skater_info['ded'].find_all('th')[7].get_text())
        try:
            # print(f"****{skater_info['ded'].find_all('td')}****")
            key = skater_info['ded'].find_all('td')[1].get_text()
            skater_info['ded_' + key] = skater_info['ded'].find_all('td')[2].get_text()
        except:
            pass
        skater_info['maj'] = tables[(4 * i) + 3]
        # for item in skater_info['maj'].find_all('td'):
        #    skater_info[item['class'][0]] = item.get_text()
        name = skater_info['sum'].find_all('td')[1].get_text()
        metadata = dict()
        metadata["competition"] = soup.title.text
        metadata["name"] = name
        metadata["nation"] = skater_info['sum'].find_all('td',{'class':'nation'})[0].text
        metadata["program"] = skater_info['sum'].find_all('th',{'class':'evt'})[0].text
        metadata["rank"] = int(skater_info['sum'].find_all('td')[0].text)
        metadata["starting_number"] = None
        metadata["total_component_score"] = str2num(skater_info['sum'].find_all('td',{'class':'totComp'})[0].text)
        metadata["total_deductions"] = str2num(skater_info['sum'].find_all('td',{'class':'totDed'})[0].text)
        metadata["total_element_score"] = str2num(skater_info['sum'].find_all('td',{'class':'totElm'})[0].text)
        metadata["total_segment_score"] = str2num(skater_info['sum'].find_all('td',{'class':'totSeg'})[0].text)
        metadata["total_base_value"] = str2num(skater_info['elm'].find_all('td',{'class':'tbvv'})[0].text)
        metadata["general_component_factor"] = general_component_factor

        # put it all together
        skater_json = dict()
        skater_json['metadata'] = metadata
        skater_json['elements'] = elements
        skater_json['components'] = components
        performances.append(skater_json)
    event_sheet['file'] = filename
    event_sheet['performances'] = performances
    return event_sheet


# filename = 'soup-test/segm010.html'
# print("*************parsing started****************")
# event_sheet = parse_html_detailed_scores(filename)
# print("*************parsing completed****************")
# # json_str = json.dumps(event_sheet, indent=4)

# filename = 'soup-test/CAT010SEG010.html'
# print("*************parsing started****************")
# event_sheet = parse_html_program(filename)
# print("*************parsing completed****************")
# json_str = json.dumps(event_sheet, indent=4)

filename = 'soup-test/comp_index.html'
print("*************parsing started****************")
event_sheet = parse_html_competition(filename)
print("*************parsing completed****************")
json_str = json.dumps(event_sheet, indent=4)

print(json_str)
