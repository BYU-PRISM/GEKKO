# Changelog
All notable changes to the GEKKO project are documented in this file.

## [Unreleased]
### Added
- Energy dispatch optimization benchmark problems with Jupyter notebook

### Changed

## [v1.2.1] - Version 1.2.1 Stable Release, Date: 2024-07-03
### Added
- `pyomo` extension and interface to `gekko`
- Example Jupyter notebook for Optimization Under Uncertainty with GPR Model

### Changed
- Replace `match` in `gk_solver_extension.py` with `if` statements - breaks compatibility with Python versions below 3.10
- Fix `get_objective_values(self)` in `gk_solver_extension_*.py` to maintain compatibility with earlier Python versions
- Split `gk_solver_extension.py` into 3 files: 
    - `gk_solver_extension.py`: Holds the code for running the different converter modules, and an abstract base `GKConverter` class that the converters need to implement. This base class reduces repeated code and provides a template if this module were to be extended again in the future. 
    - `gk_solver_extension_amplpy.py`: Holds the `amplpy` converter - changed to fit with the new abstract base converter class.
    - `gk_solver_extension_pyomo.py`: Holds the `pyomo` converter
- Modified the option `m.options.SOLVER_EXTENSION`:
    - `0` / `GEKKO` (default): Solver extension off, solve GEKKO as normal
    - `1` / `AMPL` / `AMPLPY`: Solver extension on, solve through `amplpy` - maintains compatibility with previous version
    - `2` / `PYOMO`: Solver extension on, solve through `pyomo`
- Update documentation 
    - Rewrote a lot of `docs/solver_extension.rst` to include the pyomo converter
    - Updated `docs/global.rst` - `SOLVER_EXTENSION` option in global options
- The two converters continue to not require `amplpy` or `pyomo` to be installed, unless the solver extension module is used.

## [v1.1.3] - Version 1.1.3 Stable Release, Date: 2024-06-17
- Improve model initialization (Timer 47) with improved duplicate variable name searching for larger models
- Update local APM executables to v1.0.3 with `remote=False`
  - Windows apm.exe still 32-bit, includes APOPT, BPOPT, IPOPT solvers
  - Linux apm 64-bit, includes APOPT and BPOPT solvers
  - MacOS apm_mac 64-bit, includes APOPT and BPOPT solvers
  - ARM: apm_arm 32 bit, aarch64 64 bit includes BPOPT solver
- Web service `remote=True` is 64-bit with APOPT, BPOPT, IPOPT solvers

## [v1.1.1] - Version 1.1.1 Stable Release, Date: 2024-04-11
- Fix Gekko arx bug for MIMO systems
- Fix Gekko GPR bug for multiple features

## [v1.1.0] - Version 1.1.0 Stable Release, Date: 2024-03-26
### Added
- Added `support` library for RAG-based Chatbot Support in Gekko
- Added examples that use the `support` module to create an agent to answer questions

### Changed
- Modified documentation to include information about the `support` module

