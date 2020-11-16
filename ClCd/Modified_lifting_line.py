import numpy as np
import matplotlib.pyplot as plt
from numpy import genfromtxt
import scipy.interpolate as interpolate
import warnings
import os

""" objects for assigning lift and drag properties"""


class ModLiftingLine:
    def __init__(self, cd0, wing_ar, oswald_e, aoa_stall):
        if aoa_stall > (np.pi*20/180) or aoa_stall < 0:
            raise Exception(" stall angle cannot exceed 20 deg or be less than zero")

        if wing_ar <= 0:
            raise Exception(" aspect ratio cannot be equal to or less that 0")

        if wing_ar <= 0:
            raise Exception(" aspect ratio cannot be equal to or less that 0")

        if cd0 < 0:
            raise Exception(" zero lift drag cannot be less that 0")

        self.wing_ar = wing_ar
        self.oswald_e = oswald_e
        self.aoa_stall = aoa_stall
        self.cd0 = cd0
        self.interpolant_lift, self.interpolant_drag = self.build_cl_cd_interpolant()

    def build_cl_cd_interpolant(self):
        # builds cl and cd_stall distribution using lifting line theory. also includes post stall values (fixed)
        # requires further work !!
        cl_a = 2 * np.pi / (1 + (2 / self.wing_ar * self.oswald_e))
        #aoa = np.arange(0, self.aoa_stall, (1 / 180) * np.pi)
        N = 20
        aoa = np.linspace(0, self.aoa_stall, N)

        cl = cl_a * aoa
        strt_d = 3
        strt_l = 5
        cwd = os.path.dirname(__file__)
        cd_csv = genfromtxt(cwd + '\C_d.csv', delimiter=',')
        aoa_d = np.pi * cd_csv[strt_d:, 0] / 180
        cd_d = cd_csv[strt_d:, 1]
        cl_csv = genfromtxt(cwd + '\C_l.csv', delimiter=',')
        aoa_l = np.pi * cl_csv[strt_l:, 0] / 180
        cl_d = cl_csv[strt_l:, 1]

        aoa_f = np.concatenate((aoa, aoa_l))
        cl_f = np.concatenate((cl, cl_d))

        interpolant_drag = interpolate.interp1d(aoa_d, cd_d)
        interpolant_lift = interpolate.interp1d(aoa_f, cl_f)

        return interpolant_lift, interpolant_drag

    def cl_cd(self, aoa):
        if abs(aoa) > (np.pi*100/180):
            warnings.warn('angle of attack is out of bounds, max 90 deg')

        cl_t = self.interpolant_lift(abs(aoa))
        if aoa > 0:
            cl = cl_t
        else:
            cl = -cl_t
        if abs(aoa) > self.aoa_stall:
            cd_stall = self.interpolant_drag(abs(aoa))
            warnings.warn('stall is for qualitative purposes only')
        else:
            cd_stall = 0  # stall drag otherwise zero (requires improvements)

        cdi = (cl ** 2) / (np.pi * self.wing_ar * self.oswald_e)

        cd = self.cd0 + cdi + cd_stall
        return cl, cd

    def plot(self):
        cl_a = 2 * np.pi / (1 + (2 / self.wing_ar * self.oswald_e))
        aoa = np.arange(0, self.aoa_stall, (1 / 180) * np.pi)
        cl = cl_a * aoa
        strt_d = 3
        strt_l = 5
        cwd = os.path.dirname(__file__)
        cd_csv = genfromtxt(cwd + '\C_d.csv', delimiter=',')
        aoa_d = np.pi * cd_csv[strt_d:, 0] / 180
        cd_d = cd_csv[strt_d:, 1]
        cl_csv = genfromtxt(cwd + '\C_l.csv', delimiter=',')
        aoa_l = np.pi * cl_csv[strt_l:, 0] / 180
        cl_d = cl_csv[strt_l:, 1]

        N = 200
        amin, amax = np.min(aoa_d), np.max(aoa_d)
        aoa_dq = np.linspace(amin, amax, N)
        aminl, amaxl = 0, np.max(aoa_l)
        aoa_lq = np.linspace(aminl, amaxl, N)

        fig = plt.figure()
        plt.subplot(1, 1, 1)
        plt.plot(180 * aoa_d / np.pi, cd_d, 'xr')
        plt.plot(180 * aoa / np.pi, cl, 'xb')
        plt.plot(180 * aoa_l / np.pi, cl_d, 'xb')
        plt.plot(180 * aoa_dq / np.pi, self.interpolant_drag(aoa_dq), 'r')
        plt.plot(180 * aoa_lq / np.pi, self.interpolant_lift(aoa_lq), 'b')
        plt.show()


if __name__ == '__main__':
    cd0 = 0.03
    wing_ar = 0.3141592653589793
    oswald_e = 0.0031415926535897933
    aoa_stall = 0.0017453292519943296

    # ['Cl error with, para:wing_ar = 0.3141592653589793oswald_e =0.0031415926535897933 aoa_stall = 0.0017453292519943296']
    Mod = ModLiftingLine(cd0, wing_ar, oswald_e, aoa_stall)
    Mod.build_cl_cd_interpolant()
    Mod.plot()

    Mod.interpolant_lift()