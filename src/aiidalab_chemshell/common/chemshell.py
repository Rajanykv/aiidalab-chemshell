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

    WATER40 =  0
    HEPTANE40 = auto()
    METHANOL40 = auto()
    CHLOROFORM40 = auto()

    @property
    def properties(self) -> tuple :
        match self:
            case SolventBoxOptions.WATER40:
                #return Props(dataroot/"water-box40-100ns.pqr", "Water Box 40A cube", 40, "water")
                return Props("Water Box 220A cube", 220, "water")
            case SolventBoxOptions.HEPTANE40:
                return Props("Heptane Box 40A cube", 40, "heptane")
            case SolventBoxOptions.METHANOL40:
                return Props("Methanol Box 40A cube", 40, "methanol")
            case SolventBoxOptions.CHLOROFORM40:
                return Props("Chloroform 40A cube", 40, "chloroform")
            case _:
                return Props("Select",0,"Select")
