"""Module containing common settings for configuring ChemShell."""

from enum import Enum, auto, IntEnum
from pathlib import Path


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

class SolventBoxOptions(Enum):
    """Enum defining the available Solvent Boxes."""

    _ignore_ = 'dataroot'
    dataroot = Path("/opt/chemsh-py/data/solvent_boxes")

    WATER30 = dataroot/"water-box30-100ns.pqr"
    WATER40 =  dataroot/"water-box40-100ns.pqr"
    HEPTANE30 = dataroot/"heptane-box30-100ns.pqr"
    HEPTANE40 = dataroot/"heptane-box40-100ns.pqr"
    METHANOL30 = dataroot/"methanol-box30-100ns.pqr"
    METHANOL40 = dataroot/"methanol-box40-100ns.pqr"
    CHLOROFORM30 = dataroot/"chloroform-box30-100ns.pqr"
    CHLOROFORM40 = dataroot/"chloroform-box40-100ns.pqr"

    @property
    def label(self) -> str:
        """Convert enum value into a more human readable string."""
        match self:
            case SolventBoxOptions.WATER30:
                return "Water Box 30A cube"
            case SolventBoxOptions.WATER40:
                return "Water Box 40A cube"
            case SolventBoxOptions.HEPTANE30:
                return "Heptane Box 30A cube"
            case SolventBoxOptions.HEPTANE40:
                return "Heptane Box 40A cube"
            case SolventBoxOptions.METHANOL30:
                return "Methanol Box 30A cube"
            case SolventBoxOptions.METHANOL40:
                return "Methanol Box 40A cube"
            case SolventBoxOptions.CHLOROFORM30:
                return "Chloroform 30A cube"
            case SolventBoxOptions.CHLOROFORM40:
                return "Chloroform 40A cube"
            case _:
                return ""
