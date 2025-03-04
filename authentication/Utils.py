from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_email_text(email, body):
    email_sender = EmailMessage(
        subject="join to our team",
        body=body,
        to=[
            email
        ]
    )
    email_sender.send()


def send_html_email(email, context):
    # قراءة محتوى HTML من ملف
    html_content = render_to_string('Untitled-1.html', context=context)
    # إنشاء رسالة بريد إلكتروني
    email = EmailMessage(
        subject="permit to work",
        body=html_content,
        to=[
            email
        ]
    )

    email.content_subtype = "html"
    # email.attach_alternative(html_content, "text/html")

    # إرسال البريد الإلكتروني
    email.send()


def send_email_without_file(*, html=False, **data):
    email = EmailMessage(**data)
    if html:
        email.content_subtype = "html"
    email.send()
