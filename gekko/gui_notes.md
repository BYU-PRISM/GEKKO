# Notes on Gekko Gui development

## Priorities
- squish any bugs that may arise
  - backend tends to crash in Windows IPython env

## Todo
- check for memory leaks (serious problems for operators running it for months on end)
- Get dynamic plotting working
- Get some initial figures to Dr. Hedengren
- Integrate in a `hist_hor` optional parameter for API, default to 50-100
- Break up tab into variables, intermediates, and parameters

## Ideas
- a 'selected plot' allowing sidebar to contain options that update that selected plot
- divide out variables tab into `vars`, `params`, `intermediates`
  - wait on Logan to distinguish between intermediates and constants
- could add any extra settings like poll rate to a `tools` tab
- add trajectory hi and lo traces, default to hidden


## Notes
- Made intermediates hidden by default
