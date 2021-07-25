task = '''
Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
'''

import requests
import urllib
import json

if __name__ == '__main__':
    print(task)

    # https://github.com/public-apis/public-apis
    #
    # # pastebin
    # api_key = ''
    # username = ''
    # password = ''
    #
    # url = 'https://pastebin.com/api/api_login.php'
    # data = {'api_dev_key':api_key, 'api_user_name': username, 'api_user_password': password}
    # req = requests.post(url, data=urllib.parse.urlencode(data))
    # if req.status_code != 200:
    #     raise Exception(str(req.status_code) + ' ' + req.text + ' http error!')
    #
    # user_key = req.text
    #
    # url = 'https://pastebin.com/api/api_post.php'
    # data = 'api_option=list&api_user_key=' + user_key + '&api_dev_key=' + api_key + '&api_results_limit=100'
    # req = requests.post(url, data=data)
    # if req.status_code != 200:
    #     raise Exception(str(req.status_code) + ' http error!')
    #
    # with open('pastebin.list.xml', 'w') as f_out:
    #     f_out.write(req.text)

    # pastebin do not work - always Exception: 401 Bad API request http error!

    # IBM text to speech

    with open('ibm.text.to.speech.json', 'r') as f_out:
        credentials = json.loads(f_out.read())

    # curl -X POST -u "apikey:{apikey}" --header "Content-Type: application/json" --header "Accept: audio/wav" --data "{\"text\":\"hello world\"}" --output hello_world.wav "{url}/v1/synthesize"

    url = credentials['url'] + '/v1/synthesize'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'audio/wav',
        'Authorization': ''
    }
    data = {
        'text': 'hello world'
    }
    req = requests.post(url, headers=headers, data=json.dumps(data), auth=requests.auth.HTTPBasicAuth('apikey', credentials['apikey']))
    if req.status_code != 200:
        raise Exception(str(req.status_code) + ' ' + req.text + ' http error!')

    print(req.status_code)
    print(req.headers)
    with open('out.wav', 'wb') as f_out:
        f_out.write(req.content)
