"""Job conductor plugin codes
"""
import sys
import json
import time

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

"""
To specify a relative input (an input to a plugin which is created as a result of a previous
plugin), follow this schema:

    - For created items:
        - path: (required if not _id) Full path of the new item which is being used as an input. 
        - _id: (required if not path) _id property of new item
    - For created files:
        - itemPath (required if not itemId) Full path of the item which contains the file
        - itemId (required if not itemPath) _id property of item which contains the file
        - fileName (required if not fileId) name property of the file
        - fileId (required if not fileName) _id property of the file
    - For created annotations:
        - itemPath (required if not itemId) Full path of the item which contains the annotation(s)
        - itemId (required if not itemPath) _id property of the item which contains the annotation(s)
        - annotationName (required if not annotationId) (ensure uniqueness) name of the annotation(s)
        - annotationId (required if not annotationName) _id property of the annotation(s)

    Example: These are some example inputs to a plugin that calculates features for a given annotation that 
    is created by a segmentation plugin earlier.

    job_dict = {
        "_id": "63e6bc1da00b00eade3047c3" # _id here refers to the _id of the slicer_cli_web cli
        "parameters": {
            "feature_extraction_annotation": "{{"type": "annotation", "item_type": "_id","item_query":"64ef9c712d82d04be3e2b330", "annotation_type": "name", "annotation_query":"Spots"}}"
        }
    }
        
"""

def find_item(gc,type: str, query:str):

    if type=='path':
        item_info = gc.get(f'/resource/lookup',parameters={'path': query})
    elif type=='_id':
        item_info = gc.get(f'/item/{query}')

    return item_info

def find_file(gc, item_type:str, item_query:str, file_type:str, file_query:str):

    if item_type == 'path':
        item_info = find_item(item_type, item_query)
    elif item_type=='_id':
        item_info = {'_id': item_query}
    
    if file_type == 'fileName':
        item_files = gc.get(f'/item/{item_info["_id"]}/files',parameters = {'limit': 0})

        file_names = [i['name'] for i in item_files]
        file_info = item_files[file_names.index(file_query)]
    
    elif file_type == '_id':
        file_info = {'_id': file_query}

    return file_info

def find_annotation(gc, item_type, item_query, annotation_type, annotation_query):

    if item_type=='path': 
        item_info = find_item(item_type,item_query)
    elif item_type == '_id':
        item_info = {'_id': item_query}

    if annotation_type == 'annotationName':
        item_annotations = gc.get(f'/annotation',parameters={'itemId': item_info["_id"]})

        annotation_names = [i['annotation']['name'] for i in item_annotations]
        annotation_info = item_annotations[annotation_names.index(annotation_query)]
    elif annotation_type=='annotationId':
        annotation_info = {'_id': annotation_query}

    return annotation_info

def populate_inputs(gc,job_dict)->dict:
    
    # Checking job_dict for any {{}} indicating something that needs to be filled in
    for key,val in job_dict['parameters'].items():

        if "{{" in val:
            populate_args = json.loads(val[1:-1])
            if populate_args['type']=='item':
                new_val = find_item(populate_args['item_type'],populate_args['item_query'])['_id']
            elif populate_args['type']=='file':
                new_val = find_item(populate_args['item_type'],populate_args['item_query'],populate_args['file_type'],populate_args['file_query'])['_id']
            elif populate_args['type']=='annotation':
                new_val = find_item(populate_args['item_type'],populate_args['item_query'],populate_args['annotation_type'],populate_args['annotation_query'])['_id']

            job_dict['parameters'][key] = new_val
        
    return job_dict


def run_job(gc,job_dict)->dict:
    
    run_job_output = gc.post(
        f'/slicer_cli_web/cli/{job_dict["_id"]}',
        parameters = {
            'girderApiUrl': gc.apiUrl,
            'girderToken': gc.token
        } | job_dict['parameters']
    )

    return run_job_output

def check_job_status(gc,job_id)->int:
    job_info = gc.get(f'/job/{job_id}')

    return JOB_STATUS_KEY[job_info['status']]


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
        while not current_status in ["SUCCESS","ERROR","CANCELED"]:
            time.sleep(args.check_interval)
            current_status = check_job_status(gc,running_job_info)

            if current_status in ['ERROR','CANCELED']:
                raise SystemError
    

if __name__=='__main__':
    main(CLIArgumentParser().parse_args())

