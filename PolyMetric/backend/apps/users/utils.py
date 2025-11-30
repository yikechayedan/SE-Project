# apps/users/utils.py
import random
import string
from django.core.cache import cache

def generate_code(length=6):
    """生成6位数字验证码"""
    return ''.join(random.choices(string.digits, k=length))

def save_code(email, code, expire=300):
    """保存验证码到cache，有效期5分钟"""
    cache.set(f"verify_code_{email}", code, expire)

def check_code(email, code):
    """校验验证码是否正确"""
    real = cache.get(f"verify_code_{email}")
    return real == code
