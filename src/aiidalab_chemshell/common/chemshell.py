"""Module containing common settings for configuring ChemShell."""

from enum import Enum, auto, IntEnum
from pathlib import Path
from collections import namedtuple

class BasisSetOptions(Enum):
    """Pre-defined basis set levels for simplified ChemShell inputs."""

    FAST = 0
    BALANCED = auto()
    QUALITY = auto()

    @property
    def label(self) -> str:
        """Convert enum value to a string representation for ChemShell input."""
        match self:
            case BasisSetOptions.FAST:
                return "3-21G"
            case BasisSetOptions.BALANCED:
                return "cc-pvdz"
            case BasisSetOptions.QUALITY:
                return "aug-cc-pvtz"
            case "":
                return ""

    @property
    def functional(self) -> str:
        match self:
            case BasisSetOptions.FAST:
                return "BLYP"
            case BasisSetOptions.BALANCED:
                return "B3LYP"
            case BasisSetOptions.QUALITY:
                return "B3LYP"
            case "":
                return ""

class WorkflowOptions(IntEnum):
    """Enum defining the available ChemShell based AiiDA workflows."""

    GEOMETRY = 0
    SINGLE_POINT = auto()
    ATOMIC_ENERGIES = auto()
    NEB = auto()
    CHARGE_FITTING = auto()
    SOLVATION = auto()

    @property
    def label(self) -> str:
        """Convert enum value into a more human readable string."""
        match self:
            case WorkflowOptions.GEOMETRY:
                return "Geometry Optimisation"
            case WorkflowOptions.SINGLE_POINT:
                return "Single Point Energy"
            case WorkflowOptions.ATOMIC_ENERGIES:
                return "Isolated Atomic Energies"
            case WorkflowOptions.NEB:
                return "Nudged Elastic Band"
            case WorkflowOptions.CHARGE_FITTING:
                return "ESP/RESP Charge Fitting"
            case WorkflowOptions.SOLVATION:
                return "Solvation"
            case _:
                return ""

    @property
    def tab_label(self) -> str:
        """Create a tab title for the given enum option."""
        match self:
            case WorkflowOptions.GEOMETRY:
                return "Optimisation"
            case WorkflowOptions.SINGLE_POINT:
                return "SP Energy"
            case WorkflowOptions.ATOMIC_ENERGIES:
                return "Atomic Energies"
            case WorkflowOptions.NEB:
                return "NEB"
            case WorkflowOptions.CHARGE_FITTING:
                return "Charge Fitting"
            case WorkflowOptions.SOLVATION:
                return "Solvation"
            case _:
                return "ChemShell"

#Props = namedtuple("Props", ["filepath", "label", "cube_length", "name"])
Props = namedtuple("Props", ["label", "cube_length", "name"])
dataroot = Path("/opt/chemsh-py/data/solvents")
class SolventBoxOptions(Enum):
    """Enum defining the available Solvent Boxes."""

    #_ignore_ = 'dataroot'

    WATER80 =  0
    HEPTANE80 = auto()
    METHANOL80 = auto()
    CHLOROFORM80 = auto()

    @property
    def properties(self) -> tuple :
        match self:
            case SolventBoxOptions.WATER80:
                #return Props(dataroot/"water-box80-100ns.pqr", "Water Box 80A cube", 80, "water")
                return Props("Water Box 220A cube", 220, "water")
            case SolventBoxOptions.HEPTANE80:
                return Props("Heptane Box 80A cube", 80, "heptane")
            case SolventBoxOptions.METHANOL80:
                return Props("Methanol Box 80A cube", 80, "methanol")
            case SolventBoxOptions.CHLOROFORM80:
                return Props("Chloroform 80A cube", 80, "chloroform")
            case _:
                return Props("Select",0,"Select")
