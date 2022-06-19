"""
Python model 'Test_Model2Food.py'
Translated using PySD 
"""

from pathlib import Path
import numpy as np
import xarray as xr

from pysd.py_backend.statefuls import Integ
from pysd import Component

__pysd_version__ = "3.2.0"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 1,
    "final_time": lambda: 13,
    "time_step": lambda: 1 / 4,
    "saveper": lambda: time_step(),
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="INITIAL TIME", units="Months", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    The initial time for the simulation.
    """
    return __data["time"].initial_time()


@component.add(
    name="FINAL TIME", units="Months", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    The final time for the simulation.
    """
    return __data["time"].final_time()


@component.add(
    name="TIME STEP", units="Months", comp_type="Constant", comp_subtype="Normal"
)
def time_step():
    """
    The time step for the simulation.
    """
    return __data["time"].time_step()


@component.add(
    name="SAVEPER",
    units="Months",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1},
)
def saveper():
    """
    The save time step for the simulation.
    """
    return __data["time"].saveper()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(
    name="Births",
    units="Per Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"birth_rate": 1, "population": 1},
)
def births():
    return birth_rate() * population()


@component.add(
    name="Deaths",
    units="Per Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"death_rate": 1, "population": 1},
)
def deaths():
    return death_rate() * population()


@component.add(
    name="Food Available Per Person",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"food_available": 1, "population": 1},
)
def food_available_per_person():
    return food_available() / population()


@component.add(
    name="Birth Rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"food_available_per_person": 1},
)
def birth_rate():
    return food_available_per_person() * 0.01


@component.add(
    name="Death Rate",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"food_available_per_person": 1},
)
def death_rate():
    return np.interp(
        food_available_per_person(),
        [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
        [
            2.0,
            1.341,
            0.8987,
            0.6024,
            0.4038,
            0.2707,
            0.1814,
            0.1216,
            0.08152,
            0.05465,
            0.03663,
        ],
    )


@component.add(name="Food Available", comp_type="Constant", comp_subtype="Normal")
def food_available():
    return 100000000


@component.add(
    name="Population",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_population": 1},
    other_deps={
        "_integ_population": {"initial": {}, "step": {"births": 1, "deaths": 1}}
    },
)
def population():
    """
    80000000 people
    """
    return _integ_population()


_integ_population = Integ(
    lambda: births() - deaths(), lambda: 80000000, "_integ_population"
)
