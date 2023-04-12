from bs4 import BeautifulSoup

fp = open('segm010.html','r')
soup = BeautifulSoup(fp, features='html.parser')
tables = soup.find_all('table')

n_skaters = len(tables)//4 # each skater has 4 tables
event_sheet = list()

for i in range(n_skaters):
    skater_info = dict()
    skater_info['sum'] = tables[4*i]
    for item in skater_info['sum'].find_all('td'):
        skater_info[item['class'][0]] = item.get_text()
    #skater_info['elm'] = tables[(4*i)+1]
    #for item in skater_info['elm'].find_all('td'):
    #    skater_info[item['class'][0]] = item.get_text()
    skater_info['ded'] = tables[(4*i)+2]
    print(f"{skater_info['ded']}")
    skater_info['total_ded'] = skater_info['ded'].find_all('th')[7].get_text()
    try:
        print(f"****{skater_info['ded'].find_all('td')}****")
        key = skater_info['ded'].find_all('td')[1].get_text()
        skater_info['ded_'+key] = skater_info['ded'].find_all('td')[2].get_text()
    except:
        pass
    skater_info['maj'] = tables[(4*i)+3]
    #for item in skater_info['maj'].find_all('td'):
    #    skater_info[item['class'][0]] = item.get_text()
    name = skater_info['sum'].find_all('td')[1].get_text()
    skater_info['name'] = name
    event_sheet.append(skater_info)


print("*************parsing completed****************")

print(event_sheet[0])
