# -*- coding: utf-8 -*-

import json
import os

from .properties import parameter_options, variable_options


#%% Post-solve processing

def load_JSON(self):
    f = open(os.path.join(self.path,'options.json'))
    data = json.load(f)
    f.close()
    #global (APM) options
    for o in self.options._output_option_list+self.options._inout_option_list:
        self.options.__dict__[o] = data['APM'][o]
    #Variable options (FV/MV/SV/CV)
    for vp in self.parameters:
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
    for vp in self.variables:
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

def load_results(self):
    if (os.path.isfile(os.path.join(self.path, 'results.json'))):
        f = open(os.path.join(self.path,'results.json'))
        data = json.load(f)
        f.close()

        for vp in self.parameters:
            if vp.type is not None:
                try:
                    vp.VALUE = data[vp.name]
                    vp.value.change = False
                except Exception:
                    print(vp.name+ " not found in results file")
        for vp in self.variables:
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




def load_csv_results(self):

    # Load results.csv into a dictionary keyed with variable names
    if (os.path.isfile(os.path.join(self.path, 'results.csv'))):
        with open(os.path.join(self.path,'results.csv')) as f:
            reader = csv.reader(f, delimiter=',')
            y={}
            for row in reader:
                if len(row)==2:
                    y[row[0]] = float(row[1])
                else:
                    y[row[0]] = [float(col) for col in row[1:]]
        # Load variable values into their respective objects from the dictionary
        for vp in self.parameters+self.variables:
            try:
                vp.VALUE = y[str(vp)]
            except Exception:
                pass
        # Return solution
        return y

    else:
        print("Error: 'results.csv' not found. Check above for addition error details")
        return {}
