from django.shortcuts import redirect
from django.views import View
from django.conf import settings

from oauth2client.client import flow_from_clientsecrets


def get_auth_service():
    return flow_from_clientsecrets(
        settings.CLIENT_SECRETS, scope=settings.SCOPE,
        redirect_uri=settings.REDIRECT_URI)


class Auth(View):

    def get(self, request):
        flow = get_auth_service()
        return redirect(flow.step1_get_authorize_url())


class AuthCallback(View):

    def get(self, request):
        flow = get_auth_service()
        code = request.GET.get('code')

        if code:
            credentials = flow.step2_exchange(request.GET['code'])
            request.session[settings.CREDENTIALS_KEY] = credentials.to_json()

        return redirect('main')
