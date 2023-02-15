#!/usr/bin/env python

"""
    datasets.py: This is a data holder module with various datatypes
    1. Layer: Contains individual layer's conductivity and thickness <1D>
    2. Site: Contains sites with individual multiple layer
    3. Holds multiple types of sites/layers
"""

__author__ = "Chakraborty, S."
__copyright__ = ""
__credits__ = []
__license__ = "MIT"
__version__ = "1.0."
__maintainer__ = "Chakraborty, S."
__email__ = "shibaji7@vt.edu"
__status__ = "Research"

import numpy as np
import pandas as pd
from scipy import constants as C


class Layer(object):
    def __init__(self, name, tickness, conductivity):
        self.name = name
        self.thickness = tickness
        self.conductivity = conductivity
        self.resistivity = 1.0 / conductivity
        return


class Site(object):
    def __init__(self, layers, desciption, name):
        self.layers = layers
        self.desciption = desciption
        self.name = name
        return

    def get_thicknesses(self, index=None):
        th = [l.tickness for l in self.layers]
        th = th[index] if index else th
        return th

    def get_conductivities(self, index=None):
        cd = [l.conductivity for l in self.layers]
        cd = cd[index] if index else cd
        return cd

    def get_resistivities(self, index=None):
        rv = [l.resistivity for l in self.layers]
        rv = rv[index] if index else rv
        return rv

    def get_names(self, index=None):
        na = [l.name for l in self.layers]
        na = na[index] if index else na
        return na

    def get(self, index=None):
        o = pd.DataFrame()
        o["names"] = self.get_names(index)
        o["conductivities"] = self.get_conductivities(index)
        o["resistivities"] = self.get_resistivities(index)
        o["thicknesses"] = self.get_thicknesses(index)
        return o

    def calcZ(self, freqs, layer=0):
        freqs = np.asarray(freqs)
        resistivities = np.asarray(self.get_resistivities())
        thicknesses = np.asarray(self.get_thicknesses())
        n = len(resistivities)
        nfreq = len(freqs)
        omega = 2 * np.pi * freqs
        complex_factor = 1j * omega * C.mu_0

        k = np.sqrt(1j * omega[np.newaxis, :] * C.mu_0 / resistivities[:, np.newaxis])
        Z = np.zeros(shape=(n, nfreq), dtype=complex)
        with np.errstate(divide="ignore", invalid="ignore"):
            Z[-1, :] = complex_factor / k[-1, :]
            r = np.zeros(shape=(n, nfreq), dtype=complex)
            for i in range(n - 2, -1, -1):
                r[i, :] = (1 - k[i, :] * Z[i + 1, :] / complex_factor) / (
                    1 + k[i, :] * Z[i + 1, :] / complex_factor
                )
                Z[i, :] = (
                    complex_factor
                    * (1 - r[i, :] * np.exp(-2 * k[i, :] * thicknesses[i]))
                    / (k[i, :] * (1 + r[i, :] * np.exp(-2 * k[i, :] * thicknesses[i])))
                )
        if freqs[0] == 0.0:
            Z[:, 0] = 0.0
        layer = layer if layer else 0
        Z_output = np.zeros(shape=(4, nfreq), dtype=complex)
        Z_output[1, :] = Z[layer, :] * (1.0e-3 / C.mu_0)
        Z_output[2, :] = -Z_output[1, :]
        return Z_output

    @staticmethod
    def init(conductivities, thicknesses, names, desciption, site_name):
        layers = []
        for c, t, n in zip(conductivities, thicknesses, names):
            layers.append(Layer(n, t, c))
        return Site(layers, desciption, site_name)


PROFILES = dict(
    BM=Site.init(
        conductivities=[0.2, 0.0003333, 0.02, 0.1, 1.12201],
        thicknesses=[2000, 75000, 332000, 250000, np.inf],
        names=[
            "Sediments",
            "Crust",
            "Lithosphere",
            "Upper Mantle",
            "Lower Mantle",
        ],
        desciption="This model is Ben's model",
        site_name="Ben's Model",
    ),
    OM=Site.init(
        conductivities=[3.3333333, 0.2, 0.0003333, 0.02, 0.1, 1.12201],
        thicknesses=[1000, 2000, 75000, 332000, 250000, np.inf],
        names=[
            "Seawater",
            "Sediments",
            "Crust",
            "Lithosphere",
            "Upper Mantle",
            "Lower Mantle",
        ],
        desciption="This model is modified Ben's model. An 1 km thick ocean on top of Ben's model.",
        site_name="Ocean Model",
    ),
    DB=Site.init(
        conductivities=[0.00005, 0.005, 0.001, 0.01, 0.3333333],
        thicknesses=[15000, 10000, 125000, 200000, np.inf],
        names=[
            "Sediments",
            "Crust",
            "Lithosphere",
            "Upper Mantle",
            "Lower Mantle",
        ],
        desciption="This model is suggested by David.",
        site_name="David's Model",
    ),
    UN=Site.init(
        conductivities=[0.2, 0.2, 0.2, 0.2, 1.12201],
        thicknesses=[2000, 75000, 332000, 250000, np.inf],
        names=[
            "Sediments",
            "Crust",
            "Lithosphere",
            "Upper Mantle",
            "Lower Mantle",
        ],
        desciption="This model is suggested by David.",
        site_name="Uniform Model",
    ),
    CS=Site.init(
        conductivities=[3.3333333, 0.3333333, 0.00033333333, 0.001, 0.01, 0.1, 1],
        thicknesses=[100, 3000, 20000, 140000, 246900, 250000, 340000],
        names=[
            "Seawater",
            "Sediments",
            "Crust",
            "Lithosphere",
            "Upper Mantle",
            "Transition Zone",
            "Lower Mantle",
        ],
        desciption="Used in IGS study by David",
        site_name="Continental Shelf",
    ),
    SO=Site.init(
        conductivities=[3.3333333, 0.3333333, 0.00033333333, 0.001, 0.01, 0.1, 1],
        thicknesses=[1000, 2000, 10000, 70000, 327000, 250000, 340000],
        names=[
            "Seawater",
            "Sediments",
            "Crust",
            "Lithosphere",
            "Upper Mantle",
            "Transition Zone",
            "Lower Mantle",
        ],
        desciption="Used in IGS study by David",
        site_name="Shallow Ocean",
    ),
    DO=Site.init(
        conductivities=[3.3333333, 0.3333333, 0.00033333333, 0.001, 0.01, 0.1, 1],
        thicknesses=[4000, 2000, 10000, 70000, 327000, 250000, 340000],
        names=[
            "Seawater",
            "Sediments",
            "Crust",
            "Lithosphere",
            "Upper Mantle",
            "Transition Zone",
            "Lower Mantle",
        ],
        desciption="Used in IGS study by David",
        site_name="Deep Ocean",
    ),
)
