.. _global_options:

Global Options
====================


.. toctree::
	:maxdepth: 2

..	index
..	overview
..	modelparts
..	imode
..	tuning_params
..	MV_options
..	CV_options
..	imode
..	questions


The following is a list of global model attributes. Each attribute is available through the model attributes `options`, eg: ::

    from gekko import GEKKO
    m = GEKKO()
    m.options.IMODE = 3

GEKKO only allows input options to be written, while all options can be read.

This is a complete list of the configuration parameters. Each section includes an indication of the variable type (Integer or Real), the default value, data flow, and description.


.. _appinfo:

APPINFO
------------------------

Type: Integer, Output

Default Value: 0

Description: Application information: 0=good, error otherwise

Explanation: APPINFO is an error code when the solution is not successful. The meaning of an error code is different for each solver that is selected. The one common code is a value of 0 that always indicates a successful solution. APPINFO is a more detailed error report than APPSTATUS that only gives a binary indication of application success.


.. _appinfo:

APPINFOCHG
------------------------

Type: Integer, Output

Default Value: 0

Description: Application information change (new-old): 0=no change

Explanation: APPINFOCHG is the difference between the prior value of APPINFO and the most current value of APPINFO. The difference is useful in determining when an application solution may have changed due to several factors as reported by the error code when APPINFOCHG is non-zero.


.. _appstatus:

APPSTATUS
------------------------

Type: Integer, Output

Default Value: 1

Description: Application status: 1=good, 0=bad

Explanation: APPSTATUS is the overall health monitoring for an application. An application may be unsuccessful for a number of reasons and the APPSTATUS changes to 0 (bad) if it is not able to provide a solution. The APPSTATUS is 1 (good) when the solver converges to a successful solution and there are no errors in reporting the solution.


.. _auto_cold:

AUTO_COLD
---------------------------

Type: Integer, Input

Default Value: 0

Description:
Automatically cold start model after a specified number of bad cycles
0  = do not auto coldstart
1+ = cold start after specified number of bad cycles as recorded by BAD_CYCLES

Explanation: AUTO_COLD is the number of consecutive bad cycles to wait to attempt a COLDSTART as an initialization mode for an application. It is by default at 0 (no action with bad cycles) but can be set to a higher integer level (1+) as a trigger to initiate a coldstart. When the AUTO_COLD limit is reached, the COLDSTART flag is set to 1 (ON) and it remains on until there is a successful solution. Once a successful solution is found, COLDSTART and BAD_CYCLES are set to zero.


.. _bad_cycles:

BAD_CYCLES
---------------------

Type: Integer, Input/Output

Default Value: 0

Description: Counter on number of bad cycles
0  = initial value
1+ = number of consecutive unsuccessful solution attempts

Explanation: BAD_CYCLES is a counter that increments when the application fails to produce a successful solution. When BAD_CYCLES reaches the AUTO_COLD limit, a COLDSTART is initiated. Once a successful solution is found, COLDSTART and BAD_CYCLES are set to zero.



.. _bnds_chk:

BNDS_CHK
------------------------

Type: Integer, Input

Default Value: 1

Description: Bounds checking: 1=ON, 0=OFF

Explanation: BNDS_CHK validates a measurement with VLHI, VLLO, and VDVL properties. When BNDS_CHK is OFF, there is no checking of the validity limits. Although an application may have specific validity limits set, it is occasionally desirable to take off the checks to observe raw data input to the model without error detection. All measurement validation actions are reported in the text file dbs_read.rpt. BNDS_CHK, FRZE_CHK, and MEAS_CHK are options regarding data cleansing before it enters the applications. When a measurement is bad, the LSTVAL is restored as the measured value or else LSTVAL+VDVL or LSTVAL-VDVL. The VDVL shift depends on whether VLACTION is 0 (keep LSTVAL) or else is 1 (step by VDVL towards measurement).


.. _coldstart:

COLDSTART
------------------------

Type: Integer, Input/Output

Default Value: 0

Description: Cold start model: 0=warm start, 1=cold start, 2=decompose problem

Explanation: COLDSTART is an initialization mode for an application. It is by default at 0 (no initialization) but can be set to higher levels (1 or 2) to handle cases where initialization of the problem is a key enabler for a successful solution or to reset an application after a failed solution or a period of inactivity. The initialization values are typically taken from a prior solution as stored in t0 files on the server. When COLDSTART>=1, the t0 files are ignored and the initialization values are taken from the file, the DBS file, and the CSV file in that order. A value of 1 indicates that all FV, MV, and CV STATUS values are turned off (0) temporarily to reduce the number of degrees of freedom and achieve a feasible, yet suboptimal solution. A value of 2 is a more aggressive initialization where the degrees of freedom are turned off and the sparsity of the problem is analyzed to create a sequence of lower block triangular segments. These segments are solved sequentially and an error is reported if a particular block is infeasible. Therefore, COLDSTART=2 is one method to help identify equations or variables bounds that may be causing an infeasible solution. Once the application is successfully solved with COLDSTART>=1, the value of COLDSTART is automatically reset to 0 for the next solution.


.. _csv_read:

CSV_READ
------------------------

Type: Integer, Input

Default Value: 2

Description: CSV read: 0=Off, 1=Batch, 2=Sequential

