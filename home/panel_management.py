
import base64
import datetime
import json
import math

import aiohttp
import jdatetime
import pytz

from django.conf import settings



ZONE = pytz.timezone("Asia/Tehran")
HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36", "Cookie":settings.PANEL_COOKIES}
IPS_MAP = {"MTN": settings.DOMAIN, "MCI":settings.DOMAIN}
IP_DOM = IPS_MAP['MTN']



async def load_all_configs():
    json_data = {"obj":[]}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{settings.PANEL_DOMAIN}/inbound/list", headers=HEADERS) as response:
                json_data = await response.json()
    except:
        pass
    return json_data['obj']





async def search_config_by_uuid(config_key, return_raw_data=False):
    get_response = await load_all_configs()
    config_found = None
    for any_config in get_response:
        try:
            get_uuid = json.loads(any_config['settings'])['clients'][0]['id']
        except:
            continue
        if str(get_uuid) == str(config_key):
            config_found = any_config
            break

    if config_found:
        if config_found['protocol'] == "vless":
            try:
                load_streem_settings = json.loads(config_found['streamSettings'])
                get_transmition = load_streem_settings['security']
                public_key = load_streem_settings['realitySettings']['settings']['publicKey']
                sni_key = load_streem_settings['realitySettings']['serverNames'][0]
                short_id = load_streem_settings['realitySettings']['shortIds'][0]
            except:
                return None
            if get_transmition == "reality":
                get_size = float(config_found['total'])
                usage_size = float(config_found['up']) + float(config_found['down'])
                get_time = float(config_found['expiryTime'])

                if get_size == 0:
                    new_name_size = "نامحدود"
                else:
                    new_name_size = convert_size(get_size-usage_size)

                if get_time == 0:
                    new_name_time = "نامحدود"
                else:
                    get_current_time = datetime.datetime.now(ZONE).timestamp()

                    minues_time = get_time - (get_current_time*1000)

                    if minues_time > 0:
                        new_name_time = str(int(minues_time / 86400000))
                    else:
                        new_name_time = "0"

                    new_name_time += " day"
                    
                config_name = config_found['remark']

                split_name = config_name.split("|")
                if split_name and len(split_name) == 2:
                    config_base_name = split_name[0].strip()
                else:
                    config_base_name = "NewConfig"

                if return_raw_data:
                    if get_time == 0:
                        get_time_text = "نامحدود"
                    else:
                        get_time_text = jalali_time(get_time / 1000)
                    return {"remain_size":new_name_size, "total_size": convert_size(get_size), "total_time": get_time_text, "remain_time":new_name_time, "name":config_base_name}

                string_config = ""
                for key,value in IPS_MAP.items():
                    name = f"{key}-{config_base_name} | {new_name_size}_{new_name_time}"
                    string_config += f"vless://{str(config_key)}@{value}:{config_found['port']}?type=tcp&security=reality&fp=chrome&pbk={public_key}&sni={sni_key}&sid={short_id}&spx=%2F#{name}\n"


            
                return base64.b64encode(string_config.encode("utf-8")).decode("utf-8")









        elif config_found['protocol'] == "vmess":
            get_size = float(config_found['total'])
            usage_size = float(config_found['up']) + float(config_found['down'])
            get_time = float(config_found['expiryTime'])


            if get_size == 0:
                new_name_size = "نامحدود"
            else:
                new_name_size = convert_size(get_size-usage_size)

            if get_time == 0:
                new_name_time = "نامحدود"
            else:
                get_current_time = datetime.datetime.now(ZONE).timestamp()

                minues_time = get_time - (get_current_time*1000)

                if minues_time > 0:
                    new_name_time = str(int(minues_time / 86400000))
                else:
                    new_name_time = "0"

                new_name_time += " day"
                
            config_name = config_found['remark']

            split_name = config_name.split("|")
            if split_name and len(split_name) == 2:
                config_base_name = split_name[0].strip()
            else:
                config_base_name = "NewConfig"

            if return_raw_data:
                return {"remain_size":new_name_size, "total_size": convert_size(get_size), "total_time": jalali_time(get_time / 1000), "remain_time":new_name_time, "name":config_base_name}


            config_found['remark'] = f"{config_base_name} | {new_name_size}_{new_name_time}"

            create_raw_data = {'v': '2', 'ps': config_found['remark'], 'add': IP_DOM, 'port': config_found['port'], 'id': str(config_key), 'aid': 0, 'net': 'tcp', 'type': 'http', 'host': 'soft98.ir', 'path': '/', 'tls': 'none'}
            encode_data = base64.b64encode(json.dumps(create_raw_data).encode('utf-8')).decode("utf-8")
            return base64.b64encode(f"vmess://{encode_data}".encode('utf-8')).decode("utf-8")
    return None



def jalali_time(time_int):
    parse_time = jdatetime.datetime.fromtimestamp(time_int, ZONE)
    return parse_time.strftime("%H:%M:%S %Y/%m/%d")
    

    
def convert_size(size_bytes):
   if size_bytes <= 0:
       return "0 بایت"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)

   return f"{s} {size_name[i]}"




