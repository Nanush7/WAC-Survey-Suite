# WAC Survey Validator
Script to validate WCA Advisory Council's surveys.

## Requirements
 - Python >=3.11

## Installation
1. Clone the repository or download the source code from [Releases](https://github.com/Nanush7/wac-survey-validator/releases).
2. `$ python3 -m pip install -r requirements.txt`

## Usage
**Move the survey CSV and tokens file to the script's directory.**

```
usage: main.py [-h] [--dry-run] [-o OUTPUT_PATH] [-l] [-q] [--no-warn] [-v]
               [--log-file] [--no-colors]
               input_path tokens

Script to validate survey tokens.

options:
  -h, --help            show this help message and exit

General options:
  input_path            Plain text file with the tokens
  tokens                Token list file
  --dry-run             Use the run_delete method without generating the validated
                        file. For debugging purposes
  -o OUTPUT_PATH, --output OUTPUT_PATH
                        Validated responses
  -l                    Generate a list of responses to delete, instead of
                        generating a validated CSV file.

Log options:
  -q, --quiet           Do not log anything
  --no-warn             Do not show warnings
  -v, --verbose         Show debug messages
  --log-file            Log Output to output.log
  --no-colors           Disable colored logs
```

### Usage examples
**To get a new CSV file without the invalid responses:**
`$ python3 main.py <survey_file_name>.csv <tokens_file_name>.txt`

This will generate a `Validated.csv` file.

***

**To get a list of responses to delete from the survey's website:**
`$ python3 main.py <survey_file_name>.csv <tokens_file_name>.txt -l`

This will generate a `ToDelete.txt` file with all the response IDs to delete.
