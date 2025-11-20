import os
import sys
import django

# Setup Django environment BEFORE importing anything else that uses settings
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from apps.learning.models import Module
from apps.learning.serializers import ModuleSerializer
from django.contrib.auth.models import AnonymousUser

def test_module_serialization_anonymous():
    try:
        # Get Module 1
        module = Module.objects.get(pk=1)
        print(f"Found module: {module.title}")

        # Mock request
        factory = APIRequestFactory()
        request = factory.get('/api/learning/modules/1/')
        
        # Anonymous User
        request.user = AnonymousUser()
        
        # Wrap in DRF Request
        drf_request = Request(request)
        
        # Serialize
        serializer = ModuleSerializer(module, context={'request': drf_request})
        data = serializer.data
        print("Anonymous serialization successful!")
        
    except Module.DoesNotExist:
        print("Module 1 does not exist.")
    except Exception as e:
        print(f"Serialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_module_serialization_anonymous()

