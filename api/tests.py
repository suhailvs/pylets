from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase

from coinapp.models import Listing
from rest_framework.authtoken.models import Token

User = get_user_model()
BASE_URL = "/api/v1/"

print_json = lambda r: print(r.json())

class VerifyUserTest(APITestCase):
    fixtures = [
        "datas.json",
    ]
    def setUp(self):
        self.user_sulaiman = User.objects.get(username="KKDE003")
        self.users = {
            "KKDE001":Token.objects.get_or_create(user_id=1)[0], # same exchange
            "PIXL001":Token.objects.get_or_create(user_id=4)[0], # diferent exchange
        }
    def verify_sufail(self, token,trust_score):
        user_sufail = User.objects.get(username="KKDE005") 
        response = self.client.post(f"{BASE_URL}verifyuser/",{"candidate_id": user_sufail.id, "trust_score":trust_score},
            headers={"Authorization": f"Token {token}"},
        )
        if token == self.users['PIXL001']: # if sabareesh
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        else:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

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
        
        # using suhail's token, verify newuser(sufail) with low trust_score
        response = self.verify_sufail(self.users['KKDE001'],0.3)
        # sufail verification failed since low trust_score
        user_sufail.refresh_from_db()
        self.assertEqual(user_sufail.is_active, False)

        # try to login sufail(not verified)
        response = self.client.post(f"{BASE_URL}login/",{"username": "KKDE005", "password": "dummypassword"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['is_active'], False)
        self.assertEqual(response.json()['message'], 'Verification is pending.')

        # using sabareesh's token, verify newuser(sufail) with high trust_score
        response = self.verify_sufail(self.users['PIXL001'],0.9)
        # sufail verification failed since sabareesh's exchange is different from sufail's
        user_sufail.refresh_from_db()
        self.assertEqual(user_sufail.is_active, False)

        # verify sufail with high trust_score
        response = self.verify_sufail(self.users['KKDE001'],0.9)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_sufail.refresh_from_db()
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
        
class ListingTest(APITestCase):
    fixtures = [
        "datas.json",
    ]
    def setUp(self):
        self.listing_id = 1
        self.url = f"{BASE_URL}listings/{self.listing_id}/" 
        self.listing_exists = lambda: Listing.objects.filter(id=self.listing_id).exists()
        self.users = {
            "KKDE001":Token.objects.get_or_create(user_id=1)[0],
            "KKDE002":Token.objects.get_or_create(user_id=2)[0],
        }
    
    def test_view_listing(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.users["KKDE002"].key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_delete(self):
        self.assertTrue(self.listing_exists())
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.users["KKDE001"].key)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.listing_exists())

    def test_other_user_cannot_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.users["KKDE002"].key)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(self.listing_exists())


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
        

