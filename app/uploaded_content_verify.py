from aip import AipImageCensor
from flask import current_app
import os

class ContentVerify:
    def __init__(self):
        self.client = AipImageCensor(
                current_app.config['APP_ID'],
                current_app.config['API_KEY'],
                current_app.config['SECRET_KEY']
            )

    def verify_uploaded_images(self, img):
        filename = img.filename
        _, suffix = os.path.splitext(filename)
        if not suffix == '.gif':
            result = self.client.imageCensorUserDefined(img.read())
        else:
            result = self.client.antiPornGif(img.read())

        msg = self.extract_msg(result, suffix)
        ok_or_not = self.is_ok(msg, suffix)
        return msg, ok_or_not
# TODO 修改上传错误的msg

    def extract_msg(self, result, suffix):
        if "error_msg" in result:
            return [result['error_msg']]

        if not suffix == '.gif':
            if 'data' not in result.keys():
                return [""]
            data = result['data']
            msg = [d["msg"] for d in data]
            return msg
        else:
            data = result['result']
            msg = [d["class_name"] for d in data]
            return msg

    def is_ok(self, msg, suffix):
            if not suffix == ".gif":
                return ("存在色情内容" not in msg) and ("存在政治敏感内容" not in msg)
            else:
                return "色情" not in msg