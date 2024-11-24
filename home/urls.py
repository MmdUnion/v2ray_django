from django.urls import path
from django.conf import settings
from . import views

app_name = "home"


urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("subscription/<uuid:config_key>", views.SubscriptionView.as_view(), name="subscription"),
    path("view/<uuid:config_key>", views.SeeConfigView.as_view(), name="see_config"),
    path(settings.USER_LOGIN_URL, views.LoginView.as_view(), name="login_view"),
    path("account/panel/main/", views.PanelView.as_view(), name="panel_view"),
    path("send-ticket/", views.TicketView.as_view(), name="ticket_view"),
    path("send-seen-ticket/", views.TicketSeenView.as_view(), name="ticket_seen_view"),
]