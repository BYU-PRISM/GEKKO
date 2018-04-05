# Notes on Gekko Gui development

## Priorities
- squish any bugs that may arise
  - backend tends to crash in Windows IPython env

## Todo
- check for memory leaks (serious problems for operators running it for months on end)
- Look into real-time plotting
- refactor backend to send back a better formatted object
  - list of vars, params, intermediates...
- Figure out how the update object shoudl look

## Ideas
- a 'selected plot' allowing sidebar to contain options that update that selected plot
- divide out variables tab into `vars`, `params`, `intermediates`
- could add any extra settings like poll rate to a `tools` tab
- add trajectory hi and lo traces, default to hidden