Explanation: CSV_READ indicates whether a comma separated value data file should be used by the application as part of initializing a problem and loading data. The name of the CSV file is the same as the name of the model file.

Values assigned to GEKKO variables and the model time are primarily communicated to APMonitor through the csv file. If CSV_READ=0, only scalar values of parameters and variables are read through the .apm file. If CSV_READ=1, all parameter values are also read in. If CSV_READ=2, all parameter and (initial) variable values are loaded.

Only values defined by the user since model initialization or the last solve are written to the csv. All other values are loaded back from the APM internal .t0 database files and timeshifted according to the TIME_SHIFT option.
If a measurement (.MEAS) is defined, the associated variable value is not written to the csv. Also, if a variable value is fixed with the fix() command, the fixed value is written in the csv file.



.. _csv_write:

CSV_WRITE
------------------------

Type: Integer, Input

Default Value: 0

Description: CSV write: 0=Off, 1=Write results.csv, 2=Write results_all.csv

Explanation: CSV_WRITE is an option that controls how much information is written to results files.
When it is 0 (OFF), no result files are written. This may be desirable to further reduce the time associated with solution post-processing.
When CSV_WRITE=1, a file results.csv is written with all of the constants, parameters, and variables. The data is written in a row oriented form with each row header as the name and subsequent column values are the values at each of the time points requested in the input data file. The values from results.csv are automatically loaded back to the GEKKO variables' attribute `value`.
When CSV_WRITE=2, another file named results_all.csv is produced that contains not only the endpoints but also the intermediate collocation nodes of the solution. This data file is saved in the model path, visible by `print(m.path)`.


.. _ctrlmode:

CTRLMODE
------------------------

Type: Integer, Output

Default Value: 1

Description: Control mode: 0=terminate, 1=simulate, 2=predict, 3=control

Explanation: The CTRLMODE is the actual controller mode implemented by the application and is an output after the application has completed each cycle. The requested control mode (REQCTRLMODE) is set as an input to the desired level of control but sometimes the CTRLMODE is not able to match the request because of a failed solution, a critical MV is OFF, or other checks with the application. A CTRLMODE level of 0 indicates that the program did not run due to a request to terminate. A CTRLMODE level of 1 (cold mode) indicates that the program was run as a simulator with all STATUS values turned off on FVs, MVs, and CVs. A CTRLMODE level of 2 (warm mode) indicates that the application calculates control actions but only after the second cycle. This mode is commonly used to observe anticipated control actions before the controller is activated to level 3. The CTRLMODE level of 3 means that the controller is ON and implementing changes to the process.


.. _ctrl_hor:

CTRL_HOR
------------------------

Type: Integer, Input or Output (with CSV read)

Default Value: 1

Description: Control horizon: Horizon length where MVs can be adjusted by the solver

Explanation: CTRL_HOR is the control horizon in the beginning portion of the time horizon where MV changes are allowed. There is also a PRED_HOR (prediction horizon) that is greater than or equal to CTRL_HOR. As opposed to CTRL_HOR, no manipulated variable movement is allowed in the prediction horizon. The individual size of time steps of the control horizon are set with CTRL_TIME. The individual size of time steps of the prediction horizon are set with PRED_TIME. The PRED_TIME is generally larger than the CTRL_TIME to give a section of the overall horizon that predicts steady state arrival to the set point. When CSV_READ is on and the horizon time points are specified from the data file, the CTRL_HOR and PRED_HOR are set equal to the number of time steps present in the data file.


.. _ctrl_time:

CTRL_TIME
------------------------

Type: Real, Input or Output (with CSV read)

Default Value: 60

Description: Time for each step in the control horizon

Explanation: CTRL_TIME is the cycle time of the controller for real-time applications. The clock time trigger for initiating successive controller solutions should be synchronized with CTRL_TIME to avoid dynamic mismatch between the internal simulation time and the process measurements. When CSV_READ is on and the horizon time points are specified from the data file, the CTRL_TIME and PRED_TIME are set equal to the time increment of the first time step.


.. _ctrl_units:

CTRL_UNITS
------------------------

Type: Integer, Input

Default Value: 1

Description: Model time units (1=sec, 2=min, 3=hrs, 4=days, 5=yrs)

Explanation: CTRL_UNITS are the time units of the model. This option does not affect the solution but does affect the x-axis of the web plots. The time displayed on the web plots is shown according to the HIST_UNITS option but scaled from the model units as specified by CTRL_UNITS. The valid options are 1=sec, 2=min, 3=hrs, 4=days, and 5=yrs. If CTRL_UNITS=1 and HIST_UNITS=2 then the model is in seconds and the web plots have model predictions and measurements that are displayed in minutes.


.. _cv_type:

CV_TYPE
------------------------

Type: Integer, Input

Default Value: 1

Description: Controlled variable error model type: 1=linear, 2=squared, 3=ref traj

Explanation: CV_TYPE is a selection of the type of objective function to be used for variables defines as controlled variables (CVs) in control (IMODE=6 or 9) applications. The options are to use a linear penalty from a dead-band trajectory (CV_TYPE=1), squared error from a reference trajectory (CV_TYPE=2), or an experimental reference trajectory type (CV_TYPE=3).


.. _cv_wgt_slope:

CV_WGT_SLOPE
------------------------

Type: Real, Input

Default Value: 0.0

Description: Slope for weight on future CV error (e.g. [+] favors steady state)

