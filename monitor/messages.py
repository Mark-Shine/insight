#encoding=utf-8
from django.core.mail import send_mass_mail
from django.core.mail import EmailMultiAlternatives  
from django.template import Context, loader  
from django.conf import settings

EMAIL_HOST_USER = settings.EMAIL_HOST_USER
def build_message(recipient_list=['szh1216@gmail.com'], 
        message='alarm', subject="inform", from_email="alarm@moni.com"):
    
    return (subject, message, from_email, recipient_list)


def do_sendmail(title=u"煎茶系统邮件", msg={}, email_template="mail.html", mail_list=['75103752@qq.com']):
    t = loader.get_template(email_template)  
    subject, from_email, to = title, EMAIL_HOST_USER, mail_list  
    html_content = t.render(Context(msg))
    msg = EmailMultiAlternatives(subject, html_content, from_email, to)  
    msg.attach_alternative(html_content, "text/html") 
    try:
        msg.send() 
        print "email success" 
    except Exception, e:
        print "emaill error"
        raise e
        

def do_sendsms():
    pass