from django.conf import settings


def context(request):
    return {
        'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
        'TABLE_ID': settings.TABLE_ID,
    }
