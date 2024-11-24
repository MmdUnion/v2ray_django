import requests
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import TicketModel


def send_telegram_message(params):
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'
    try:
        requests.post(url, json=params)
    except Exception as err:
        print(err)


@receiver(post_save, sender=TicketModel)
def save_profile(sender, instance, **kwargs):
    if instance.send_telegram_alert:
        params = {'chat_id': settings.TELEGRAM_ADMIN_ID, 'text': f"""
🟡پیام جدید دریافت شد: 
کاربر: {instance.for_user.first_name}
نام کاربری: {instance.for_user.username} 
پیام: [{instance.message_text[:30]}]   
        """}

        send_telegram_message(params)


@receiver(user_login_failed)
def handle_user_login_failed(sender, credentials, request, **kwargs):
    ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')

    username = request.POST.get("username")
    params = {'chat_id': settings.TELEGRAM_ADMIN_ID, 'text': f"""
    ورود ناموفق❌
    نام کاربری: {username}
    آیپی: {ip}
    """}
    send_telegram_message(params)


@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
    params = {'chat_id': settings.TELEGRAM_ADMIN_ID, 'text': f"""
    ورود موفق✅
    نام کاربری: {user.username}
    آیپی: {ip}
    """}
    send_telegram_message(params)





