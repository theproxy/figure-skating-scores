from bs4 import BeautifulSoup
from bs4 import Comment
import json
import os
import requests
from urllib.parse import urlparse, quote
import re
import time

def get_version(soup):
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    version = None
    for comment in comments:
        if 'ijsLive' in comment:
            # version = comments[1].strip().split(' ')[-1]
            words = comment.strip().split(' ')
            for word_idx, word in enumerate(words):
                if word == 'ijsLive':
                    version = words[word_idx + 1]

    print(f"Version is {version}")
    return version

def str2num(input):
    # print(f"{input} // {[c for c in input]}")
    if input == '-':
        return '-'
    if input == []:
        return None

    if input == "":
        return None

    return float(input)


def get_html(url, save=True, dir=os.path.join('data','html'), refresh=False):
    """
    Fetches the content of a URL and returns a dictionary with the filename, base URL, and content.
    If save is True, the file is saved as filename in a directory based on the URL.
    If refresh is True, always make a new request even if the file already exists on disk.
    """
    # Extract the filename from the URL
    parsed_url = urlparse(url.strip())
    filename = parsed_url.path.split('/')[-1].strip()

    # Create a directory based on the URL
    path_without_filename = parsed_url.path.rsplit('/', 1)[0] + '/'
    url_dir = os.path.join(dir, parsed_url.netloc, quote(path_without_filename, safe=''))

    if not os.path.exists(url_dir):
        print(f"*** Making {url_dir} directory ***")
        os.makedirs(url_dir, exist_ok=True)


    # Check if the file already exists on disk
    file_path = os.path.join(url_dir, filename)
    if not refresh and os.path.exists(file_path):
        print(f"Using cached file: {file_path}")
        with open(file_path, 'rb') as f:
            content = f.read()
    else:
        print(f"Fetching {url}")
        # Fetch the content from the URL
        response = requests.get(url)
        time.sleep(.5)
        content = response.content

        # Save the file if save is True
        if save:
            with open(file_path, 'wb') as f:
                f.write(content)


    # Create a dictionary with the URL info and return it
    url_info = {
        'filename': parsed_url.path.split('/')[-1],
        'full_path': url,
        'url_path': path_without_filename,
        'base': f"{parsed_url.scheme}://{parsed_url.netloc}",
        'content': content,
        'file_path': file_path,
        'dir_path': url_dir,
    }

    return url_info


def parse_html_competition(filename,detailed=False):
    fp = open(filename,'r')
    soup = BeautifulSoup(fp, features='html.parser')
    fp.close()
    version = get_version(soup)
    competition = dict()

    if version > '2.0' and version < '2.3.0':
        competition['name'] = soup.title.text
        competition['date'] = soup.find_all('h3', {"class": "date"})[0].text
        competition['venue'] = soup.find_all('div')[1].find_all('h3')[1].text
        competition['location'] = soup.find_all('div')[1].find_all('h3')[2].text
        competition['events'] = list()
        event_list = soup.find_all('table')[2].find_all('tr')
        for count, event in enumerate(event_list):
            if count == 0:
                continue  # header
            try:
                event_info = dict()
                event_info['name'] = event.find_all('td', {'class': 'event'})[0].text.strip()
                event_info['datetime'] = event.find_all('td', {'class': 'event'})[1].text.strip()
                event_info['state'] = event.find_all('td', {'class': 'stat'})[0].text.strip()
                event_info['file'] = event.find_all('td', {'class': 'stat'})[0].find('a')['href']
                competition['events'].append(event_info)
            except:
                # Free Dance elements, they are parsed differently #TODO: how does this show category + dance??
                # print(f"Error: {event}")
                event_info = dict()
                event_info['name'] = event.find_all('td', {'class': 'time'})[0].text.strip()
                event_info['datetime'] = event.find_all('td', {'class': 'event'})[0].text.strip()
                event_info['state'] = event.find_all('td', {'class': 'stat'})[0].text.strip()

                #event_info['file'] = event.find_all('td', {'class': 'stat'})[0].find('a')['href']
                #TODO: This has a chance to have no link anywhere
                outside_event_info_file = event.find_all('td', {'class': 'stat'})[0].find('a')
                if outside_event_info_file is not None:
                    event_info['file'] = outside_event_info_file['href']
                else:
                    event_info['file'] = None
                competition['events'].append(event_info)
                continue

    if version >= '2.3.0':

        competition['name'] = soup.title.text
        competition['date'] = soup.find_all('h3',{"class":"date"})[0].text
        competition['venue'] = soup.find_all('div')[1].find_all('h3')[1].text
        competition['location'] = soup.find_all('div')[1].find_all('h3')[2].text
        competition['events'] = list()
        event_list = soup.find_all('table')[2].find_all('tr')
        for count, event in enumerate(event_list):
            try:
                if count == 0:
                    continue # header
                event_info = dict()
                event_info['name'] = event.find_all('td',{'class':'event'})[0].text.strip()
                event_info['datetime'] = event.find_all('td',{'class':'event'})[1].text.strip()
                event_info['state'] = event.find_all('td',{'class':'stat'})[0].text.strip()
                event_info['file'] = event.find_all('td', {'class': 'stat'})[0].find('a')['href']
                competition['events'].append(event_info)
            except Exception as e:
                print(f"Issue with event {event_info['name']} at {competition['name']}")

    return competition


