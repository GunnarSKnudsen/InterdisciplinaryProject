# execute notebooks
import subprocess
import sys
import time
import datetime
import shutil

def execute_notebook(notebook_path):
    """
    Execute a Jupyter notebook via nbconvert and collect output.
    :param notebook_path: path to the notebook to execute
    :param output_path: path to the output notebook
    :return: executed notebook as a string
    """
    print("Executing notebook: ", notebook_path)
    start_time = time.time()
    subprocess.check_call([sys.executable, '-m', 'nbconvert', '--to', 'notebook', '--execute', '--inplace', '--ExecutePreprocessor.timeout=60000', notebook_path])
    print("Finished executing notebook: ", notebook_path)
    print("Time elapsed: ", datetime.timedelta(seconds=time.time() - start_time))

def execute_script(script_path):
    """
    Execute a script
    :param script_path: path to the script to execute
    :param output_path: path to the output notebook
    :return: executed notebook as a string
    """
    print("Executing script: ", script_path)
    start_time = time.time()
    subprocess.check_call([sys.executable, script_path])
    print("Finished executing script: ", script_path)
    print("Time elapsed: ", datetime.timedelta(seconds=time.time() - start_time))

def set_settings_file(setting_file):
    # copy settings file to input_data
    shutil.copyfile(setting_file, f"input_data/settings.json")

NAME = "Niedermayer"

set_settings_file(f"settings/{NAME}.json")
#execute_script("preprocessing.py")
#print("Finished preprocessing")
#execute_notebook("CompaniesToExclude.ipynb")
#print("Finished CompaniesToExclude")
#execute_notebook("calculate_AR.ipynb")
#print("Finished calculate_AR")
execute_notebook("Statistics.ipynb")
print("Finished Statistics")