Explanation: CV_WGT_SLOPE is how the controlled variable WSPHI, WSPLO, or WSP change with time over the control horizon. This option is used to favor either near-term attainment of the setpoint or long-term (future) steady state tracking. It is normally set to zero but can be adjusted to be positive to increase the weighting for future time points or negative to decrease the weighting for future time points.


.. _cv_wgt_start:

CV_WGT_START
------------------------

Type: Integer, Input

Default Value: 0

Description: Start interval for controlled variable error model weights

Explanation: CV_WGT_START is the time step that the controlled variables WSPHI, WSPLO, or WSP start. Before this time step, there is no penalty so that there are no near term objectives to reach a setpoint or trajectory. This option is used to consider long-term (future) steady state tracking while ignoring the near-term path to achieve the final target. It is normally set to zero but can be adjusted to be any positive integer between 0 and the number of time steps in the horizon.



.. _cyclecount:

CYCLECOUNT
--------------

Type: Integer, Input with Output (+1)

Default Value: 0

Description: Cycle count, increments every cycle

Explanation: CYCLECOUNT is a counter that records the number of cycles of the application. It is both an input and output value because the CYCLECOUNT value can be reset. The CYCLECOUNT may be reset when it is desirable to record when a certain event occurs such as a set point change or when the application is re-initialized.


.. _dbs_level:

DBS_LEVEL
------------------

Type: Integer, Input

Default Value: 1

Description: Database level limited to a subset of options
0=Basic, Limited Options
1=All Options

Explanation: DBS_LEVEL is an input option to control what is written to the DBS (database) file. When DBS_LEVEL=0, only a subset of basic parameters are written to the DBS file. This is used for compatibility with some industrial control systems that only support a subset of parameters. The basic global parameters are the following:

APPINFO, APPINFOCHG, APPSTATUS, COLDSTART, CYCLECOUNT,
DIAGLEVEL, ITERATIONS, OBJFCNVAL, REQCTRLMODE, SOLVESTATUS,
SOLVETIME

Local parameters that are designated as basic types are only used when DBS_LEVEL=0:

BIAS, COST, CRITICAL, DCOST, DMAX, DMAXHI, DMAXLO, FSTATUS,
LOWER, LSTVAL, MEAS, MODEL, NEWVAL, NXTVAL, PSTATUS, REQONCTRL,
SP, SPHI, SPLO, STATUS, TAU, UPPER, VDVL, VLHI, VLLO, WSPHI,
WSPLO



.. _dbs_read:

DBS_READ
------------------------

Type: Integer, Input

Default Value: 1

Description: Database read: 0=OFF, 1={Name = Value, Status, Units}, 2={Name,Value}

Explanation: DBS_READ specifies when to read the input DBS files with 0=OFF, 1=Read values with Units, and 2=Read values without Units. There are several text file database (DBS) files that are read at the start of an application for both configuring the problem as well as reading in measurements. The DBS files are skipped when DBS_READ=0 except for header parameters. The DBS files are read in the order of defaults.dbs, {problem name}.dbs, measurements.dbs (source is replay.csv when REPLAY>=1), and overrides.dbs. The DBS files may be need to be skipped to re-initialize an application without feedback from the process.


.. _dbs_write:

DBS_WRITE
------------------------

Type: Integer, Input

Default Value: 1

Description: Database write: 0=OFF, 1={Name = Value, Status, Units}, 2={Name,Value}

Explanation: DBS_WRITE specifies when to write the output DBS files with 0=OFF, 1=Write values with Units, and 2=Write values without Units. It may be desirable to turn off the DBS file writing when the DBS file sends feedback to the process and the application is under development.


.. _diaglevel:

DIAGLEVEL
------------------------

Type: Integer, Input

Default Value: 0

Description: Diagnostic level: 0=none, 1=messages, 2=file checkpoints, 4=diagnostic files, 5=check 1st deriv

Explanation: DIAGLEVEL is the diagnostic level for an application. With higher levels, it is used to give increasingly greater detail about the model compilation, validation, and traceability of information. At level 0, there is minimal information reported that typically includes a summary of the problem and the solver output. At level 1, there are more information messages and timing information for the different parts of the program execution. At level 2, there are diagnostic files created at every major step of the program execution. A diagnostic level of >=2 slows down the application because of increased file input and output, validation steps, and reports on problem structure. Additional diagnostic files are created at level 4. The analytic 1st derivatives are verified with finite differences at level 5 and analytic 2nd derivatives are verified with finite differences at level 6. The DIAGLEVEL is also sent to the solver to indicate a desire for more verbose output as the level is increased. Some solvers do not support increased output as the diagnostic level is increased. A diagnostic level up to 10 is allowed.


.. _ev_type:

EV_TYPE
------------------------

Type: Integer, Input

Default Value: 1

Description: Estimated variable error model type: 1=linear, 2=squared, 3=approximate linear

Explanation: EV_TYPE applies a specific objective function. Linear is an l1-norm, or in other words the solver minimizes the sum of the absolute value of the difference between the CV and the set point. Squared is an l2-norm or sum squared error (SSE), or in other words the solver minimizes the sum of the squared difference between the CV and the set point. l1-norm can be useful when noise or measurement error is expected because it better rejects those. Option 3 is not typically used as an approximate absolute value function that uses a nonlinear function instead of slack variables.


