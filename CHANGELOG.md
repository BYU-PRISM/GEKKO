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

## [0.0.1a1] - 2018-01-10
### Initial GEKKO public release, alpha version

[Unreleased]: https://github.com/BYU-PRISM/GEKKO/compare/0.1...HEAD
[0.1]: https://github.com/BYU-PRISM/GEKKO/compare/0.1rc7...0.1
[0.1rc7]: https://github.com/BYU-PRISM/GEKKO/compare/0.1rc4...0.1rc7
[0.1rc4]: https://github.com/BYU-PRISM/GEKKO/compare/0.1b2...0.1rc4
[0.1b2]: https://github.com/BYU-PRISM/GEKKO/compare/0.1b1...0.1b2
[0.1b1]: https://github.com/BYU-PRISM/GEKKO/compare/v0.1a2...0.1b1
[0.1a2]: https://github.com/BYU-PRISM/GEKKO/compare/0.0.4...v0.1a2
