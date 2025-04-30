# need to run pip install pytest requests
import requests

BASE_URL = "http://localhost:8000/api/v1/"
class TestPeer2Peer:
    def test_login_and_make_transaction(self):
        response = requests.post(f"{BASE_URL}login/",json={"username": "KKDE003", "password": "sumee1910"})
        assert response.status_code == 200
        assert response.json()['username'] == "KKDE003"
        token = response.json()["key"]
        print(token)
        response = requests.post(f"{BASE_URL}transactions/",
            json={"user": "KKDE003", "password": "sumee1910"})