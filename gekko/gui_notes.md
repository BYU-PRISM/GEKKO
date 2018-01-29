# Notes on Gekko Gui development

## Questions

## Answered Questions  
- Are the JSON structures pretty static or will there be field that only appear
  depending on what the user chooses? If not, can it be made static
  - pretty static. We can deal with exceptions as they come
- I managed to remove the Plotly logo. Do you have an opinion on this?
  - Either way. We should make sure to give them credit somewhere.
- Do you already have a debug or dev/production variables? Auto opening the webpage
  works great with flask in `DEBUG=False`, but double loads the page in `DEBUG=True`.
  - No existing variable. Just use one for the GUI
- Any thoughts on including dimensions into the variables somehow so they can be displayed?
  - Total units integration is a future idea. Nothing for right now.
- Any Ideas on how to determine which lines to display by default. 70B vs 0.01?
  - Parameters and Variables
- Do you have a problem using bootstrap? What about using it from a CDN?
  - resolved. added flask route to serve bootstrap locally
- How do you work with a dev version of gekko?
  - `pip install -e .`
- What would be the best method to call `display_results()`?
  - `m.GUI()`
- I just added all the dash dependencies to setup.py. Is that what you want?
  - yes.

## For Alpha release
- Map python vars to the chart labels
- Clean up the options.json display into pretty tabs

## Todo
- make sure the right port is displayed in the event that dash chooses something
  other than `localhost:8050`
  - `app.port`?
- Organize tables into tabs
  - may wait a little on this one as a tab component is actively being developed
- Pretty up the graph
  - add log scale options
- Decide what to put on each graph or at least what to display by default
- Map the user var names to the model var names


## Bugs
- When DASH renders it somehow triggers a rerender that even makes GEKKO
  reoptimize the whole model.
  - RESOLVED: It looks like this is actually due to Flask being in `DEBUG=True`. For some
    reason this causes a complete rerender. If this is a problem then simply set
    `DEBUG=False`