## [v1.0.7] - Version 1.0.7 Stable Release, Date: 2024-03-5
### Added
- Added [LP, QP, NLP, MILP, and MINLP examples](https://github.com/BYU-PRISM/GEKKO/blob/master/examples/Optimization_Introduction.ipynb).
- Added `apm_aarch64` binary for local solve on ARM64 / AARCH64 devices, only BPOPT solver for ARM 32 and 64-bit
- Added `pyampl` interface to use ampl / pyomo solvers

### Changed
- Changes to `gk_write_files.py` with `.join()` instead of `+` to create data file and solver options files `ipopt.opt` and `apopt.opt`.
- Print message when using `remote=True` for greater transparency
- `m.options.SOLVER` can now be specified with the solver name such as `APOPT`, `BPOPT`, `IPOPT`, etc
- Updated documentation for gekko `m.erf()` and `m.erfc()` functions.
- Added `apm_aarch64` executable to `setup.py` to be included in `bin` folder
- Update `setup.py` for Python 3.12 and 3.13 compatibility

## [v1.0.6] - Version 1.0.6 Stable Release, Date: 2023-01-24
### Changed
- Removed `np.warnings.filterwarnings()` function call in `gekko.py` for the `sysid()` method. This was removed in `numpy-1.24.1`.
- Fixed bug on `m.options.max_time` to use subprocess Timeout error exception

## [v1.0.5] - Version 1.0.5 Stable Release, Date: 2022-07-22
### Added
- New Gekko import functions for GPFlow models from `gpflow`
- New Gekko import functions for Gaussian Processes models from `scikit-learn`
- New Gekko import functions for SVR models from `scikit-learn`
- New Gekko import functions for Neural Network Regressor models from `scikit-learn`

### Changed
- Documentation updated for new `ML.py` capabilities with example problems.

## [v1.0.4] - Version 1.0.4 Stable Release, Date: 2022-05-12
### Added
- Example problem `test_count_bins.py` on counting discrete options in a list.
- Example problem `test_arc_hyperbolics.py` for `asinh()`, `acosh()`, and `atanh()`.

### Changed
- Bug fix for `asinh()`, `acosh()`, and `atanh()`.
- Placeholder file (copy of `apm` for Linux) for `apm_arm` until new version is available.
- Prepare `meta.yaml` and `LICENSE` for `conda-forge` release with package `grayskull`.

## [v1.0.2] - Version 1.0.2 Stable Release, Date: 2021-11-16
### Added
- Added `m.Minimize()` and `m.Maximize()` documentation for improved readability of objective functions

### Changed
- Improve documentation of variable declarations
- Fixed bug with CSV file write in gk_write_files.py when only one column (time)

## [v1.0.1] - Version 1.0.1 Stable Release, Date: 2021-08-07
### Added
- New sigmoid function `m.sigmoid()` in Gekko
- New sigmoid function `sigmd(x)` in APMonitor with v1.0.1 release

### Changed
- Updated APM local and remote server to APM v1.0.1 for Windows, Linux, MacOS
- Big fix to `gk_write_file.py` for long variable or parameter names that were truncated at 25 characters. There is no limit to variable names now.
- Change documentation default for WSP, WSPLO, WSPHI to 20.0 (from 1.0) to be consistent with APM

## [v1.0.0] - Version 1.0.0 Stable Release, Date: 2021-05-16
### Added
- Updated local solve options for MacOS and Linux that do not include dependencies
- APMonitor v1.0.0 for remote and local solves

### Changed
- Fixed bug with `axb` function executable. The `b` dense to sparse function used a dimension for `A` rows instead of `A` columns.
- Updated with version 1.0.0 of `apm.exe` executable for Windows
- Fixed bug with `sum` function to detect when symbolic string length is over the limit of 15000 for `apm`. Use `sum` objective instead.
- Bug fixes and GitHub issue resolutions for release 1.0.0 of `apm` executable and `gekko`.
- Removed `flask` dependency on install. Only needed when `GUI=True`.
- Fixed bug with `remote=True` with `axb` function not sending the summary file.

## [v0.2.8] - Version 0.2.8 Stable Release, Date: 2020-08-11
### Added
- Added documentation for `fix_initial`, `free_initial`, `fix_final`, and `free_final`.

### Changed
- Updated documentation for `Connection`
- Fixed bug with `lb` and `ub` not used by FVs and MVs during declaration 

## [v0.2.7] - Version 0.2.7 Stable Release, Date: 2020-08-05
### Added
- New functions `fix_initial`, `free_initial`, `fix_final` to help with specifying degrees of freedom for common changes to the default fixed / free specifications.
- Additional documentation for modes of operation
- Matrix (2D) optimization AX=B example problem `test_matrix.py`
- Example 2nd order differential equation
- Example 3rd order differential equation with parameter estimation
- A few other examples for testing

### Changed
- Lower and Upper bounds for `Param`
- Fixed axb function with dense Ax=b (from incorrect A^T x=b)
- Upgrade `Param` so that new `value` updates the values in the CSV file.

## [v0.2.6] - Version 0.2.6 Stable Release, Date: 2019-11-12
### Added
- New integral function `m.integral` and documentation

### Changed
- Local MacOS solve with linked static gcc-gfortran lib
- Changed `shell=False` for IPython notebooks in Windows with local subprocess call

## [v0.2.5] - Version 0.2.5 Stable Release, Date: 2019-11-11
### Added
- Optional E matrix for state_space function: E dx/dt = Ax+Bu
- Re-implemented changes to if2 and sos1 that were removed from v0.2.4

### Changed
- Equation accepts single equation, list, or tuple
- Improved error message when remote server unreachable
- Fix state_space function for input D when not None

## [v0.2.4] - Version 0.2.4 Stable Release, Date: 2019-11-7
### Added
- New Special Ordered Set (SOS1) model
- New example problem that uses the SOS1 model
- New MATLAB interface to Gekko
- New bspline options (smoothing factor, order in x and y directions)
- New if2 function that uses an MPCC switch (m.sign2)
- New Maximize and Minimize functions (Obj minimizes)

### Changed
- Bug fix in bspline that prevented x and y of different sizes
- Removed Windows command window pop-up with local mode

## [v0.2.3] - Version 0.2.3 Stable Release, Date: 2019-08-15
### Stable release

### Added
- Improved m.fix function to allow specification changes beyond just dynamic mode
- Added m.free function to change a fixed value into a calculated value for both steady state and dynamic modes
- Additional example of the Chemical library use for a simple blending problem

### Changed
- Improved variable initialization to allow variable names, GK_Value, and number types
- m.Connections to support fix / free (calculated) specifications
- Updated gekko to support new functions in APM 0.9.1
- Default phase in the Chemical library changed from vapor to liquid
- Use app.communicate instead of readline to avoid filling up child buffer and creating lock for remote=False solve

## [v0.2.2] - Version 0.2.2 Stable Release, Date: 2019-07-17
### Stable release

### Added
- Additional example problems, test suite
- New Chemical module - see test_thermo.py and test_chemical.py in examples
- m.remove() function to delete application directory
- m.delay() as a times series delay model
- Added MATLAB examples for calling Gekko functions
- Documentation pages for Chemical module and Machine Learning module (rst files)

### Changed
- Improved documentation for model building and logical conditions
- Modified Brain (Machine Learning) capabilities - see test_brain.py in examples

## [v0.2.1] - Version 0.2.1 Stable Release, Date: 2019-05-10
### Stable release

### Added
- APM MacOS local executable v0.8.9

## [v0.2.0] - Version 0.2.0 Stable Release, Date: 2019-05-04
### Stable release

### Added
- Additional example problems, test suite

### Changed
- APM Windows local executable v0.8.9 
- APM ARM local executable v0.8.9 
- APM Linux local executable v0.8.9 

## [0.2rc6] - Version 0.2 Release Candidate 6, Date: 2019-04-15
### Added
- New axb object for Ax=b, Ax<b, and Ax>b linear equations
- New qobj object for quadratic objectives 0.5 x^T A x + b^T x
- New if3 conditional statement that translates conditional statemment to Mixed Integer problem

### Changed
- New APM 0.8.9 local executable with axb and qobj improvements

## [0.2rc5] - Version 0.2 Release Candidate 5, Date: 2019-04-03
### Added
- New thermo objects
- New vsum for vertical (data direction) summation for IMODE=2, IMODE=4+
- New sum for more efficient summation in GEKKO with APMonitor object
- New APM 0.8.8 local executable for IMODE 7 bug fix
- New PWL (Piecewise linear) object

### Changed
- Improved sysid (System Identification) for fast identification when not constrained
- Write values from JSON for Parameters on solver exit. It was previously ignoring Param values. This is needed for Thermo objects that are constants.
- Bug fix for y=m.Var(x.value) in gk_operators.py

### Removed
- None

## [0.1] - Version 0.1 Stable Release, Date: 2019-03-01
### Initial stable release

## [0.1rc7] - Version 0.1 Release Candidate 7, Date: 2019-02-01
### Final 0.1 release candidate
### Added
- System identification and ARX model support as new objects

## [0.1rc4] - Version 0.1 Release Candidate 4, Date: 2019-02-12
### 0.1 release candidate 4
### Added
- Additional APMonitor object support
- Support for ARM processors

## [0.1b2] - Version 0.1 Beta 2, Date: 2018-11-13
### 0.1 beta release 2
### Added
- Additional GUI support

### Changed
- Remote option with GEKKO initialization, not solve command

## [0.1a2] - Version 0.1 Alpha 2, Date: 2018-03-28
### 0.1 alpha release 2
### Added
- Initial GUI support

## 0.0.1a1 - Version 0.0.1 Alpha 1, Date: 2018-01-05
### Initial GEKKO public release, alpha version

[Unreleased]: https://github.com/BYU-PRISM/GEKKO/compare/v1.2.1...HEAD
[v1.2.1]: https://github.com/BYU-PRISM/GEKKO/compare/v1.1.3...v1.2.1
[v1.1.3]: https://github.com/BYU-PRISM/GEKKO/compare/v1.1.1...v1.1.3
[v1.1.1]: https://github.com/BYU-PRISM/GEKKO/compare/v1.1.0...v1.1.1
[v1.1.0]: https://github.com/BYU-PRISM/GEKKO/compare/v1.0.7...v1.1.0
[v1.0.7]: https://github.com/BYU-PRISM/GEKKO/compare/v1.0.6...v1.0.7
[v1.0.6]: https://github.com/BYU-PRISM/GEKKO/compare/v1.0.5...v1.0.6
[v1.0.5]: https://github.com/BYU-PRISM/GEKKO/compare/v1.0.4...v1.0.5
[v1.0.4]: https://github.com/BYU-PRISM/GEKKO/compare/v1.0.2...v1.0.4
[v1.0.2]: https://github.com/BYU-PRISM/GEKKO/compare/v1.0.1...v1.0.2
[v1.0.1]: https://github.com/BYU-PRISM/GEKKO/compare/v1.0.0...v1.0.1
[v1.0.0]: https://github.com/BYU-PRISM/GEKKO/compare/v0.2.8...v1.0.0
[v0.2.8]: https://github.com/BYU-PRISM/GEKKO/compare/v0.2.7...v0.2.8
[v0.2.7]: https://github.com/BYU-PRISM/GEKKO/compare/v0.2.6...v0.2.7
[v0.2.6]: https://github.com/BYU-PRISM/GEKKO/compare/v0.2.5...v0.2.6
[v0.2.5]: https://github.com/BYU-PRISM/GEKKO/compare/v0.2.4...v0.2.5
[v0.2.4]: https://github.com/BYU-PRISM/GEKKO/compare/v0.2.2...v0.2.4
[v0.2.3]: https://github.com/BYU-PRISM/GEKKO/compare/v0.2.2...v0.2.3
[v0.2.2]: https://github.com/BYU-PRISM/GEKKO/compare/v0.2.1...v0.2.2
[v0.2.1]: https://github.com/BYU-PRISM/GEKKO/compare/v0.2.0...v0.2.1
[v0.2.0]: https://github.com/BYU-PRISM/GEKKO/compare/0.2rc6...v0.2.0
[0.2rc6]: https://github.com/BYU-PRISM/GEKKO/compare/0.2rc5...0.2rc6
[0.2rc5]: https://github.com/BYU-PRISM/GEKKO/compare/0.1...0.2rc5
[0.1]: https://github.com/BYU-PRISM/GEKKO/compare/0.1rc7...0.1
[0.1rc7]: https://github.com/BYU-PRISM/GEKKO/compare/0.1rc4...0.1rc7
[0.1rc4]: https://github.com/BYU-PRISM/GEKKO/compare/0.1b2...0.1rc4
[0.1b2]: https://github.com/BYU-PRISM/GEKKO/compare/0.1b1...0.1b2
[0.1b1]: https://github.com/BYU-PRISM/GEKKO/compare/v0.1a2...0.1b1
[0.1a2]: https://github.com/BYU-PRISM/GEKKO/compare/0.0.4...v0.1a2