.. _ev_wgt_slope:

EV_WGT_SLOPE
------------------------

Type: Real, Input

Default Value: 0.0

Description: Slope for weight on more current EV error (e.g. favor near-term matching)

Explanation: EV_WGT_SLOPE is how the weight on measurement error (WMEAS) and prior model difference (WMODEL) change with time over the estimation horizon. This option is typically used to favor alignment of the most recent data. It is normally set to zero but can be adjusted to be positive to increase the weighting for more recent data points.



.. _filter:

FILTER
------------

Type: Floating Point, Input

Default Value: 1.0

Description: Measurement first-order filter: (0-1)

Explanation: FILTER determines how much of the raw measurement is used to update the value of MEAS. A filter of 0 indicates that the measurement should not be used in updating the MEAS value. The FILTER parameter applies to all inputs into the model from the CSV (data) file and also from the DBS (database) file. FILTER at 1.0 uses all of the measurement and ignores any prior measurement value and 0.5 uses half of each.

 CSV (data) file

 Model = Model * (1-FILTER) + Measured * FILTER


 DBS (database) file

 MEAS =  MEAS * FILTER + LSTVAL * (1-FILTER)

The FSTATUS parameter is used to adjust the fractional update from new measurements, but this only applies to a single entity at a time. FILTER applies globally to all inputs. Both FSTATUS and FILTER are useful to control the flow of information into the model. It is sometimes desirable to set FILTER or FSTATUS to a low value (close to 0) when the solver is not able to find a solution because of big input changes. A drawback of a filter on data is that raw inputs are not used in the application and it takes several cycles to reach true input values.



.. _frze_chk:

FRZE_CHK
---------------

Type: Integer, Input

Default Value: 1

Description: Frozen measurement checking
1=ON
0=OFF

Explanation: FRZE_CHK is a checking mechanism to ensure that a measurement has variation and is not frozen at the same value for repeat cycles of the application. If the measurement does not change, it is marked as bad and not used in the application. FRZE_CHK is useful for certain types of measurements that are known to periodically fail and stay at a constant value, such as gas chromatographs. FRZE_CHK can also detect when the application is cycling at a faster rate than the measurement device can deliver a new measurement. FRZE_CHK may be undesirable if the sensor resolution gives a false indication of a frozen measurement when it is actually a steady signal and poor sensor resolution. When FRZE_CHK is OFF, there is no checking of the difference from the prior measurement. BNDS_CHK, FRZE_CHK, and MEAS_CHK are options regarding data cleansing before it enters the applications.



.. _hist_hor:

HIST_HOR
------------------------

Type: Integer, Input

Default Value: 0

Description: History horizon in web plot displays: Integer >= 0

Explanation: HIST_HOR is the number of historical data points to display in the web browser plots. The history horizon values are appended to hst files stored on the server. When HIST_HOR is very large, it can slow down the rendering of the plots or expand the display horizon so much that it can be difficult to distinguish near-term movement. The HIST_HOR does not affect the solution, only the display of prior results. The history always trails off the back of the horizon for simulation, estimation, or control modes. For simulation and control, the newest history points are the initial conditions from the prior cycle. For estimation, the newest history points are also from the initial conditions. Initial conditions from estimation problems are not the current time but from the earliest part of the moving horizon that is time shifted off of the estimation horizon.


.. _hist_units:

HIST_UNITS
------------------------

Type: Integer, Input

Default Value: 0

Description: History time units on plots only (0=same as CTRL_UNITS, 1=sec, 2=min, 3=hrs, 4=days, 5=yrs)

Explanation: HIST_UNITS are the plots displayed in the web browser. This option does not affect the solution but does affect the x-axis of the web plots. The time displayed on the web plots is shown according to the HIST_UNITS option but scaled from the model units as specified by CTRL_UNITS. The valid options are 1=sec, 2=min, 3=hrs, 4=days, and 5=yrs. If CTRL_UNITS=1 and HIST_UNITS=2 then the model is in seconds and the web plots have model predictions and measurements that are displayed in minutes.


.. _icd_calc:

ICD_CALC
------------------------

Type: Integer, Input

Default Value: 0

Description: Specifications for initial condition differentials (MHE only): 0=OFF, 1=ON

Explanation: ICD_CALC is an option for the initial conditions that are associated with differential variables in estimation applications (IMODE=5 or 8). When ICD_CALC=1 (ON), the algebraic variables remain fixed at current values but the differential variables become adjustable by the solver. Any value in the time horizon can be fixed or calculated by setting FIXED or CALCULATED in a CONNECTIONS section of the model. The ICD_CALC option is typically used when estimation problems have uncertain initial conditions, especially during initialization. Leaving ICD_CALC=1 (ON), may reduce the predictive capability of a model to check for conservation of mass or energy because the differential equations are not enforced for the initial conditions.


.. _imode:

IMODE
------------------------

Type: Integer, Input

Default Value: 3

Description: Model solution mode: 1=ss, 2=mpu, 3=rto, 4=sim, 5=est, 6=ctl

