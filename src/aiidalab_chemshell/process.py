"""Module for handling AiiDA processes."""

import ipywidgets as ipw
import traitlets as tl
from aiida.engine import submit
from aiida.orm import Dict, load_code
from aiida.plugins import WorkflowFactory
from aiida.orm import SinglefileData

from aiidalab_chemshell.common.chemshell import WorkflowOptions
from aiidalab_chemshell.common.chemshell import SolventBoxOptions
from aiidalab_chemshell.models.structure import StructureInputModel
from aiidalab_chemshell.models.workflow import ChemShellWorkflowModel
from aiidalab_chemshell.wizards.resources import ComputationalResourcesModel
from aiidalab_chemshell.wizards.results import ResultsModel

GeometryOptimisationWorkflow = WorkflowFactory("chemshell.opt")


class BaseAppModel(tl.HasTraits):
    """
    The shared AiiDAlab application MVC model.

    A single model backing both the "New Calculation" and "Batch Processing"
    pages. The ``batch`` flag selects the process class used on submission and
    constrains the batch page to single point energy calculations, while the
    composed sub-models and submission wiring remain identical.
    """

    block_results = tl.Bool(True, allow_none=False)

    def __init__(self, batch: bool = False):
        """
        AppModel constructor.

        Parameters
        ----------
        batch : bool
            If True, configure the model for batch processing; otherwise
            configure it for a single "New Calculation" workflow.
        """
        super().__init__()
        self.batch = batch
        self.structure_model = StructureInputModel()
        self.workflow_model = ChemShellWorkflowModel()
        if self.batch:
            # The batch page only runs single point energy calculations.
            self.workflow_model.workflow = WorkflowOptions.SINGLE_POINT
        self.resource_model = ComputationalResourcesModel()
        self.results_model = ResultsModel()

        self.resource_model.observe(self._submit_model, "submitted")
        ipw.dlink((self, "block_results"), (self.results_model, "blocked"))

        self.process = None

        return

    def _submit_model(self, _) -> None:
        """Handle the submission of the AiiDA process."""
        if ChemShellProcess.validate_model(self):
            self.process = ChemShellProcess(self)
            self.process.submit_process()
            self.block_results = False
            self.results_model.process_uuid = self.process.node.uuid
        else:
            print("ERROR: Input Validation Failed")
        return

    def reset(self) -> None:
        """Reset the state of the model."""
        self.submitted = False


class MainAppModel(BaseAppModel):
    """The main "New Calculation" AiiDAlab application MVC model."""

    def __init__(self):
        """MainAppModel constructor."""
        super().__init__(batch=False)


class BatchAppModel(BaseAppModel):
    """The batch processing AiiDAlab application MVC model."""

    def __init__(self):
        """BatchAppModel constructor."""
        super().__init__(batch=True)


