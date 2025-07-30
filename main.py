from codebase import utility as util
from codebase import constants as const

import subprocess

util.log("\n[bold cyan]🔧  Setup Initiated[bold cyan]\n")

choice = util.prompt_model_choice()
job_type = const.job_names[choice-1]

if choice == 1 :
    # run send.py
    subprocess.run(['python', '-m', 'jobs.send'])
    util.rich_divider()
else :
    # run receive.py
    subprocess.run(['python', '-m', 'jobs.receive'])
    util.rich_divider()
    