Explanation: IMODE sets the mode or type of model solution. IMODE=1-3 uses steady state models, meaning that all differential variables are set to zero and there are no model dynamics. Options 4-9 calculate the dynamics with either simulation, estimation, or control. There are three modes each for steady state (IMODE=1-3), simultaneous method to compute the dynamics (IMODE=4-6), and sequential method to compute the dynamics (IMODE=7-9). The first option in each set is simulation (IMODE=1, 4, and 7) where the problem must have the same number of variables and equations and optimization is not allowed. The second option in each set is estimation where model parameters such as FVs and MVs or initial conditions are adjusted to match measured values (IMODE=2, 5, and 8). The third option in each set is optimization or control where controlled variables are driven to a desired target value or an objective function is either maximized or minimized (IMODE=3, 6, 9).



.. _iterations:

ITERATIONS
--------------

Type: Integer, Output

Default Value: 1

Description: Iterations for solution: >=1

Explanation: ITERATIONS are the number of major iterations required to find a solution. If the number of iterations reaches MAX_ITER, the unfinished solution is returned with an error message. The number of iterations is typically in the range of 3-100 for most problems although this number can be higher for large-scale or complex systems.



.. _linear:

LINEAR
--------------

Type: Integer, Input

Default Value: 0

Description: 0 - Nonlinear problem
1 - Linear problem

Explanation: Linear programming (LP) or mixed integer linear programming (MILP) problems can typically be solved much faster than a comparably sized nonlinear programming problem. The LINEAR option indicates whether the problem is linear. This allows the modeling language to set options in certain nonlinear solvers that improve the efficiency of the solution. All of the solvers built into APMonitor are nonlinear programming (NLP) or mixed-integer nonlinear programming (MINLP) solvers. Some of the solvers have simplifications to handle linear problems as well. This option does not override the choice of solver with SOLVER but does communicate to the solver that the problem has linear structure.



.. _max_iter:

MAX_ITER
------------------------

Type: Integer, Input

Default Value: 100

Description: Maximum iteration: >=1

Explanation: MAX_ITER is the maximum number of major iterations for solution by the solver. If this number is reached, the result cannot be trusted because the equation convergence or objective minimization does not satisfy the Karush Kuhn Tucker conditions for optimality. Reaching the maximum number of iterations can happen when the problem is large, difficult, highly nonlinear or if the problem is infeasible. Increasing MAX_ITER for infeasible problems will not lead to a feasible solution but can help detect the infeasible conditions.



.. _max_memory:

MAX_MEMORY
-----------------------

Type: Integer, Input

Default Value: 4

Description: Maximum memory utilized during model compilation with range 10^2 to 10^10

Explanation: Computer memory is allocated at run-time based on the size of the problem but there are particular parts during the model compilation that need an upper limit on model complexity. MAX_MEMORY=4 allows up to 10^4 = 10,000 sparsity elements per equation but can go up to 10^10. There are rare cases when more sparsity elements are needed than the default of 10,000. In these cases, an error message states that the amount of memory should be increased with the option MAX_MEMORY. A good practice is to increase MAX_MEMORY by an order of magnitude (+1) until the error is not encountered. Increasing MAX_MEMORY requires more Random Access Memory (RAM) when the model is compiled at the start of each optimization problem.



.. _max_time:

MAX_TIME
------------------------

Type: Real, Input

Default Value: 1.0e20

Description: Maximum run time in seconds

Explanation: MAX_TIME is the maximum amount of clock time in seconds that the solver should continue. Solutions forced to terminate early by this constraint do not satisfy the Karush Kuhn Tucker conditions for optimality. Even with this constraint, the application may fail to terminate at the required time because there are limited checks within the solvers. If a solver is stuck in a single major iteration when the time limit is reached, the program will terminate once that major iteration is completed. A supervisory application at the operating system level should generally be used to terminate applications that exceed a maximum desired amount of clock or CPU time.


.. _meas_chk:

MEAS_CHK
------------------------

Type: Integer, Input

Default Value: 1

Description: Measurement checking: 1=ON, 0=OFF

Explanation: MEAS_CHK indicates whether to check the validity of measurements before they are used in an application. When MEAS_CHK=0 (OFF), there is no checking of the measurement. Although an application may have specific validation limits, it is occasionally desirable to take off the checks to observe raw data input to the model without error detection. All measurement validation actions are reported in the text file dbs_read.rpt. BNDS_CHK, FRZE_CHK, and MEAS_CHK are options regarding data cleansing before it enters the applications. When a measurement is bad, the LSTVAL is restored as the measured value or else LSTVAL+VDVL or LSTVAL-VDVL. The VDVL shift depends on whether VLACTION is 0 (keep LSTVAL) or else is 1 (step by VDVL towards measurement).


.. _mv_dcost_slope:

MV_DCOST_SLOPE
------------------------

Type: Real, Input

Default Value: 0.1

Description: Slope for penalization on future MV moves (i.e. reduces controller procrastination)

Explanation: MV_DCOST_SLOPE implements a linear increase in movement penalty (DCOST). The increase in DCOST favors near term movement in the manipulated variable. One issue with a deadband trajectory is a phenomena called controller procrastination where the optimal solution delays a move because it gives an equal objective function to wait one or more cycles. This causes the controller to be stuck in a state of inaction. Favoring movement on the first step of the controller avoids this delay in implementing the needed changes.


.. _mv_step_hor_global:

MV_STEP_HOR
------------------------

Type: Integer, Input

