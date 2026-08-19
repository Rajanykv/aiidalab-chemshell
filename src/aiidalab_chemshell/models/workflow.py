"""Defines the MVC models for ChemShell workflow specification."""

from aiida.orm import SinglefileData
from aiida_chemshell.utils import ChemShellQMTheory
from traitlets import (
    Bool,
    HasTraits,
    Instance,
    Unicode,
    UseEnum,
    Int, Float,
)

from aiidalab_chemshell.common.chemshell import BasisSetOptions, WorkflowOptions
from aiidalab_chemshell.models.structure import StructureInputModel
from aiidalab_chemshell.common.chemshell import SolventBoxOptions


class ChemShellWorkflowModel(HasTraits):
    """The model for setting up a ChemShell workflow."""

    # workflow = Integer(0, allow_none=False).tag(sync=True)
    workflow = UseEnum(WorkflowOptions, WorkflowOptions.GEOMETRY, allow_none=False)

    qm_theory = UseEnum(ChemShellQMTheory, ChemShellQMTheory.NWCHEM, allow_none=False)
    mm_theory = Unicode("DL_POLY", allow_none=True)
    qm_region = Unicode("", allow_none=False)
    use_dft = Bool(True).tag(sync=True)
    basis_quality = UseEnum(BasisSetOptions, BasisSetOptions.FAST, allow_none=False)
    functional = Unicode("B3LYP", allow_none=False)
    basis_set = Unicode("cc-pvdz", allow_none=False)
    force_field = Instance(SinglefileData, allow_none=True)
    submitted = Bool(False).tag(sync=True)
    use_mm = Bool(False).tag(sync=True)
    vibrational_analysis = Bool(False).tag(sync=True)
    gradients = Bool(True)
    hessian = Bool(False)

    structure_2 = StructureInputModel()

    chargefit_method = Unicode("resp", allow_none=False)
    chargefit_npoints = Int(50, allow_none=False)
    chargefit_type = Unicode("shell", allow_none=False)
    chargefit_vdw_scale = Float(1.5, allow_none=True)
    chargefit_nlayers = Int(1, allow_none=True)
    chargefit_tolerance = Float(1e-12, allow_none=False)

    default_guide = ""

class SolvationWorkflowModel(ChemShellWorkflowModel):
    """The model for setting up a Solvation workflow."""

    from pathlib import Path
    workflow = UseEnum(WorkflowOptions, WorkflowOptions.SOLVATION, allow_none=True)
    submitted = Bool(False).tag(sync=True)

    solvent_box = Instance(SinglefileData, default=SinglefileData(file=SolventBoxOptions.WATER30.value), allow_none=False)

    @property
    def has_file(self) -> bool:
        """True if a raw structure file object has been attached to the model."""
        return self.solvent_box is not None
