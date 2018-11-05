# Notes on Gekko Gui development

## Todo
- check for memory leaks (serious problems for operators running it for months on end)
- Get some initial figures to Dr. Hedengren
- Integrate in a `hist_hor` optional parameter for API, default to 50-100
- Break up tab into variables, intermediates, and parameters

## Ideas
- a 'selected plot' allowing sidebar to contain options that update that selected plot
- divide out variables tab into `vars`, `params`, `intermediates`
- could add any extra settings like poll rate to a `tools` tab
- add trajectory hi and lo traces, default to hidden

## Questions


## Notes
- trs_hi/lo - additional slack variables - ignore
- wsp - weighted set points - ignore
- err_hi/lo - ignore
- what to plot
  - tr_hi, tr_lo, bcv(biased control variable) for operators
  - add just var for engineer (unbiased)

- store history for MV, FV, CV, SV
  - value var.MODEL in options.json for CV, SV
  - value var.MEAS in options.json for MV, FV
