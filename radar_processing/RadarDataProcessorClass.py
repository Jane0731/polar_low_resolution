import struct
import numpy as np

class RadarDataProcessor:
    def __init__(self, fname):

        if '.gz' in fname:
            import gzip
            print('unzip files')
            f = gzip.open(fname).read()
        else:
            f = open(fname, "rb").read()
        header_end = 160  # after  160 units is data, before it is header info
        # get header in format char(len=16)+36integers
        header = struct.unpack('<16s36i', f[0:header_end])
        print('header:', header)
        info = np.array(header[1:-1])
        if (len(str(header[0], 'utf-8')) == 12):
            self.name = str(header[0], 'utf-8')[0:16:4]
        else:
            self.name = str(header[0][0:4], 'utf-8')
        # self.name='test'
        self.h_scale = info[0]
        info_flt = info/info[0]
        self.radar_elev = info_flt[1]
        self.rlat = info_flt[2]
        print('rlat:', self.rlat)
        self.rlon = info_flt[3]
        print('rlon:', self.rlon)
        self.yyyy = int(info_flt[4])
        self.mm = int(info_flt[5])
        self.dd = int(info_flt[6])
        self.hh = int(info_flt[7])
        self.mn = int(info_flt[8])
        self.ss = int(info_flt[9])
        self.nyquist = info_flt[10]
        self.nivcp = int(info_flt[11])
        self.itit = info[12]
        self.theta = info_flt[13]       # elevation angle
        self.nray = int(info_flt[14])
        self.ngate = int(info_flt[15])
        self.azm_start = info_flt[16]
        # self.azm_sp = info_flt[17]
        self.azm_sp = 360./self.nray
        self.gate_start = info_flt[18]   # gate start is m
        self.gate_sp = info_flt[19]  # unit=m
        self.var_scale = info_flt[20]
        self.var_miss = info[21]
        self.rf_miss = -44400
        n = self.nray*self.ngate
        data = struct.unpack('<'+str(n)+'i', f[header_end:])
        self.data = np.reshape(data/self.var_scale,
                               (self.nray, self.ngate), order='C')
        print('data_shape:', self.data.shape)