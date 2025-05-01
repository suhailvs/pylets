"""
for testing frontendapp you must change line 
`if settings.DEBUG:`->`if True:` in mysite/urls.py
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class CreateExchangeTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("signup_new")

    def test_createexchange(self):
        data = {"code":"KKED", "name":"Kolakkode Exchange", "address":"aa", "dummy_country_dropdown":"IN","country_city":"IN-KL",
            "phone": '7238233233',"password1": "dummypassword","password2":"dummypassword","email":"suhail@gmail.com", 
            "government_id":"123123","date_of_birth":"1988-12-04","tandc":True}
        response = self.client.post(self.url,data,follow=True)
        # check on dummy_country_dropdown dropdown, India is selected
        self.assertInHTML(
            '<option value="IN" selected="">India</option>', response.content.decode()
        )

        # check on country_city dropdown, Kerala is selected
        self.assertInHTML(
            '<option value="IN-KL" selected="">Kerala</option>', response.content.decode()
        )
        data['first_name']="Suhail"

        response = self.client.post(self.url,data,follow=True)
        # check user logged in
        self.assertInHTML(
            f'<a href="{reverse("frontendapp:user_detail", args=("KKED","1"))}"><strong>KKED001</strong> </a>', 
            response.content.decode()
        )


class TransactionTest(TestCase):
    fixtures = [
        "datas.json",
    ]

    def setUp(self):
        self.client = Client()
        self.url = reverse("frontendapp:home")
        self.nusra = User.objects.get(username="KKDE002")
        self.sulaiman = User.objects.get(username="KKDE003")

    def test_login_and_make_seller_transaction(self):
        response = self.client.get(self.url, follow=True)
        self.assertInHTML("<h2>Log in</h2>", response.content.decode())

        # login as sulaiman and make a seller transaction of 10$ -> nusra
        self.client.post(
            reverse("login"),
            {"username": self.sulaiman.username, "password": "sumee1910"},
            follow=True,
        )
        response = self.client.post(
            self.url,
            {
                "transaction_type": "seller",
                "to_user": self.nusra.id,
                "amount": 10,
                "description": "caring",
            },
        )

        response = self.client.get(self.url)
        # check sulaiman has 10$ balance
        self.assertInHTML(
            '<h3 class="text-muted">Balance: 10$</h3>', response.content.decode()
        )

        # login as nusra. check she has -10$ balance
        response = self.client.post(
            reverse("login"),
            {"username": self.nusra.username, "password": "sumee1910"},
            follow=True,
        )
        self.assertInHTML(
            '<h3 class="text-muted">Balance: -10$</h3>', response.content.decode()
        )

    def test_buyer_transaction(self):
        self.client.post(
            reverse("login"),
            {"username": self.sulaiman.username, "password": "sumee1910"},
            follow=True,
        )
        # test buyer transaction
        response = self.client.post(
            self.url,
            {
                "transaction_type": "buyer",
                "to_user": self.nusra.id,
                "amount": "13",
                "description": "purchased bread",
            },
        )

        response = self.client.get(self.url)
        # check sulaiman has -13$ balance
        self.assertInHTML(
            '<h3 class="text-muted">Balance: -13$</h3>', response.content.decode()
        )

    def test_max_transaction(self):
        # settings.MAXIMUM_BALANCE exceeded then 400
        pass


class ListingTest(TestCase):
    fixtures = [
        "datas.json",
    ]

    def setUp(self):
        self.client = Client()
        self.url = reverse(
            "frontendapp:user_detail", kwargs={"exchange": "KKDE", "user": 1}
        )

    def test_offerings_list(self):
        response = self.client.get(self.url)
        rice_offering = """        
            <a href="/listing/1/preview/" class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">Food_Drink</h5>
                <small class="text-body-secondary">Nov. 1, 2024</small>
                </div>
                <p class="mb-1">#1: rice</p>
                <small class="text-body-secondary">rate: 50$ per kg</small>
            </a>  
        """
        self.assertInHTML(rice_offering, response.content.decode())

    def test_offering_create(self):
        self.client.post(
            reverse("login"),
            {"username": "KKDE001", "password": "sumee1910"},
            follow=True,
        )
        response = self.client.get(self.url)
        self.assertInHTML("Add new offering", response.content.decode())
        # contains category
        self.assertInHTML(
            '<option value="Accommodation_Space">Accommodation and Space</option>',
            response.content.decode(),
        )
        # create a new offering
        response = self.client.post(
            self.url,
            {
                "action": "add",
                "listing_type": "O",
                "category": "Food_Drink",
                "title": "test heading",
                "description": "test detail",
                "rate": "test rate",
            },
            follow=True,
        )

        self.assertIn(
            "Listing activated: 2: test heading",
            str(list(response.context["messages"])[0]),
        )
        self.assertEqual(
            "O",
            response.context["userlistings"]
            .filter(title="test heading")
            .first()
            .listing_type,
        )
        response = self.client.get(self.url)
        self.assertInHTML("Add new offering", response.content.decode())
        self.assertIn("test heading", response.content.decode())

    def test_want_create(self):
        self.client.post(
            reverse("login"),
            {"username": "KKDE001", "password": "sumee1910"},
            follow=True,
        )
        response = self.client.get(self.url)
        self.assertInHTML("Add new want", response.content.decode())

        # create a new offering
        response = self.client.post(
            self.url,
            {
                "action": "add",
                "listing_type": "W",
                "category": "Food_Drink",
                "title": "test heading want",
                "description": "test detail",
            },
            follow=True,
        )
        self.assertIn(
            "Listing activated: 2: test heading want",
            str(list(response.context["messages"])[0]),
        )
        self.assertEqual(
            "W",
            response.context["userlistings"]
            .filter(title="test heading want")
            .first()
            .listing_type,
        )
        response = self.client.get(self.url)
        self.assertIn("test heading want", response.content.decode())

    def test_listing_delete(self):
        # nusra must not able to delete rice listing
        self.client.post(
            reverse("login"),
            {"username": "KKDE002", "password": "sumee1910"},
            follow=True,
        )
        response = self.client.post(
            reverse("frontendapp:listing_delete", kwargs={"pk": 1}), follow=True
        )

        response = self.client.get(self.url)
        self.assertIn("rice", [l.title for l in response.context["userlistings"]])

        # suhail can delete rice listing
        self.client.post(
            reverse("login"),
            {"username": "KKDE001", "password": "sumee1910"},
            follow=True,
        )
        response = self.client.post(
            reverse("frontendapp:listing_delete", kwargs={"pk": 1}), follow=True
        )

        response = self.client.get(self.url)
        self.assertNotIn("rice", [l.title for l in response.context["userlistings"]])

    def test_listing_preview(self):
        response = self.client.get(reverse("frontendapp:listing_preview", kwargs={"pk": 1}))
        self.assertIn("Matta rice", response.content.decode())
