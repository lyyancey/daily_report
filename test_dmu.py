import requests
from urllib.parse import quote
from urllib.parse import unquote
import smtplib
import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header
import json
import random
import yaml
import logging
import time

logging.basicConfig(filename="log.txt", level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Report():
    def __init__(self):
        pass

    def create_url(self, uuid_number, uuid_name, class_num, mor, aft, ni, trail, people):
        return 'https://www.dmuisatc.com/DMU_WEB/student_5/info/?jsonnumber={}&jsonname={}&jsonclass={}%E7%BA%A7%E7%A1%95%E5%A3%AB%E7%A0%94%E7%A9%B6%E7%94%9F%E4%B8%AD%E9%98%9F&morning={}%E2%84%83&afternoon={}%E2%84%83&night={}%E2%84%83&jsonbody=1&jsonbodychangeinfo=&textarea={}&textprople={}&jsontouch=1&jsontouchchangeinfo=0&jsonisolate=1&jsonisolatechangeinfo=0&latitude=38.86838&longitude=121.52678'.format(uuid_number, quote(uuid_name), class_num, mor, aft, ni, quote(trail), quote(people))

    def request_h(self, url):
        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "content-type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://servicewechat.com/wx8a86613d14cbe10c/12/page-frame.html",
            "Connection": "close",
            "Host": "www.dmuisatc.com:443"
        }
        try:
            r = requests.get(url, headers=headers)
        except Exception as e:
            logging.info("创建连接时发生错误：\n")
            logging.info(e)

        return r

class Mail():
    def __init__(self, config):
        self.mail_host = config["mail_host"]
        self.mail_pass = config["mail_pass"]
        self.sender = config["mail_account"]

    def send(self, receivers, status, user_info, is_inschool, pic_file_name):
        # 设置总的邮件体对象，类型为MIXED
        date = datetime.datetime.now()
        msg_root = MIMEMultipart('mixed')
        # 邮件添加的头尾信息等
        msg_root['From'] = '{}<{}>'.format(self.sender, self.sender)
        msg_root['To'] = receivers
        # 邮件的主题，显示在接收邮件的预览页面
        subject = '您的信息：{}\r\n是否在校：{}\r\n填报状态：{}\r\n'.format(user_info, is_inschool, status)
        msg_root['subject'] = Header(subject, 'utf-8')

        # 构造图片
        image_file = open(pic_file_name, 'rb').read()
        image = MIMEImage(image_file)
        image.add_header('Content-ID', '<image1>')
        # 如果不加下边这行代码的话，会在收件方方面显示乱码的bin文件，下载之后也不能正常打开
        image["Content-Disposition"] = 'attachment; filename="red_people.png"'
        msg_root.attach(image)
        try:
            sftp_obj = smtplib.SMTP(self.mail_host, 25)
            sftp_obj.login(self.sender, self.mail_pass)
            sftp_obj.sendmail(self.sender, receivers, msg_root.as_string())
            sftp_obj.quit()
            logging.info('sendemail successful!')
            return '邮件发送成功'
        except Exception as e:
            logging.info('sendemail failed next is the reason:')
            logging.info(e)
            logging.info('\n')
            return '邮件发送失败'

class DataLoder():
    def __init__(self, user_info_file, config_file) -> None:
        self.users_info = user_info_file
        self.config_file = config_file

    def get_user_info(self):
        json_list = []
        for line in open(self.users_info, 'r',encoding='utf-8'):
            json_obj = json.loads(line)
            json_list.append(json_obj)
        return json_list

    def get_config(self):
        with open(self.config_file, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            return data


if __name__ == '__main__':

    try:
        data_loader = DataLoder('user_info.json', 'my_config.yaml')
        user_infos = data_loader.get_user_info()
        mail_config = data_loader.get_config()
        # print(data_loader.get_config())
        # print(user_infos)
        report = Report()
        mail = Mail(mail_config)
        # logging.info(user_infos)
        requests.adapters.DEFAULT_RETRIES = 10
        for user_info in user_infos:
            # logging.info(user_info)
            url = report.create_url(user_info["uuid_number"], user_info["uuid_name"], user_info["class_num"], user_info["mor"], user_info["aft"], user_info["ni"], user_info["trail"], user_info["people"])
            res = report.request_h(url)
            s = requests.session()
            s.keep_alive = False
            logging.info("填报返回的信息为：")
            logging.info(res.text)
            logging.info('\n')
            if mail_config["send_email"] and user_info["is_send"]:
                res = json.loads(res.text)
                status = '填报失败'
                if res["status"] == '1':
                    status = '填报成功'
                is_inschool = '不在校'
                if res["inschool"] == '1':
                    is_inschool = '在校'
                file_name = './pic/{}.jpg'.format(str(random.randint(1, 31)))
                mail.send(user_info["email"], status, res["message"], is_inschool, file_name)
            time.sleep(10)
    except Exception as e:
        logging.info(e)
    logging.info('---------------------------------------------------------------------------------------')