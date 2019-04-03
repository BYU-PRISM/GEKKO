# Changelog
All notable changes to the GEKKO project will be documented in this file.

## [Unreleased]

## [0.2rc5] - 2019-04-03
### Added
- New thermo objects
- New vsum for vertical (data direction) summation for IMODE=2, IMODE=4+
- New sum for more efficient summation in GEKKO with APMonitor object
- New APM 0.8.8 local executable for IMODE 7 bug fix
- New PWL (Piecewise linear

### Changed
- Improved sysid (System Identification) for fast identification when not constrained
- Write values from JSON for Parameters on solver exit. It was previously ignoring Param values. This is needed for Thermo objects that are constants.

### Removed
- None

## [0.1] - 2019-03-01
### Initial stable release

## [0.1rc7] - 2019-02-01
### Final 0.1 release candidate
### Added
- System identification and ARX model support as new objects

## [0.1rc4] - 2019-02-12
### 0.1 release candidate 4
### Added
- Additional APMonitor object support
- Support for ARM processors

## [0.1b2] - 2018-11-13
### 0.1 beta release 2
### Added
- Additional GUI support

### Changed
- Remote option with GEKKO initialization, not solve command

## [0.1a2] - 2018-03-28
### 0.1 alpha release 2
### Added
- Initial GUI support

## 0.0.1a1 - 2018-01-05
### Initial GEKKO public release, alpha version

[Unreleased]: https://github.com/BYU-PRISM/GEKKO/compare/0.1...HEAD
[0.1]: https://github.com/BYU-PRISM/GEKKO/compare/0.1rc7...0.1
[0.1rc7]: https://github.com/BYU-PRISM/GEKKO/compare/0.1rc4...0.1rc7
[0.1rc4]: https://github.com/BYU-PRISM/GEKKO/compare/0.1b2...0.1rc4
[0.1b2]: https://github.com/BYU-PRISM/GEKKO/compare/0.1b1...0.1b2
[0.1b1]: https://github.com/BYU-PRISM/GEKKO/compare/v0.1a2...0.1b1
[0.1a2]: https://github.com/BYU-PRISM/GEKKO/compare/0.0.4...v0.1a2
