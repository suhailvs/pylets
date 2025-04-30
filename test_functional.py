import requests

BASE_URL = "http://localhost:8000/api/v1/"
class TestPeer2Peer:
    def test_login_and_txn(self):
        response = requests.post(f"{BASE_URL}login/",json={"username": "KKDE003", "password": "sumee1910"})
        assert response.status_code == 200
        assert response.json()['username'] == "KKDE003"
        token = response.json()["key"]
        print(token)
        # send nusra 10 rupees
        response = requests.post(f"{BASE_URL}transactions/",
            json={"user": "2", "amount": 10, "message":"{BASE_URL}"},
            headers={"Authorization": f"Token {token}"},)        
        assert response.status_code == 200

    
    