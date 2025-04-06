from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()
BASE_URL = "/api/v1/"


class TransactionTest(APITestCase):
    fixtures = [
        "sample.json",
    ]

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
                "user": User.objects.get(username="8921513696").id,
                "amount": 10,
                "message": "caring",
            },
            headers={"Authorization": f"Token {token}"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check sulaiman has 10$ balance
        response = self.client.get(
            f"{BASE_URL}user/balance/", headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual(response.json(), -10)

        # login as nusra. check she has -10$ balance
        response = self.client.post(
            f"{BASE_URL}login/",
            {"username": "8921513696", "password": "sumee1910"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], "8921513696")
        response = self.client.get(
            f"{BASE_URL}user/balance/",
            headers={"Authorization": f"Token {response.json()['key']}"},
        )
        self.assertEqual(response.json(), 10)
    

    def test_buyer_transaction(self):
        # test buyer transaction
        # check sulaiman has -13$ balance
        pass
    

class TransactionMaxMinTest(APITestCase):
    fixtures = [
        "sample.json",
    ]
    def setUp(self):
        self.user_nusra = User.objects.get(username="8921513696")
        # add lots of balance to user_sulaiman        
        user_sulaiman = User.objects.get(username="8921513696")
        user_sulaiman.balance= settings.MAXIMUM_BALANCE+1
        user_sulaiman.save()
        
    def test_max_balance(self):
        # send an amount of maximum_amt+1 to nusra
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
                "amount": settings.MAXIMUM_BALANCE+1,
                "message": "caring",
            },
            headers={"Authorization": f"Token {token}"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)



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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['message'], 'Verification is pending.')
   
