import numpy as np
import matplotlib.pyplot as plt
from numpy import genfromtxt
import scipy.interpolate as interpolate
from ClCd.Modified_lifting_line import ModLiftingLine
"""This is a preliminary tool box to be used to estimate the available power from a hydro-kinetic kite used 
in an oscillatory style of movement(shallow water streams, eg river or shallow tidal), 
later this will be expanded to full 3D movement """


class FluidProp:
    """ use to pass fluid properties to objects that need it only used for desinty as of now"""
    def __init__(self, velocity_mag=1.5):
        self.density = 997  # kg/m^3


class ActuatorDisk:
    """ idealised actuator disk as an ideal turbine, other builds have turbine with empirical data"""
    def __init__(self, fluidprop=FluidProp()):
        self.duct_exit_area = 0.2*2*0.1  # m^3
        self.density = fluidprop.density  # kg\m^3
        self.bpvr = 1  # back pressure velocity ratio of a ducted turbine
        self.induction_ratio = 0.33

    def thrust_ideal(self, v):
        # calculates thrust force normal to disk using upstream velocity
        c_t_total = self.bpvr*4*self.induction_ratio*(1-self.induction_ratio)
        thrust = 0.5 * c_t_total * self.density*self.duct_exit_area*v**2
        return thrust

    def power_ideal(self, v):
        # calculates power force normal to disk
        c_p_total = self.bpvr*4 * self.induction_ratio * (1 - self.induction_ratio)**2
        power = 0.5 * c_p_total * self.density*self.duct_exit_area*v**3
        return power

    def change_specific_energy_ideal(self, v):
        # calculates the change in specific potential energy (similar to hydraulic head) across the disk
        del_e = 4*self.induction_ratio*(1-self.induction_ratio)*0.5*v**2
        return del_e

    def volume_flow(self, v):
        # calculates volume flow across the disk
        v_diff_exit = self.bpvr*(1-self.induction_ratio)*v
        volume_flow = self.duct_exit_area*v_diff_exit
        return volume_flow


class Tether:
    """ simple tether place holder for now"""
    def __init__(self, unloaded_length=25):
        self.length = unloaded_length  # m


class Surface:
    """ generic surface aero-properties can be set by the cl_cd object"""
    def __init__(self, area, cl_cd_obj=None, fluidprop=FluidProp()):
        self.cl_cd_obj = cl_cd_obj
        self.fluidprop = fluidprop
        self.surface_area = area

    def lift_drag(self, aoa, velocity_magnitude):
        if self.cl_cd_obj is not None:
            cl, cd = self.cl_cd_obj.cl_cd(aoa)
            lft = self.calculate_force(cl, velocity_magnitude, self.fluidprop.density)
            drg = self.calculate_force(cd, velocity_magnitude, self.fluidprop.density)
        else:
            drg = 0
            lft = 0
        return lft, drg

    def calculate_force(self, c, velocity_magnitude, density):
        return c*self.surface_area*0.5*density*velocity_magnitude**2


class TempCraft:
    """ this serves as a quick, dirty and temporary craft. only consists of a wing and turbine
    (control surfaces will be included in future builds)"""

    def __init__(self, fluidprop =FluidProp()):
        self.mass = 100
        wing_cd0 = 0.03
        wing_ar = 10
        wing_oswald_e = 0.9
        wing_aoa_stall = (14/180)*np.pi
        wing_area = 0.2*2
        wing_cld = ModLiftingLine(wing_cd0, wing_ar, wing_oswald_e, wing_aoa_stall)  # modified to include post stall
        wing = Surface(wing_area, wing_cld, fluidprop)
        turbine = ActuatorDisk(fluidprop)
        self.surfaces = [wing]
        self.turbines = [turbine]


class TempSystem:

    """ this serves as a quick, dirty and temporary simulator for the combined system
    which handles the state and dynamics of the system.
    Later the entire thing will be vectorised and positions will be handled by the objects themselves"""

    def __init__(self, craft=TempCraft(), tether=Tether()):
        self.v_stream = 1.5
        self.craft = craft
        self.tether = tether
        self.beta = 0
        self.theta = 0  #
        self.theta_d = 0  # Theta dot
        self.theta_dd = 0  # Theta double dot
        self.theta_dd_old = 0
        self.smoothing_factor = 0.01
        self.power = 0

    def update_theta_dd(self):
        v_theta = self.theta_d * self.tether.length
        gamma = np.pi/2-self.beta
        w_theta = self.v_stream * np.sin(self.theta) + v_theta
        w_r = self.v_stream * np.cos(self.theta)
        w_t = (w_theta ** 2 + w_r ** 2) ** 0.5
        delta = np.arccos(w_theta / w_t)
        aoa = delta-gamma
        w_tur = w_t * np.cos(aoa)

        #  calculate forces
        lift, drag = self.craft.surfaces[0].lift_drag(aoa, w_t)
        thrust = self.craft.turbines[0].thrust_ideal(w_tur)
        self.power = self.craft.turbines[0].power_ideal(w_tur)
        volume_flow = self.craft.turbines[0].volume_flow(w_tur)
        del_e = self.craft.turbines[0].change_specific_energy_ideal(w_tur)
        f_theta = -drag*np.cos(delta)+lift*np.sin(delta)-thrust*np.cos(delta)
        self.theta_dd = f_theta / (self.craft.mass*self.tether.length)

        #  trackers for testing and will get removed later
        self.aoa = aoa
        self.lift = lift
        self.drag = drag
        self.thrust = thrust
        self.w_t = w_t

    def step_time(self, dt):
        #  step forward in time (simple Euler method)
        self.theta_dd = self.theta_dd*(1-self.smoothing_factor)+self.theta_dd_old*self.smoothing_factor
        self.update_theta_dd()
        self.theta_d = self.theta_d + self.theta_dd*dt
        self.theta = self.theta + self.theta_d * dt
        self.theta_dd_old = self.theta_dd


class SystemController:
    def __init__(self):
        self.dummy = 0

    def simple_oscillate_control(self, time, amp, time_period):
        """ used as a control system just changes beta with time"""
        time_shift = 0
        del_epsi = 2 * np.pi * time_shift / time_period
        epsi = 2 * np.pi * time / time_period
        beta = amp * np.sin(epsi + del_epsi)
        return beta

    def get_delta(self, theta, v_theta, v_stream):
        w_theta = v_stream * np.sin(theta) + v_theta
        w_r = v_stream * np.cos(theta)
        w_t = (w_theta ** 2 + w_r ** 2) ** 0.5
        delta = np.arccos(w_theta / w_t)
        return delta

    def aoa_control(self, aoa, theta, theta_lim, v_theta, v_stream):
        """ used as a control system sets a fixed aoa"""
        delta = self.get_delta(theta, v_theta, v_stream)
        aoa_out = aoa
        if v_theta > 0 and theta < theta_lim:
            aoa_out = aoa
        elif v_theta > 0 and theta > theta_lim:
            aoa_out = -aoa
        elif v_theta < 0 and theta > -theta_lim:
            aoa_out = -aoa
        elif v_theta < 0 and theta < theta_lim:
            aoa_out = aoa
        gamma = delta - aoa_out
        beta = np.pi / 2 - gamma
        return beta
