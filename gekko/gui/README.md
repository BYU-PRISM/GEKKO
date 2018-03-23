# GUI for Project GEKKO

> A Vue.js gui for project GEKKO.

This simple gui is used for visualizing the results from a Gekko model
optimization. It can be launched by calling `model.GUI()` from the python Gekko
script. It interfaces with the python API set up in `gekko/gk_gui.py`.

## Build Setup

``` bash
# install dependencies
npm install

# serve in dev mode with hot reload at localhost:8080
# Remember to also set `DEV=True` in `gk_gui.py`
npm run dev

# build for production with minification. Places built files in `gekko/static`
npm run build

# build for production and view the bundle analyzer report
npm run build --report
```

## Project details

### Polling system
Due to the nature of the program there is a need for regular communication
between the frontend and backend. This allows the frontend to know when the
backend crashed, the backend to intuitively exit when the frontend is closed
and allows the frontend to oick up any updates in the model that may be passed
by the backed. It will also soon allow for realtime plotting as project gekko
steps through the solution.