def parse_html_program(filename, detailed=True):
    # print(f"PHP-> {filename}")
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
    try:
        program['detailed'] = soup.find_all('li',{'class':'judgeDetailRef'})[0].find('a')['href']
    except KeyError as e:
        print(f"No key found, probably no detailed scores: {e}")
        program['detailed'] = None

    if detailed == True:
        # get path
        head, tail = os.path.split(filename)
        detailed_file = os.path.join(head,program['detailed'])
        print(f"{head} and {detailed_file}")
        detailed_results = parse_html_detailed_scores(detailed_file)
        program['detailed_resuilts'] = detailed_results

    return program

def parse_html_detailed_scores(filename):
    # print(f"PHDS -> {filename}")
    fp = open(filename, 'r')
    soup = BeautifulSoup(fp, features='html.parser')
    fp.close()
    version = get_version(soup)
    event_sheet = dict()
    performances = list()

    if version > '2.0' and version < '2.3.0':
        tables = soup.find_all('table')
        n_skaters = len(tables) // 4  # each skater has 4 tables
        for i in range(n_skaters):
            skater_info = dict()
            skater_info['sum'] = tables[4 * i]
            skater_info['elm'] = tables[(4 * i) + 1]
            skater_info['ded'] = tables[(4 * i) + 2]
            skater_info['maj'] = tables[(4 * i) + 3]

            ## PARSE SUM TABLE
            for item in skater_info['sum'].find_all('td'):
                skater_info[item['class'][0]] = item.get_text().strip()

            ## PARSE ELM TABLE
            elem_nums = skater_info['elm'].find_all('td', {'class': 'num'})
            n_elements = 0
            for element_num in elem_nums:
                if int(element_num.text) > n_elements:
                    n_elements = int(element_num.text)
            # print(f"Detected {n_elements} elements")

            elements = list()
            components = list()
            for count, row in enumerate(skater_info['elm'].find_all('tr'), start=0):
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
                        current_elem[f"J{judge_count + 1}"] = str2num(current_judge_score)
                    # print(current_elem)
                    elements.append(current_elem)
                if count == n_elements + 1:
                    # total BV and total elem score
                    # total_bv_score = str2num(row.find_all('td',{'class': 'tbvv'})[0].text)
                    total_element_score = str2num(row.find_all('td', {'class': 'tps'})[0].text)
                if count == (n_elements + 2):
                    pass  # header
                if count == (n_elements + 3):
                    # composition
                    current_component = dict()
                    current_component['component_desc'] = "Skating Skills"
                    current_component['factor'] = str2num(row.find_all('td', {'class': 'cf'})[0].text)
                    current_component['scores_of_panel'] = str2num(row.find_all('td', {'class': 'panel'})[0].text)
                    current_component['ref'] = None  # IDK?
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
                    continue
                if count == (n_elements + 5):
                    # presentation
                    current_component = dict()
                    current_component['component_desc'] = "Performance"
                    current_component['factor'] = str2num(row.find_all('td', {'class': 'cf'})[0].text)
                    current_component['scores_of_panel'] = str2num(row.find_all('td', {'class': 'panel'})[0].text)
                    current_component['ref'] = None  # IDK?
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
                if count == (n_elements + 6):
                    continue
                if count == (n_elements + 7):
                    # skating skills
                    try:
                        current_component = dict()
                        current_component['component_desc'] = "Interpretation of the Music"
                        current_component['factor'] = str2num(row.find_all('td', {'class': 'cf'})[0].text)
                        current_component['scores_of_panel'] = str2num(row.find_all('td', {'class': 'panel'})[0].text)
                        current_component['ref'] = None  # IDK?
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
                    except Exception as e:
                        print(f"Exception in detailed parsing {e}, row: {row}, count: {count}")
                if count == (n_elements + 13):
                    # General Component Factor
                    general_component_factor = str2num(row.find_all('td', {"class": "gcfv"})[0].text.strip())
                    total_factored_score = str2num(row.find_all('td', {"class": "score"})[0].text.strip())

            ## PARSE DED TABLE
            ## PARSE MAJ TABLE

            ## Compile Metadata
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

    if version >= '2.3.0':
        tables = soup.find_all('table')

        n_skaters = len(tables) // 4  # each skater has 4 tables


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

