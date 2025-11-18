from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserTests(APITestCase):
    def setUp(self):
        self.user_data = {
            "username": "userdata",
            "email": "sdf@example.com",
            "phone": "13802000000",
            "password": "testpassword"
        }
        self.user = User.objects.create_user(**self.user_data)
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh_token.access_token)

    def test_register(self):
        unique_username = "newuser"  # 使用唯一的用户名
        self.user_data["username"] = unique_username
        response = self.client.post("/api/users/register/", self.user_data, format="json")
        print("REGISTER RESPONSE:", response.data)  # 打印错误信息
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["code"], 200)

   # def test_login(self):
    #    response = self.client.post("/api/users/login/", {"username": "testuser", "password": "testpassword"}, format="json")
    #    self.assertEqual(response.status_code, status.HTTP_200_OK)
    #    self.assertIn("access", response.data)

    def test_login(self):
        response = self.client.post("/api/users/login/", {
            "username": "userdata",  # 使用 setUp 中创建的用户名
            "password": "testpassword"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_get_user_info(self):
        response = self.client.get("/api/users/me/", HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password(self):
        response = self.client.put("/api/users/change_password/", {
            "old_password": "testpassword",
            "new_password": "newpassword"
        }, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        response = self.client.post("/api/users/logout/", {"refresh": str(self.refresh_token)}, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_list(self):
        admin_user = User.objects.create_superuser(username="admin", password="admin123", email="admin@example.com")
        self.client.force_authenticate(user=admin_user)
        response = self.client.get("/api/users/admin/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
