MCP Helpers
==================

The ``gekko.gk_mcp`` add-on module provides a sidecar helper layer for working with GEKKO models directly from Python code. It does not modify the base GEKKO implementation. Instead, it operates on a live ``GEKKO()`` object or creates a new one when needed.

Core usage follows this pattern:

.. code-block:: python

   from gekko import GEKKO
   from gekko import gk_mcp

   m = GEKKO(remote=False)
   helper = gk_mcp.ModelMCP(m)

   dof = helper.get_degrees_of_freedom()
   options = helper.get_options()
   tuning = helper.suggest_tuning_changes(goal="faster solve")

The helper can also create a model:

.. code-block:: python

   from gekko import gk_mcp

   m = gk_mcp.create_model(remote=False, name="my_model")

Available Functions
-------------------

- ``create_model``: create a new ``GEKKO()`` object.
- ``attach_model`` / ``ModelMCP``: wrap an existing ``GEKKO()`` object with direct helper methods.
- ``materialize_model``: write `.apm`, `.csv`, `.info`, and `measurements.dbs` files for the current model state.
- ``bundle_model``: copy the current model artifacts into ``.mcp/runs/<run_id>`` for later inspection.
- ``get_degrees_of_freedom``: return structural counts and a solver-reported or estimated degrees-of-freedom summary.
- ``get_options``: parse ``measurements.dbs``, ``.info``, and ``options.json`` into grouped tuning data.
- ``summarize_results``: summarize ``results.json`` when it is available.
- ``diagnose_model``: inspect current artifacts plus optional stdout and stderr text to classify failures.
- ``suggest_tuning_changes``: return rule-based tuning suggestions from the current model artifacts.
- ``check_python_syntax``: catch Python parser errors before running a model script.
- ``scaffold_model_script``: generate starter scripts for steady-state, dynamic optimization, MHE, and MPC use cases.
- ``run_python_script``: execute a Python model script and bundle its artifacts.

Building a New Model
--------------------

You can build directly with ``GEKKO()`` and then inspect the current model:

.. code-block:: python

   from gekko import GEKKO, gk_mcp

   m = GEKKO(remote=False)
   x = m.Var(value=1)
   y = m.Var(value=2)
   m.Equations([x + y == 5, x - y == 1])

   helper = gk_mcp.ModelMCP(m)
   print(helper.materialize())
   print(helper.get_degrees_of_freedom())

If you want a script template first:

.. code-block:: python

   from gekko import gk_mcp
   from pathlib import Path

   workspace = Path(".")
   template = gk_mcp.scaffold_model_script(workspace, problem_type="steady_state", model_name="demo")
   syntax = gk_mcp.check_python_syntax(source=template["source"])

Syntax errors are reported with the line, column, and offending text so an LLM can repair the script before execution.

Diagnosing Solve Failures
-------------------------

When a solve fails, pass the current model and any captured solver output:

.. code-block:: python

   from gekko import gk_mcp

   helper = gk_mcp.ModelMCP(m)
   diagnosis = helper.diagnose(stdout_text=solver_stdout, stderr_text=solver_stderr)
   print(diagnosis)

The diagnosis looks for:

- Python syntax and runtime exceptions
- APMonitor ``@error`` blocks
- infeasibility messages
- time limits and convergence issues
- negative or suspicious degrees of freedom

The return value includes supporting file paths so the LLM can inspect the compiled model and tuning files alongside the failure summary.

Tuning to Improve Performance
-----------------------------

Use the helper on the current model after materialization or solve:

.. code-block:: python

   from gekko import gk_mcp

   helper = gk_mcp.ModelMCP(m)
   options = helper.get_options()
   results = helper.summarize_results()
   tuning = helper.suggest_tuning_changes(goal="faster solve with smoother MV movement")

Typical suggestions include:

- reducing ``NODES`` for smaller solves
- enabling ``SCALING``
- increasing ``MV.DCOST`` to smooth controller action
- setting a finite ``MV.DMAX``
- decreasing ``CV.TAU`` for tighter tracking
- increasing ``FSTATUS`` or ``WMEAS`` for estimation workflows

Optional Run Bundles
--------------------

If you want a persistent copy of the current model artifacts, create a bundle:

.. code-block:: python

   bundle = helper.bundle(stdout_text=solver_stdout, stderr_text=solver_stderr)

Bundles are stored under:

.. code-block:: text

   .mcp/runs/<run_id>/

This is useful when an LLM needs to inspect a model repeatedly after the original temporary GEKKO run directory changes.
