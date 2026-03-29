from django.test import TestCase
from django.urls import reverse

from .models import User


class RegistrationTest(TestCase):
    def test_registration(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "full_name": "New Student",
                "email": "new@student.com",
                "role": "student",
                "password1": "pass12345",
                "password2": "pass12345",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="new@student.com").exists())
