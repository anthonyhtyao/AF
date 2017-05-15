from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

def sendEmail(txt='',html='',data={},title='',to=[]):
    emailTxt = get_template(txt)
    emailHtml = get_template(html)
    d = Context(data)
    textContent = emailTxt.render(d)
    htmlContent = emailHtml.render(d)
    msg = EmailMultiAlternatives(title,textContent,'auroreformosane@gmail.com',to)
    msg.attach_alternative(htmlContent, "text/html")
    msg.send()
    return True

