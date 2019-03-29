# -*- coding: utf-8 -*-

import json
import os

from .properties import parameter_options, variable_options


#%% Post-solve processing

## options.JSON has all APM options
def load_JSON(self):
    f = open(os.path.join(self._path,'options.json'))
    data = json.load(f)
    f.close()
    #global (APM) options
    for o in self.options._output_option_list+self.options._inout_option_list:
        self.options.__dict__[o] = data['APM'][o]
    #Variable options (FV/MV/SV/CV)
    for vp in self._parameters:
        if vp.type != None: #(FV/MV/SV/CV) not Param or Var
            for o in parameter_options[vp.type]['outputs']+parameter_options[vp.type]['inout']:
                if o == 'VALUE':
                    continue
                elif o == 'PRED': #Pred can be an array of up to 10
                    if o in data[vp.name]: #single value
                        vp.__dict__[o] = data[vp.name][o]
                    else:
                        try: #fill in an array up to 10 values
                            pred = []
                            for i in range(11):
                                pred.append(data[vp.name][o+'['+str(i)+']'])
                        except:
                            pass
                        finally:
                            vp.__dict__[o] = pred
                elif o == 'DPRED': #Pred can be an array of up to 10
                    if o in data[vp.name]: #single value
                        vp.__dict__[o] = data[vp.name][o]
                    else:
                        try: #fill in an array up to 10 values
                            dpred = []
                            for i in range(1,11):
                                pred.append(data[vp.name][o+'['+str(i)+']'])
                        except:
                            pass
                        finally:
                            vp.__dict__[o] = dpred
                else: #everything besides value, dpred and pred
                    vp.__dict__[o] = data[vp.name][o]
    for vp in self._variables:
        if vp.type != None: #(FV/MV/SV/CV) not Param or Var
            for o in variable_options[vp.type]['outputs']+variable_options[vp.type]['inout']:

                if o == 'VALUE':
                    continue
                elif o == 'PRED': #Pred can be an array of up to 10
                    if o in data[vp.name]: #single value
                        vp.__dict__[o] = data[vp.name][o]
                    else:
                        try: #fill in an array up to 10 values
                            pred = []
                            for i in range(11):
                                pred.append(data[vp.name][o+'['+str(i)+']'])
                        except:
                            pass
                        finally:
                            vp.__dict__[o] = pred
                else: #everything besides value and pred
                    vp.__dict__[o] = data[vp.name][o]
    return data


## results.json has variable value results
def load_results(self):
    if (os.path.isfile(os.path.join(self._path, 'results.json'))):
        f = open(os.path.join(self._path,'results.json'))
        data = json.load(f)
        f.close()

        for vp in self._parameters:
            try:
                vp.VALUE = data[vp.name]
                vp.value.change = False
            except Exception:
                print(vp.name+ " not found in results file")
        for i in self._intermediates:
            try:
                i.value.value = data[i.name]
                i.value.change = False
            except Exception:
                print(i.name+ " not found in results file")
        for vp in self._variables:
            try:
                vp.VALUE = data[vp.name]
                vp.value.change = False
            except Exception:
                print(vp.name+ " not found in results file")

        return data

    else:
        print("Error: 'results.json' not found. Check above for additional error details")
        return {}

    print(data['APM']['SOLVESTATUS'])
    return data


