"""Defines the input widget for the a base single point energy calculation."""

import ipywidgets as ipw
import traitlets as tl

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
            <h3 style ="text-align: center;">Solvation Workflow</h3>
            <p style ="text-align: center;">
              Perform Solvation of a given solute in a solvation box of choice.
            </p>
            """,
            # layout ={"margin": "auto"},
        )
        self.children = [self.header, LoadingWidget()]
        self.basic_view = ipw.HTML("<p style =\"text-align: center;\">No solvent box selected for viewing...</p>")
        self.viewer = self.basic_view
        return

    def render(self) -> None:
        """Render the widget."""
        if self.rendered:
            return
        self.rendered = True

        shared_layout = ipw.Layout(width ='50%', margin='5px')
        shared_layout2 = ipw.Layout(width ='500px', margin='5px')
        shared_style = {'description_width': '50%'}
        shared_style2 = {'description_width': '100px'}

        #background-color: #007bff;
        #bg_color = "#2196F3"
        self.step_style ="""
             width: 60%; height: 30px;
             background-color: {bg_color};
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
            value = f"""
            <div style ="{self.step_style.format(bg_color = "#2196F3")}">
             Step 1: Optimise the Solute structure
             </div>
             """
        )
        self.esp_label = ipw.HTML(
            value = f"""
            <div style ="{self.step_style.format(bg_color='#00BCD4')}">
             Step 2.1: Do Charge Fitting on the Optimised Solute
             </div>
             """
        )
        self.md_label = ipw.HTML(
            value = f"""
            <div style ="{self.step_style.format(bg_color='#00BCD4')}">
            Step 2.2: Run MD equillibration in the selected Solvent
             </div>
             """
        )
        self.solvation_label = ipw.HTML(
            value = f"""
            <div style ="{self.step_style.format(bg_color = "#2196F3")}">
            Step 2: Solvate in a Solvent of choice
             </div>
             """
        )
        self.qmmm_label = ipw.HTML(
            value = f"""
            <div style ="{self.step_style.format(bg_color = "#2196F3")}">
            Step 3: Run QM/MM
             </div>
             """
        )
        self.submit_dry_btn = ipw.Button(
            description ="Submit a Dry Run of MD",
            button_style ="primary",
            tooltip ="Submit the part of the calculation",
            layout ={"width": "30%", "height": "30px", "margin": "30px auto 30px auto"},
            style ={"button_color": "#005A5B", "text_color": "white"}
            #style ={"button_color": "#5CB85C", "text_color": "white"}
        )
        self.submit_dry_btn.on_click(self._submit_dry)

        self.advanced_qm_options = ipw.Checkbox(
            value = False, description="Show Advanced QM Options",
            layout = shared_layout2,
            style = shared_style2,
            index = True
        )
        self.advanced_qm_options.observe(self._render_input_options, names ="value")

        self.esp_qm_options = ipw.Checkbox(
            value = False, description="Show QM Option for (R)ESP",
            layout = shared_layout2,
            style = shared_style2,
        )
        self.esp_qm_options.observe(self._render_options, names ="value")

        self.advanced_qmmm_qm_options = ipw.Checkbox(
            value = False, description="Show Advanced QM Options for QMMM",
            layout = shared_layout2,
            style = shared_style2,
        )
        self.advanced_qmmm_qm_options.observe(self._render_options, names ="value")

        self.advanced_qmmm_options = ipw.Checkbox(
            value = False, description="Show Advanced QMMM Options",
            layout = shared_layout2,
            style = shared_style2,
        )
        self.advanced_qmmm_options.observe(self._render_options, names ="value")

        self.advanced_qmmm_mm_options = ipw.Checkbox(
            value = False, description="Show Advanced MM Options for QMMM",
            layout = shared_layout2,
            style = shared_style2,
        )
        self.advanced_qmmm_mm_options.observe(self._render_options, names ="value")

        self.advanced_md_mm_options = ipw.Checkbox(
            value = False, description="(Optional) Upload force field file for the solute",
            layout = shared_layout2,
            style = shared_style2,
        )
        self.advanced_md_mm_options.observe(self._render_options, names ="value")

        self.advanced_md_options = ipw.Checkbox(
            value = False, description="Show Advanced MD Options",
            layout = shared_layout2,
            style = shared_style2,
        )
        self.advanced_md_options.observe(self._render_options, names ="value")

        self.advanced_esp_options = ipw.Checkbox(
            value = False,
            description ="Show Advanced ChargeFit Options",
            layout = shared_layout2,
            style = shared_style2,
        )
        self.advanced_esp_options.observe(self._render_options, names ="value")

        self.do_md_dryrun = ipw.Dropdown(
            options = {"Full run" : False, "Dry Run" : True},
            value = False,
            description = "Choose Full-Run/Dryrun",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        #link((self.model, "md_dryrunmd"), (self.do_md_dryrun, "value"))
        self.do_opt_dryrun = ipw.Dropdown(
            options = {"Do Optimisation" : False, "Don't do optimisation" : True},
            value = False,
            description = "Choose to Optimise Solute",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "opt_dryrun"), (self.do_opt_dryrun, "value"))

        self.do_charge_dryrun = ipw.Dropdown(
            options = {"Do charge fit" : False, "Skip charge fit" : True},
            value = False,
            description = "Choose Full-Run/Dryrun",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "charge_dryrun"), (self.do_charge_dryrun, "value"))

        self.basis_dropdown = ipw.Dropdown(
            options ={e.name: e for e in BasisSetOptions},
            description ="Basis Quality:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        self.basis_dropdown.observe(self._update_basis_set, "value")
        #self.basis_dropdown.index = 1

        self.UPLOAD = tl.Instance(SinglefileData)

        box_options = [(b.properties.label,b.properties.filepath) for b in SolventBoxOptions] +[("Upload new Box", self.UPLOAD)]

        self.solventbox_dropdown = ipw.Dropdown(
            options = box_options,
            disabled = False,
            description ="Choose Solvent Box",
            layout = shared_layout,
            style = shared_style,
        )
        self.solventbox_dropdown.index = 3
        self.model.solvent_box = SinglefileData(file = self.solventbox_dropdown.value)
        self.solventbox_dropdown.observe(self._update_solventbox_set, names ="value")

        self.solventbox_view_select = ipw.Checkbox(
            value = False,
            description ="View Solvent Box",
            layout = shared_layout,
            style = shared_style,
            index = True
        )
        self.solventbox_view_select.observe(self._view_solventbox, names ="value")

        self.solvent_structfile = FileUploadWidget(description ="Solvent Structure:")
        self.solvent_structfile.layout.display="none"
        self.solvent_structfile.observe(self._on_file_upload, names="file")

        #self.solventbox_size = ipw.Dropdown(
        #    disabled = False,
        #    description ="Box Half Side-length",
        #    layout = shared_layout,
        #    style = shared_style,
        #)
        #self.solventbox_size.index = 0

        self.boxlength_options = [str(b.properties.cube_length) for b in SolventBoxOptions]
        self.solventbox_size = ipw.Combobox(
            options = self.boxlength_options,
            ensure_option=False,
            placeholder='Type Length',
            value= "40",
            disabled = False,
            description ="Half Side-length",
            layout = shared_layout,
            style = shared_style,
        )
        self.model.solvent_boxsize= int(self.solventbox_size.value)

        #self.solventname_drop = ipw.Dropdown(
        #    options = [b.properties.name for b in SolventBoxOptions],
        #    disabled = False,
        #    description ="Solvent Name",
        #    layout = shared_layout,
        #    style = shared_style,
        #)
        #self.solventname_drop.index = 0

        self.name_options = [b.properties.name for b in SolventBoxOptions]
        self.solventname_drop = ipw.Combobox(
            options = self.name_options,
            ensure_option=False,
            placeholder='Type name',
            value= "chloroform",
            disabled = False,
            description ="Solvent Name",
            layout = shared_layout,
            style = shared_style,
        )
        self.model.solvent_name = self.solventname_drop.value

        self.qm_method_dropdown = ipw.Dropdown(
            options ={"DFT" : True, "HF" : False},
            description ="SCF method:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "use_dft"), (self.qm_method_dropdown, "value"))

        self.basis_string = ipw.Text(
            value ="",
            description ="Basis Set:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "basis_set"), (self.basis_string, "value"))

        self.backend = ipw.Dropdown(
            options ={e.name: e for e in ChemShellQMTheory},
            description ="QM Backend:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "qm_theory"), (self.backend, "value"))

        self.functional = ipw.Text(
            value ="B3LYP",
            description ="Functional:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "functional"), (self.functional, "value"))

        self.dispersion = ipw.Text(
            value ="",
            description ="Dispersion:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "nw_dispersion"), (self.dispersion, "value"))

        self.energy_tol = ipw.FloatText(
            description ="Energy Tolerance:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "nw_tol_energy"), (self.energy_tol, "value"))

        self.qm_container = ipw.VBox([self.backend, self.qm_method_dropdown, self.basis_string, self.functional, self.dispersion, self.energy_tol])

        self.esp_basis_string = ipw.Text(
            value ="",
            description ="Basis Set:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "esp_basis_set"), (self.esp_basis_string, "value"))
        self.esp_functional = ipw.Text(
            value ="B3LYP",
            description ="Functional:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "esp_functional"), (self.esp_functional, "value"))
        self.esp_qm_method_dropdown = ipw.Dropdown(
            options ={"DFT" : True, "HF" : False},
            description ="SCF method:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "esp_use_dft"), (self.esp_qm_method_dropdown, "value"))

        self.esp_qm_container = ipw.VBox([self.esp_qm_method_dropdown, self.esp_basis_string, self.esp_functional])

        # MM Backend
        self.mm_theory_dropdown = ipw.Dropdown(
            options = self._get_mm_theory_options(),
            value = "DL_POLY",
            description ="MM Theory:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
         )
        ipw.dlink((self.mm_theory_dropdown, "value"), (self.model, "mm_theory"))

        # Force Field File
        self.ff_file = FileUploadWidget(description ="Force Field:")
        link((self.ff_file, "file"), (self.model, "force_field"))

        self.esp_method_dropdown = ipw.Dropdown(
            options =["resp", "esp"],
            value ="resp",
            description ="ESP Method:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "chargefit_method"), (self.esp_method_dropdown, "value"))

        self.chargefit_npoints = ipw.IntText(
            value =50,
            description ="Npoints",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "chargefit_npoints"), (self.chargefit_npoints, "value"))

        self.chargefit_type = ipw.Text(
            value ="shell",
            description ="Type",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "chargefit_type"), (self.chargefit_type, "value"))

        self.chargefit_tolerance = ipw.FloatText(
            value =1e-12,
            description ="Tolerance",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "chargefit_tolerance"), (self.chargefit_tolerance, "value"))

        self.chargefit_vdw_scale = ipw.FloatText(
            value =1.5,
            description ="VdW scale",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "chargefit_vdw_scale"), (self.chargefit_vdw_scale, "value"))

        self.chargefit_nlayers = ipw.IntText(
            value =1,
            description ="Nlayers",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "chargefit_nlayers"), (self.chargefit_nlayers, "value"))

        self.rcut = ipw.FloatText(
            value =20.0,
            description ="Rcut",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "md_rcut"), (self.rcut, "value"))

        self.temperature = ipw.FloatText(
            value =300.0,
            description ="Temperature",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "md_temperature"), (self.temperature, "value"))

        self.minimisation_step = ipw.FloatText(
            value= 1.0, step= 0.5,
            description = "Minimisation Step Size",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "md_minimise_step"), (self.minimisation_step, "value"))

        self.length_npt = ipw.IntText(
            value =5,
            description ="N Steps for NPT",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "md_length_npt"), (self.length_npt, "value"))

        self.length_nvt = ipw.IntText(
            value =5,
            description ="N Steps for NVT",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "md_length_nvt"), (self.length_nvt, "value"))

        self.length_tot_run = ipw.IntText(
            value =100,
            description ="N Steps for Production Run",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "md_length_production"), (self.length_tot_run, "value"))

        self.length_ncycles = ipw.IntText(
            value =10,
            description ="Maximum Cycles",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "md_max_ncycles"), (self.length_ncycles, "value"))

        self.n_minimise_npt = ipw.IntText(
            value =10,
            description ="N Steps NPT minimisation",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "md_minimisation_npt"), (self.n_minimise_npt, "value"))

        self.n_minimise_nvt = ipw.IntText(
            value =10,
            description ="N Steps NVT minimisation",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "md_minimisation_nvt"), (self.n_minimise_nvt, "value"))

        self.n_snapshots = ipw.IntText(
            value =10,
            description ="Num of Snapshots",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "md_nsnapshots"), (self.n_snapshots, "value"))

        self.solutes_dist = ipw.FloatText(
            value =20.0,
            description ="Solutes distance",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        #link((self.model, "md_solutes_dist"), (self.solutes_dist, "value"))

        self.padding = ipw.FloatText(
            value =20.0,
            description ="Padding",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "md_padding"), (self.padding, "value"))

        self.fixed_npt = ipw.Text(
            value ='',
            description ="Atoms fixed for NPT",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "md_fixed_npt"), (self.fixed_npt, "value"))

        self.fixed_nvt = ipw.Text(
            value ='',
            description ="Atoms fixed for NVT",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "md_fixed_nvt"), (self.fixed_nvt, "value"))

        self.esp_container = ipw.VBox([self.chargefit_npoints, self.chargefit_type, self.chargefit_tolerance, self.chargefit_vdw_scale, self.chargefit_nlayers])

        self.md_container = ipw.VBox([self.temperature, self.rcut, self.length_npt, self.length_nvt, self.length_tot_run, self.minimisation_step, self.length_ncycles, self.n_snapshots, self.n_minimise_nvt, self.n_minimise_npt, self.padding, self.fixed_nvt, self.fixed_npt])
        #self.md_container = ipw.VBox([self.temperature, self.rcut, self.length_npt, self.length_nvt, self.length_tot_run, self.n_snapshots, self.n_minimise_nvt, self.n_minimise_npt, self.padding, self.fixed_nvt, self.fixed_npt])

        self.shell_radius = ipw.FloatText(
            value =20.0,
            description ="Radius of Shell",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "qmmm_shell_radius"), (self.shell_radius, "value"))

        self.active_radius = ipw.FloatText(
            value =12.0,
            description ="Radius of Active region",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "qmmm_active_region_radius"), (self.active_radius, "value"))

        self.snap_label = ipw.Label(value="Number of MD Snapshots to run QMMM for, Leave 0 for all snapshots",
        )
        self.qmmm_nsnapshots = ipw.IntText(
            value = 0,
            disabled = False,
            layout=ipw.Layout(width="80px", margin = "0px 0px 0px 5px"),
            #layout = shared_layout,
            #style = shared_style,
            #style={"description_width": "initial"}
        )
        link((self.model, "qmmm_snapshots"), (self.qmmm_nsnapshots, "value"))

        self.snapshot_box = ipw.HBox([self.snap_label, self.qmmm_nsnapshots],
          layout=ipw.Layout(align_items="center", margin="0px 0px 0px 100px")
        )

        self.qmmm_method_dropdown = ipw.Dropdown(
            options ={"DFT" : True, "HF" : False},
            description ="SCF method:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "qmmm_use_dft"), (self.qmmm_method_dropdown, "value"))

        self.qmmm_basis_string = ipw.Text(
            value ="",
            description ="Basis Set:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "qmmm_basis_set"), (self.qmmm_basis_string, "value"))
        self.qmmm_functional = ipw.Text(
            value ="B3LYP",
            description ="Functional:",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "qmmm_functional"), (self.qmmm_functional, "value"))

        self.qmmm_dryrun = ipw.Dropdown(
            options = {"Full run" : False, "Dry run" : True},
            value = True,
            description = "Choose Full-Run/Dry Run",
            disabled = False,
            layout = shared_layout,
            style = shared_style,
        )
        link((self.model, "qmmm_dryrun"), (self.qmmm_dryrun, "value"))

        self.qmmm_opt = ipw.Checkbox(
            value = False,
            description = "Do Optimisation",
            layout = shared_layout2,
            style = shared_style2,
        )
        link((self.model, "qmmm_opt"), (self.qmmm_opt, "value"))

        self.qmmm_qm_container = ipw.VBox([self.qmmm_method_dropdown, self.qmmm_basis_string, self.qmmm_functional, ])
        self.qmmm_adv_container = ipw.VBox([ self.shell_radius, self.active_radius,])

        self.qmmm_container = ipw.VBox([self.qmmm_label, self.qmmm_dryrun, self.qmmm_opt, self.snapshot_box, self.advanced_qmmm_options,])

        self.mm_container = ipw.VBox([self.ff_file])

        self.solvent_container = ipw.VBox([self.solventbox_dropdown, self.solventname_drop, self.solventbox_size])

        self._render_basic_options()

    def _render_basic_options(self) -> None:
        """Render the simplified input options view."""
        children = [
            self.header,
            self.opt_label,
            self.do_opt_dryrun,
            self.advanced_qm_options,
            self.basis_dropdown,
            self.solvation_label,
            self.solvent_container,
            self.solvent_structfile,
            self.solventbox_view_select,
            self.viewer,
            self.esp_label,
            self.do_charge_dryrun,
            self.advanced_esp_options,
            self.esp_method_dropdown,
            self.esp_qm_options,
            self.md_label,
            self.mm_theory_dropdown,
            self.advanced_md_options,
            self.advanced_md_mm_options,
            self.submit_dry_btn,
            #self.do_md_dryrun,
            self.qmmm_container,
            self.advanced_qmmm_qm_options,
            self.advanced_qmmm_mm_options,
        ]
        self.children = children
        return

    def _render_advanced_options(self) -> None:
        """Render the advanced input options view."""
        children = [self.header, self.opt_label, self.do_opt_dryrun, self.advanced_qm_options, self.basis_dropdown]

        if self.advanced_qm_options.value:
            children.append(self.qm_container)

        children.extend([
            self.solvation_label,
            self.solvent_container,
            self.solvent_structfile,
            self.solventbox_view_select,
            self.viewer,
        ])
        children.extend([self.esp_label, self.do_charge_dryrun, self.advanced_esp_options,
                        self.esp_method_dropdown])

        if self.advanced_esp_options.value:
            children.append(self.esp_container)

        children.append(self.esp_qm_options)
        if self.esp_qm_options.value:
            children.append(self.esp_qm_container)

        children.extend([self.md_label, self.advanced_md_options])
        children.append(self.mm_theory_dropdown)
        if self.advanced_md_options.value:
            children.append(self.md_container)
        children.append(self.advanced_md_mm_options)
        if self.advanced_md_mm_options.value:
            children.append(self.mm_container)
        children.append(self.submit_dry_btn)

        children.append(self.qmmm_container)
        if self.advanced_qmmm_options.value:
            children.append(self.qmmm_adv_container)
        children.append(self.advanced_qmmm_qm_options)
        if self.advanced_qmmm_qm_options.value:
            children.append(self.qmmm_qm_container)

        children.append(self.advanced_qmmm_mm_options)
        if self.advanced_qmmm_mm_options.value:
            children.append(self.mm_container)

        self.children = children

        return

    def _render_options(self, change: dict) -> None:
        """Switch between basic and advanced views."""
        if change["new"]:
            self._render_advanced_options()
        else:
            if not self._rendered:
                self._render_basic_options()
            else:
                self._render_advanced_options()
        self._rendered = True
        return

    def _render_input_options(self, change: dict) -> None:
        """Switch between basic and advanced views."""
        if change["new"]:
            self._render_advanced_options()
        else:
            if not self._rendered:
                self._render_basic_options()
            else:
                self._render_advanced_options()
            # Update the linked basis set value
        self._update_basis_set({"new": self.basis_dropdown.value, "old": None})
        self._rendered = True
        return

    def _update_basis_set(self, change: dict) -> None:
        """Update the basis set based of the simplified input options."""
        if change["new"] == change["old"]:
            return
        self.model.basis_set = change["new"].label
        self.model.functional = change["new"].functional
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
                contents = read(handle, format ="proteindatabank")
                xyzfile = write("structurepqr.xyz", contents, format ="xyz")
                newfile = SinglefileData(file = str(Path("structurepqr.xyz").resolve()))
            return newfile

        else:
            return file

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

    def _on_file_upload(self, change: dict) -> None:
        self.model.solvent_box = change["new"]

    def _update_solventbox_set(self, change: dict) -> None:
            """Update Solvent boxes based of the user's choice."""
            if change["new"] == change["old"]:
                return
            if change["new"] is self.UPLOAD:
                self.solvent_structfile.layout.display="flex"
            else:
                self.model.solvent_box = SinglefileData(file = change["new"])
                self.solvent_structfile.layout.display="none"

                #self.solventname_drop.index = self.solventbox_dropdown.index
                #self.solventbox_size.index = self.solventbox_dropdown.index
                self.solventbox_size.value = str(self.boxlength_options[self.solventbox_dropdown.index])
                self.solventname_drop.value = self.name_options[self.solventbox_dropdown.index]
                self.model.solvent_name = self.solventname_drop.value
                self.model.solvent_boxsize= int(self.solventbox_size.value)
            return

    def disable(self, disabled: bool = True) -> None:
        """Recursively disable or enable all child widgets in a container."""

        def _toggle(widget):
            if hasattr(widget, "disabled"):
                widget.disabled = disabled
            elif hasattr(widget, "style"):
                if disabled and hasattr(widget.style, "text_color"):
                    widget.style.text_color = "grey"
            if widget is self.submit_dry_btn:
              if widget.disabled:
                  self.submit_dry_btn.description = "Submitted MD Dry run"
              else:
                  self.submit_dry_btn.description = "Submit a Dry Run of MD"
            if hasattr(widget, "children"):
                for child in widget.children:
                    _toggle(child)
        _toggle(self)
        return

    def _submit_dry(self,_):
        self.disable(True)
        self.model.md_dryrunmd = True

#    def disable(self, disable: bool = True) -> None:
#        """Disable/Enable the wigets input options."""
#        for child in self.children:
#            child.disabled = disable
#        return
