# Changelog
All notable changes to the GEKKO project are documented in this file.

## [Unreleased]
### Added

### Changed

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

[Unreleased]: https://github.com/BYU-PRISM/GEKKO/compare/v0.2.5...HEAD
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
