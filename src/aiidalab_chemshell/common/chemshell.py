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

Props = namedtuple("Props", ["filepath", "label", "cube_length", "name"])
dataroot = Path("/opt/chemsh-py/data/solvent_boxes")
class SolventBoxOptions(Enum):
    """Enum defining the available Solvent Boxes."""

    #_ignore_ = 'dataroot'

    WATER30 = 0
    WATER40 =  auto()
    HEPTANE30 = auto()
    HEPTANE40 = auto()
    METHANOL30 = auto()
    METHANOL40 = auto()
    CHLOROFORM30 = auto()
    CHLOROFORM40 = auto()

    @property
    def properties(self) -> tuple :
        match self:
            case SolventBoxOptions.WATER30:
                return Props(dataroot/"water-box30-100ns.pqr" , "Water Box 30A cube", 30, "water")
            case SolventBoxOptions.WATER40:
                return Props(dataroot/"water-box40-100ns.pqr", "Water Box 40A cube", 40, "water")
            case SolventBoxOptions.HEPTANE30:
                return Props(dataroot/"heptane-box30-100ns.pqr", "Heptane Box 30A cube", 30, "heptane")
            case SolventBoxOptions.HEPTANE40:
                return Props(dataroot/"heptane-box40-100ns.pqr", "Heptane Box 40A cube", 40, "heptane")
            case SolventBoxOptions.METHANOL30:
                return Props(dataroot/"methanol-box30-100ns.pqr", "Methanol Box 30A cube", 30, "methanol")
            case SolventBoxOptions.METHANOL40:
                return Props(dataroot/"methanol-box40-100ns.pqr", "Methanol Box 40A cube", 40, "methanol")
            case SolventBoxOptions.CHLOROFORM30:
                return Props(dataroot/"chloroform-box30-100ns.pqr", "Chloroform 30A cube", 30, "chloroform")
            case SolventBoxOptions.CHLOROFORM40:
                return Props(dataroot/"chloroform-box40-100ns.pqr", "Chloroform 40A cube", 40, "chloroform")
            case _:
                return Propes("Select","Select",0,"Select")
