import argparse
from typing import Union

# CLAMS Imports
from clams import ClamsApp, Restifier
from mmif import Mmif, View, Annotation, Document, AnnotationTypes, DocumentTypes

# App Imports
import PIL
import math
import uuid 
import cv2 
import utils 
import pytesseract

#=============================================================================|
class Chyronrecognition(ClamsApp):

    def __init__(self):
        super().__init__()

    def _appmetadata(self):
        # see metadata.py 
        pass

    def _annotate(self, mmif: Union[str, dict, Mmif], **parameters) -> Mmif:
        # see https://sdk.clams.ai/autodoc/clams.app.html#clams.app.ClamsApp._annotate
        if not isinstance(mmif, Mmif):
            mmif = Mmif(mmif) 
        
        video_filename = mmif.get_document_location(DocumentTypes.VideoDocument)
        config = self.get_configuration(**parameters)
        unit = config["timeUnit"]
        new_view = mmif.new_view()
        self.sign_view(new_view, config)
        new_view.new_contain(
            AnnotationTypes.TimeFrame,
            timeUnit=unit,
            document=mmif.get_documents_by_type(DocumentTypes.VideoDocument)[0].id 
        )
        new_view.new_contain(DocumentTypes.TextDocument)
        new_view.new_contain(AnnotationTypes.Alignment)

        chyron_results = self.run_chyrondetection(video_filename, **parameters)
        for chyron_result in chyron_results:
            timeframe_annotation = new_view.new_annotation(AnnotationTypes.TimeFrame)
            timeframe_annotation.add_property("start", chyron_result["start_frame"])
            timeframe_annotation.add_property("end", chyron_result["end_frame"])
            timeframe_annotation.add_property("frameType", "chyron")

            text_document = new_view.new_textdocument(chyron_result["text"])

            align_annotation = new_view.new_annotation(AnnotationTypes.Alignment)
            align_annotation.add_property("source", timeframe_annotation.id)
            align_annotation.add_property("target", text_document.id)
        return mmif 

    @staticmethod
    def process_chyron(start_seconds, end_seconds, start_frame, end_frame, frame_list, chyron_box):
        #frames = [frame_list[0], frame_list[math.floor(len(frame_list) /2)], frame_list[-1]]
        texts = []
        for _id, frame in enumerate(frame_list):
            bottom_third = frame[math.floor(0.6 * frame.shape[0]):,:]
            img = utils.preprocess(bottom_third)
            img = PIL.Image.fromarray(img)
            if chyron_box:
                img = img[chyron_box[1]:chyron_box[3],chyron_box[0]:chyron_box[2]]
            #img.save(f"sample_images{guid}_{_id}.png")
            text = pytesseract.image_to_string(
                img, 
                config="-c tessedit_char_whitelist='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.\n'"
            )
            texts.append(text)
        text = max(texts,key=len)
        return {
            "start_seconds":start_seconds,
            "end_seconds": end_seconds,
            "start_frame": start_frame,
            "end_frame": end_frame,
            "chyron_box": chyron_box,
            "text":text
        }
    
    @staticmethod
    def frame_has_chyron(frame, threshold):
        return utils.get_chyron(frame, threshold)
    
    @staticmethod
    def filter_boxes(box_list, frame_height):
        if not box_list:
            return None
        bottom_third_boxes = [box for box in box_list if box[1] > (math.floor(.4 * frame_height))]
        return max(bottom_third_boxes, key=lambda x: (x[3]-x[1]) *(x[2]-x[0]), default=None)
    
    def run_chyrondetection(
            self, video_filename, **kwargs
    ):
        sample_ratio = int(kwargs.get("sampleRatio", 10))
        min_duration = int(kwargs.get("minFrameCount", 10))
        threshold = 0.5 if "threshold" not in kwargs else float(kwargs["threshold"])

        cap = cv2.VideoCapture(video_filename)
        counter = 0
        chyrons = []
        in_chyron = False
        start_frame = None
        start_seconds = None 
        frame_list = []
        chyron_box = None 
        while True:
            ret, frame = cap.read()
            if not ret:
                break 
            if counter > 30 * 60 * 60 * 5:
                if in_chyron:
                    frame_list.append(frame)
                    if counter - start_frame > min_duration:
                        chyrons.append(
                            self.process_chyron(
                            start_seconds = start_seconds,
                            end_seconds   = cap.get(cv2.CAP_PROP_POS_MSEC),
                            start_frame   = start_frame,
                            end_frame     = counter,
                            frame_list    = frame_list,
                            chyron_box    = chyron_box
                            )
                        )
                        frame_list = []
                break 

            if counter % sample_ratio == 0:
                result = self.frame_has_chyron(frame, threshold=threshold)
                chyron_box = self.filter_boxes(result, frame.shape[0])
                if chyron_box:
                    frame_list.append(frame)
                    if not in_chyron:
                        in_chyron = True
                        start_frame = counter
                        start_seconds = cap.get(cv2.CAP_PROP_POS_MSEC)
                else:
                    if in_chyron:
                        in_chyron = False
                        if counter - start_frame > min_duration:
                            chyrons.append(
                                self.process_chyron(
                                    start_seconds = start_seconds,
                                    end_seconds   = cap.get(cv2.CAP_PROP_POS_MSEC),
                                    start_frame   = start_frame,
                                    end_frame     = counter,
                                    frame_list    = frame_list,
                                    chyron_box    = chyron_box
                                )
                            )
                            frame_list = []
            counter += 1
        return chyrons
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port", action="store", default="5000", help="set port to listen"
    )
    parser.add_argument("--production", action="store_true", help="run gunicorn server")
    # more arguments as needed
    # parser.add_argument(more_arg...)

    parsed_args = parser.parse_args()

    # create the app instance
    app = Chyronrecognition()

    http_app = Restifier(app, port=int(parsed_args.port)
    )
    if parsed_args.production:
        http_app.serve_production()
    else:
        http_app.run()
