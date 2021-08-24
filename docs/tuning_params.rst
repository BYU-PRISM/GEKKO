

.. _tuning_params:



Tuning Parameters
====================================

.. toctree::
	:maxdepth: 2


Local Options: DBS Parameters for Variables

The following is a list of parameters that may be found in the DBS file for variables listed in the INFO file. It is a complete list of the configuration parameters for FV, MV, SV, CV type parameters and variables. Each section includes an indication of the variable type (Integer or Real), the default value, data flow, and description.


.. _aws:

AWS
----
Local Options |  Global Options

Type: Floating Point, Output

Default Value: 0

Description: Anti-Windup Status for a Manipulated Variable
0: Not at a limit
1: An upper or lower bound is reached

Explanation: Anti-Windup Status (`AWS`) is terminology borrowed from classical controls such as Proportional Integral Derivative (PID) controllers. Anti-Windup refers to the integral action that is paused when the controller reaches a saturation limit. An example of a saturation limit is a valve that is limited to 0-100% open. If the controller requests -10%, the valve is still limited to 0%. The AWS indication is useful to show when a controller is being driven by an optimization objective versus constraints that limit movement. A Key Performance Indicator (KPI) of many controllers is the fraction of time that a MV is not at an upper or lower bound limit.


.. _bias:

BIAS
-------

Type: Floating Point, Input/Output

Default Value: 0.0

Description: Additive correction factor to align measurement and model values for Controlled Variables (CVs)
`BIAS` is additive factor that incorporates the difference between the current measured value and the initial condition of the controller. :ref:`fstatus` determines how much of the raw measurement is used to update the value of :ref:`meas`. A feedback status of 0 indicates that the measurement should not be used and the `BIAS` value is kept at the initial value of 0. A feedback status of 1 uses all of the measurement in updating `MEAS`. A feedback status in between 0 and 1 updates `MEAS` with a fractional contribution from :ref:`lstval` and the new measurement. The value of `BIAS` is updated from `MEAS` and the unbiased model prediction (`Model_u`).

.. math::

	BIAS = MEAS - Model_u

The `BIAS` is added to each point in the horizon and the controller objective function drives the biased model (`Model_b`) to the requested set point range.

.. math::

	Model_b = Model_u + BIAS

The value of BIAS can also be set to an external value by setting the option `BIAS` option directly and setting `FSTATUS` to 0 (OFF).


.. _cost:

COST
-----------

Type: Real, Input

Default Value: 0.0

Description: Cost weight: (+)=minimize, (-)=maximize

Explanation: Multiplies the parameter by the `COST` value specified. This is used to scale the terms in the objective function. It is important that each term in the objective function is scaled to be of the same order of magnitude to ensure that the optimizer considers each of them (unless different weighting is specifically desired).


.. _critical:

CRITICAL
-----------

Type: Integer, Input

Default Value: 0

Description: Critical: 0=OFF, 1=ON

Explanation: Turns the application off ( :ref:`reqctrlmode` =1) if the instrument that provides the measurement has a :ref:`pstatus` =0 (bad measurement). A critical measurement has this flag on to give control back to the operator if the measurement fails to deliver a good value.


.. _dcost:

DCOST
-----------

Type: Real, Input

Default Value: 0.00001

Description: Delta cost penalty for MV movement

Explanation: Adds a term to the objective function that gives a minor penalty for changing the MV. The weight of the penalty is adjusted with the input value. This is useful for systems where excessive movement to the MV causes damage to equipment or undesirable results. By assigning a weight that is small in comparison to the objective function value, optimal performance is achieved while changing the MV only
when necessary.

.. math::

	objective \mathrel{+}= \sum_{i=1} \left\Vert x_{i-1} - x_i \right\Vert _p

Where `p` is equal to :ref:`ev_type` (for `IMODE=5or8`) or :ref:`cv_type` (for `IMODE=6or9`).


.. _dmax:

