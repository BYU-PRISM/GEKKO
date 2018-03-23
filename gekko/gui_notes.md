# Notes on Gekko Gui development

## Priorities
- squish any bugs that may arise
- refactor backend to have one grand intuitive object
- refactor frontend to use Vuex as a central data store

## Todo
- Decide what to put on each graph or at least what to display by default
- check for memory leaks (could cause serious problems for operators where it may be running for months on end)
- Get tabs col ready to be used interactively
- Look into real-time plotting
- switch over to using vuex to manage state across components and centralize api calls


## Ideas
- a 'selected plot' allowing sidebar to contain options that update that selected plot
- divide out variables tab into `vars`, `params`, `intermediates`
- could add any extra settings like poll rate to a `tools` tab
- add trajectory hi and lo traces, default to hidden
