from apiclient.discovery import build
from httplib2 import Http
from oauth2client.client import OAuth2Credentials

from django.conf import settings


class FusionTable(object):
    """Container object that builds the service for handling
       requests to fusiontables api."""

    def __init__(self, service):
        self.service = service

    @classmethod
    def build_service(cls, request):
        credentials = request.session[settings.CREDENTIALS_KEY]
        oauth_credentials = OAuth2Credentials.from_json(credentials)
        http_auth = oauth_credentials.authorize(Http())
        return cls(build('fusiontables', 'v2', http=http_auth))


class LocationTable(FusionTable):
    """Container for saving and deleting data from location fusion table."""

    def save(self, location):
        sql = (
            "INSERT INTO {} (Address, Location) VALUES ('{}', '{},{}')".format(
                settings.TABLE_ID,
                location.address,
                location.latitude,
                location.longitude))
        return self.service.query().sql(sql=sql).execute()

    def clear(self):
        sql = 'DELETE FROM {}'.format(settings.TABLE_ID)
        return self.service.query().sql(sql=sql).execute()
