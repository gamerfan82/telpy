import requests

import requests
username = 'gamerfan82'
token = 'df0617391acfbb4d0f3ef9130487d8c7b4d7b23e'
#/api/v0/user/{username}/consoles/{id}/get_latest_output/
response = requests.post(
    'https://www.pythonanywhere.com/api/v0/user/{username}/consoles/{id}/send_input/'.format(
        username=username,
        id="39795363"
    ),
    headers={'Authorization': 'Token {token}'.format(token=token)},
    json={"input": "python3.11 .pythonstartup.py\n"}
)
#pip install -r requirements.txt
if response.status_code == 200:
    print("Command sent successfully. : "+ response.text)
else:
    print(f"Error {response.status_code}: {response.text}")