def test():

    filename = 'soup-test/SEGM034.html'
    filename = 'soup-test/segm010.html'
    print("*************parsing started****************")
    event_sheet = parse_html_detailed_scores(filename)
    print("*************parsing completed****************")
    detailed_json_str = json.dumps(event_sheet, indent=4)
    #
    filename = 'soup-test/CAT010SEG010.html'
    filename = 'soup-test/CAT036SEG034.html'
    print("*************parsing started****************")
    event_sheet = parse_html_program(filename)
    print("*************parsing completed****************")
    category_json_str = json.dumps(event_sheet, indent=4)

    filename = 'soup-test/comp_index.html'
    filename = 'soup-test/30348.asp'
    print("*************parsing started****************")
    event_sheet = parse_html_competition(filename)
    print("*************parsing completed****************")
    json_str = json.dumps(event_sheet, indent=4)
    print(json_str)
    print(detailed_json_str)
    print(category_json_str)

def remove_comment(line):
    m = re.match(r'^([^#]*)#(.*)$', line)
    if m:  # The line contains a hash / comment
        line = m.group(1)
    return line


if __name__ == "__main__":
    urls = """
    #2023
    https://ijs.usfigureskating.org/leaderboard/results/2023/32241/index.asp #genesse Biennial Invitational
    https://ijs.usfigureskating.org/leaderboard/results/2023/32243/index.asp #north atlatnic
    https://ijs.usfigureskating.org/leaderboard/results/2023/32091/index.asp # 11th annual snowtown invitational
    http://ijs.usfigureskating.org/leaderboard/results/2023/32190/index.asp # Magnolia Open
    https://ijs.usfigureskating.org/leaderboard/results/2023/32268/index.asp # Florida Open
    https://ijs.usfigureskating.org/leaderboard/results/2023/32147/index.asp # 2023 Morris Open
    # Capital Regional Council Kickoff
    https://ijs.usfigureskating.org/leaderboard/results/2023/32228/index.asp # 2023 Southern Connecticut Open
    https://ijs.usfigureskating.org/leaderboard/results/2023/30947/index.asp # Crossroads FSC Spring-Tacular Competition
    https://ijs.usfigureskating.org/leaderboard/results/2023/32083/index.asp # Westchester Classic
    https://ijs.usfigureskating.org/leaderboard/results/2023/32246/index.asp # Northstar Spring Classic
    # Three Rivers Spring Skate (----PDF provided---)
    https://ijs.usfigureskating.org/leaderboard/results/2023/32234/index.asp # May Day Open
    https://ijs.usfigureskating.org/leaderboard/results/2023/32235/index.asp # North Shore Open
    https://ijs.usfigureskating.org/leaderboard/results/2023/32262/index.asp # Central Carolina Skating Classic
    https://ijs.usfigureskating.org/leaderboard/results/2023/32232/index.asp # Nassau County Figure Skating Championships
    # 32nd Annual Spring Skate Festival
    # Colonial Open
    # Cardinal Classic
    # White Rose Invitational
    ######## Midwest
    https://ijs.usfigureskating.org/leaderboard/results/2023/32132/index.asp # 43rd annual northland figure skating competition
    https://ijs.usfigureskating.org/leaderboard/results/2023/32180/index.asp # albert viviani memorial competition
    https://ijs.usfigureskating.org/leaderboard/results/2023/32231/index.asp # alamo skate
    https://ijs.usfigureskating.org/leaderboard/results/2023/32119/index.asp # omaha winter festival skating competition
    https://ijs.usfigureskating.org/leaderboard/results/2023/32260/index.asp # 2023 Columbus Invitational
    https://ijs.usfigureskating.org/leaderboard/results/2023/32099/index.asp # Houston Invitational
    https://ijs.usfigureskating.org/leaderboard/results/2023/32128/index.asp # 2023 Denver Invitational
    https://ijs.usfigureskating.org/leaderboard/results/2023/32222/index.asp # Eau Claire Figure Skating Club 34th Annual
    # Skate Kansas City
    https://ijs.usfigureskating.org/leaderboard/results/2023/32273/index.asp # Louisville Skating Academy Spring Invitational
    https://ijs.usfigureskating.org/leaderboard/results/2023/32151/index.asp # Howard E Van Camp Invitational
    https://ijs.usfigureskating.org/leaderboard/results/2023/32267/index.asp # cleveland invitational championship
    https://ijs.usfigureskating.org/leaderboard/results/2023/32280/index.asp # wim competition
    https://ijs.usfigureskating.org/leaderboard/results/2023/32283/index.asp # for collins classic
    https://ijs.usfigureskating.org/leaderboard/results/2023/32251/index.asp #2023 sugar skate
    https://ijs.usfigureskating.org/leaderboard/results/2023/32157/index.asp # tri-state competition
    https://ijs.usfigureskating.org/leaderboard/results/2023/32216/index.asp #2023 skate nashville
    https://ijs.usfigureskating.org/leaderboard/results/2023/32276/index.asp # spring funtastics
    https://ijs.usfigureskating.org/leaderboard/results/2023/32308/index.asp #skate bloomington 2023
    https://ijs.usfigureskating.org/leaderboard/results/2023/32272/index.asp # skate austin bluebonnet open
    https://ijs.usfigureskating.org/leaderboard/results/2023/0032139/index.asp #47th annual ladybug
    # Spring Fling --- PDF
    https://ijs.usfigureskating.org/leaderboard/results/2023/32213/index.asp #Magic City Ice Classic
    https://ijs.usfigureskating.org/leaderboard/results/2023/32287/index.asp # Memorial Trophy 2023
    # 39th Annual Margaret Faulkner Springtime Invitational
    # Excel and Beyond Competition
    # Traverse City Cherry Classic
    # Metro Indy Skating Challenge
    # Heart of America Invitational
    # Skate Dallas
    #2022
    https://ijs.usfigureskating.org/leaderboard/results/2022/30862/index.asp # excel national festival
    https://ijs.usfigureskating.org/leaderboard/results/2022/30235/index.asp # 10th Annual Snowtown Invitational Competition
    https://ijs.usfigureskating.org/leaderboard/results/2022/30441/index.asp # 2022 Magnolia Open
    https://ijs.usfigureskating.org/leaderboard/results/2022/30348/index.asp # Morris Open
    # PDF??? Cardinal Classic 2022
    https://ijs.usfigureskating.org/leaderboard/results/2022/30455/index.asp # 35th Annual Florida Open Championships
    https://ijs.usfigureskating.org/leaderboard/results/2022/30340/index.asp # Crossroads FSC Spring‐tacular Competition
    https://ijs.usfigureskating.org/leaderboard/results/2022/30357/index.asp # Southern CT Open
    https://ijs.usfigureskating.org/leaderboard/results/2022/30408/index.asp # May Day Open and Compete USA
    http://ijs.usfigureskating.org/leaderboard/results/2022/30356/index.asp # North Shore Open
    https://ijs.usfigureskating.org/leaderboard/results/2022/30266/index.asp # Westchester Classic
    https://ijs.usfigureskating.org/leaderboard/results/2022/30595/index.asp # Colonial Open
    """.strip()
    url_list = []
    for url in urls.split('\n'):
        url_parsed = remove_comment(url).strip()
        if url_parsed != "":
            url_list.append(url_parsed)
    url_list

    competitions = []
    for url in url_list:
        competition = dict()
        content = get_html(url)
        data = parse_html_competition(content['file_path'])
        competition['url'] = url
        competition['meta'] = content
        competition['data'] = data
        competitions.append(competition)

    competition_tree = list()
    for competition in competitions:
        competition_node = dict()
        meta = competition['meta']
        print(f"****** {competition['data']['name']} ******")
        event_list = list()
        for event in competition['data']['events']:
            event_node = dict()
            try:
                event_url = meta['base'] + meta['url_path'] + event['file']
            except Exception as e:
                print(f"Could not get event_url: {e}")
            event_file = get_html(event_url)
            event_info = parse_html_program(event_file['file_path'], detailed=False)
            if event_info['detailed'] != None:
                event_detail_url = meta['base'] + meta['url_path'] + event_info['detailed']
                detailed_file = get_html(event_detail_url)
                try:
                    event_detailed_info = parse_html_detailed_scores(detailed_file['file_path'])
                    event_info['detailed_scores'] = event_detailed_info
                except Exception as e:
                    print(f"Error in {e}: {detailed_file}")
            event_list.append(event_info)

        competition_node['name'] = competition['data']['name']
        competition_node['event'] = event_list
        competition_node['date'] = competition['data']['date']
        competition_tree.append(competition_node)
        write_path = os.path.join('data','json')
        # filename is competition name with begin date appeneded
        filename = "".join(competition_node['name'].split())+"_"+"".join(competition['data']['date'].split(' ')[0].split('/'))
        if not os.path.exists(write_path):
            os.mkdir(write_path,parents=True, exists_ok=True)
        with open(os.path.join(write_path,filename+".json"),'w') as write_fp:
            json.dump(competition_node, write_fp)
