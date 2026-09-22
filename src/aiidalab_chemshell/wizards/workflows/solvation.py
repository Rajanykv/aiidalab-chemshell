"""Defines the input widget for the a base single point energy calculation."""

import ipywidgets as ipw
from aiida_chemshell.utils import ChemShellQMTheory
from alc_aiidalab_widgets.widgets import (
    FileUploadWidget,
    StructureViewWidget,
)

from traitlets import Bool, HasTraits, link
from aiida.orm import SinglefileData

from aiidalab_chemshell.common.chemshell import BasisSetOptions
from aiidalab_chemshell.common.chemshell import SolventBoxOptions
from aiidalab_chemshell.common.utils import LoadingWidget
from aiidalab_chemshell.models.workflow import ChemShellWorkflowModel

class SolvationWidget(ipw.VBox):
    """Widget for ChemShell Solvation workflow inputs."""

    def __init__(self, model: ChemShellWorkflowModel, **kwargs):
        """
        SolvationWidget constructor.

        Parameters
        ----------
        model : ChemShellWorkflowModel
            The model that defines the data related to this step in the setup wizard.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(**kwargs)
        self.model = model
        self.rendered = False
        self.header = ipw.HTML(
            """
            <h3 style="text-align: center;">Solvation Workflow</h3>
            <p style="text-align: center;">
              Perform Solvation of a given solute in a solvation box of choice.
            </p>
            """,
            # layout={"margin": "auto"},
        )
        self.children = [self.header, LoadingWidget()]
        self.basic_view = ipw.HTML("<p style=\"text-align: center;\">No solvent box selected for viewing...</p>")
        self.viewer = self.basic_view
        return

    def render(self) -> None:
        """Render the widget."""
        if self.rendered:
            return
        self.rendered = True

        shared_layout = ipw.Layout(width='50%', margin='5px')
        shared_layout2 = ipw.Layout(width='500px', margin='5px')
        shared_style = {'description_width': '50%'}
        shared_style2 = {'description_width': '100px'}

        #background-color: #007bff;
        step_style ="""
             width: 60%; height: 30px;
             background-color: #2196F3;
             color: white;
             margin: auto;
             display: flex;
             align-items: center;
             justify-content: center;
             border-radius: 7px;
             font-weight: bold;
             text-align: center;
             """
        self.opt_label = ipw.HTML(
            value=f"""
            <div style="{step_style}">
             Step 1: Optimise the Solute structure
             </div>
             """
        )
        self.esp_label = ipw.HTML(
            value=f"""
            <div style="{step_style}">
             Step 2: Do Charge Fitting on the Optimised Structure
             </div>
             """
        )
        self.md_label = ipw.HTML(
            value=f"""
            <div style="{step_style}">
             Step 2: Equillibrate in a Solvent of choice
             </div>
             """
        )
        self.advanced_qm_options = ipw.Checkbox(
            value=False, description="Show Advanced QM Options",
            layout = shared_layout2,
            style = shared_style2,
            index=True
        )
        self.advanced_qm_options.observe(self._render_input_options, names="value")

        self.esp_qm_options = ipw.Checkbox(
            value=False, description="Show QM Option for (R)ESP",
            layout = shared_layout2,
            style = shared_style2,
            index=True
        )
        self.esp_qm_options.observe(self._render_input_options, names="value")

        self.advanced_mm_options = ipw.Checkbox(
            value=False, description="Show Advanced MM Options",
            layout = shared_layout2,
            style = shared_style2,
            index=True
        )
        self.advanced_mm_options.observe(self._render_input_options, names="value")

        self.advanced_md_options = ipw.Checkbox(
            value=False, description="Show Advanced MD Options",
            layout = shared_layout2,
            style = shared_style2,
            index=True
        )
        self.advanced_md_options.observe(self._render_input_options, names="value")

        self.advanced_esp_options = ipw.Checkbox(
            value=False,
            description="Show Advanced ChargeFit Options",
            layout = shared_layout2,
            style = shared_style2,
            index=True
        )
        self.advanced_esp_options.observe(self._render_input_options, names="value")

        self.do_md_dryrun = ipw.Dropdown(
            options = {"Full run" : False, "Initial setup" : True},
            description = "Choose Full-Run/Initialisation only",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "md_dryrunmd"), (self.do_md_dryrun, "value"))

        self.basis_dropdown = ipw.Dropdown(
            options={e.name: e for e in BasisSetOptions},
            description="Basis Quality:",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        #self.label = ipw.Label(
        #    value="Choose Solvent Box",
        #    layout=ipw.Layout(width='100%')
        #)
        self.solventbox_dropdown = ipw.Dropdown(
            options={b.label: b for b in SolventBoxOptions},
            disabled=False,
            description="Choose Solvent Box",
            layout=shared_layout,
            style=shared_style,
        )
        self.solventbox_dropdown.index = 0
        self._update_solventbox_set({"new": self.solventbox_dropdown.value, "old": None})
        self.solventbox_dropdown.observe(self._update_solventbox_set, names="value")
        #self.solventbox_container = ipw.VBox([self.label, self.solventbox_dropdown])

        self.solventbox_view_select = ipw.Checkbox(
            value=False,
            description="View Solvent Box",
            layout = shared_layout,
            style = shared_style,
            index=True
        )
        self.solventbox_view_select.observe(self._view_solventbox, names="value")

        self.qm_method_dropdown = ipw.Dropdown(
            options={"DFT" : True, "HF" : False},
            description="SCF method:",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "use_dft"), (self.qm_method_dropdown, "value"))

        self.basis_string = ipw.Text(
            value="",
            description="Basis Set:",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "basis_set"), (self.basis_string, "value"))

        self.backend = ipw.Dropdown(
            options={e.name: e for e in ChemShellQMTheory},
            description="QM Backend:",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "qm_theory"), (self.backend, "value"))

        self.functional = ipw.Text(
            value="B3LYP",
            description="Functional:",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "functional"), (self.functional, "value"))

        self.qm_container = ipw.VBox([self.backend, self.qm_method_dropdown, self.basis_string, self.functional])

        self.esp_basis_string = ipw.Text(
            value="",
            description="Basis Set:",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "esp_basis_set"), (self.esp_basis_string, "value"))
        self.esp_functional = ipw.Text(
            value="B3LYP",
            description="Functional:",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "esp_functional"), (self.functional, "value"))
        self.esp_qm_method_dropdown = ipw.Dropdown(
            options={"DFT" : True, "HF" : False},
            description="SCF method:",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "esp_use_dft"), (self.esp_qm_method_dropdown, "value"))

        self.esp_qm_container = ipw.VBox([self.esp_qm_method_dropdown, self.esp_basis_string, self.esp_functional])

        self.enable_mm_chk = ipw.Checkbox(
            value=False, description="Use QM/MM",
            layout = shared_layout2,
            style = shared_style2,
        )
        self.enable_mm_chk.observe(self._render_input_options, names="value")

        self.advanced_mm_options.observe(self._render_input_options, names="value")
        ipw.dlink((self.enable_mm_chk, "value"), (self.model, "use_mm"))

        # MM Backend
        self.mm_theory_dropdown = ipw.Dropdown(
            options=self._get_mm_theory_options(),
            value = "DL_POLY",
            description="MM Theory:",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
         )
        ipw.dlink((self.mm_theory_dropdown, "value"), (self.model, "mm_theory"))

        # QM region for QM/MM calculation
        self.qm_region_text = ipw.Text(
            value="",
            description="QM Region:",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.qm_region_text, "value"), (self.model, "qm_region"))

        # Force Field File
        self.ff_file = FileUploadWidget(description="Force Field:")
        link((self.ff_file, "file"), (self.model, "force_field"))

        self.esp_method_dropdown = ipw.Dropdown(
            options=["resp", "esp"],
            value="resp",
            description="ESP Method:",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "chargefit_method"), (self.esp_method_dropdown, "value"))

        self.chargefit_npoints = ipw.IntText(
            value=50,
            description="Npoints",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "chargefit_npoints"), (self.chargefit_npoints, "value"))

        self.chargefit_type = ipw.Text(
            value="shell",
            description="Type",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "chargefit_type"), (self.chargefit_type, "value"))

        self.chargefit_tolerance = ipw.FloatText(
            value=1e-12,
            description="Tolerance",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "chargefit_tolerance"), (self.chargefit_tolerance, "value"))

        self.chargefit_vdw_scale = ipw.FloatText(
            value=1.5,
            description="VdW scale",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "chargefit_vdw_scale"), (self.chargefit_vdw_scale, "value"))

        self.chargefit_nlayers = ipw.IntText(
            value=1,
            description="Nlayers",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "chargefit_nlayers"), (self.chargefit_nlayers, "value"))

        self.rcut = ipw.FloatText(
            value=20.0,
            description="Rcut",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "md_rcut"), (self.rcut, "value"))

        self.temperature = ipw.FloatText(
            value=300.0,
            description="Temperature",
            disabled=False,
            layout=shared_layout,
            style=shared_style,
        )
        link((self.model, "md_temperature"), (self.temperature, "value"))

#            "length_npt" : self.model.workflow_model.md_length_npt,
#            "length_nvt" : self.model.workflow_model.md_length_nvt,
#            "length_production" : self.model.workflow_model.md_length_production,
#            "max_ncycles" : self.model.workflow_model.md_max_ncycles,
#            'minimisation_npt' :self.model.workflow_model.md_minimisation_npt,
#            'minimisation_nvt' : self.model.workflow_model.md_minimisation_nvt,
#            'solutes_dist' : self.model.workflow_model.md_solutes_dist,
#            'padding' : self.model.workflow_model.md_padding,
#            'nsnapshots' : self.model.workflow_model.md_nsnapshots,
#            "fixed_npt" : self.model.workflow_model.md_fixed_npt,



        self.esp_container = ipw.VBox([self.chargefit_npoints, self.chargefit_type, self.chargefit_tolerance, self.chargefit_vdw_scale, self.chargefit_nlayers])

        self.md_container = ipw.VBox([self.temperature, self.rcut])

        self._render_basic_options()

    def _render_basic_options(self) -> None:
        """Render the simplified input options view."""
        children = [
            self.header,
            self.opt_label,
            self.advanced_qm_options,
            self.basis_dropdown,
            self.esp_label,
            self.advanced_esp_options,
            self.esp_method_dropdown,
            self.esp_qm_options,
            self.md_label,
            self.solventbox_dropdown,
            self.solventbox_view_select,
            self.viewer,
            self.mm_theory_dropdown,
            self.ff_file,
            #self.advanced_mm_options,
            self.advanced_md_options,
            self.do_md_dryrun,
            self.enable_mm_chk,
        ]
        if self.enable_mm_chk.value:
            children.append(self.qm_region_text)
            children.append(self.ff_file)
        self.children = children
        return

    def _render_advanced_options(self) -> None:
        """Render the advanced input options view."""
        children = [self.header, self.opt_label, self.advanced_qm_options]

        if self.advanced_qm_options.value:
            children.append(self.qm_container)

        children.extend([self.esp_label, self.advanced_esp_options,
                        self.esp_method_dropdown])

        if self.advanced_esp_options.value:
            children.append(self.esp_container)

        children.append(self.esp_qm_options)
        if self.esp_qm_options.value:
            children.append(self.esp_qm_container)

        children.extend([
            self.md_label,
            self.solventbox_dropdown,
            self.solventbox_view_select,
            self.viewer,
            self.mm_theory_dropdown,
            self.ff_file,
            #self.advanced_mm_options
        ])

        #if self.advanced_mm_options.value:
        #    children.append(self.mm_container)

        children.append(self.advanced_md_options)
        if self.advanced_md_options.value:
            children.append(self.md_container)

        children.append(self.enable_mm_chk)
        if self.enable_mm_chk.value:
            children.append(self.qm_region_text)

        children.append(self.do_md_dryrun)

        self.children = children
        return

    def _render_input_options(self, change: dict) -> None:
        """Switch between basic and advanced views."""
        if change["new"]:
            self._render_advanced_options()
        else:
            self._render_basic_options()
            # Update the linked basis set value
            self._update_basis_set({"new": self.basis_dropdown.value, "old": None})
        return

    def _update_basis_set(self, change: dict) -> None:
        """Update the basis set based of the simplified input options."""
        if change["new"] == change["old"]:
            return
        self.model.basis_set = change["new"].label
        return
    def _update_solventbox_set(self, change: dict) -> None:
        """Update Solvent boxes based of the user's choice."""
        if change["new"] == change["old"]:
            return
        self.model.solvent_box = SinglefileData(file=change["new"].value)
        return
    def _view_solventbox(self, change: dict) -> None:
        if change["new"]:
            file_to_view = self._convert_fileformat(self.model.solvent_box)
            self.viewer = StructureViewWidget(file_to_view)
        else:
            self.viewer = self.basic_view
        self._render_basic_options()
        return

    def _convert_fileformat(self, file:SinglefileData) -> SinglefileData:
        if file.filename.lower().endswith(".pqr") or file.filename.lower().endswith(".pdb"):
            from ase.io import read, write
            from pathlib import Path
            with file.open() as handle:
                contents = read(handle, format="proteindatabank")
                xyzfile = write("structurepqr.xyz", contents, format="xyz")
                newfile = SinglefileData(file=str(Path("structurepqr.xyz").resolve()))
            return newfile

        else:
            return file


    def disable(self, disable: bool = True) -> None:
        """Disable/Enable the wigets input options."""
        for child in self.children:
            child.disabled = disable
        return


    def _get_qm_theory_options(self) -> list[str]:
        """Get the available QM theory options."""
        try:
            from aiida_chemshell.utils import ChemShellQMTheory

            return list(ChemShellQMTheory.__members__.keys())
        except ImportError:
            return []
        except Exception as e:
            raise e

    def _get_mm_theory_options(self) -> list[str]:
        """Get the available MM theory options."""
        try:
            from aiida_chemshell.utils import ChemShellMMTheory

            return list(ChemShellMMTheory.__members__.keys())
        except ImportError:
            return []
        except Exception as e:
            raise e

#    def disable(self, change: dict) -> None:
#        """Disable the contained widgets."""
#        for child in self.children:
#            child.disabled = change["new"]
#        return
