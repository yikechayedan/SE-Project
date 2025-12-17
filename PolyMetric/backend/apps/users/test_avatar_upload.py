import requests
import mimetypes

# 你的 access token
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY0NjY5NjA3LCJpYXQiOjE3NjQ2NjI0MDgsImp0aSI6Ijk2ZmM0YjQ5MjVlMzQ0YzE5ZGVmYjFkY2VlMGE0OGE0IiwidXNlcl9pZCI6IjEwIn0.j4hZxEvj1uLzLCY1utTj43uR0Gv7gkcapu6Z_yjOSoo"


# 本地后端接口地址
url = "http://127.0.0.1:8000/api/users/avatar/"


# 头像文件路径（你本地电脑上任意一张图片）
file_path = r"C:\Users\刘思远\Desktop\软工\头像测试\20kb.jpg"

# 自动根据文件后缀推断 MIME 类型
mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"


files = {
    "avatar": ("20kb.jpg", open(file_path, "rb"), mime_type)
}


headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}

response = requests.post(url, files=files, headers=headers)

print("状态码:", response.status_code)
print("响应内容:", response.json())
