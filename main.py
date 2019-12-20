'''
Created on Dec 14, 2019

@author: MEBMASTER
'''
import os
import json
import numpy as np
import itertools
import shlex
import subprocess
import platform
import time
import sys

def check_program(data):
    path = data['program-path']
    assert os.path.isfile(data['program-path']), f"Program could not be found at {path}"
    return path

def check_ends(data):
    try:
        prepend = data['prepend']
    except:
        prepend = ""
    try:
        append = data['append']
    except:
        append = ""
    return str(prepend), str(append)
    

def check_logs(data):
    try:
        path = data['logs']['path']
        assert os.path.isdir(path), f"{path} is not a directory"
        try:
            name = data['logs']['name']
        except:
            name = ""
    except:
        print("No log directory set, the output will not be saved")
        return False,"",""
    return True, path, name

def get_fixed_parameters(data):
    def get_param(param, value):
        if type(value) is dict:
            try:
                typev = value['type']
            except:
                typev = 'literal'
            if typev == 'string':
                return f"{param} \"{str(value['value'])}\""
            else:
                return f"{param} {str(value['value'])}"
        else:
            return f"{param} {str(value)}"
    try:
        json_fixed_params = data['fixed-parameters']
    except:
        print("No fixed parameters found")
        json_fixed_params = {}
    
    return " ".join([get_param(param,value) for param,value in json_fixed_params.items()])

def get_variable_parameters(data):
    def get_param(param,value):
        try:
            #List of values
            listv = value['list']
        except:
            #Number with stepsize
            listv = None
        if listv != None:
            #List of values
            try:
                typev = value['type']
            except:
                typev = 'literal'
            if typev == 'string':
                return [f"{param} \"{str(e)}\"" for e in listv]
            else:
                return [f"{param} {str(e)}" for e in listv]
        else:
            #Number with stepsize
            start = value['start']
            stop = value['stop']
            step = value['stepsize']
            
            try:
                typev = value['type']
            except:
                typev = 'int'
            if typev == 'float':
                return [f"{param} {str(e)}" for e in np.arange(float(start),float(stop),float(step))]
            else:
                return [f"{param} {str(e)}" for e in range(int(start),int(stop),int(step))]
    try:
        json_var_params = data['variable-parameters']
    except:
        print("No variable parameters found")
        json_var_params = {}
    var_params = [get_param(param,value) for param,value in json_var_params.items()]
    
    #Makes all combinations of variable parameters
    return [" ".join(x) for x in itertools.product(*var_params)]

def get_output_variable(data,var_par_len):
    
    try:
        key,value = [(key,value) for key,value in data['output-parameter'].items() if key is not "type"][0]
        [os.makedirs(f"{value}/{i}", exist_ok=True) for i in range(var_par_len)]
        print("Created output directories")
        return [f"{key} {value}/{i}/output.dat" for i in range(var_par_len)]
    except:
        return ""
    
    
def create_commands(prepend,program_path,fixed_params,out_params,variable_params,append):
    return [f"{prepend}{program_path} {fixed_params} {out_param} {var_params}{append}" for var_params,out_param in zip(variable_params,out_params)]

def execute_commands(commands,write_logs,log_path,log_name):
    for i,command in enumerate(commands):
        print(i,command)
        use_posix = platform.system() != "Windows"
        tokenized = shlex.split(command, posix=use_posix)
        time_started = time.time()
        process = subprocess.Popen(tokenized,
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)
        stdout, stderr = process.communicate()
        time_completed = time.time()
        
        if write_logs:
            if log_name == "":
                log_name = "stdout.txt"
            meta = f"Command: {command}\nStarted: {time_started}\nCompleted: {time_completed}\nDuration: {time_completed-time_started}"
            os.makedirs(f"{log_path}/{i}", exist_ok = True)
            with open(f"{log_path}/{i}/meta.txt", "w") as text_file:
                text_file.write(meta)
            with open(f"{log_path}/{i}/{log_name}", "w") as text_file:
                text_file.write(stdout)
            if stderr != "":
                with open(f"{log_path}/{i}/stderr.txt", "w") as text_file:
                    text_file.write(stderr)
        

if __name__ == "__main__":
    try:
        settings = sys.argv[1]
    except:
        settings = "settings.json"  
    with open(settings) as json_file:
        data = json.load(json_file)
    program_path = check_program(data)
    write_logs,log_path,log_name = check_logs(data)
    command_prepend, command_append = check_ends(data)
    fixed_params = get_fixed_parameters(data)
    var_params = get_variable_parameters(data)
    out_params = get_output_variable(data, len(var_params))
    commands = create_commands(command_prepend, program_path, fixed_params, out_params, var_params, command_append)
    execute_commands(commands, write_logs, log_path, log_name)
    
    
    






