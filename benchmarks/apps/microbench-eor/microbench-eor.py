import pathlib, os, subprocess, json

from datetime import datetime as dt
import reframe.utility.sanity as sn

import reframe as rfm
from reframe.core.backends import getlauncher
from reframe.core.builtins import sanity_function, parameter, run_before, run_after, performance_function

from astropy.io import fits

@rfm.simple_test
class MicrobenchEOR(rfm.RunOnlyRegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['default']

    eor_code_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "EOR_Code")
    eor_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "EOR_Data")
    os.makedirs(eor_data_dir, exist_ok=True)

    hera_pspec_dir = os.path.join(eor_code_dir, 'hera_pspec')

    tasks = parameter([1])
    num_tasks_per_node = 1
    cpus_per_task = parameter([16])

    executable = "apptainer"

    @run_before('setup')
    def build_singularity(self):
        if not os.path.isfile(os.path.join(self.eor_code_dir, "singularity_images/hera-pspec-mambaorg.sif")):
            og_dir = os.getcwd()
            os.chdir(os.path.join(self.eor_code_dir, "singularity_images"))
            subprocess.run(
                ["singularity",
                 "build",
                 "hera-pspec-mambaorg.sif",
                 "hera-pspec-mambaorg.def"
                 ]
            )
            os.chdir(og_dir)

    @run_before('setup')
    def download_data(self):
        data_set = os.path.join(self.eor_data_dir, "")
        if not os.path.isfile(data_set):
            file = f""
            file_name = data_set
            subprocess.run(["wget", "-O", file_name, file])

    @run_before('run')
    def add_prerun_cmds(self):
        self.prerun_cmds = [
        ]

    @run_before('run')
    def set_executable_opts(self):
        os.mkdir(os.path.join(self.outputdir, "outputs"))
        self.executable_opts = [
            "run",
            "--bind", f"{self.eor_data_dir}:/data",
            "--bind", f"{self.outputdir}:/project",
            os.path.join(self.eor_code_dir, 'singularity_images/hera-pspec-mambaorg.sif'),
            os.path.join(self.eor_code_dir, "scripts/pspec_params_micro.yaml")
        ]

    @sanity_function
    def validate(self):
        with open(os.path.join(self.output_dir, "rfm_job.out")) as myfile:
            if "All PSPEC MERGE jobs ran through" in myfile.read():
                return True
            else:
                return False

#    @run_after('sanity')
#    def free_space(self):
#        subprocess.run(["rm", "-rf", os.path.join(self.outputdir, "intermediate-products")])
#        subprocess.run(f"rm {self.outputdir}/*.fits", shell=True, check=True)
