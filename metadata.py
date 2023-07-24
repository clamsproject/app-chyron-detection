"""
The purpose of this file is to define the metadata of the app with minimal imports. 

DO NOT CHANGE the name of the file
"""

from mmif import DocumentTypes, AnnotationTypes

from clams.app import ClamsApp
from clams.appmetadata import AppMetadata


# DO NOT CHANGE the function name 
def appmetadata() -> AppMetadata:
    """
    Function to set app-metadata values and return it as an ``AppMetadata`` obj.
    Read these documentations before changing the code below
    - https://sdk.clams.ai/appmetadata.html metadata specification. 
    - https://sdk.clams.ai/autodoc/clams.appmetadata.html python API
    
    :return: AppMetadata object holding all necessary information.
    """
    
    # Basic Information
    metadata = AppMetadata(
        name="Chyron Detection",
        description="This tool detects chyrons, generates time segments.",
        app_license="MIT",  
        identifier="chyron-detection",
        url="https://github.com/clamsproject/app-chyron-detection",
    )

    # I/O Spec
    metadata.add_input(DocumentTypes.VideoDocument)
    metadata.add_output(AnnotationTypes.TimeFrame, properties={"frameType": "chyron"})
    
    # Runtime Parameters
    metadata.add_parameter(name="timeUnit",
                           description="unit for output timeframe",
                           type="string",
                           default="frames",
                           choices=["frames", "seconds", "milliseconds"])

    metadata.add_parameter(name="sampleRatio",
                           description="Frequency to sample frames",
                           type="integer",
                           default=5)

    metadata.add_parameter(name="minFrameCount",
                           description="Minimum number of frames required for a timeframe to be included",
                           type="integer",
                           default=10)
    
    metadata.add_parameter(name="threshold",
                           description="Threshold from 0-1, lower accepts more potential chyrons",
                           type="number",
                           default=0.5)

    return metadata


# DO NOT CHANGE the main block
if __name__ == '__main__':
    import sys
    metadata = appmetadata()
    for param in ClamsApp.universal_parameters:
        metadata.add_parameter(**param)
    sys.stdout.write(metadata.jsonify(pretty=True))
