# Changelog
All notable changes to the GEKKO project will be documented in this file.

## [Unreleased]

## [0.2.0] - Version 0.2.0 Stable Release, Date: 2019-05-04
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

[Unreleased]: https://github.com/BYU-PRISM/GEKKO/compare/0.2rc6...HEAD
[0.2.0]: https://github.com/BYU-PRISM/GEKKO/compare/0.2rc6...0.2.0
[0.2rc6]: https://github.com/BYU-PRISM/GEKKO/compare/0.2rc5...0.2rc6
[0.2rc5]: https://github.com/BYU-PRISM/GEKKO/compare/0.1...0.2rc5
[0.1]: https://github.com/BYU-PRISM/GEKKO/compare/0.1rc7...0.1
[0.1rc7]: https://github.com/BYU-PRISM/GEKKO/compare/0.1rc4...0.1rc7
[0.1rc4]: https://github.com/BYU-PRISM/GEKKO/compare/0.1b2...0.1rc4
[0.1b2]: https://github.com/BYU-PRISM/GEKKO/compare/0.1b1...0.1b2
[0.1b1]: https://github.com/BYU-PRISM/GEKKO/compare/v0.1a2...0.1b1
[0.1a2]: https://github.com/BYU-PRISM/GEKKO/compare/0.0.4...v0.1a2
