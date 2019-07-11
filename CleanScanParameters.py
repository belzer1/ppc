import csv 

class CleanScanParameters:
    """
    Manages the lasers required currents and temperatures for a given temperature/power
    This information is needed when doing Clean Jumps or Clean Scans
    """
    def __init__(self,power):
        self.frequency_full = []
        self.sled_full = []
        self.filter1_full = []
        self.filter2_full = []
        self.adjust1_full = []
        self.adjust2_full = []
        self.current_full = []

        with open('clean_scan_parameters/' + power + '.csv','r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            for row in reader:
                self.frequency_full.append(float(row[1]))
                self.sled_full.append(float(row[2]))
                self.filter1_full.append(float(row[3]))
                self.filter2_full.append(float(row[4]))
                self.current_full.append(float(row[5]))
                self.adjust1_full.append(float(row[6]))
                self.adjust2_full.append(float(row[7])) 

    def set_frequency_range(self,freq_start,freq_stop, freq_spacing):
        """
        freq_spacing must be multiple of 0.050 (50 GHz)
        """
        spacing = int((freq_spacing/0.05)) #freq_spacing input in GHz
        start = self.frequency_full.index(freq_start)
        stop = self.frequency_full.index(freq_stop)+1

        self.frequency = self.frequency_full[start:stop:spacing]
        self.sled = self.sled_full[start:stop:spacing]
        self.filter1 = self.filter1_full[start:stop:spacing]
        self.filter2 = self.filter2_full[start:stop:spacing]
        self.adjust1 = self.adjust1_full[start:stop:spacing]
        self.adjust2 = self.adjust2_full[start:stop:spacing]
        self.current = self.current_full[start:stop:spacing]
