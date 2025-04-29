from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase
from coinapp.models import Block
User = get_user_model()
BASE_URL = "/api/v1/"

print_json = lambda r: print(r.json())

class VerifyUserTest(APITestCase):
    fixtures = [
        "datas.json",
    ]
    def setUp(self):
        self.user_sulaiman = User.objects.get(username="KKDE003")
        
    def test_create_and_verify_user(self):
        # new user registration
        response = self.client.post(
            f"{BASE_URL}registration/",
            {
                "first_name":"sufail","password": "dummypassword",'phone': 'dummyphone',
                "government_id":"", "date_of_birth":"1991-12-21","exchange":"1",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_sufail = User.objects.get(username="KKDE005") 
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
        response = self.client.post(f"{BASE_URL}login/",{"username": "KKDE005", "password": "dummypassword"})
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
        response = self.client.post(f"{BASE_URL}login/",{"username": "KKDE005", "password": "dummypassword"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['username'], "KKDE005")

class TransactionTest(APITestCase):
    fixtures = [
        "datas.json",
    ]
    def setUp(self):
        self.user_nusra = User.objects.get(username="KKDE002")
        self.user_sulaiman = User.objects.get(username="KKDE003")
        
    def test_login_and_make_transaction(self):
        # login as sulaiman and make a seller transaction of 10$ -> nusra
        response = self.client.post(
            f"{BASE_URL}login/",
            {"username": "KKDE003", "password": "sumee1910"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], "KKDE003")
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
        print('test_peer_to_peer',Block.objects.all().first().data)
        # check sulaiman has 10$ balance
        response = self.client.get(
            f"{BASE_URL}ajax/?purpose=userbalance", headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual(response.json()['data'], -10)

        # login as nusra. check she has -10$ balance
        response = self.client.post(
            f"{BASE_URL}login/",
            {"username": "KKDE002", "password": "sumee1910"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], "KKDE002")
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
            {"username": "KKDE003", "password": "sumee1910"},
            format="json",
        )
        token = response.json()["key"]
        response = self.client.post(
            f"{BASE_URL}transactions/",
            {
                "user": User.objects.get(username="PIXL001").id,
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
            {"username": "KKDE003", "password": "sumee1910"},
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
            {"username": "KKDE002", "password": "sumee1910"},
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
    fixtures = [
        "datas.json",
    ]
    def test_create_user_and_login(self):
        # create a new user
        response = self.client.post(
            f"{BASE_URL}registration/",
            {"password": "mypass1234","phone":"9000000000","government_id":"123456","date_of_birth":"1988-12-04","exchange":"1"},
        )
        # print_json(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for item in [
            {'password':'wrongpassword','response':{'non_field_errors': ['Unable to log in with provided credentials.']}}, # wrong password
            {'password':'mypass1234','response':{'is_active': False, 'message': 'Verification is pending.'}}, # correct password, but user is inactive
        ]:
            response = self.client.post(
                f"{BASE_URL}login/",
                {"username": "KKDE005", "password": item['password']},
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json(), item['response'])
        



class UserDetailsTest(APITestCase):
    fixtures = [
        "datas.json",
    ]
    def test_user_details(self):
        # login and check userdetails api
        response = self.client.post(
            f"{BASE_URL}login/",
            {"username": "KKDE002", "password": "sumee1910"},
        )
        
        token = response.json()["key"]
        response = self.client.get(
            f'{BASE_URL}user/{User.objects.get(username="KKDE002").id}/',
            headers={"Authorization": f"Token {token}"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

