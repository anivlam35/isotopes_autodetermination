import requests, time
from bs4 import BeautifulSoup as BS

class ParameterError(Exception):
    def __init__(self, text):
        self.txt = text

def nudat_parsing(dict):
    parameters_dict = {'spnuc':'name', 'nuc':'', 'z':'', 'a':'', 'n':'', 'zmin':'', 'zmax':'', 'amin':'', 'amax':'', 'nmin':'', 'nmax':'', 'evenz':'any',
              'evena':'any', 'evenn':'any', 'tled':'disabled', 'tlmin':'0', 'utlow':'FS', 'tlmax':'1E10', 'utupp':'GY', 'dmed':'disabled',
              'dmn':'ANY', 'rted':'enabled', 'rtn':'G', 'reed':'disabled', 'remin':'661', 'remax':'662', 'ried':'enabled', 'rimin':'1',
              'rimax':'200', 'ord':'zate', 'out':'wp', 'unc':'nds', 'sub':'Search'}
    parameters_dict_keys = parameters_dict.keys()
    for key in dict.keys():
        if key in parameters_dict_keys:
            parameters_dict.update({key:dict.get(key)})
        else:
            raise ParameterError('Wrong parameter name is set!')
    data_str = str(parameters_dict)[1:-1].replace(': ', '=').replace(', ', '&').replace("'", "")
    url = 'https://www.nndc.bnl.gov/nudat3/dec_searchi.jsp'
    url += '?' + data_str
    # f = open('test_html_file.txt', 'w')
    # f.write(requests.get(url).text)
    # f.close()
    # f = open('test_html_file.txt', 'r')
    # ws_html_data = f.read()
    # f.close()

    ws_html_data =requests.get(url).text
    if '500 Internal Server Error' in ws_html_data:
        print('500 Internal Server Error')
        time.sleep(300)
        return nudat_parsing(dict)
    soup = BS(ws_html_data, "html5lib")
    if parameters_dict.get('nuc') == '':
        isotopes = []
        energy_intens = []
        for table in soup.find_all("table", {'cellpadding':"2", 'cellspacing':"1"}):
            isotope = table.tbody.contents[1].find_all('td')[1].contents[0] + table.tbody.contents[1].find_all('td')[2].contents[0]
            if len(table.tbody.contents[1].find_all("td", {'class':"align", 'nowrap':""})[2].contents) == 3:
                hl_time = table.tbody.contents[1].find_all("td", {'class':"align", 'nowrap':""})[2].contents[0].replace('\xa0', '').replace(' ', '')
            elif len(table.tbody.contents[1].find_all("td", {'class':"align", 'nowrap':""})[2].contents) == 1:
                hl_time = table.tbody.contents[1].find_all("td", {'class': "align", 'nowrap': ""})[2].contents[
                    0].replace('\xa0', '').replace(' ', '')
            else:
                list = table.tbody.contents[1].find_all("td", {'class':"align", 'nowrap':""})[2].contents
                hl_time = (list[0][:-3] + 'e' + list[1].contents[0] + list[2]).replace('\xa0', '').replace(' ', '')
            isotopes.append([isotope, hl_time])

        # isotope = table[0].tbody.contents[1].find_all('td')[1].contents[0] + table[0].tbody.contents[1].find_all('td')[2].contents[0]
        # life_time = table[0].tbody.contents[1].find_all("td", {'class':"align", 'nowrap':""})[2].contents[0].replace('\xa0', '')[1:-1]


        for table in soup.find_all("table", {'cellpadding':"2", 'cellspacing':"4"}):
            if len(table.tbody.contents[3].contents[1]) == 1:
                gamma_energy = float(table.tbody.contents[3].contents[1].contents[0].replace('\xa0', '').replace(' ', '').replace('?', '').replace('S', ''))
                intensity = round(float(table.tbody.contents[3].contents[2].contents[0].replace('\xa0', '').replace(' ', '').replace('%','')) / 100,4)
                energy_intens.append([gamma_energy, 0, intensity])
            else:
                # print(table.tbody.contents[3].contents[1].contents)
                gamma_energy = float(table.tbody.contents[3].contents[1].contents[0].replace('\xa0', '').replace(' ', ''))
                try:
                    num_of_symb = len(table.tbody.contents[3].contents[1].contents[0].replace('\xa0', '').replace(' ', '').split('.')[1])
                except:
                    num_of_symb = 0
                gamma_energy_err = round(float(table.tbody.contents[3].contents[1].contents[1].contents[0]) * (10 ** (-num_of_symb)), 4)
                intensity = round(float(table.tbody.contents[3].contents[2].contents[0].replace('\xa0', '').replace(' ', '').replace('%', '')) / 100,4)
                energy_intens.append([gamma_energy, gamma_energy_err, intensity])
        result = [[isotopes[i][0], isotopes[i][1], str(energy_intens[i][0]), str(energy_intens[i][1]), str(energy_intens[i][2])] for i in range(len(isotopes))]
        return result
    else:
        energy_intens = []
        for table in soup.find_all("table", {'cellpadding': "2", 'cellspacing': "4"}):
            for i in range(3, len(table.tbody.contents), 2):
                if 'XR' in str(table.tbody.contents[i]):
                    pass
                else:
                    gamma_energy = float(table.tbody.contents[i].contents[1].contents[0].replace('\xa0', '').replace(' ', ''))
                    gamma_energy_err = round(float(table.tbody.contents[i].contents[1].contents[1].contents[0]) * (10 ** (-len(table.tbody.contents[i].contents[1].contents[0].replace('\xa0', '').replace(' ', '').split('.')[1]))), 6)
                    intensity = round(float(table.tbody.contents[i].contents[2].contents[0].replace('\xa0', '').replace(' ', '').replace('%', '')) / 100, 6)
                    if len(table.tbody.contents[i].contents[2].contents) == 3:
                        intensity_err = round(float(table.tbody.contents[i].contents[2].contents[1].contents[0]) * (10 ** (-len(table.tbody.contents[i].contents[2].contents[0].replace('\xa0', '').replace(' ', '').replace('%', '').split('.')[1]) - 2)), 6)
                    else:
                        intensity_err = 0
                    energy_intens.append([gamma_energy, gamma_energy_err, intensity, intensity_err])
        return energy_intens

def main():
    print(nudat_parsing({'reed': 'enabled', 'remin': '183.63', 'remax': '190.798', 'ried': 'enabled', 'rimin': '0.5'}))


if __name__ == "__main__":
    main()
