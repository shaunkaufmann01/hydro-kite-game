import unittest
from ClCd.Modified_lifting_line import ModLiftingLine
import numpy as np
import scipy.interpolate as interpolate
from numpy import genfromtxt
import os

# loading in data
strt_d = 3
strt_l = 5
cwd = os.path.dirname(__file__)
path_cl = cwd[0:-4] + 'ClCd\C_l.csv'
cl_csv = genfromtxt(path_cl, delimiter=',')
aoa_post_stall = np.pi * cl_csv[strt_l:, 0] / 180
cl_data_stall = cl_csv[strt_l:, 1]

path_cd = cwd[0:-4] + 'ClCd\C_d.csv'
cd_csv = genfromtxt(path_cd, delimiter=',')
aoa_post_stall_d = np.pi * cd_csv[strt_l:, 0] / 180
cd_data_stall_d = cd_csv[strt_l:, 1]
#


class TestModLiftingLine(unittest.TestCase):
    def setUp(self):
        self.cd0 = np.pi * np.array([0, 0.5, 0.9, 1])
        self.infinity = float("inf")
        self.wing_ar = np.pi * np.array([0.1, 1, 5, 200, 1000, self.infinity])
        self.oswald_e = np.pi * np.array([0.001, 0.5, 0.9, 1])
        self.aoa_stall = np.pi * np.array([0.1, 5, 10, 14, 16, 19]) / 180

        # exception checks
        self.aoa_stall_except = 21
        self.cd0_except = -0.1

    # self.assertEqual(1.225, 1)

    def test_build_cl_cd_interpolant(self):
        """ used to check the lift curver for different design paramters """
        N = 4
        for wing_art in self.wing_ar:
            for oswald_et in self.oswald_e:
                for aoa_stallt in self.aoa_stall:
                    test_instance = ModLiftingLine(0.01, wing_art, oswald_et, aoa_stallt)
                    interpolant_lift, interpolant_drag = test_instance.build_cl_cd_interpolant()
                    aoa = np.linspace(0, aoa_stallt, N)
                    for a in aoa:
                        with self.subTest():
                            cl_a = 2 * np.pi / (1 + (2 / wing_art * oswald_et))
                            cl_check = cl_a * a
                            message = [
                                'pre stall Cl error with, para:' + 'wing_ar = ' + str(wing_art) + 'oswald_e =' + str(
                                    oswald_et) + ' aoa_stall = ' + str(aoa_stallt)]
                            self.assertAlmostEqual(interpolant_lift(a), cl_check, msg=message)

                    for i in range(len(aoa_post_stall)):
                        with self.subTest():
                            message = [
                                'post stall Cl error with, para:' + 'wing_ar = ' + str(wing_art) + 'oswald_e =' + str(
                                    oswald_et) + ' aoa_stall = ' + str(aoa_stallt)]
                            self.assertAlmostEqual(interpolant_lift(aoa_post_stall[i]), cl_data_stall[i], msg=message)

                    for i in range(len(aoa_post_stall_d)):
                        with self.subTest():
                            message = ['Cd error with, para:' + 'wing_ar = ' + str(wing_art) + 'oswald_e =' + str(
                                oswald_et) + ' aoa_stall = ' + str(aoa_stallt)]
                            self.assertAlmostEqual(interpolant_drag(aoa_post_stall_d[i]), cd_data_stall_d[i],
                                                   msg=message)

    def test_cl_cd(self):
        aoa = np.arange((-90 / 180) * np.pi, (90 / 180) * np.pi, (5 / 180) * np.pi)
        aoa_stall = np.pi * 14 / 180
        wing_art = 10
        oswald_et = 0.9
        test_instance = ModLiftingLine(0.01, wing_art, oswald_et, aoa_stall)

        aoa_post_stall = np.pi * cl_csv[strt_l:, 0] / 180
        cl_data_stall = cl_csv[strt_l:, 1]

        aoa_post_stall_d = np.pi * cd_csv[strt_l:, 0] / 180
        cd_data_stall_d = cd_csv[strt_l:, 1]

        interpolant_drag = interpolate.interp1d(aoa_post_stall_d, cd_data_stall_d)
        interpolant_lift = interpolate.interp1d(aoa_post_stall, cl_data_stall)

        for a in aoa:
            with self.subTest():
                cl, cd = test_instance.cl_cd(a)
                if abs(a) < aoa_stall:
                    cl_a = 2 * np.pi / (1 + (2 / wing_art * oswald_et))
                    cl_check = cl_a * a
                    message = ['pre stall Cl error with aoa = ' + str(180 * a / np.pi)]
                    self.assertAlmostEqual(cl, cl_check, msg=message)

                """   needs more work
                else:
                    "check stall regions this is more qualitative than quantitative so does not need to be accurate"
                    cd_check = interpolant_drag(abs(a))
                    cl_check = interpolant_lift(abs(a))
                    if a < 0:
                        cl_check = -cl_check
                    message_l = ['post stall Cl error with aoa = ' + str(180*a/np.pi)]
                    self.assertAlmostEqual(cl, cl_check, msg=message_l, delta=1)
                    message_d = ['post stall CD error with aoa = ' + str(180*a/np.pi)]
                    self.assertAlmostEqual(cd, cd_check, msg=message_d,  delta=1)
                """


# Some code to make the tests actually run.
if __name__ == '__main__':
    unittest.main()
