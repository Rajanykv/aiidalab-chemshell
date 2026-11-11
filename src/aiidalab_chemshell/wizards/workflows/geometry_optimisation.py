"""Defines the input widget for the base geometry optimisation workflow."""

import ipywidgets as ipw
from aiida_chemshell.utils import ChemShellQMTheory
from alc_aiidalab_widgets.widgets import FileUploadWidget, AiiDADatabaseQueryWidget
from traitlets import link
from aiida.orm import List, SinglefileData

from aiidalab_chemshell.common.chemshell import BasisSetOptions
from aiidalab_chemshell.common.utils import LoadingWidget
from aiidalab_chemshell.models.workflow import ChemShellWorkflowModel


class ChemShellOptionsWidget(ipw.VBox):
    """Widget for selecting the ChemShell input options."""

    def __init__(self, model: ChemShellWorkflowModel, **kwargs):
        """
        ChemShellOptionsWidget constructor.

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
            <h3 style="text-align: center;"> QM/MM Geometry Optimisation </h3>
            <p>
                Perform a geometry optimisation on the given structure via either QM or
                QM/MM. Uses NWChem for the QM region and DL_POLY for the (optional) MM
                region. The quality of the calculation can be controlled via the basis
                set option, higher quality basis set will result in a more accurate QM
                calculation but will increase the time required.
            </p>
            """,
            layout={"margin": "auto"},
        )

        # Force Field File
        self.ff_file = FileUploadWidget(description="Force Field:")

        self.children = [self.header, LoadingWidget()]

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
        self._render_input_options({"new": self.advanced_options.value})
        return

    # def _update_basis_quality(self, _) -> None:
    #     print(self.model.basis_quality)
    #     return

    def render(self):
        """Render the options widget contents if not already rendered."""
        if self.rendered:
            return
        self.rendered = True

        self.advanced_options = ipw.Checkbox(
            value=False, description="Show Advanced Options", index=True
        )
        self.advanced_options.observe(self._render_input_options, "value")

        shared_layout = ipw.Layout(width ='50%', margin='5px 0px 0px 10px')
        shared_style = {'description_width': '50%'}
        # QM Backend
        self.qm_theory_dropdown = ipw.Dropdown(
            options=self._get_qm_theory_options(),
            description="QM Theory:",
            disabled=False,
            layout = shared_layout,
            style = shared_style,
        )

        # Basis Quality
        self.basis_dropdown = ipw.Dropdown(
            options={e.name: e for e in BasisSetOptions},
            description="Basis Quality:",
            disabled=False,
            layout = shared_layout,
            style = shared_style,
        )
        self.basis_dropdown.observe(self._update_basis_set, "value")
        self.basis_dropdown.index = 1

        self.basis_string = ipw.Text(
            value="",
            description="Basis Set:",
            disabled=False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "basis_set"), (self.basis_string, "value"))

        self.backend = ipw.Dropdown(
            options={e.name: e for e in ChemShellQMTheory},
            description="QM Backend:",
            disabled=False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "qm_theory"), (self.backend, "value"))
        self.functional = ipw.Text(
            value="B3LYP",
            description="Functional:",
            disabled=False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "functional"), (self.functional, "value"))

        # Enable vibrational analysis
        self.enable_vib = ipw.Checkbox(
            value=True, description="Vibrational Frequencies", index=True
        )
        ipw.dlink((self.enable_vib, "value"), (self.model, "vibrational_analysis"))

        # DFT checkbox
        # self.enable_dft = ipw.Checkbox(value=False, description="Use DFT", index=True)
        # ipw.dlink((self.enable_dft, "value"), (self.model, "use_dft"))

        # QM/MM Checkbox
        self.enable_mm_chk = ipw.Checkbox(
            value=False, description="Use QM/MM", indent=True
        )
        self.enable_mm_chk.observe(self._enable_mm_options, "value")
        ipw.dlink((self.enable_mm_chk, "value"), (self.model, "use_mm"))

        # MM Backend
        # self.mm_theory_dropdown = ipw.Dropdown(
        #     options=self._get_mm_theory_options(),
        #     description="MM Theory:",
        #     disabled=True,
        #     layout={"width": "50%"},
        # )

        # QM region for QM/MM calculation
        self.qm_region_text = ipw.Text(
            value="",
            description="QM Region:",
            disabled=False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.qm_region_text, "value"), (self.model, "qm_region"))

        # Active region for QM/MM calculation
        self.active_region_text = ipw.Text(
            value="",
            description="Active Region:",
            disabled=False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.active_region_text, "value"), (self.model, "active_region"))

        self.opt_cycles = ipw.IntText(
            value =500,
            description ="Num of Optimisation cycles:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "opt_cycles"), (self.opt_cycles, "value"))

        self.energy_cycles = ipw.IntText(
            value =500,
            description ="Num of Energy cycles in Opt:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "energy_cycles"), (self.energy_cycles, "value"))


        self.qm_region_database = AiiDADatabaseQueryWidget(
            title="AiiDA Database",
            query=[List]
        )
        self.qm_region_database.observe(self._on_database_qm, "data_object")

        self.active_region_database = AiiDADatabaseQueryWidget(
            title="AiiDA Database",
            query=[List]
        )
        self.active_region_database.observe(self._on_database_active, "data_object")

        self.active_database_check = ipw.Checkbox(
            value=False, description="AiiDa DataBase", index=True,
        )
        self.active_database_check.observe(self._render_input_options, "value")

        self.qm_database_check = ipw.Checkbox(
            value=False, description="AiiDa DataBase", index=True,
        )
        self.qm_database_check.observe(self._render_input_options, "value")

        self.qm_region = ipw.HBox([self.qm_region_text, self.qm_database_check])
        self.active_region = ipw.HBox([self.active_region_text, self.active_database_check])

        # Force Field Options
        # Force Field File
        self.ff_file = FileUploadWidget(description="Force Field:",
            layout = shared_layout,
            style = shared_style,
        )
        link((self.ff_file, "file"), (self.model, "force_field"))

        self.ff_database_check = ipw.Checkbox(
            value=False, description="AiiDa DataBase", index=True,
        )
        self.ff_database_check.observe(self._render_input_options, "value")

        self.ff_database = AiiDADatabaseQueryWidget(
            title="AiiDA Database",
            query=[SinglefileData]
        )
        self.ff_database.observe(self._on_database_ff, "data_object")

        self.ff_container = ipw.HBox([self.ff_file, self.ff_database_check])


        self._render_input_options({"new": self.advanced_options.value})
        return

    def _render_basic_options(self) -> None:
        """Render the simplified input options view."""
        children = [
            self.header,
            self.advanced_options,
            self.basis_dropdown,
            self.enable_vib,
            self.enable_mm_chk,
        ]
        if self.enable_mm_chk.value:
            children.append(self.ff_container)
            if self.ff_database_check.value:
                children.append(self.ff_database)
            children.append(self.qm_region)
            if self.qm_database_check.value:
                children.append(self.qm_region_database)
            children.append(self.active_region)
            if self.active_database_check.value:
                children.append(self.active_region_database)
        self.children = children
        return

    def _render_advanced_options(self) -> None:
        """Render the advanced input options view."""
        children = [
            self.header,
            self.advanced_options,
            self.backend,
            self.basis_string,
            self.functional,
            self.opt_cycles,
            self.energy_cycles,
            self.enable_vib,
            self.enable_mm_chk,
        ]
        if self.enable_mm_chk.value:
            children.append(self.ff_container)
            if self.ff_database_check.value:
                children.append(self.ff_database)
            children.append(self.qm_region)
            if self.qm_database_check.value:
                children.append(self.qm_region_database)
            children.append(self.active_region)
            if self.active_database_check.value:
                children.append(self.active_region_database)
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

    def disable(self, val: bool) -> None:
        """Disable the input fields."""
        for child in self.children:
            child.disabled = val
        self.ff_file.disable(val)
        return

    def _update_basis_set(self, change: dict) -> None:
        """Update the basis set based of the simplified input options."""
        if change["new"] == change["old"]:
            return
        self.model.basis_set = change["new"].label
        return

    def _on_database_active(self, change: dict) -> None:
        """When data is loaded from AiiDA database."""
        if change["new"] == change["old"]:
            return
        if isinstance(change["new"], List):
            new_list = change["new"].get_list()
            self.model.active_region = ", ".join(map(str, new_list))
        return

    def _on_database_qm(self, change: dict) -> None:
        """When data is loaded from AiiDA database."""
        if change["new"] == change["old"]:
            return
        if isinstance(change["new"], List):
            new_list = change["new"].get_list()
            self.model.qm_region = ", ".join(map(str, new_list))
        return

    def _on_database_ff(self, change: dict) -> None:
        """When data is loaded from AiiDA database."""
        if change["new"] == change["old"]:
            return
        if isinstance(change["new"], SinglefileData):
            self.model.force_field = change["new"]
        return
