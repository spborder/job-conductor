"""Job conductor plugin codes
"""
import os
import sys
import json
import time

import requests
import girder_client
from ctk_cli import CLIArgumentParser

JOB_STATUS_KEY = {
    0: 'INACTIVE',
    1: 'QUEUED',
    2: 'RUNNING',
    3: 'SUCCESS',
    4: 'ERROR',
    5: 'CANCELED'
}


def populate_inputs(gc,job_dict)->dict:
    pass

def run_job(gc,job_dict)->dict:
    pass

def check_job_status(gc,job_id)->int:
    pass


def main(args):

    sys.stdout.flush()

    gc = girder_client.GirderClient(
        apiUrl = args.girderApiUrl
    )
    gc.setToken(args.girderToken)

    print('Input arguments: ')
    for a in vars(args):
        print(f'{a}: {getattr(args,a)}')

    job_list = json.loads(args.job_list)

    for job_idx, job in enumerate(job_list):
        
        new_job_dict = populate_inputs(gc,job)
        running_job_info = run_job(gc,new_job_dict)

        current_status = check_job_status(gc,running_job_info['_id'])
        while not current_status in [3,4,5]:
            time.sleep(5)
            current_status = check_job_status(gc,running_job_info)
    

if __name__=='__main__':
    main(CLIArgumentParser().parse_args())