DMAX
-----------

Type: Real, Input

Default Value: 1.0e20

Description: Delta MV maximum step per horizon interval

Explanation: Applies a hard constraint that prevents the MV from being changed by more than the specified value in one time step. This can be used to prevent large jumps in the MV value in the case where that is either undesirable or infeasible. The time step is defined as the length of the first time step in the csv file.


.. _dmaxhi:

DMAXHI
-----------

Type: Real, Input

Default Value: 1.0e20

Description: Delta MV positive maximum step per horizon interval

Explanation: Like :ref:`dmax`, but only with positive changes. Applies a hard constraint that prevents the MV from being changed by more than the specified value in one time step, but this constraint only applies to increases in the MV value. This can be used to prevent large jumps in the MV value in the case where that is either undesirable or infeasible.


.. _dmaxlo:

DMAXLO
-----------

Type: Real, Input

Default Value: -1.0e20

Description: Delta MV negative maximum step per horizon interval

Explanation: Like :ref:`dmax`, but only with negative changes. Applies a hard constraint that prevents the MV from being changed by more than the specified value in one time step, but this constraint only applies to decreases in the MV value. This can be used to prevent large jumps in the MV value in the case where that is either undesirable or infeasible.


.. _dpred:

DPRED
-----------

Type: Real, Output

Default Value: 0.0

Description: Delta prediction changes for each step'

Explanation: Changes in the manipulated variables (MVs) are listed for the first 10 steps of the horizon including `DPRED[1]`, `DPRED[2]`, etc. Values of zero indicate that there are no changes. With `REQCTRLMODE=1` (COLD), all :ref:`dpred` values are zero. With `REQCTRLMODE=2` (WARM), only `DPRED[1]` is required to be zero but the other segments may be non-zero. With `REQCTRLMODE=3` (CONTROL), the first `DPRED` value is changing.


.. _fstatus:

FSTATUS
-----------

Type: Real, Input

Default Value: 1.0

Description: Feedback status: 1=ON, 0=OFF

Explanation: Determines how much of the measurement ( :ref:`meas`) to use in updating the values in the model. A feedback status of 0 indicates that the measurement should not be used either in estimation or in updating a parameter in the model. A feedback status of 1 uses all of the measurement. A feedback status in between updates the model OR parameter value (x) according to the formula:

.. math::

	x = LSTVAL * (1-FSTATUS) + MEAS * FSTATUS


.. _fdelay:

FDELAY
-----------

Type: Integer, Input

Default Value: 0

Description: Feedback delay: 0=No Delay, >=1 horizon steps for delay

Explanation: The feedback delay places the measurement at the appropriate point in the horizon for dynamic estimation. Typical examples are laboratory measurement or gas chromatographs that report measurements that were taken in the past, usually with a 10 min - 2 hour delay. When the new value is reported, it should be placed at the appropriate point in the data time horizon. `FDELAY` is the number of horizon steps in the past where the measurement was actually taken.


.. _lower:

LOWER
-----------

Type: Real, Input

Default Value: -1.0e20

Description: Lower bound

Explanation: `LOWER` is the lower limit of a variable. If the variable guess value is below the lower limit, it is adjusted to the lower limit. The lower limit is also checked with the upper limit to ensure that it is less than or equal to the upper limit. If the lower limit is equal to the upper limit, the variable is fixed at that value.


.. _lstval:

LSTVAL
-----------

Type: Real, Output

Default Value: 1.0

Description: Last value from previous solution

Explanation: The last value (`LSTVAL`) is the value from the prior solution of the optimization problem or simulation.


.. _meas:

MEAS
-----------

Type: Real, Input

Default Value: 1.0

Description: Measured value

Explanation: The measurement of a variable or parameter. The value of `MEAS` is initialized to the initial model value. The `MEAS` value is used in the application if :ref:`fstatus` is greater than zero, but not when `FSTATUS=0`.

