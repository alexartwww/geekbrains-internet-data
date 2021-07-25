task = '''
Посмотреть документацию к API GitHub, разобраться как вывести
список репозиториев для конкретного пользователя,
сохранить JSON-вывод в файле *.json.
'''

import requests
import json

if __name__ == '__main__':
    print(task)
    req = requests.get('https://api.github.com/users/alexartwww/repos')
    if req.status_code != 200:
        raise Exception(str(req.status_code) + ' http error!')

    reposData = json.loads(req.text)
    with open('alexartwww.repos.json', 'w') as f_out:
        f_out.write(json.dumps(reposData, indent=4))
