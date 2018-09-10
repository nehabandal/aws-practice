import csv
import smtplib
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from cryptography.fernet import Fernet
import datetime


class ScalePublish:

    def send_log_file(self, encrypt_key):
        '''
        Method for sending log file report
        '''

        fromaddr = "nbandal@tibco.com"
        toaddr = "slande@tibco.com, nbandal@tibco.com"

        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr

        try:
            filename = "scale_down_success_%s_%s_%s.html" % (tenant_name, region_name, datetime.datetime.today().date())
            attachment = open(filename, "rb")
        except FileNotFoundError:
            filename = "scale_down_failed_%s_%s_%s.html" % (tenant_name, region_name, datetime.datetime.today().date())
            attachment = open(filename, "rb")

        if filename == "scale_down_success_%s_%s_%s.html" % (
        tenant_name, region_name, datetime.datetime.today().date()):
            msg['Subject'] = "Scale down report for %s tenant and %s region:SUCCESS" % (tenant_name, region_name)
        else:
            msg['Subject'] = "Scale down report for %s tenant and %s region:FAILED" % (tenant_name, region_name)

        body = "Hi,\nPlease find attached html file for scale down process performed on " + str(
            datetime.datetime.today().date()) + "\n\n\n\nThanks, \nTibco Team"

        msg.attach(MIMEText(body, 'plain'))

        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(part)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(fromaddr, bytes(encrypt_key).decode("utf-8"))
        text = msg.as_string()
        server.sendmail(fromaddr, ["slande@tibco.com", "nbandal@tibco.com"], text)
        server.quit()

    def pwd_encrypt(self):
        key = b'4uBSLmry1VHk_Wp387ROK63IoqbVxbxQhBuhqwwJXgY='
        cipher_suite = Fernet(key)
        with open('pwd.bin', 'rb') as file_object:
            for line in file_object:
                encryptedpwd = line
        uncipher_text = (cipher_suite.decrypt(encryptedpwd))
        return uncipher_text


if __name__ == "__main__":
    region_name = sys.argv[1]
    tenant_name = sys.argv[2]
    scale_publish = ScalePublish()

    uncipher_text = scale_publish.pwd_encrypt()
    scale_publish.send_log_file(uncipher_text)
