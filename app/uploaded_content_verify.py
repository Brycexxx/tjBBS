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
        if isinstance(img, str):
            _, suffix = os.path.splitext(img)
            if not suffix == '.gif':
                result = self.client.imageCensorUserDefined(img)
            else:
                result = self.client.antiPornGif(img)
        else:
            filename = img.filename
            _, suffix = os.path.splitext(filename)
            if not suffix == '.gif':
                result = self.client.imageCensorUserDefined(img.read())
            else:
                result = self.client.antiPornGif(img.read())

        msg = self.extract_msg(result, suffix)
        ok_or_not = self.is_ok(msg, suffix)
        return msg, ok_or_not


    def verify_uploaded_avatar(self, avatar):
        filename = avatar.filename
        _, suffix = os.path.splitext(filename)
        result = self.client.faceAudit(avatar.read())
        msg = result['result'][0]['data']['antiporn']
        if "conclusion" in msg:
            if not msg['conclusion'] == "色情":
                return '', True
            else:
                return msg['conclusion'] + "，上传失败！", False
        else:
            return '审核失败，请重试！', False


    def verify_text(self, text):
        result = self.client.antiSpam(text)
        spam_code = result['result']['spam']
        if spam_code == 0:
            return '', True
        elif spam_code == 1:
            return "涉及敏感词，审核未通过，提交失败！", spam_code, False
        else:
            return "待审核，您将在12小时内收到审核结果", spam_code, False



    def extract_msg(self, result, suffix):
        if "error_msg" in result:
            return [{"error_msg": result['error_msg']}]

        if not suffix == '.gif':
            if 'data' not in result.keys():
                return [""]
            data = result['data']
            msg = [d["msg"] for d in data]
            return msg
        else:
            data = result['conclusion']
            msg = [data]
            return msg

    def is_ok(self, msg, suffix):
        if isinstance(msg[0], dict):
            return False
        if not suffix == ".gif":
            return ("存在色情内容" not in msg) and ("存在政治敏感内容" not in msg)
        else:
            return "色情" not in msg
