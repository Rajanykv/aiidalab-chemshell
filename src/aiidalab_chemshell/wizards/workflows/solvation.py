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
from aiidalab_chemshell.models.workflow import SolvationWorkflowModel

class SolvationWidget(ipw.VBox):
    """Widget for ChemShell Solvation workflow inputs."""

    def __init__(self, model: SolvationWorkflowModel, **kwargs):
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
            <p>
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

        self.advanced_qm_options = ipw.Checkbox(
            value=False, description="Show Advanced QM Options",
            layout = shared_layout2,
            style = shared_style2,
            index=True
        )
        self.advanced_qm_options.observe(self._render_input_options, names="value")

        self.advanced_esp_options = ipw.Checkbox(
            value=False,
            description="Show Advanced ChargeFit Options",
            layout = shared_layout2,
            style = shared_style2,
            index=True
        )
        self.advanced_esp_options.observe(self._render_input_options, names="value")

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

        self.enable_mm_chk = ipw.Checkbox(
            value=False, description="Use QM/MM", indent=True
        )
        self.enable_mm_chk.observe(self._enable_mm_options, "value")
        ipw.dlink((self.enable_mm_chk, "value"), (self.model, "use_mm"))

        # MM Backend
        self.mm_theory_dropdown = ipw.Dropdown(
            options=self._get_mm_theory_options(),
            description="MM Theory:",
            disabled=True,
            layout=shared_layout,
            style=shared_style,
         )

        # QM region for QM/MM calculation
        #self.qm_region_text = ipw.Text(
        #    value="",
        #    description="QM Region:",
        #    disabled=False,
        #    layout=shared_layout,
        #    style=shared_style,
        #)
        #link((self.qm_region_text, "value"), (self.model, "qm_region"))

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
        self.esp_container = ipw.VBox([self.chargefit_npoints, self.chargefit_type, self.chargefit_tolerance, self.chargefit_vdw_scale, self.chargefit_nlayers])

        self._render_basic_options()

    def _render_basic_options(self) -> None:
        """Render the simplified input options view."""
        children = [
            self.header,
            self.solventbox_dropdown,
            self.solventbox_view_select,
            self.viewer,
            self.advanced_qm_options,
            self.basis_dropdown,
            self.advanced_esp_options,
            self.esp_method_dropdown,
            self.enable_mm_chk,
        ]
        if self.enable_mm_chk.value:
            children.append(self.qm_region_text)
            children.append(self.ff_file)
        self.children = children
        return

    def _render_advanced_options(self) -> None:
        """Render the advanced input options view."""
        children = [self.header, self.solventbox_dropdown, 
                    self.solventbox_view_select, self.viewer,
                    self.advanced_qm_options]
        if self.advanced_qm_options.value:
            children.append(self.qm_container)
        children.append(self.advanced_esp_options)
        children.append(self.esp_method_dropdown)
        if self.advanced_esp_options.value:
            children.append(self.esp_container)
        children.append(self.enable_mm_chk)
        if self.enable_mm_chk.value:
            children.append(self.qm_region_text)
            children.append(self.ff_file)
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
        if file.filename.lower().endswith(".pqr"):
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

    def _enable_mm_options(self, _) -> None:
        self._render_input_options({"new": self.advanced_qm_options.value})
        return

    def _enable_mm_options(self, _) -> None:
        self._render_input_options({"new": self.advanced_qm_options.value})
        return

#    def disable(self, change: dict) -> None:
#        """Disable the contained widgets."""
#        for child in self.children:
#            child.disabled = change["new"]
#        return
