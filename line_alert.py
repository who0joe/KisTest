# -*- coding: utf-8 -*-

import requests


def SendMessage(msg):
    try:

        TARGET_URL = 'https://notify-api.line.me/api/notify'
        TOKEN = '3GcXAvBoJOnyZu6yO1fFieSfjqNiKE7UN1nAOKLq42T' 

        response = requests.post(
            TARGET_URL,
            headers={
                'Authorization': 'Bearer ' + TOKEN
            },
            data={
                'message': msg
            }
        )

    except Exception as ex:
        print(ex)



print("메세지")
SendMessage("가나다")