# shell-parameter-tester

This allows you to test different combinations of parameters of CLI programs.

## How to use
The parameters you want passed to the script is specified in a json file. By default this script searches for a settings.json in the current working directory, but you can also pass the file as an argument when calling this script.

### Setting the program path
In order to run your program, the script will need to know the location. This is specified in the `program-path` key.
```json
{
  "program-path": "/path/to/my/program/JavaApp.jar"
}
```

### Fixed parameters
These are parameters that stay the same. These can be specified in two ways. They are always set in the `fixed-parameter` schema. 
Method one is simply setting a key and a value. 
```json
{
  "fixed-parameters": {
    "-my_fixed_tag": "my_value"
  }
}
```
The second method is using a subschema instead as a value. Using this, the script will search for the value key and format it according to the type value. When the type is `string`, the script will enclose the value in `""`. The other type is `literal`, which returns the same as method one.
```json
{
  "fixed-parameters": {
    "-my_other_fixed_tag": {
      "value": "my_value",
      "type": "string"
    }
  }
}
```
It does not matter if a number is enclosed in `""`

### [Variable parameters](var-param)
This is the fun part. Parameters that will be varied are put in the `variable-parameters` schema. There are two different ways to specify variable parameters. You can either use a list or a range. Using a range looks like this:
```json
{
  "variable-parameters": {
    "-my_var_param": {
      "start": 10,
      "stop": 20,
      "stepsize": 2,
      "type": "int"
    }
  }
}
```
With ranges the type must be either `int` or `float`.

Using a list looks like this:
```json
{
  "variable-parameters": {
    "-my_second_var_param": {
      "list": ["hoho","hehe"],
      "type": "string"
    }
  }
}
```
With lists, the type must be either `string` or `literal`.

The script will make all combinations of variable parameters. The output of joining the two previous example would be:

`-my_var_param 10 -my_second_var_param "hoho"`

`-my_var_param 10 -my_second_var_param "hehe"`

`-my_var_param 12 -my_second_var_param "hoho"`

`-my_var_param 12 -my_second_var_param "hehe"`

...

`-my_var_param 20 -my_second_var_param "hehe"`

### [Output parameter](#output-param)
Currently, the script only supports one output parameter. This will usually be an output file your program needs. This is specified in the `output-parameter` schema. Here, the parameter your program uses for output must be specified as a key, and the path as the value. The script creates a directory for every parameter combination using this path. These directories are numbered from `0` to the amount of commands created by your parameters. Furthermore, you can set the `type` of this path, either `string` or `literal`. 
```json
"output-parameter": {
  "-o": "C:/test",
  "type": "literal"
}
```
Using this example and the examples from [the variable parameters section](#var-param), since there are 10 total combinations, there will be created 10 new directories in the directory `C:/test`, numbered `0`-`9`.



### Prepend and append
If you want to prepend or append something to the command, use the `prepend` and `append` keys. This is prepended/appended with no extra whitespace, so if this is necessary, make sure to include it in the value.
```json
{
  "prepend": "java -jar "
}
```

### Logs
Optionally you can enable logs, which write the stdout and stderr to files. This is done by specifying the `logs` schema. Here, the key `path` and `name` can be set. `path` is the path to a directory in which you want to put the logs. This works like [the output parameter](#output-param), whereby it creates directories numbered `0` to the amount of commands created by your parameters. Ideally this should be the same path as used in your `output-parameter`. 

You can also set the `name` key, to set the name of the file created from the stdout. Stderr will always be called `stderr.txt`.
```json
"logs": {
  "path": "C:/test",
  "name": "JavaApp_stdout.txt"
}
```
Additionally, a filed called meta.txt will be put in the directories, which gives information on the exact command executed, as well as the time started, completed, and total duration of your program.
