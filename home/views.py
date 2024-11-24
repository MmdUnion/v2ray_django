import asyncio
import json

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View

from .forms import LoginForm
from .models import TicketModel, UserConfigModel
from .panel_management import (convert_size, IPS_MAP, jalali_time,
                               load_all_configs, search_config_by_uuid)


class HomeView(View):
    template_name = "home/home.html"
    def get(self, request):
        return render(request, self.template_name)



class LoginView(View):
    template_name = "home/login.html"
    form_class = LoginForm


    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home:panel_view")
        return super().dispatch(request, *args, **kwargs)


    def get(self, request):
        return render(request, self.template_name, {"form":self.form_class})

    def post(self, request):
        form_input = self.form_class(request.POST)

        if form_input.is_valid():
            cleaned_data = form_input.cleaned_data
            username, password = cleaned_data['username'], cleaned_data['password']
            auth_user = authenticate(request, username=username, password=password)
            if auth_user:
                login(request, auth_user)
                return redirect("home:panel_view")
            else:
                form_input.add_error("", "نام کاربری یا رمز عبور صحیح نیست!")
        return render(request, self.template_name, {"form":form_input})



class TicketView(LoginRequiredMixin, View):
    login_url = settings.USER_LOGIN_URL

    def post(self, request):
        get_text_message = request.POST.get("text_message")
        if get_text_message:
            if get_text_message and 1 <= len(get_text_message) <= 4096:
                new_ticket = TicketModel(message_text=get_text_message, for_user=request.user, admin_seen=False, send_by_admin=False, user_seen=True, send_telegram_alert=True)
                new_ticket.save()
                return JsonResponse({"success":True})

        return JsonResponse({"success":False})
        


class TicketSeenView(LoginRequiredMixin, View):
    login_url = settings.USER_LOGIN_URL

    def post(self, request):
        TicketModel.objects.filter(for_user=request.user).update(user_seen=True)
        return JsonResponse({"success":True})

        

class PanelView(LoginRequiredMixin, View):
    login_url = settings.USER_LOGIN_URL
    template_name = "home/panel.html"

    def get(self, request):
        get_configs = UserConfigModel.objects.filter(for_user=request.user)
        get_tickets = TicketModel.objects.filter(for_user=request.user)

        ticket_cleaned = self.sort_tickets(get_tickets)



        # get_user_configs
        result_configs = []
        loop = asyncio.new_event_loop()

        load_configs = loop.run_until_complete(load_all_configs())
        for any_config in load_configs:
            for list_configs in get_configs:
                if any_config['id'] == list_configs.config_id:
                    result_configs.append(any_config)


        sort_data = self.sort_and_prepare_data(result_configs, ticket_cleaned)

        return render(request, self.template_name, {"config_data":sort_data})





    def sort_tickets(self, ticket_data):
        result_data = []
        send_seen = False
        for any_item in ticket_data:
            send_admin = "u" # user
            if any_item.send_by_admin:
                send_admin = "a" # admin
            if not any_item.user_seen:
                send_seen = True

            result_data.append(f"{send_admin}:{any_item.message_text}")
        return [result_data, send_seen]





    def sort_and_prepare_data(self, list_configs, ticket_clean):
        result_dict = {}
        custom_dict = {}
        for any_item in list_configs:
            list_appended_user_config = []

            upload_download = any_item['up'] + any_item['down']
            total = any_item['total']


            if total <= 0:
                total = "نامحدود"
                remain_size = "نامحدود"
            else:
                remain_size = convert_size(total- upload_download)
                total = convert_size(total)

            get_time = float(any_item['expiryTime'])
            
            if get_time <= 0:
                get_time = "نامحدود"
            else:
                get_time = jalali_time(get_time/1000)




            try:
                port = any_item['port']
                status = any_item['enable']
                name = any_item['remark'].split("|")[0].strip()
                load_streem_settings = json.loads(any_item['streamSettings'])
                public_key = load_streem_settings['realitySettings']['settings']['publicKey']
                sni_key = load_streem_settings['realitySettings']['serverNames'][0]
                short_id = load_streem_settings['realitySettings']['shortIds'][0]
            except:
                return None

            try:
                get_uuid = json.loads(any_item['settings'])['clients'][0]['id']
            except:
                continue
            sub_link = f"https://{settings.DOMAIN}/subscription/{get_uuid}"
            for key,value in IPS_MAP.items():
                list_appended_user_config.append({"uuid":get_uuid, "name":name, "status":status, "size":total, "remain_size":remain_size, "remain_time":get_time, "special_name":f"{key}-{name}","id":any_item['id'], "sub_link":sub_link,"raw_config":f"vless://{get_uuid}@{value}:{port}?type=tcp&security=reality&fp=chrome&pbk={public_key}&sni={sni_key}&sid={short_id}&spx=%2F#{key}-{name}"})

            custom_dict[any_item['id']] = list_appended_user_config



        result_dict['configs'] = custom_dict
        result_dict['tickets'] = ticket_clean
        return result_dict


class SubscriptionView(View):
    async def get(self, *args, **kwargs):
        try:
            get_config_key = kwargs.get("config_key")
        except:
            get_config_key = None

        if get_config_key:
            get_config_response = await search_config_by_uuid(get_config_key)
            if get_config_response:
                return HttpResponse(get_config_response)
        raise Http404


class SeeConfigView(View):
    template_name = "home/view_config.html"

    async def get(self, *args, **kwargs):
        try:
            get_config_key = kwargs.get("config_key")
        except:
            get_config_key = None

        if get_config_key:
            get_config_response = await search_config_by_uuid(get_config_key, return_raw_data=True)
            if get_config_response:
                return render(*args, self.template_name, get_config_response)



        raise Http404
