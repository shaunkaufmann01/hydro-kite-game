import numpy as np
import matplotlib.pyplot as plt
from numpy import genfromtxt
import scipy.interpolate as interpolate
import os

""" objects for assigning lift and drag properties"""


class ModLiftingLine:
    def __init__(self, cd0, wing_ar, oswald_e, aoa_stall):
        self.wing_ar = wing_ar
        self.oswald_e = oswald_e
        self.aoa_stall = aoa_stall
        self.cd0 = cd0
        self.cl_spline, self.cd_stall_spline = self.build_cl_cd_spline()

    def build_cl_cd_spline(self, plot=False):
        # builds cl and cd_stall distribution using lifting line theory. also includes post stall values (fixed)
        # requires further work !!
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

        aoa_f = np.concatenate((aoa, aoa_l))
        cl_f = np.concatenate((cl, cl_d))

        td, coe_d, kd = interpolate.splrep(aoa_d, cd_d, s=0, k=2)
        spline_drag = interpolate.BSpline(td, coe_d, kd, extrapolate=False)

        tf, coe_f, kf = interpolate.splrep(aoa_f, cl_f, s=0, k=2)
        spline_liftt = interpolate.BSpline(tf, coe_f, kf, extrapolate=False)

        if plot:
            tl, coe_l, kl = interpolate.splrep(aoa_l, cl_d, s=0, k=2)
            spline_lift = interpolate.BSpline(tl, coe_l, kl, extrapolate=False)

            N = 100
            xmin, xmax = np.min(aoa_d), np.max(aoa_d)
            xx = np.linspace(xmin, xmax, N)
            xminl, xmaxl = np.min(aoa_l), np.max(aoa_l)
            xxl = np.linspace(xminl, xmaxl, N)
            xminf, xmaxf = np.min(aoa_f), np.max(aoa_f)
            xxf = np.linspace(xminf, xmaxf, N)

            fig = plt.figure()
            plt.subplot(1, 1, 1)
            plt.plot(180 * aoa_d / np.pi, cd_d, 'x')
            plt.plot(180 * aoa / np.pi, cl, 'x')
            plt.plot(180 * aoa_l / np.pi, cl_d, '*')
            plt.plot(180 * xx / np.pi, spline_drag(xx), 'r')
            plt.plot(180 * xxl / np.pi, spline_lift(xxl), 'g')
            plt.plot(180 * xxf / np.pi, spline_liftt(xxf), 'b')
            plt.plot(180 * aoa_f / np.pi, cl_f, '+')

        return spline_liftt, spline_drag

    def cl_cd(self, aoa):
        cl_t = self.cl_spline(abs(aoa))
        if aoa > 0:
            cl = cl_t
        else:
            cl = -cl_t
        if abs(aoa) > self.aoa_stall:
            cd_stall = self.cd_stall_spline(abs(aoa))
        else:
            cd_stall = 0  # stall drag otherwise zero (requires improvements)

        cdi = (cl ** 2) / (np.pi * self.wing_ar * self.oswald_e)

        cd = self.cd0 + cdi + cd_stall
        return cl, cd



