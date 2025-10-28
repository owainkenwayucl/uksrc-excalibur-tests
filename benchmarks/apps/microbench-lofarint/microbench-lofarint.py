import pathlib, os, subprocess

from datetime import datetime as dt
import reframe.utility.sanity as sn

import reframe as rfm
from reframe.core.backends import getlauncher
from reframe.core.builtins import sanity_function, parameter, run_before, run_after, performance_function

@rfm.simple_test
class MicrobenchLOFARINT(rfm.RunOnlyRegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['default']

    lofarint_code_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LOFARINT_Code")
    lofarint_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LOFARINT_Data")

    tasks = parameter([1])
    num_tasks_per_node = 1
    cpus_per_task = parameter([16])

    executable = "toil-cwl-runner"

    @run_before('setup')
    def download_linc(self):
        LINC_dir = os.path.join(self.lofarint_code_dir, "LINC")
        if not os.path.exists(LINC_dir):
            os.makedirs(self.lofarint_code_dir, exist_ok=True)
            os.makedirs(LINC_dir, exist_ok=True)
            print(f"git clone https://git.astron.nl/RD/LINC.git {LINC_dir}")
            subprocess.call(["git", "clone", "https://git.astron.nl/RD/LINC.git", LINC_dir])
        else:
            print("LINC already downloaded")

    @run_before('setup')
    def download_vlbi(self):
        VLBI_dir = os.path.join(self.lofarint_code_dir, "VLBI")
        if not os.path.exists(VLBI_dir):
            os.makedirs(self.lofarint_code_dir, exist_ok=True)
            os.makedirs(VLBI_dir, exist_ok=True)
            print(f"git clone https://git.astron.nl/RD/VLBI-cwl.git {VLBI_dir}")
            subprocess.call(["git", "clone", "https://git.astron.nl/RD/VLBI-cwl.git", VLBI_dir])
        else:
            print("VLBI already downloaded")

    @run_before('setup')
    def download_singularity_image(self):
        vlbi_singularity_dir = os.path.join(self.lofarint_code_dir, "singularity_images")

        vlbi_singularity_sif = os.path.join(vlbi_singularity_dir, "flocs_v5.6.0_sandybridge_sandybridge.sif")
        if not os.path.isfile(vlbi_singularity_sif):
            print(f"wget -O {vlbi_singularity_sif} https://public.spider.surfsara.nl/project/lofarvwf/fsweijen/containers/flocs_v5.6.0_sandybridge_sandybridge.sif")
            subprocess.call(["wget", "-O", vlbi_singularity_sif, "https://public.spider.surfsara.nl/project/lofarvwf/fsweijen/containers/flocs_v5.6.0_sandybridge_sandybridge.sif"])
        else:
            print("VLBI singularity image already downloaded")

        vlbi_singularity_link = os.path.join(vlbi_singularity_dir, "vlbi-cwl.sif")
        if not os.path.isfile(vlbi_singularity_link):
            print(f"ln -s {vlbi_singularity_sif} {vlbi_singularity_link}")
            subprocess.call(["ln", "-s", vlbi_singularity_sif, vlbi_singularity_link])
        else:
            print("VLBI singularity image already linked")

        vlbi_singularity_latest_link = os.path.join(vlbi_singularity_dir, "vlbi-cwl_latest.sif")
        if not os.path.isfile(vlbi_singularity_latest_link):
            print(f"ln -s {vlbi_singularity_sif} {vlbi_singularity_latest_link}")
            subprocess.call(["ln", "-s", vlbi_singularity_sif, vlbi_singularity_latest_link])
        else:
            print("VLBI singularity image already linked with latest")

    @run_before('setup')
    def download_data(self):
        data_set = os.path.join(self.lofarint_data_dir, "L693725_SB282_uv.MS")
        if not os.path.exists(data_set):
            os.makedirs(self.lofarint_data_dir, exist_ok=True)
            for i in range(1,40):
                file = f"https://zenodo.org/records/17236157/files/LOFARINT_Data_{i}.tar?download=1"
                file_name = f"{self.lofarint_data_dir}/LOFARINT_Data_{i}.tar"
                print(f"wget -O {file_name} {file}")
                subprocess.call(["wget", "-O", file_name, file])
            print("cat LOFARINT_Data_{1..39}.tar | tar -xvfi -")
            subprocess.call(["cat", "LOFARINT_Data_{1..39}.tar", "|", "tar", "-xvif", "-"])
        else:
            print("Data already downloaded")

    @run_before('run')
    def set_executable_opts(self):
        self.executable_opts = [
            "--singularity",
            "--clean", "never",
            "--retryCount", "0",
            "--disableCaching",
            "--logFile", os.path.join(self.stagedir, "logs/microbench-lofarint.log"),
            "--writeLogs", os.path.join(self.stagedir, "logs"),
            "--tmp-outdir-prefix", self.stagedir,
            "--jobStore", os.path.join(self.stagedir, "job_store"),
            "--bypass-file-store",
            "setup",
            self.lofarint_data_dir
        ]
