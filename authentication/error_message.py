from django.core.mail import send_mail
from django.http import HttpResponseServerError
import traceback


class ErrorNotificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # إرسال إشعار بالبريد عند حدوث خطأ
        subject = 'Error Notification'
        message = f'An error occurred:\n\n{"".join(traceback.format_exception(type(exception), exception, exception.__traceback__))}'
        from_email = 'no-reply@yallasafety.com'
        to_email = ['om23440@gmail.com']
        send_mail(subject, message, from_email, to_email, fail_silently=False)
        # return super().
        return self.get_response
