Job Conductor
==============

This is a plugin designed to coordinate the execution of multiple plugins in a sequential fashion with options for dynamic input parameters defined as outputs in previous plugins.

.. code-block:: python

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