`MEAS` must be a scalar and only one measurement is loaded in each `solve()` command. If multiple measurements are needed, they can be loaded through the :ref:`value` attribute in their respective locations.


.. _meas_gap:

MEAS_GAP
-----------

Type: Real, Input

Default Value: 1.0

Description: Deadband for noise rejection of measurements in MHE

Explanation: Used in estimation problems with :ref:`ev_type` =1 (l1-norm objective). The measurement gap (`MEAS_GAP`) defines a dead-band region around the measurement. If the model prediction is within that dead-band, there is no objective function penalty. Outside of that region, there is a linear penalty specified with the :ref:`wmeas` parameter. The :ref:`wmodel` parameter is the weighting given to deviation from the prior model prediction but does not have a deadband around the prior model prediction. The gap is only around the measured values.


.. _model:

MODEL
-----------

Type: Real, Output

Default Value: 1.0

Description: Model predicted value

Explanation: The MODEL value is a property of SV (State Variable) and CV (Controlled Variable) types. It is the predicted value of the current time. The current time is the first time step for a simulator or controller and the last value in the horizon for estimation.


.. _mv_step_hor:

MV_STEP_HOR
-----------

Type: Integer, Input

Default Value: 0 (for global :ref:`mv_step_hor_global` ) or 1 (for MV(#).MV_STEP_HOR)

Description: Step length for manipulated variables: 0 uses global :ref:`mv_step_hor_global` as default

Explanation: The manipulated variable step horizon (MV_STEP_HOR) is by default to allow the MV to be adjusted every time set of the collocation. There are cases where the MV should not move every time step but should be constrained to move only a certain multiple of the collocation time step. With MV_STEP_HOR = 2, the manipulated variable is allowed to move on the first step and every other step thereafter. MV_STEP_HOR = 5, the manipulated variable is allowed to move on the first step and every 5th step thereafter. There is also a global parameter :ref:`mv_step_hor_global` that is used as a global configuration for all MVs when the individual MV option is set to 0.


.. _newval:

NEWVAL
-----------

Type: Real, Output

Default Value: 1.0

Description: New value implemented by the estimator or controller (NEWVAL = MEAS when not in control)

Explanation: The new value of the parameter estimate (FV) or manipulated variable (MV). This value is taken from the first step of the controller or the last step of the estimator. The NEWVAL is set equal to the measured value if the FV or MV status is off and the FSTATUS (feedback status) is ON (1).


.. _nxtval:

NXTVAL
-----------

Type: Real, Output

Default Value: 1.0

Description: Next value that the estimator or controller would implement if CTRLMODE=3.

Explanation: The next value (NXTVAL) to be implemented by the controller. This is especially useful for a controller in WARM mode (CTRLMODE=2) where no values are changed on the first step (still in manual mode) but the control actions are computed beyond the first step. This is a useful mode to inspect the controller performance before it is turned on.


.. _objpct:

OBJPCT
-----------

Type: Real, Output

Default Value: 0.0

Description: Percent of objective function contribution considering all SV and CV variables

Explanation: The objective function percent is useful to see which controlled variables (CVs) are contributing the most to the controller overall objective function. If one of the CVs has a high OBJPCT, it may be dominating the controller action and the tuning factors WSP (CV_TYPE=2) or WSPHI/WSPLO (CV_TYPE=1) should be adjusted accordingly.


.. _ostatus:

OSTATUS
-----------

Type: Integer, Output

Default Value: 0

Description: Bit encoding for status messages

Explanation: Status messages encoded in binary form for transfer and decoding. This is deprecated and will be removed in a future release.


.. _ostatuschg:

OSTATUSCHG
-----------

Type: Integer, Output

Default Value: 0

Description: Change in bit encoding for status messages

Explanation: Change of status messages, encoded in binary form for transfer and decoding. This is deprecated and will be removed in a future release.


.. _pred:

PRED
-----------

Type: Real, Output

Default Value: 1.0

Description: Prediction horizon

Explanation: The first predictions of a state (SV) or controlled (CV) variable. The number of PRED values is limited to the first 10 but can be less with a shorter horizon. PRED[0] is the initial condition while PRED[1] is the first predicted step. The other values PRED[2], PRED[3], … , PRED[10] are the predicted model values up to a horizon of 10 time points.


.. _pstatus:

PSTATUS
-----------

Type: Integer, Input

Default Value: 1

Description: Instrument status: 1=GOOD, 0=BAD

Explanation: An indication of the instrument health. If PSTATUS is 0 then the instrument is determined to be bad and the measurement should not be used. By default, all instruments are assumed to be reporting good values.


.. _reqonctrl:

REQONCTRL
-----------

Type: Integer, Input

Default Value: 0

Description: Required for control mode to be ON (3): 1=ON, 0=OFF

Explanation: Certain Manipulated Variables (MVs) and Controlled Variables (CVs) are critical to the operation of the entire application. When any of the MVs or CVs with REQONCTRL are turned off, the entire application is turned off (CTRLMODE=1). The requested control mode (REQCTRLMODE) is the requested controller mode but this option downgrades the controller to a simulation mode if a critical MV or CV is OFF.


.. _sp:

SP
-----------

Type: Real, Input

Default Value: 0.0

Description: Set point for squared error model

Explanation: The target value for a controller that is using a squared error objective (single trajectory track). The setpoint (SP) is the final target value.


.. _sphi:

SPHI
-----------

Type: Real, Input

Default Value: 1.0e20

Description: Set point high for linear error model

Explanation: The upper range of the target region (dead-band) for a controller that is using an l1-norm error objective. The setpoint high (SPHI) is the upper final target value.


.. _splo:

SPLO
-----------

Type: Real, Input

Default Value: -1.0e20

Description: Set point low for linear error model

Explanation: The lower range of the target region (dead-band) for a controller that is using an l1-norm error objective. The setpoint low (SPLO) is the lower final target value.


.. _status:

STATUS
-----------

Type: Integer, Input

Default Value: 0

Description: Status: 1=ON, 0=OFF

Explanation: The STATUS specifies when a parameter (FV or MV) that is normally fixed (OFF) can become calculated (ON). Similarly, STATUS set to ON, allows a controlled variable (CV) to be included as a model predictive controller set point target or steady state optimizer target. The STATUS value indicates whether that variable should be included in the optimization (ON) or is merely a fixed input or prediction (OFF). It is acceptable to have only a subset of parameters (FVs or MVs) or variables (CVs) with STATUS set to ON. The STATUS can be turned ON or OFF for each cycle of the controller as needed without disrupting the overall application. An estimator uses STATUS for FVs and MVs but uses FSTATUS (not STATUS) to determine when measurements are used.


.. _tau:

TAU
-----------

Type: Real, Input

Default Value: 60.0

Description: Time constant for controlled variable response

Explanation: The time constant is a tuning parameter for the speed of response of a reference trajectory. When the set point is stepped to a new value, the time constant (TAU) adjusts the speed of response with SP_tr = (1-exp(-t/TAU)) (SPnew - SPold) + SPold where SPold is the prior set point, SPnew is the new set point, t is the time, TAU is the time constant, and SP_tr is the resultant trajectory.


.. _tier:

TIER
-------
Type: Integer, Input

Default Value: 1

Description: Tiered order of Manipulated Variables (MVs) and Controlled Variables (CVs)

Explanation: TIER is an ascending order of precedence for optimization. Tuning an application with multiple objectives can be challenging to coordinate the weights of competing objectives although there is a clear rank priority order. TIER gives the option to split the degrees of freedom into multiple sub-optimization problems. The highest priority values are optimized first while the subsequent priority values are optimized as a next step. Valid TIER values for MVs and CVs are between 1 and 100. There are up to 100 optimization levels and individual MVs / CVs must be at the same TIER value to be included in the sub-optimization problem. The STATUS must also be ON (1) for an MV to be a degree of freedom. The STATUS must also be ON (1) for an CV to be included in the objective function. If there is a sub-optimization problem that has no MV degrees of freedom, a warning message is displayed.


.. _tr_open:

TR_OPEN
-----------

Type: Real, Input

Default Value: 1.0

Description: Initial trajectory opening ratio (0=ref traj, 1=tunnel, 2=funnel)

Explanation: TR_OPEN controls the trajectory opening for :ref:`cv_type` = 1. It is the ratio of opening gap to the final gap of :ref:`sphi` - :ref:`splo`. A value of `TR_OPEN = 2` means that the initial trajectory is twice the width of the final gap of `SPHI - SPLO`. With `TR_OPEN = 0`, the initial trajectory starts at the same point and widens with a first order response as specified by :ref:`tau` to final destinations of SPHI and SPLO. Each CV can have a different TR_OPEN.


.. _tr_init:

TR_INIT
-----------

Type: Integer, Input

Default Value: 0

Description: Setpoint trajectory initialization (0=dead-band, 1=re-center with coldstart/out-of-service, 2=re-center always)

Explanation: `TR_INIT` is an option to specify how the initial conditions of the controlled variable's (CV) setpoint reference trajectory should change with each cycle. The trajectory is set by :ref:`tau`. An option of 0 specifies that the initial conditions should start at SPHI and SPLO, creating an unchanging target over the horizon. An option of 1 makes the initial conditions equal to the current process variable value only on coldstart ( :ref:`coldstart`>=1) or with :ref:`ctrlmode` <=2 when the controller is out of service. Otherwise, the reference trajectory is updated from the first step of the prior solution. When `TR_INIT=2`, the reference trajectory realigns to the variable's initial condition with each cycle. Each CV can have a different `TR_INIT`. The trajectory is also influenced by :ref:`tr_open`.


.. _upper:

UPPER
-----------

Type: Real, Input

Default Value: 1.0e20

Description: Upper bound

Explanation: `UPPER` is the the upper limit of a variable. If the variable guess value is above the upper limit, it is adjusted to the upper limit before it is given to the solver. The upper limit is also checked with the lower limit ( :ref:`lower`) to ensure that it is greater than or equal to the lower limit. If the upper limit is equal to the lower limit, the variable is fixed at that value.


.. _value:

VALUE
------

Type: Real, Input/Output

Default Value: 1

Description: Value of the variable

Explanation: `VALUE` is a floating point number of a variable.


.. _vdvl:

VDVL
-----------

Type: Real, Input

Default Value: 1.0e20

Description: Delta validity limit

Explanation: `VDVL` is the maximum change of a measured value before it is considered an unrealistic change. The change in measured values is recorded at every cycle of the application and compared to the `VDVL` limit. Validity limits are placed to catch instrument errors that may otherwise create bad inputs to the application. If a delta validity limit is exceeded, the action is to either freeze the measured value at the last good value ( :ref:`vlaction` =0) or change the measured value by a maximum of `VDVL` in the direction of the bad measurement ( :ref:`vlaction` =1). Another way to minimize the impact of unrealistic changes in measurements is to set :ref:`fstatus` between 0 and 1 with values closer to 0 becoming insensitive to measurement changes.


.. _vlaction:

VLACTION
-----------

Type: Integer, Input

Default Value: 0

Description: Validity Limit Action

Explanation: `VLACTION` is the validity limit action when :ref:`vdvl` is exceeded. The change in measured values is recorded at every cycle of the application and compared to the `VDVL` limit. Validity limits are placed to catch instrument errors that may otherwise create bad inputs to the application. If a delta validity limit is exceeded, the action is to either freeze the measured value at the last good value (`VLACTION=0`) or change the measured value by a maximum of `VDVL` in the direction of the bad measurement (`VLACTION=1`).


.. _vlhi:

VLHI
-----------

Type: Real, Input

Default Value: 1.0e20

Description: Upper validity limit

Explanation: `VLHI` is the upper validity limit for a measured value. Validity limits are one way to protect an application against bad measurements. This gross error detection relies on a combination of change values and absolute limits to determine when a measurement should be rejected. If `VLHI` is exceeded, the measured value is placed at `VLHI` or the maximum move allowed by :ref:`vdvl` when :ref:`vlaction` =1. If :ref:`vlaction` =0, there is no change in the measured value when a limit ( :ref:`vdvl`, :ref:`vlhi`, :ref:`vllo`) is exceeded.


.. _vllo:

VLLO
-----------

Type: Real, Input

Default Value: -1.0e20

Description: Lower validity limit

Explanation: VLLO is the lower validity limit for a measured value. Validity limits are one way to protect an application against bad measurements. This gross error detection relies on a combination of change values and absolute limits to determine when a measurement should be rejected. If the VLLO limit is crossed, the measured value is placed at VLLO or the maximum move allowed by VDVL when VLACTION=1. If VLACTION=0, there is no change in the measured value when a limit (VDVL, VLHI, VLLO) is exceeded.


.. _wmeas:

WMEAS
-----------

Type: Real, Input

Default Value: 20.0

Description: Objective function weight on measured value

Explanation: A weighting factor to penalize deviation of current model predictions from measured values. This is used in estimation applications ( :ref:`imode` =2, 5, or 8) where the penalty. The infinite estimation horizon approximation is especially useful for systems that have weakly observable or unobservable states. A higher `WMODEL` can also help to reduce the aggressiveness of the estimator in aligning with the measurements by balancing with a penalty against shifting too far from the prior predictions. The :ref:`wmodel` value should never be equal to or larger than the `WMEAS` value for :ref:`ev_type` =1 (l1-norm). A `WMODEL` value higher than `WMEAS` will ignore measured values in favor of matching prior model predictions.


.. _wmodel:

WMODEL
-----------

Type: Real, Input

Default Value: 2.0d0

Description: Objective function weight on model value

Explanation: A weighting factor to penalize deviation of current model predictions from prior model predictions. This is used in estimation applications (IMODE=2, 5, or 8) where the penalty from a prior model prediction is a “forgetting factor” that approximates an infinite estimation horizon or favors prior predictions. The infinite estimation horizon approximation is especially useful for systems that have weakly observable or unobservable states. A higher WMODEL can also help to reduce the aggressiveness of the estimator in aligning with the measurements by balancing with a penalty against shifting too far from the prior predictions. The WMODEL value should never be equal to or larger than the WMEAS value for EV_TYPE=1 (l1-norm). A WMODEL value higher than WMEAS will ignore measured values in favor of matching prior model predictions.


.. _wsp:

WSP
-----------

Type: Real, Input

Default Value: 20.0

Description: Objective function weight on set point for squared error model

Explanation: A weighting factor to penalize a squared error from the setpoint trajectory with final target SP. The weighting factor is positive to drive the response to the SP trajectory and negative to drive it away from the SP. A negative WSP is highly unlikely and the value should generally be positive.


.. _wsphi:

WSPHI
-----------

Type: Real, Input

Default Value: 20.0

Description: Objective function weight on upper set point for linear error model

Explanation: A weighting factor to penalize deviation above the upper setpoint trajectory with final target SPHI. If there is no penalty to cross the upper setpoint, WSPHI can be set to zero.


.. _wsplo:

WSPLO
-----------

Type: Real, Input

Default Value: 20.0

Description: Objective function weight on lower set point for linear error model

Explanation: A weighting factor to penalize deviation below the lower setpoint trajectory with final target SPLO. If there is no penalty to cross the lower setpoint trajectory, WSPLO can be set to zero.
