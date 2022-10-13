from nudat_parsing import nudat_parsing as npar
import numpy as np

class ExperimentalData():
    def __init__(self, file):
        f = open(file, 'r')
        lines = f.readlines()
        f.close()
        calibration_pars = [0.49481662, 27.7425981, 1.00485671e-04, 2.16712299e-01]
        self.chanel = []
        self.energy = []
        self.energy_err = []
        self.intensity = []
        self.intensity_err = []
        self.fwhm = []
        self.fwhm_err = []
        for i in range(3, len(lines)):
            data = [float(el) for el in lines[i].split('\t')[2:-2]]
            self.chanel.append(data[0])
            self.energy.append(round(data[0] * calibration_pars[0] + calibration_pars[1], 3))
            self.energy_err.append(round(np.sqrt((data[3] ** 2) + (data[0] * calibration_pars[2]) ** 2 + calibration_pars[3] ** 2),3))
            self.intensity.append(data[4])
            self.intensity_err.append(data[5])
            self.fwhm.append(data[6])
            self.fwhm_err.append(data[7])

    def __delete__(self, en):
        index = self.energy.index(en)
        self.chanel.pop(index)
        self.energy.pop(index)
        self.energy_err.pop(index)
        self.intensity.pop(index)
        self.intensity_err.pop(index)
        self.fwhm.pop(index)
        self.fwhm_err.pop(index)

    def ordering(self, myarr, indexes):
        new_arr = []
        for index in indexes:
            new_arr.append(myarr[index])
        return new_arr

    def intensitysort(self):
        local_intens = sorted(self.intensity.copy(), reverse=True)
        indxs = []
        for el in local_intens:
            indxs.append(self.intensity.index(el))

        self.chanel = [self.chanel[el] for el in indxs]
        self.energy = [self.energy[el] for el in indxs]
        self.energy_err = [self.energy_err[el] for el in indxs]
        self.intensity = [self.intensity[el] for el in indxs]
        self.intensity_err = [self.intensity_err[el] for el in indxs]
        self.fwhm = [self.fwhm[el] for el in indxs]
        self.fwhm_err = [self.fwhm_err[el] for el in indxs]



def search_isotopes(en, err, isotopes):
    result = []
    e_min = en - err
    e_max = en + err
    print(e_min, e_max)
    nd_data = npar({'reed': 'enabled', 'remin': str(e_min), 'remax': str(e_max), 'ried': 'enabled', 'rimin': '0.5'})
    print(e_min, e_max)
    for sugg in nd_data:
        if sugg[0] in isotopes:
            result.append(sugg)
    if len(result) == 0:
        return search_isotopes(en, err*2, isotopes)
    else:
        return result


def main():
    data = ExperimentalData('results.txt')
    # k = data.intensity.index(max(data.intensity))

    f = open('radioactive_rows.txt', 'r')
    isotopes = f.read().split(',')
    f.close()
    isotopes.append('40K')
    isotopes.append('137Cs')



    f = open('isotopes_determination.txt', 'w')
    for k in range(len(data.energy)):
        f.write(str(data.energy[k]) + ':\n')
        result_part = search_isotopes(data.energy[k], data.energy_err[k], isotopes)
        print(result_part)
        for el in result_part   :
            print(el)
            f.write('\t' + ('\t').join(el) + '\n')
        f.write('\n')
        print('\n', 'recorded', '\n')
    f.close()







if __name__=="__main__":
    main()