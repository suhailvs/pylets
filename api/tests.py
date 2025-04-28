from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()
BASE_URL = "/api/v1/"

print_json = lambda r: print(r.json())

class VerifyUserTest(APITestCase):
    fixtures = [
        "datas.json",
    ]
    def setUp(self):
        self.user_sulaiman = User.objects.get(username="8547622462")
        
    def test_create_and_verify_user(self):
        # new user registration
        response = self.client.post(
            f"{BASE_URL}registration/",
            {
                "first_name":"sufail","username": "6238287359", "password": "sumee1910",
                "government_id":"", "date_of_birth":"1991-12-21","exchange":"1",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_sufail = User.objects.get(username="6238287359")
        # login as sulaiman and verify sufail without trust_score
        response = self.client.post(
            f"{BASE_URL}login/",
            {"username": self.user_sulaiman.username, "password": "sumee1910"},
        )
        token = response.json()["key"]
        response = self.client.post(f"{BASE_URL}verifyuser/",{"candidate_id": user_sufail.id},
            headers={"Authorization": f"Token {token}"},
        )

        user_sufail.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_sufail.is_active, False)
        # try to login sufail(not verified)
        response = self.client.post(f"{BASE_URL}login/",{"username": "6238287359", "password": "sumee1910"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['is_active'], False)
        self.assertEqual(response.json()['message'], 'Verification is pending.')

        # verify sufail with high trust_score
        response = self.client.post(f"{BASE_URL}verifyuser/",{"candidate_id": user_sufail.id, "trust_score":"0.8"},
            headers={"Authorization": f"Token {token}"},
        )
        user_sufail.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_sufail.is_active, True)

        # try to login sufail(verified)
        response = self.client.post(f"{BASE_URL}login/",{"username": "6238287359", "password": "sumee1910"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['username'], "6238287359")

class TransactionTest(APITestCase):
    fixtures = [
        "datas.json",
    ]
    def setUp(self):
        self.user_nusra = User.objects.get(username="8921513696")
        self.user_sulaiman = User.objects.get(username="8547622462")
        
    def test_login_and_make_transaction(self):
        # login as sulaiman and make a seller transaction of 10$ -> nusra
        response = self.client.post(
            f"{BASE_URL}login/",
            {"username": "8547622462", "password": "sumee1910"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], "8547622462")
        token = response.json()["key"]
        response = self.client.post(
            f"{BASE_URL}transactions/",
            {
                "user": self.user_nusra.id,
                "amount": 10,
                "message": "caring",
            },
            headers={"Authorization": f"Token {token}"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check sulaiman has 10$ balance
        response = self.client.get(
            f"{BASE_URL}ajax/?purpose=userbalance", headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual(response.json()['data'], -10)

        # login as nusra. check she has -10$ balance
        response = self.client.post(
            f"{BASE_URL}login/",
            {"username": "8921513696", "password": "sumee1910"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], "8921513696")
        response = self.client.get(
            f"{BASE_URL}ajax/?purpose=userbalance",
            headers={"Authorization": f"Token {response.json()['key']}"},
        )
        self.assertEqual(response.json()['data'], 10)
    

    def test_buyer_transaction(self):
        # test buyer transaction
        # check sulaiman has -13$ balance
        pass
    
    def test_send_transactions_only_to_own_exchange(self):
        # sulaiman is kolakkode exchange user, 
        # so must not able to send to sabareesh
        response = self.client.post(
            f"{BASE_URL}login/",
            {"username": "8547622462", "password": "sumee1910"},
            format="json",
        )
        token = response.json()["key"]
        response = self.client.post(
            f"{BASE_URL}transactions/",
            {
                "user": User.objects.get(username="8848338141").id,
                "amount": '101',
                "message": "sending amount of 101 to sabreesh must return error",
            },
            headers={"Authorization": f"Token {token}"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_max_balance(self):
        self.user_nusra.balance=settings.MAXIMUM_BALANCE-100
        self.user_nusra.save()

        # nusra has 900$, so nusra can only recieve max 100$
        # sending amount of 101 to nusra must return error
        response = self.client.post(
            f"{BASE_URL}login/",
            {"username": "8547622462", "password": "sumee1910"},
            format="json",
        )
        token = response.json()["key"]
        response = self.client.post(
            f"{BASE_URL}transactions/",
            {
                "user": self.user_nusra.id,
                "amount": '101',
                "message": "sending amount of 101 to nusra must return error",
            },
            headers={"Authorization": f"Token {token}"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_min_balance(self):
        # nusra has -990$, so nusra can only send max 10$
        self.user_nusra.balance=settings.MINIMUM_BALANCE+10
        self.user_nusra.save()

        # send 11$ to sulaiman
        response = self.client.post(
            f"{BASE_URL}login/",
            {"username": "8921513696", "password": "sumee1910"},
            format="json",
        )
        token = response.json()["key"]
        response = self.client.post(
            f"{BASE_URL}transactions/",
            {
                "user": self.user_sulaiman.id,
                "amount": 11,
                "message": "send 11$ to sulaiman must return error",
            },
            headers={"Authorization": f"Token {token}"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RegistrationTest(APITestCase):

    def test_create_user_and_login(self):
        # create a new user
        response = self.client.post(
            f"{BASE_URL}registration/",
            {"username": "1234567890", "password": "mypass1234","government_id":"123456","date_of_birth":"1988-12-04"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # wrong password in login
        response = self.client.post(
            f"{BASE_URL}login/",
            {"username": "1234567890", "password": "mypass1235"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


        # inactive username in login
        response = self.client.post(
            f"{BASE_URL}login/",
            {"username": "1234567890", "password": "mypass1234"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['message'], 'Verification is pending.')
   



class RegistrationTest(APITestCase):
    fixtures = [
        "datas.json",
    ]
    def test_user_details(self):
        # login and check userdetails api
        response = self.client.post(
            f"{BASE_URL}login/",
            {"username": "8921513696", "password": "sumee1910"},
        )
        
        token = response.json()["key"]
        response = self.client.get(
            f"{BASE_URL}user/{User.objects.get(username="8921513696").id}/",
            headers={"Authorization": f"Token {token}"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

