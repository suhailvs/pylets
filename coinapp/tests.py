from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class CreateExchangeTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("signup_new")

    def test_createexchange(self):
        response = self.client.post(
            self.url,
            {"code":"KKED", "title":"sdfa", "address":"aa", "country":"IN","username": '7238233233', "password1": "sumee1910",
             "password2":"sumee1910","email":"sdfa@gag.com", "phone":"123123","tandc":True},
            follow=True,
        )
        # print(response.content)

class TransactionTest(TestCase):
    fixtures = [
        "sample.json",
    ]

    def setUp(self):
        self.client = Client()
        self.url = reverse("coinapp:home")
        self.nusra = User.objects.get(username="8921513696")
        self.sulaiman = User.objects.get(username="8547622462")

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
        "sample.json",
    ]

    def setUp(self):
        self.client = Client()
        self.url = reverse(
            "coinapp:user_detail", kwargs={"exchange": "KKDE", "user": 1}
        )

    def test_offerings_list(self):
        response = self.client.get(self.url)
        rice_offering = """
        <div class="list-group">  
            <a href="/listing/1/preview/" class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">Food_Drink</h5>
                <small class="text-body-secondary">Nov. 1, 2024</small>
                </div>
                <p class="mb-1">#1: rice</p>
                <small class="text-body-secondary">rate: 50$ per kg</small>
            </a>            
        </div>
        """
        self.assertInHTML(rice_offering, response.content.decode())

    def test_offering_create(self):
        self.client.post(
            reverse("login"),
            {"username": "7356775981", "password": "sumee1910"},
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
                "heading": "test heading",
                "detail": "test detail",
                "rate": "test rate",
            },
            follow=True,
        )

        self.assertIn(
            "Listing activated: test heading",
            str(list(response.context["messages"])[0]),
        )
        self.assertEqual(
            "O",
            response.context["userlistings"]
            .filter(heading="test heading")
            .first()
            .listing_type,
        )
        response = self.client.get(self.url)
        self.assertInHTML("Add new offering", response.content.decode())
        self.assertIn("test heading", response.content.decode())

    def test_want_create(self):
        self.client.post(
            reverse("login"),
            {"username": "7356775981", "password": "sumee1910"},
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
                "heading": "test heading want",
                "detail": "test detail",
            },
            follow=True,
        )
        self.assertIn(
            "Listing activated: test heading want",
            str(list(response.context["messages"])[0]),
        )
        self.assertEqual(
            "W",
            response.context["userlistings"]
            .filter(heading="test heading want")
            .first()
            .listing_type,
        )
        response = self.client.get(self.url)
        self.assertIn("test heading want", response.content.decode())

    def test_listing_delete(self):
        # nusra must not able to delete rice listing
        self.client.post(
            reverse("login"),
            {"username": "8921513696", "password": "sumee1910"},
            follow=True,
        )
        response = self.client.post(
            reverse("coinapp:listing_delete", kwargs={"pk": 1}), follow=True
        )

        response = self.client.get(self.url)
        self.assertIn("rice", [l.heading for l in response.context["userlistings"]])

        # suhail can delete rice listing
        self.client.post(
            reverse("login"),
            {"username": "7356775981", "password": "sumee1910"},
            follow=True,
        )
        response = self.client.post(
            reverse("coinapp:listing_delete", kwargs={"pk": 1}), follow=True
        )

        response = self.client.get(self.url)
        self.assertNotIn("rice", [l.heading for l in response.context["userlistings"]])

    def test_listing_preview(self):
        response = self.client.get(reverse("coinapp:listing_preview", kwargs={"pk": 1}))
        self.assertIn("Matta rice", response.content.decode())
