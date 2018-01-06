# -*- coding: utf-8 -*-

import re

def convertAPM(modelfile,outputfile):
    
    f = open(filepath)
    
    lines = f.readlines()
    
    state = 0
    #constants = 1
    #parameters = 2
    #variables = 3
    #intermediates = 4
    #equations = 5
    
    with open(new_filepath, "w") as f_new:
        # Import thundersnow and setup model
        print('from thundersnow import ThunderSnow',file=f_new)
        print('',file=f_new)
        print('m = ThunderSnow()',file=f_new)
        print('',file=f_new)
        
        for line in lines:
            # Remove spaces before and after
            line = line.strip()
            # Check which section of the model we are in
            if 'Model' in line and '!' not in line:
                print('',file=f_new)
                print('#%% ' + line,file=f_new)
                print('',file=f_new)
                state = 0
                continue
            if 'Constants' in line and '!' not in line:
                print('',file=f_new)
                print('#%% ' + line,file=f_new)
                print('',file=f_new)
                state = 1
                continue
            if 'Parameters' in line and '!' not in line:
                print('',file=f_new)
                print('#%% ' + line,file=f_new)
                print('',file=f_new)
                state = 2
                continue
            if 'Variables' in line and '!' not in line:
                print('',file=f_new)
                print('#%% ' + line,file=f_new)
                print('',file=f_new)
                state = 3
                continue
            if 'Intermediates' in line and '!' not in line:
                print('',file=f_new)
                print('#%% ' + line,file=f_new)
                print('',file=f_new)
                state = 4
                continue
            if 'Equations' in line and '!' not in line:
                print('',file=f_new)
                print('#%% ' + line,file=f_new)
                print('',file=f_new)
                state = 5
                continue
        #    print(state)
            
            # Split line content from comments
            line_content = line.split('!')[0]
            
            # Replace operators with TS version
            line_content = re.sub('cos\(','m.cos(',line_content)
            line_content = re.sub('sin\(','m.sin(',line_content)
            line_content = re.sub('tan\(','m.tan(',line_content)
            line_content = re.sub('exp\(','m.exp(',line_content)
            line_content = re.sub('sqrt\(','m.sqrt(',line_content)
            line_content = re.sub('log10\(','m.log10(',line_content)
            line_content = re.sub('\^','**',line_content)
            
            # Split line by spaces
            words = line_content.split()
            
            # Replace derivative signs with dt()
            for i, word in enumerate(words):
                if('$' in word):
                    subwords = re.split("[, \-!?:()\*^]+",word)
                    for subword in subwords:
                        if '$' in subword:
                            words[i] = words[i].replace(subword,subword[1:]+str('.dt()'))
            
            # Check for end of line comments
            comment = '' # Initialize comment as empty
            if(len(line.split('!'))>1):
                comment = ' #' + line.split('!')[1]
            
            # Check for empty line
            if not words and len(line)==0:
                print('',file=f_new)
            # Check for full line comments
            elif(line[0]=='!'):
                print(line.replace('!','#'),file=f_new)
            elif(state==1):
                # Constants
                print(str(words[0]) + ' = m.Const('+''.join(words[2:])+',\''+str(words[0])+'\')' + comment,file=f_new)
            elif(state==2):
                # Parameters
                print(str(words[0]) + ' = m.Param('+''.join(words[2:])+',\''+str(words[0])+'\')' + comment,file=f_new)
            elif(state==3):
                # Variables
                # Initialize lower and upper bounds
                lb = ''
                ub = ''
                # Parse bounds if any
                if('<' in words):
                    ub = ',' + words[words.index('<')+1]
                if('<=' in words):
                    ub = ',' + words[words.index('<=')+1]
                if('>' in words):
                    lb = ',' + words[words.index('>')+1]
                if('>=' in words):
                    lb = ',' + words[words.index('>=')+1]
                # Split out just variable value
                value = re.split(',|<|<=|>|>=',''.join(words[2:]))[0]
                print(str(words[0]) + ' = m.Var('+value+lb+ub+',\''+str(words[0])+'\')' + comment,file=f_new)
            elif(state==4):
                # Intermediates
                print(str(words[0]) + ' = m.Inter('+''.join(words[2:])+',\''+str(words[0])+'\')' + comment,file=f_new)
            elif(state==5):
                # Equations
                # Check for objective function
                if(words[0]=='minimize'):
                    print('m.Obj('+''.join(words[1:])+')' + comment,file=f_new)
                elif(words[0]=='maximize'):
                    print('m.Obj(-'+''.join(words[1:])+')' + comment,file=f_new)
                # Otherwise add new equation
                else:
                    print('m.Equation('+''.join(words).replace('=','==').replace('<==','<=').replace('>==','>=')+')' + comment,file=f_new)
    
    f.close()
    
    return

if __name__ == "__main__":
    filepath = r'model_template_density_climb_drag_opt_drag_solver_clean_dragsurface.apm'
    new_filepath = 'converted.py'
    convertAPM(filepath,new_filepath)