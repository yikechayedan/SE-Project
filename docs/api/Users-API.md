Users 模块 API 文档
API U1：用户注册

POST /api/users/register/
权限：无需登录

Request Body
{
  "username": "newuser",
  "password": "123456",
  "email": "user@test.com",
  "phone": "13800000000"
}

Response（201）
{
  "code": 200,
  "msg": "注册成功",
  "data": {
    "id": 1,
    "username": "newuser",
    "email": "user@test.com",
    "phone": "13800000000",
    "avatar": null,
    "bio": null
  }
}

API U2：用户登录（JWT）

POST /api/users/login/
权限：无需登录

使用 SimpleJWT TokenObtainPairView

Request Body
{
  "username": "newuser",
  "password": "123456"
}

Response（200）
{
  "refresh": "xxx",
  "access": "xxx"
}

API U3：刷新 Token

POST /api/users/token/refresh/

Request Body
{
  "refresh": "xxx"
}

API U4：修改密码

PUT /api/users/change_password/
权限：已登录

Request Body
{
  "old_password": "123456",
  "new_password": "newpassword"
}

Response
{
  "code": 200,
  "msg": "更新成功"
}

API U5：退出登录（Token 拉黑）

POST /api/users/logout/
权限：已登录

Request Body
{
  "refresh": "xxx"
}

Response
{
  "code": 200,
  "msg": "退出成功"
}

API U6：管理员获取用户列表

GET /api/users/admin/users/
权限：管理员

Response
[
  {
    "id": 1,
    "username": "user1",
    "email": "user1@test.com",
    "phone": "13800000000",
    "avatar": null,
    "bio": "简介"
  }
]

API U7：管理员删除用户

DELETE /api/users/admin/users/{id}/
权限：管理员

API U8：忘记密码（发送验证码）

POST /api/users/forgot-password/
权限：无需登录

Request Body
{
  "email": "user@test.com"
}

Response
{
  "code": 200,
  "msg": "验证码已发送到您的邮箱"
}

API U9：验证邮箱验证码

POST /api/users/verify-code/

{
  "email": "user@test.com",
  "code": "123456"
}

API U10：重置密码

POST /api/users/reset-password/

{
  "email": "user@test.com",
  "code": "123456",
  "password": "newpassword"
}

API U11：上传头像

POST /api/users/avatar/
权限：已登录
Content-Type：multipart/form-data

Form Data
avatar: image.jpg

Response
{
  "code": 200,
  "msg": "头像上传成功",
  "data": {
    "avatar": "http://127.0.0.1:8000/media/avatars/xxx.jpg"
  }
}

API U12：获取用户公开信息

GET /api/users/{id}/public/
权限：无需登录

Response
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "id": 2,
    "username": "user2",
    "email": "user2@test.com",
    "phone": "13800000000",
    "avatar": null,
    "bio": "简介",
    "show_followed_models": true,
    "show_followed_datasets": false,
    "is_followed": false,
    "followers_count": 10,
    "following_count": 3
  }
}

API U13：关注用户

POST /api/users/{id}/follow/
权限：已登录

Response（201）
{
  "code": 201,
  "msg": "关注成功"
}

API U14：取消关注用户

DELETE /api/users/{id}/follow/
权限：已登录

Response
{
  "code": 200,
  "msg": "取消关注成功"
}

API U15：获取我关注的用户列表

GET /api/users/followed/
权限：已登录

Response
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 2,
      "username": "user2",
      "avatar": null,
      "bio": "简介",
      "show_followed_models": true,
      "show_followed_datasets": false,
      "followed_at": "2025-12-01T10:00:00"
    }
  ]
}

API U16：更新隐私设置

PUT /api/users/privacy/
权限：已登录

Request Body
{
  "show_followed_models": false,
  "show_followed_datasets": true
}

API U17：获取 / 更新当前用户信息（Me）
获取当前用户信息

GET /api/users/me/

{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "id": 1,
    "username": "current",
    "email": "current@test.com",
    "avatar": null,
    "bio": "测试用户",
    "show_followed_models": true,
    "show_followed_datasets": true
  }
}

更新当前用户信息

PUT / PATCH /api/users/me/

{
  "bio": "新的个人简介"
}