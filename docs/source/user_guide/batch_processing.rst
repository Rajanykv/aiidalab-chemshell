.. _batch_processing:

Batch Processing
================

Alongside the main :ref:`New Calculation <workflows>` page, the AiiDAlab ChemShell plugin
provides a dedicated **Batch Processing** page for running the same calculation across a
whole collection of structures at once. It is accessed via the *Batch Calculation* button
found in the start banner and in the navigation header shared across the plugin's pages.

The batch page is built on the same wizard style interface as the main calculation page,
so much of its operation will already be familiar. The key difference is that, rather than
configuring a single structure and a choice of workflow, it takes a *set* of structures
and runs each one through an identical **single point energy** calculation. This makes it
well suited to tasks such as evaluating the energies of every frame of a trajectory or a
library of candidate structures under a common set of parameters.

Configuration Wizard
--------------------

As with the main page, the batch page is broken down into a series of wizard steps, each
with a **submit** button that locks in the user's choices before proceeding.

Select Structures Input
~~~~~~~~~~~~~~~~~~~~~~~~

This step replaces the single structure input of the main page with a *batch* input. The
supported inputs are:

- A multi-frame ``.xyz`` file, where each frame is treated as a separate structure.
- An AiiDA ``TrajectoryData`` object, for example one produced by a previous calculation
  or made available through the AiiDA command line interface (CLI).

Each frame of the supplied input is run as an individual single point energy calculation.
Aside from accepting these multi-structure inputs, the step behaves the same as the
standard :ref:`Structure Input <workflows>` step.

.. note:: 

  At present the visualisation of trajectories supplied via a multi-frame ``.xyz`` file is
  not fully supported and thus just the first frame will be shown in the viewer window.
  

Configure Workflow
~~~~~~~~~~~~~~~~~~

The workflow step reuses the same configuration options as the
:ref:`Single Point Energy <workflows>` workflow on the main calculation page. Unlike the
main page there is no choice of workflow type here; every structure in the batch is run
with a single point energy calculation using the configuration defined in this step.

The single point options (including the *QM*/*QM/MM* settings, energy derivatives and
vibrational frequency options) are configured once and then applied identically to every
structure in the batch.

Configure Computational Resources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step is identical to the resource setup step of the main calculation page, allowing
the user to select the *AiiDA code instance* and the computational resources used to run
the calculations. See :ref:`resource_management` for more details on configuring the
underlying *computer* and *code* instances.

Results
~~~~~~~

The final step provides the combined job monitor and results viewer, in the same manner
as the main calculation page. Here the progress of the individual calculations making up
the batch can be monitored and their results inspected once complete. As with the main
page, results objects appear under each finished process and can be visualised directly
within the interface.


.. note::

    For a description of the underlying single point energy configuration options, and of
    the shared structure, resource and results steps, see the main
    :ref:`ChemShell Workflow Configuration <workflows>` page.