Default Value: 1 (for MV_STEP_HOR) or 0 (for MV(#).MV_STEP_HOR)

Description: Step length for manipulated variables: 0 uses MV_STEP_HOR as default

Explanation: MV_STEP_HOR is the horizon length between each allowable movement of the manipulated variables. There are cases where the MV should not move every time step but should be constrained to move only a certain multiple of the collocation time step. With MV_STEP_HOR = 2, the manipulated variable is allowed to move on the first step and every other step thereafter. MV_STEP_HOR = 5, the manipulated variable is allowed to move on the first step and every 5th step thereafter. There is also a parameter MV_STEP_HOR that is used as a global configuration for all MVs when the individual MV option is set to 0.


.. _mv_type:

MV_TYPE
------------------------

Type: Integer, Input

Default Value: 0

Description: Manipulated variable type: 0=zero order hold, 1=linear

Explanation: MV_TYPE specifies either a zero order hold (0) or a first order linear (1) interpolation between the MV endpoints. When the MV_STEP_HOR is two or greater, the MV_TYPE is applied only to each segment where adjustments are allowed. The MV segment is otherwise equal to the prior time segment. The MV_TYPE only influences the solution when the number of NODES is between 3 and 6. It is not important when NODES=2 because there are no interpolation nodes between the endpoints.


.. _nodes:

NODES
------------------------

Type: Integer, Input

Default Value: 3

Description: Nodes in each horizon step

Explanation: NODES are the number of collocation points in the span of each time segment. For dynamic problems, the time segments are linked together into a time horizon. Successive endpoints of the time segments are merged to form a chain of model predictions. Increasing the number of nodes will generally improve the solution accuracy but also increase the problem size and computation time. Solution accuracy can also be improved by adding more time segments.


.. _objfcnval:

OBJFCNVAL
------------------------

Type: Real, Output

Default Value: 0.0

Description: Objective function value

Explanation: OBJFCNVAL is the objective function value reported by the solver. All objectives are converted to a minimization form before solution is attempted. Any maximization terms are multiplied by -1 to convert to an equivalent minimization form. For maximization problems, the objective function should be multiplied by -1 after retrieving OBJFCNVAL. The objective function may include multiple terms, not just a single objective. OBJFCNVAL is a summation of all objectives.


.. _otol:

OTOL
------------------------

Type: Real, Input

Default Value: 1.0e-6

Description: Objective function tolerance for successful solution

Explanation: OTOL is the relative objective function tolerance for reporting a successful solution. A lower value of OTOL, such as 1e-8, will give a more precise answer but at the expense of more iterations. The default of 1e-6 is generally sufficient for most problems. However, there are times when there are multiple objectives and higher precision is required to fully resolve minor objectives. OTOL and RTOL (relative tolerance on the equations) should generally be adjusted together.


.. _pred_hor:

PRED_HOR
------------------------

Type: Integer, Input or Output (with CSV read)

Default Value: 1.0

Description: Prediction horizon: Total horizon, including control horizon

Explanation: PRED_HOR is the prediction horizon that includes the control horizon and any additional points to track towards steady state. The PRED_HOR must be greater than or equal to CTRL_HOR (control horizon). As opposed to CTRL_HOR, no manipulated variable movement is allowed in the prediction horizon. The individual size of time steps of the prediction horizon beyond the control horizon are set with PRED_TIME. The PRED_TIME is generally larger than the CTRL_TIME to give a section of the overall horizon that predicts steady state arrival to the set point. When CSV_READ is on and the horizon time points are specified from the data file, the CTRL_HOR and PRED_HOR are set equal to the number of time steps present in the data file.


.. _pred_time:

PRED_TIME
------------------------

Type: Real, Input or Output (with CSV read)

Default Value: 60.0

Description: Time for each step in the horizon

Explanation: PRED_TIME is the prediction time of a controller beyond the control horizon. PRED_TIME is typically set to a larger value than CTRL_TIME to reach steady state conditions but also have fine resolution for near term movement of MVs. When CSV_READ is on and the horizon time points are specified from the data file, the CTRL_TIME and PRED_TIME are set equal to the time increment of the first time step.


.. _reduce:

REDUCE
-------------------

Type: Integer, Input

Default Value: 0

Description: Number of pre-processing cycles to identify equations or variables to eliminate

Explanation: REDUCE is the number of cycles of pre-solve analysis before sending the problem to a solver. The analysis eliminates variables and equations with the following characteristics:

* variables that don't belong to an equation or objective
* equations with assignments such as x=2.5 (set to value and fix)

	+ identified with a single non-zero in Jacobian row
	+ set variable equal to zero, evaluate residual
	+ then set x = -resid/jac (when abs(jac)>tolerance)
	+ check that upper or lower limits are not violated

* equations that connect two variables y = z (merge)

	+ set variables equal to zero, evaluate residual
	+ if abs(residual)~0 and abs(jac_1 - jac_2) ~ 0, merge

* independent blocks of linear equations (not yet implemented)

	+ perform Lower Block Triangularization (LBT)
	+ analyze independent blocks
	+ if equation blocks are linear then solve and fix

If no variables are left (all reduced) then APMonitor reports a successful solution without sending the problem to a solver. When no variables or equations are eliminated, the remainder of the REDUCE cycles are skipped. REDUCE has the potential to present a more dense and smaller problem to the solver but may also require more pre-processing time that is more efficiently utilized by the solver.


.. _replay:

REPLAY
------------------

Type: Integer, Input

Default Value: 0

Description: Row counter for data in replay.csv

Explanation: REPLAY is a row indicator that is incremented each cycle when REPLAY >= 1. When replay mode is activated, data from successive rows in replay.csv are inserted into the file measurements.dbs. The application solves and then REPLAY is incremented by 1. On the next cycle, measurements.dbs is populated from the next row and the cycle repeats. REPLAY is an efficient way of loading large amounts of data into an application without needing to load each measurement individually.



.. _reqctrlmode:

REQCTRLMODE
------------------------

Type: Integer, Input

Default Value: 3

Description: Requested control mode: 1=simulate, 2=predict, 3=control

Explanation: REQCTRLMODE is the requested controller mode as an input for the application. The requested control mode (REQCTRLMODE) is set as an input to the desired level of control but sometimes the CTRLMODE is not able to match the request because of a failed solution, a critical MV is OFF, or other checks with the application. REQCTRLMODE level of 0 indicates that the program should not run and the program terminates without attempting a solution. REQCTRLMODE level of 1 (cold mode) indicates that the program should be run as a simulator with all STATUS values turned off on FVs, MVs, and CVs. REQCTRLMODE level of 2 (warm mode) indicates that the application should calculate control actions but only after the second cycle. This mode is commonly used to observe anticipated control actions before the controller is activated to level 3. REQCTRLMODE level of 3 means that the controller should be turned ON and implement changes to the process.


.. _rtol:

RTOL
------------------------

Type: Real, Input

Default Value: 1.0e-6

Description: Equation solution tolerance

Explanation: RTOL is the relative inequality or equality equation tolerance for reporting a successful solution. A lower value of RTOL, such as 1e-8, will give a more precise answer but at the expense of more iterations. The default of 1e-6 is generally sufficient for most problems. However, there are times when the equation solution should be reported more precisely. Making RTOL too small may cause a bad solution to be reported because it surpasses the computer precision. RTOL and OTOL (relative tolerance for the objective function) should generally be adjusted together.


.. _scaling:

SCALING
------------------------

Type: Integer, Input

Default Value: 1

Description: Variable and Equation Scaling: 0=Off, 1=On (Automatic), 2=On (Manual)

Explanation: SCALING is an option to adjust variables by constants to make starting values equal to 1.0. Scaling of variables and equations generally improves solver convergence. Automatic and Internal scaling strategies are often implemented within solvers as well. The purpose of scaling is to avoid very large or very small values that may cause numerical problems with inverting matrices. Poor scaling may lead to ill-conditioned matrix inversions in finding a search direction. The difference between the largest and smallest eigenvalues should be within 12 orders of magnitude to avoid numerical problems. Scaling can be turned OFF (0) or ON (1). With SCALING=1, the scaling is taken from the initial guess values in the file. If the absolute value is less than one, no scaling is applied. With SCALING=2, the scaling is set for each variable individually.


.. _sensitivity:

SENSITIVITY
------------------------

Type: Integer, Input

Default Value: 1

Description: Sensitivity Analysis: 0=Off, 1=On

Explanation: SENSITIVITY determines whether a sensitivity analysis is performed as a post-processing step. The sensitivity analysis results are accessed either through the web-interface with the SENS tab or by retrieving the sensitivity.txt or sensitivity.htm files. The sensitivity is a measure of how the FV and MV values influence the objective function, SV, and CV final values. Another file, sensitivity_all.txt contains sensitivities for all of the dependent variable values with respect to the FV and MV values.



.. _sequential:

SEQUENTIAL
-------------

Type: Integer, Input

Default Value: 0

Description: Sequential solution method
0=Off
1=On

Explanation: SEQUENTIAL determines whether a the solution is attempted with a simultaneous (0) or sequential (1) approach. The sequential solution method solves independent decision variables in an outer loop from the system equations. This approach attempts to maintain feasibility from iteration to iteration but can significantly slow down the overall solution time. The SEQUENTIAL option can be used with any problem that has degrees of freedom such as IMODE=2,3,5,6. When IMODE=7-9 (Sequential Dynamic Simulation, Estimation, and Control), the SEQUENTIAL option is automatically elevated to 1 and placed back to the default of 0 when the solution is completed.



.. _solver:

SOLVER
------------------------

Type: Integer, Input

Default Value: 3

Description: Solver options: 0 = Benchmark All Solvers, 1-5 = Available Solvers Depending on License

Explanation: SOLVER selects the solver to use in an attempt to find a solution. There are free solvers: 1: APOPT, 2: BPOPT, 3: IPOPT distributed with the public version of the software. There are additional solvers that are not included with the public version and require a commercial license. IPOPT is generally the best for problems with large numbers of degrees of freedom or when starting without a good initial guess. BPOPT has been found to be the best for systems biology applications. APOPT is generally the best when warm-starting from a prior solution or when the number of degrees of freedom (Number of Variables - Number of Equations) is less than 2000. APOPT is also the only solver that handles Mixed Integer problems. Use option 0 to compare all available solvers.



.. _solvestatus:

SOLVESTATUS
------------------------

Type: Integer, Output

Default Value: 1

Description: Solution solve status: 1=good

Explanation: SOLVESTATUS is an indication of whether the solver returns a successful solution (1) or is unsuccessful at finding a solution (0). The solver may be unsuccessful for a variety of reasons including reaching a maximum iteration limit, an infeasible constraint, or an unbounded solution.



.. _solvetime:

SOLVETIME
------------------------

Type: Real, Output

Default Value: 1.0

Description: Solution time (seconds)

Explanation: SOLVETIME is the amount of time in seconds dedicated to solving the problem with the solver. This is less than the overall time required for the entire application because of communication overhead, processing of inputs, and writing the solution files. The overall time can be reduced by setting WEB=0 to avoid writing web-interface files when they are not needed.


.. _specs:

SPECS
------------------------

Type: Integer, Input

Default Value: 1

Description: Specifications from restart file: 1=ON, 0=OFF

Explanation: The default specifications of fixed or calculated are indicated in the restart t0 files that store prior solutions for warm starting the next solution. The SPECS option indicates whether the specifications should be read from the t0 file (ON) or ignored (OFF) when reading the t0 file for initialization.



.. _spc_chart:

SPC_CHART
-------------------

Type: Integer, Input

Default Value: 0

Description: Statistical Process Control chart
0=OFF
1=add +/- 3 set point limits (red lines)
2=add +/- 2 set point limits (yellow lines)
3=add +/- 1 set point limits (green lines)

Explanation: SPC_CHART is a web-interface trend option to create Statistical Process Control (SPC) style charts for Controlled Variables (CVs). When SPC_CHARTS=0, there are no additional limits placed on the trend. As SPC_CHARTS is increased by 1, there are additional ranges added to the CV plots. With a level of 1, new lines at +/- 3 SPHI-SPLO are added to the plot as red upper and lower control limits. With a level of 2, new lines at +/- 2 SPHI-SPLO are added to the plot as yellow upper and lower control limits. With a level of 1, new lines at +/- 1 SPHI-SPLO are added to the plot as green upper and lower control limits. Each level adds an additional two lines.


.. _stream_level:

STREAM_LEVEL
--------------------

Type: Integer, Input

Default Value: 0

Description: Stream level options
0=Mass Balance
1=Mass, Mole, and Energy Balances

Explanation: STREAM_LEVEL controls the amount of detailed contained in flowsheet models through OBJECT declarations. At the basic level (0), only mass balance equations are solved. Variables for each stream are mass flow rate and mass fractions of all species declared in the COMPOUNDS section of the model. The last mass fraction is automatically set to make the summation equal to 1.0. At more the more advanced level (1), mole and energy balances are added. The higher stream level adds temperature, pressure, enthalpy, mole fractions, volumetric flow, density, and concentration.



.. _time_shift:

TIME_SHIFT
------------------------

Type: Integer, Input

Default Value: 1

Description: Time shift for dynamic problems: 1=ON, 0=OFF

Explanation: TIME_SHIFT indicates the number of time steps that a prior solution should be shifted to provide both initial conditions and an initial guess for a dynamic simulation or optimization problem. When TIME_SHIFT = 1 (default), the solution is shifted by one time step. For real-time applications, the cycle time of the solutions should correspond to the first time increment of the application. The first time increment is either set in the CSV file in the time column or else with CTRL_TIME. Failure to synchronize the frequency of solution and the first application step size results in dynamic mismatch. The TIME_SHIFT is set to 0 if the solution should not be shifted over from a prior solution. The TIME_SHIFT can be set to >=2 when multiples of the controller cycle time have elapsed since the prior solution.


.. _web:

WEB
------------------------

Type: Integer, Input

Default Value: 1

Description: Generate HTML pages: 1=ON, 0=OFF

Explanation: WEB is an option that controls how much web-content is produced. A value of 0 indicates that a browser interface should not be created. This option can improve overall application speed because the web interface files are not created. The default value is 1 to create a single instance of the web interface when the program computes a solution. When DIAGLEVEL>=2, the web interface is also created before the program runs to allow a user to view the initial guess values.


.. _web_menu:

WEB_MENU
------------------------

Type: Integer, Input

Default Value: 1

Description: Generate HTML navigation menus: 1=ON, 0=OFF

Explanation: WEB_MENU turns OFF (0) or ON (1) the display of a navigation pane at the top of each auto-generated schematic. WEB_MENU should generally be ON (1) but can be turned off to not give options to the end user to access certain configuration options that are normally reserved for a more advanced user.


.. _web_refresh:

WEB_REFRESH
------------------------

Type: Integer, Input

Default Value: 10

Description: Automatic refresh rate on HTML pages (default 10 minutes)

Explanation: WEB_REFRESH is an internal time of the auto-generated web-interface to automatically reload the page. The default value is 10 minutes although it is not typically necessary to update the web-page. New values are automatically loaded to the web-page through AJAX communication that updates the parts of the page that need to be updated.



.. _web_plot_freq:

WEB_PLOT_FREQ
-----------------

Type: Integer, Input

Default Value: 1

Description: Automatic refresh rate on web interface plots

Explanation: WEB_PLOT_FREQ is an internal time in seconds to refresh the web-interface plots. This option does not automatically reload the page but just the plot within the web-page. The default value is 1 second but this value can be increased to lessen the network load as data is repeatedly sent from the server to the web-interface. Processes with slow dynamics or long cycle times may not need the fast refresh rates. If an error message appears, it may indicate that the plot source files were in the process of being rewritten when the new request for data was initiated. The error message is resolved by reloading the web-page.
