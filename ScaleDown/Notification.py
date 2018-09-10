import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from cryptography.fernet import Fernet


class Deploy:
    def send_log_file(self, encrypt_key):

        gmail_user = 'nbandal@tibco.com'
        toaddr = "slande@tibco.com, nbandal@tibco.com"
        gmail_password = bytes(encrypt_key).decode("utf-8")

        msg = MIMEMultipart()

        msg['From'] = gmail_user
        msg['To'] = toaddr
        temp = sys.argv[1]
        process_name = ""
        if temp == "Down":
            process_name = "Scale Down"
        elif temp == "Up":
            process_name = "Scale Up"

        msg['Subject'] = "%s Process Started" % process_name

        body = "%s Process Started" % temp
        # print(body)

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_password)
            text = msg.as_string()
            server.sendmail(gmail_user, ["slande@tibco.com", "nbandal@tibco.com"], text)
            server.close()

            print('Email sent!')
        except:
            print('Something went wrong...')

    def pwd_encrypt(self):
        key = b'4uBSLmry1VHk_Wp387ROK63IoqbVxbxQhBuhqwwJXgY='
        cipher_suite = Fernet(key)
        with open('pwd.bin', 'rb') as file_object:
            for line in file_object:
                encryptedpwd = line
        uncipher_text = (cipher_suite.decrypt(encryptedpwd))
        return uncipher_text


if __name__ == "__main__":
    d = Deploy()
    uncipher_text = d.pwd_encrypt()
    d.send_log_file(uncipher_text)
