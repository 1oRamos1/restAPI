import openai
from mistralai import Mistral
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY
mistral_client = Mistral(api_key=settings.MISTRAL_API_KEY)
