import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.learning.models import Module

def check_module_content():
    try:
        module = Module.objects.get(pk=1)
        print(f"Module: {module.title} (ID: {module.id})")
        print(f"Contents count: {module.contents.count()}")
        for c in module.contents.all():
            print(f" - Content: {c.title} (Type: {c.content_type})")
            
    except Module.DoesNotExist:
        print("Module 1 not found.")

if __name__ == '__main__':
    check_module_content()

