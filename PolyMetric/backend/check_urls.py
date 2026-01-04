#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.test_settings')
django.setup()

from django.urls import get_resolver
from django.urls.resolvers import URLResolver, URLPattern

def show_urls(urllist, depth=0):
    for entry in urllist:
        if isinstance(entry, URLResolver):
            print('  ' * depth + f'{entry.pattern}:')
            show_urls(entry.url_patterns, depth + 1)
        elif isinstance(entry, URLPattern):
            print('  ' * depth + f'{entry.pattern} -> {entry.callback}')

print("URL路由结构:")
show_urls(get_resolver().url_patterns)