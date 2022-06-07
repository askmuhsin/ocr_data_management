import imp
from paddleocr import PaddleOCR, draw_ocr
import matplotlib.pyplot as plt
from PIL import Image, ImageFont
import numpy as np
import cv2
import os

class PaddleOCRModel:
    def __init__(self):
        self.lang = 'en'
        self.init_ocr_model()
        self.font_path = './app/models/fonts/simfang.ttf'
        
        self.post_process = True
        self.inspect_output = True
        
        self.debug = True
        self.stich_text_sep = ' '

        print(os.listdir())
    
    def init_ocr_model(self):
        self.ocr = PaddleOCR(
            use_angle_cls=True, 
            lang=self.lang
        )

    def predict(self, image: np.ndarray):
        self.result = self.ocr.ocr(image, cls=True)
        self.processed_output = self._post_process() if self.post_process else {}
        self.pred_annotated_img = self._inspect_output(
            image, self.result
        ) if self.inspect_output else image
        
        if self.debug and self.post_process and self.inspect_output:
            print(self.processed_output['result'], end='\n\n')
            print(self.processed_output['stitched_text'])
            plt.figure(figsize=(20, 10))
            plt.imshow(self.pred_annotated_img)
    
    def _post_process(self):
        stitched_text = ""
        for bbox, (text, conf) in self.result:
            stitched_text += (text + self.stich_text_sep)
        
        processed_output = {
            'stitched_text': stitched_text,
            'result': self.result
        }
        return processed_output
    
    def _inspect_output(self, image: np.ndarray, result: dict):
        boxes = [line[0] for line in result]
        txts = [line[1][0] for line in result]
        scores = [line[1][1] for line in result]

        pred_annotated_img = draw_ocr(image, boxes, txts, scores, font_path=self.font_path)
        return pred_annotated_img