class ChemShellProcess:
    """Class to handle a ChemShell AiiDA process."""

    def __init__(self, model: BaseAppModel):
        """
        ChemShellProcess constructor.

        Parameters
        ----------
        model : AppModel
            The application model containing all necessary data.
        """
        self.model = model
        self.node = None
        return

    @classmethod
    def validate_model(cls, model: BaseAppModel) -> bool:
        """
        Validate the main application model.

        Parameters
        ----------
        model : AppModel
            The application model to validate.

        Returns
        -------
        bool
            True if the model is valid, False otherwise.
        """
        if model.batch:
            if (
                not model.structure_model.has_trajectory
                and not model.structure_model.has_file
            ):
                print("No batch input (trajectory or structure file) provided.")
                return False
        else:
            if not model.structure_model.has_structure:
                if not model.structure_model.has_file:
                    print("No structure provided.")
                    return False
        if model.workflow_model.use_mm:
            if not model.workflow_model.force_field:
                print("No force field provided.")
                return False
            if not model.workflow_model.qm_region:
                print("No qm_ region specified", model.workflow_model.qm_region)
                return False
        # Add more validation checks as needed
        return True

    def submit_process(self):
        """Submit the AiiDA process."""
        if self.model.batch:
            self._submit_batch_workflow()
        else:
            match self.model.workflow_model.workflow:
                case WorkflowOptions.GEOMETRY:
                    self._submit_optimisation_workflow()
                case WorkflowOptions.ATOMIC_ENERGIES:
                    self._submit_atomic_energies_workflow()
                case WorkflowOptions.CHARGE_FITTING:
                    self._submit_charge_fitting_workflow()
                case WorkflowOptions.SOLVATION:
                    self._submit_solvation_workflow()
                case _:
                    self._submit_core_calcjob()
        return

    def _submit_core_calcjob(self) -> None:
        # Get the ChemShell code instance
        builder = load_code(self.model.resource_model.code_label).get_builder()
        # Configure the structure input
        if self.model.structure_model.has_file:
            builder.structure = self.model.structure_model.structure_file
        else:
            builder.structure = self.model.structure_model.structure
        # Configure the QM theory input parameters
        builder.qm_parameters = Dict(
            {
                "theory": self.model.workflow_model.qm_theory.name,
                "method": "dft" if self.model.workflow_model.use_dft else "hf",
                "functional": self.model.workflow_model.functional,
                "basis": self.model.workflow_model.basis_set,
            }
        )
        # Configure MM parameters if QM/MM approach specified
        if self.model.workflow_model.use_mm:
            builder.mm_parameters = Dict(
                {
                    "theory": self.model.workflow_model.mm_theory,
                }
            )
            builder.force_field_file = self.model.workflow_model.force_field
            builder.qmmm_parameters = Dict(
                {
                    "qm_region": ChemShellProcess._extract_qm_region(
                        self.model.workflow_model.qm_region
                    ),
                }
            )
        # Configure additional SP based tasks
        if self.model.workflow_model.workflow == WorkflowOptions.NEB:
            builder.optimisation_parameters = Dict({"neb": "frozen"})
            if self.model.workflow_model.structure_2.has_file:
                builder.structure2 = (
                    self.model.workflow_model.structure_2.structure_file
                )
            else:
                builder.structure2 = self.model.workflow_model.structure_2.structure
        elif self.model.workflow_model.vibrational_analysis:
            builder.optimisation_parameters = Dict({"thermal": True})
        else:
            builder.calculation_parameters = Dict(
                {
                    "gradients": self.model.workflow_model.gradients,
                    "hessian": self.model.workflow_model.hessian,
                }
            )
        # Setup metadata and resource parameters
        builder.metadata.options.resources = {
            "num_mpiprocs_per_machine": self.model.resource_model.ncpus,
            "num_cores_per_machine": self.model.resource_model.ncpus,
            "num_machines": 1,
            "tot_num_mpiprocs": self.model.resource_model.ncpus,
        }
        # Only set ``withmpi`` when the code itself does not declare it.
        if builder.code.with_mpi is None:
            builder.metadata.options.withmpi = self.model.resource_model.ncpus > 1
        # Submit and apply the label/description to the CalcJob
        self.node = submit(builder)
        self.node.label = self.model.resource_model.process_label
        self.node.description = self.model.resource_model.process_description
        return

    def _submit_optimisation_workflow(self) -> None:
        """Create and submit the AiiDA Workflow for a geometry optimisation."""
        builder = WorkflowFactory("chemshell.opt").get_builder()  # pyright: ignore[reportFunctionMemberAccess]
        builder.chemsh.code = load_code(self.model.resource_model.code_label)
        if self.model.structure_model.has_file:
            builder.chemsh.structure = self.model.structure_model.structure_file
        else:
            builder.chemsh.structure = self.model.structure_model.structure

        builder.chemsh.qm_parameters = Dict(
            {
                "theory": self.model.workflow_model.qm_theory.name,
                "method": "dft",
                "functional": self.model.workflow_model.functional,
                "basis": self.model.workflow_model.basis_set,
            }
        )
        if self.model.workflow_model.use_mm:
            builder.chemsh.mm_parameters = Dict(
                {
                    "theory": self.model.workflow_model.mm_theory,
                }
            )
            builder.chemsh.force_field_file = self.model.workflow_model.force_field
            builder.chemsh.qmmm_parameters = Dict(
                {
                    "qm_region": ChemShellProcess._extract_qm_region(
                        self.model.workflow_model.qm_region
                    ),
                }
            )
        # builder.chemsh.calculation_parameters = Dict({"gradients": True})
        builder.vibrational_analysis = self.model.workflow_model.vibrational_analysis
        builder.chemsh.metadata.options.resources = {
            "num_mpiprocs_per_machine": self.model.resource_model.ncpus,
            "num_cores_per_machine": self.model.resource_model.ncpus,
            "num_machines": 1,
            "tot_num_mpiprocs": self.model.resource_model.ncpus,
        }
        # Only set ``withmpi`` when the code itself does not declare it.
        if builder.chemsh.code.with_mpi is None:
            builder.chemsh.metadata.options.withmpi = (
                self.model.resource_model.ncpus > 1
            )
        self.node = submit(builder)
        self.node.label = self.model.resource_model.process_label
        self.node.description = self.model.resource_model.process_description
        return

    def _submit_atomic_energies_workflow(self) -> None:
        """Submit the IsolatedAtomEnergy WorkChain."""
        builder = WorkflowFactory("chemshell.atomic_energies").get_builder()  # pyright: ignore[reportFunctionMemberAccess]
        builder.code = load_code(self.model.resource_model.code_label)
        if self.model.structure_model.has_file:
            builder.structure = self.model.structure_model.structure_file
        else:
            builder.structure = self.model.structure_model.structure
        builder.qm_parameters = Dict(
            {
                "theory": self.model.workflow_model.qm_theory.name,
                "method": "dft",
                "functional": self.model.workflow_model.functional,
                "basis": self.model.workflow_model.basis_set,
            }
        )
        # The IsolatedAtomicEnergiesWorkChain forwards these options to each of
        # its per-atom sub-calculations.
        builder.chemsh.metadata.options.resources = {
            "num_mpiprocs_per_machine": self.model.resource_model.ncpus,
            "num_cores_per_machine": self.model.resource_model.ncpus,
            "num_machines": 1,
            "tot_num_mpiprocs": self.model.resource_model.ncpus,
        }
        # Only set ``withmpi`` when the code itself does not declare it.
        if builder.code.with_mpi is None:
            builder.chemsh.metadata.options.withmpi = (
                self.model.resource_model.ncpus > 1
            )
        self.node = submit(builder)
        self.node.label = self.model.resource_model.process_label
        self.node.description = self.model.resource_model.process_description
        return

    def _submit_batch_workflow(self) -> None:
        """Build and submit the batch processing WorkChain."""
        from aiida_chemshell.workflows.batch_calculation import BatchProcessWorkChain
        # TODO: Register BatchProcessWorkChain as aiida entrypoint

        builder = BatchProcessWorkChain.get_builder()
        builder.code = load_code(self.model.resource_model.code_label)
        builder.combine_results = self.model.workflow_model.combine_batch_results

        # Shared QM theory parameters applied to every item in the batch.
        builder.qm_parameters = Dict(
            {
                "theory": self.model.workflow_model.qm_theory.name,
                "method": "dft" if self.model.workflow_model.use_dft else "hf",
                "functional": self.model.workflow_model.functional,
                "basis": self.model.workflow_model.basis_set,
            }
        )
        # Optional QM/MM configuration.
        if self.model.workflow_model.use_mm:
            builder.mm_parameters = Dict(
                {
                    "theory": self.model.workflow_model.mm_theory,
                }
            )
            builder.force_field_file = self.model.workflow_model.force_field
            builder.qmmm_parameters = Dict(
                {
                    "qm_region": ChemShellProcess._extract_qm_region(
                        self.model.workflow_model.qm_region
                    ),
                }
            )
        # Energy derivative requests.
        builder.calculation_parameters = Dict(
            {
                "gradients": self.model.workflow_model.gradients,
                "hessian": self.model.workflow_model.hessian,
            }
        )

        # Route the batch input to the appropriate WorkChain port.
        if self.model.structure_model.has_trajectory:
            builder.trajectory = self.model.structure_model.trajectory
        else:
            structure_file = self.model.structure_model.structure_file
            builder.structure_files = {"input_file": structure_file}

        builder.calc.metadata.options.resources = {
            "num_mpiprocs_per_machine": self.model.resource_model.ncpus,
            "num_cores_per_machine": self.model.resource_model.ncpus,
            "num_machines": 1,
            "tot_num_mpiprocs": self.model.resource_model.ncpus,
        }
        # Only set ``withmpi`` when the code itself does not declare it.
        if builder.code.with_mpi is None:
            builder.calc.metadata.options.withmpi = self.model.resource_model.ncpus > 1

        self.node = submit(builder)
        self.node.label = self.model.resource_model.process_label
        self.node.description = self.model.resource_model.process_description
        return

    def _submit_charge_fitting_workflow(self) -> None:
        """Submit the Charge Fitting Calculation."""
        builder = load_code(self.model.resource_model.code_label).get_builder()

        if self.model.structure_model.has_file:
            builder.structure = self.model.structure_model.structure_file
        else:
            builder.structure = self.model.structure_model.structure
        builder.qm_parameters = Dict(
            {
                "theory": self.model.workflow_model.qm_theory.name,
                "method": "dft" if self.model.workflow_model.use_dft else "hf",
                "functional": self.model.workflow_model.functional,
                "basis": self.model.workflow_model.basis_set,
            }
        )

        builder.metadata.options.resources = {
            "num_mpiprocs_per_machine": self.model.resource_model.ncpus,
            "num_cores_per_machine": self.model.resource_model.ncpus,
            "num_machines": 1,
            "tot_num_mpiprocs": self.model.resource_model.ncpus,
        }
        builder.chargefitting_parameters = Dict({
            'method':self.model.workflow_model.chargefit_method,
            'npoints':self.model.workflow_model.chargefit_npoints,
            'type':self.model.workflow_model.chargefit_type,
            'vdw_scale':self.model.workflow_model.chargefit_vdw_scale,
            'nlayers':self.model.workflow_model.chargefit_nlayers,
            'tolerance':self.model.workflow_model.chargefit_tolerance,
            })
             # Only set ``withmpi`` when the code itself does not declare it.
        if builder.code.with_mpi is None:
            builder.metadata.options.withmpi = (
                self.model.resource_model.ncpus > 1
            )
        if builder.code.with_mpi is None:
            builder.metadata.options.withmpi = self.model.resource_model.ncpus > 1

        # Submit and apply the label/description to the CalcJob
        self.node = submit(builder)
        self.node.label = self.model.resource_model.process_label
        self.node.description = self.model.resource_model.process_description
        return

    def _submit_solvation_workflow(self) -> None:
        """Submit the Solvation WorkChain."""
        builder = WorkflowFactory("chemshell.solvation").get_builder()  # pyright: ignore[reportFunctionMemberAccess]
        builder.code = load_code(self.model.resource_model.code_label)
        if self.model.structure_model.has_file:
            builder.structure = self.model.structure_model.structure_file
        else:
            builder.structure = self.model.structure_model.structure
        qm_parameters = {
                "theory": self.model.workflow_model.qm_theory.name,
                "method": "dft" if self.model.workflow_model.use_dft else "hf",
                "functional": self.model.workflow_model.functional,
                "basis": self.model.workflow_model.basis_set,
            }
        if self.model.workflow_model.qm_theory.name.lower() == "nwchem":
            if self.model.workflow_model.nw_dispersion:
                qm_parameters.update({"dispersion" : self.model.workflow_model.nw_dispersion})
            if self.model.workflow_model.nw_tol_energy:
                qm_parameters.update({"tol_energy" : self.model.workflow_model.nw_tol_energy})
        builder.qm_parameters = Dict(qm_parameters)

        builder.chemsh.metadata.options.resources = {
            "num_mpiprocs_per_machine": self.model.resource_model.ncpus,
            "num_cores_per_machine": self.model.resource_model.ncpus,
            "num_machines": 1,
            "tot_num_mpiprocs": self.model.resource_model.ncpus,
        }

        builder.dryrun_opt = self.model.workflow_model.opt_dryrun
        builder.dryrun_charge = self.model.workflow_model.charge_dryrun
        builder.chargefitting_parameters = Dict({
            'method':self.model.workflow_model.chargefit_method,
            'npoints':self.model.workflow_model.chargefit_npoints,
            'type':self.model.workflow_model.chargefit_type,
            'vdw_scale':self.model.workflow_model.chargefit_vdw_scale,
            'nlayers':self.model.workflow_model.chargefit_nlayers,
            'tolerance':self.model.workflow_model.chargefit_tolerance,
        })
        builder.qm_esp_parameters = Dict(
            {
                "theory": self.model.workflow_model.qm_theory.name,
                "method": "dft" if self.model.workflow_model.esp_use_dft else "hf",
                "functional": self.model.workflow_model.esp_functional,
                "basis": self.model.workflow_model.esp_basis_set,
            }
        )

        if builder.code.with_mpi is None:
            builder.chemsh.metadata.options.withmpi = (
                self.model.resource_model.ncpus > 1
            )
        import shutil
        mpirun_path = shutil.which("mpirun")
        builder.sysmpi = f"{mpirun_path}"
        mm_parameters = {
                    "theory": self.model.workflow_model.mm_theory,
                    "temperature" : self.model.workflow_model.md_temperature,
        }
        if self.model.workflow_model.mm_theory.lower() == "dl_poly":
            if self.model.workflow_model.md_rcut > 0.0:
                mm_parameters.update( {"rcut" : self.model.workflow_model.md_rcut} )
        if self.model.workflow_model.solvent_ff:
            builder.force_field_file = self.model.workflow_model.solvent_ff
        else:
            mm_parameters.update({"ff" : "charmm"})
        builder.mm_parameters = Dict(mm_parameters)

        builder.md_parameters = Dict({
           'npt' : {"length" : self.model.workflow_model.md_length_npt,
                    "minimisation" :self.model.workflow_model.md_minimisation_npt,
                   },
            "nvt" : { "length" : self.model.workflow_model.md_length_nvt,
                      "minimisation" : self.model.workflow_model.md_minimisation_nvt,
                   },
            "production" : { "length" : self.model.workflow_model.md_length_production,
                   },
            "minimise" : {'stepsize': self.model.workflow_model.md_minimise_step,
                   },
            "padding" : self.model.workflow_model.md_padding,
            "nsnapshots" : self.model.workflow_model.md_nsnapshots,
            "freeze_solute" : self.model.workflow_model.md_freeze_solute,
            #"solutes_dist" : self.model.workflow_model.md_solutes_dist,
	    #"max_ncycles" : self.model.workflow_model.md_max_ncycles,
            #"fixed_npt" : self.model.workflow_model.md_fixed_npt,
        })
        if self.model.workflow_model.solvent_box:
            builder.solvent_box =  self.model.workflow_model.solvent_box
        else:
            builder.solvent_box =  SinglefileData(file = SolventBoxOptions.CHLOROFORM40.value)

        builder.dryrunmd = self.model.workflow_model.md_dryrunmd

        qm_parameters ={
                "theory": self.model.workflow_model.qm_theory.name,
                "method": "dft" if self.model.workflow_model.qmmm_use_dft else "hf",
                "functional": self.model.workflow_model.qmmm_functional,
                "basis": self.model.workflow_model.qmmm_basis_set,
            }

        builder.qmmm_parameters = Dict({
            "qm_parameters" : qm_parameters,
            "radius_shell": self.model.workflow_model.qmmm_shell_radius,
            "radius_active": self.model.workflow_model.qmmm_active_region_radius,
            "dryrun_qmmm": self.model.workflow_model.qmmm_dryrun,
            "qmmm_opt": self.model.workflow_model.qmmm_opt,
            "opt_cycles": self.model.workflow_model.qmmm_opt_cycles,                 
            "energy_cycles": self.model.workflow_model.qmmm_energy_cycles,                
            "nsnapshots" : self.model.workflow_model.qmmm_snapshots,
        })

        builder.solvent_parameters = Dict({
            "box_halflength"  : self.model.workflow_model.solvent_boxsize,
            "solvent_name"   : self.model.workflow_model.solvent_name,
                })

        self.node = submit(builder)
        self.node.label = self.model.resource_model.process_label
        self.node.description = self.model.resource_model.process_description
        return

    @classmethod
    def _extract_qm_region(cls, input_str: str) -> list[int]:
        input = [val.strip(",") for val in input_str.split()]
        qm_region = []
        invalid_input = False
        for entry in input:
            if "," in entry:
                entries = entry.split(",")
                for sub_entry in entries:
                    if "-" in sub_entry:
                        qm_region += ChemShellProcess._expand_range_entry(
                            sub_entry, invalid_input
                        )
            if "-" in entry:
                qm_region += ChemShellProcess._expand_range_entry(entry, invalid_input)
            else:
                try:
                    val = int(entry)
                except ValueError:
                    invalid_input = True
                except Exception as e:
                    raise e
                else:
                    qm_region.append(val)
        return qm_region

    @classmethod
    def _expand_range_entry(cls, input: str, invalid_input: bool) -> list[int]:
        start, end = input.split("-")
        try:
            return list(range(int(start), int(end) + 1))
        except ValueError:
            invalid_input = True  # noqa: F841
            return []
        except Exception as e:
            raise e
