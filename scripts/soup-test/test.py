from bs4 import BeautifulSoup

fp = open('segm010.html', 'r')
soup = BeautifulSoup(fp, features='html.parser')
tables = soup.find_all('table')

n_skaters = len(tables) // 4  # each skater has 4 tables
event_sheet = list()

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
    print(f"Detected {n_elements} elements")
    elements = []
    for count,row in enumerate(skater_info['elm'].find_all('tr'),start=0):
        if count == 0:
            continue
        if count >= 1 and count <= n_elements:
            current_elem = dict()
            current_elem["base_value"] = row.find_all('td', {"class": "bv"})[0].text
            current_elem["credit_flag"] = row.find_all('td', {"class": "num"})[0].text
            current_elem["element_desc"] = row.find_all('td', {"class": "elem"})[0].text
            current_elem["element_num"] = row.find_all('td', {"class": "num"})[0].text
            current_elem["goe"] = row.find_all('td', {"class": "goe"})[0].text
            current_elem["info_flag"] = row.find_all('td', {"class": "info"})[0].text
            current_elem["ref"] = row.find_all('td', {"class": "ref"})[0].text
            current_elem["scores_of_panel"] = row.find_all('td', {"class": "psv"})[0].text
            current_elem["J1"] = row.find_all('td', {"class": "jud"})[0].text.strip()
            current_elem["J2"] = row.find_all('td', {"class": "jud"})[1].text.strip()
            current_elem["J3"] = row.find_all('td', {"class": "jud"})[2].text.strip()
            current_elem["J4"] = row.find_all('td', {"class": "jud"})[3].text.strip()
            current_elem["J5"] = row.find_all('td', {"class": "jud"})[4].text.strip()
            current_elem["J6"] = row.find_all('td', {"class": "jud"})[5].text.strip()
            current_elem["J7"] = row.find_all('td', {"class": "jud"})[6].text.strip()
            current_elem["J8"] = row.find_all('td', {"class": "jud"})[7].text.strip()
            current_elem["J9"] = row.find_all('td', {"class": "jud"})[8].text.strip()
            print(current_elem)
            elements.append(current_elem)

    skater_info['ded'] = tables[(4 * i) + 2]
    print(f"{skater_info['ded']}")
    skater_info['total_ded'] = skater_info['ded'].find_all('th')[7].get_text()
    try:
        print(f"****{skater_info['ded'].find_all('td')}****")
        key = skater_info['ded'].find_all('td')[1].get_text()
        skater_info['ded_' + key] = skater_info['ded'].find_all('td')[2].get_text()
    except:
        pass
    skater_info['maj'] = tables[(4 * i) + 3]
    # for item in skater_info['maj'].find_all('td'):
    #    skater_info[item['class'][0]] = item.get_text()
    name = skater_info['sum'].find_all('td')[1].get_text()
    skater_info['name'] = name
    event_sheet.append(skater_info)

print("*************parsing completed****************")

print(event_sheet[0])
