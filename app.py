import argparse
import logging
import warnings
from typing import Union

import cv2
from clams import ClamsApp, Restifier
from mmif import Mmif, AnnotationTypes, DocumentTypes
from mmif.utils import video_document_helper as vdh

import apputils


class ChyronDetection(ClamsApp):

    def __init__(self):
        super().__init__()

    def _appmetadata(self):
        # see metadata.py 
        pass

    def _annotate(self, mmif: Union[str, dict, Mmif], **parameters) -> Mmif:
        if not isinstance(mmif, Mmif):
            mmif = Mmif(mmif)

        vds = mmif.get_documents_by_type(DocumentTypes.VideoDocument)
        if vds:
            vd = vds[0]
        else:
            warnings.warn("No video document found in the input MMIF.")
            return mmif
        config = self.get_configuration(**parameters)
        unit = config["timeUnit"]
        new_view = mmif.new_view()
        self.sign_view(new_view, parameters)
        new_view.new_contain(AnnotationTypes.TimeFrame, timeUnit=unit, document=vd.id)
        for start_frame, end_frame in self.run_chyrondetection(vd, config):
            timeframe_annotation = new_view.new_annotation(AnnotationTypes.TimeFrame)
            timeframe_annotation.add_property("start", vdh.convert(start_frame, 'f', unit, vd.get_property("fps")))
            timeframe_annotation.add_property("end", vdh.convert(end_frame, 'f', unit, vd.get_property("fps")))
            timeframe_annotation.add_property("frameType", "chyron")
        return mmif 

    def run_chyrondetection(self, vd, configuration):
        self.logger.debug(f"video_filename: {vd.location_path()}")
        cap = vdh.capture(vd)

        self.logger.debug(f"{vd.get_property('frameCount')}, {configuration['sampleRatio']}")
        frames_to_test = vdh.sample_frames(0, int(vd.get_property('frameCount')), configuration['sampleRatio'])
        self.logger.debug(f"frames_to_test: {frames_to_test}")
        found_chyrons = []
        in_chyron = False
        start_frame = None
        cur_frame = frames_to_test[0]
        for cur_frame in frames_to_test:
            cap.set(cv2.CAP_PROP_POS_FRAMES, cur_frame - 1)
            ret, frame = cap.read()
            if not ret:
                break
            is_chyron = apputils.get_chyron(frame, threshold=configuration['threshold'])
            self.logger.debug(f"cur_frame: {cur_frame}, chyron? : {is_chyron is not None}")
            if is_chyron:
                if not in_chyron:
                    in_chyron = True
                    start_frame = cur_frame
            else:
                if in_chyron:
                    in_chyron = False
                    if cur_frame - start_frame > configuration['minFrameCount']:
                        found_chyrons.append((start_frame, cur_frame))
        if in_chyron:
            if cur_frame - start_frame > configuration['minFrameCount']:
                found_chyrons.append((start_frame, cur_frame))
        return found_chyrons


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", action="store", default="5000", help="set port to listen" )
    parser.add_argument("--production", action="store_true", help="run gunicorn server")
    # add more arguments as needed
    # parser.add_argument(more_arg...)

    parsed_args = parser.parse_args()

    # create the app instance
    app = ChyronDetection()

    http_app = Restifier(app, port=int(parsed_args.port))
    # for running the application in production mode
    if parsed_args.production:
        http_app.serve_production()
    # development mode
    else:
        app.logger.setLevel(logging.DEBUG)
        http_app.run()

    