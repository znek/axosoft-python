"""
Axosoft API.

Hook up to axosoft
"""

import requests
import json
import urllib
from .validate import validate_address, \
    validate_required_params, \
    validate_response


class Axosoft(object):

    """ Axosoft."""

    def __init__(self, client_id, client_secret, domain, token=None):
        """Init."""
        self.__consumer = {
            "client_id": client_id,
            "client_secret": client_secret,
            "domain": domain
        }
        self.__token = token
        self.__api_version = '3'
        self.__api_path = 'api'
        self.__base_url = 'https://{0}/{1}'\
            .format(
                self.__consumer["domain"],
                self.__api_path
            )
        self.__content_type = 'application/x-www-form-urlencoded;charset=utf-8'

    def is_authenticated(self):
        """ Test if there is a valid token."""
        if self.__token is None:
            authenticated = False
        else:
            try:
                self.get('me')
            except ValueError:
                authenticated = False
            else:
                authenticated = True

        return authenticated

    def authenticate_by_password(self, user, password):
        """
        Authenticate.

        Get a new token if one doesn't exist.
        Otherwise return the existing token.
        """
        authenticated = self.is_authenticated()
        if authenticated:
            return self.__token
        else:
            uri = '%s/oauth2/token' % self.__base_url
            payload = {
                'grant_type': 'password',
                'client_id': self.__consumer['client_id'],
                'client_secret': self.__consumer['client_secret'],
                'username': user,
                'password': password,
                'scope': 'read write'
            }
            response = requests.post(uri, payload)
            success = validate_response(response, 200)
            if success:
                auth = response.json()
                assert auth['token_type'] == 'bearer'
                self.__token = auth['access_token']
                return self.__token

    def begin_authentication_by_code(self, redirect_uri):
        """ Return the URL to use when authenticating with the code method. """
        # TODO python 2/3 urllib
        payload = {
            "response_type": "code",
            "client_id": self.__consumer['client_id'],
            "redirect_uri": redirect_uri,
            "scope": "read write"
        }
        url = "https://{0}/auth?{1}".format(
            self.__consumer["domain"],
            urllib.urlencode(payload)
        )
        return url

    def complete_authenticate_by_code(self, code, redirect_uri):
        """
        Authenticate.

        Get a new token if one doesn't exist.
        Otherwise return the existing token.
        """
        # TODO write a test to get auth code
        # TODO test already authenticated
        authenticated = self.is_authenticated()
        if authenticated:
            return self.__token
        else:
            uri = '%s/oauth2/token' % self.__base_url
            payload = {
                'grant_type': 'authorization_code',
                'client_id': self.__consumer['client_id'],
                'client_secret': self.__consumer['client_secret'],
                'code': code,
                'redirect_uri': redirect_uri
            }
            response = requests.post(uri, payload)
            success = validate_response(response, 200)
            if success:
                auth = response.json()
                assert auth['token_type'] == 'bearer'
                self.__token = auth['access_token']
                return self.__token

    def log_out(self):
        """ Log out of the API. """
        # TODO make sure self.__token is defined
        del self.__token
        return True

    def get(self, address, resourse_id=None, payload=None):
        """ Get a resource. """
        resource = validate_address(address, 'GET')
        uri = '{0}/v{1}/{2}'\
            .format(
                self.__base_url,
                self.__api_version,
                resource['address']
            )

        if resourse_id is not None:
            uri = '{0}/{1}'.format(uri, resourse_id)
        else:
            pass

        response = requests.get(
            uri,
            params=payload,
            headers={'Authorization': 'Bearer ' + self.__token}
        )

        validate_response(response, 200)

        response = response.json()

        return response["data"]

    def create(self, address, payload):
        """ Create a resource. """
        resource = validate_address(address, 'POST')

        validate_required_params(resource, payload)

        uri = '{0}/v{1}/{2}'\
            .format(
                self.__base_url,
                self.__api_version,
                resource['address']
            )
        headers = {
            'Content-type': 'application/json; charset=utf-8',
            'Authorization': 'Bearer ' + self.__token
        }
        response = requests.post(
            uri,
            data=json.dumps(payload),
            headers=headers
        )

        validate_response(response, 201)

        data = response.json()
        return data['data']

    def update(self, address, resourse_id, payload):
        """ Update a resource. """
        resource = validate_address(address, 'POST')

        uri = '{0}/v{1}/{2}/{3}'\
            .format(
                self.__base_url,
                self.__api_version,
                resource['address'],
                resourse_id
            )
        headers = {
            'Content-type': 'application/json; charset=utf-8',
            'Authorization': 'Bearer ' + self.__token
        }
        response = requests.post(
            uri,
            data=json.dumps(payload),
            headers=headers
        )

        validate_response(response, 200)

        data = response.json()
        return data['data']

    def delete(self, address, resourse_id):
        """ Delete a resource. """
        resource = validate_address(address, 'DELETE')

        uri = '{0}/v{1}/{2}/{3}'\
            .format(
                self.__base_url,
                self.__api_version,
                resource['address'],
                resourse_id
            )

        headers = {'Authorization': 'Bearer ' + self.__token}

        response = requests.delete(uri, headers=headers)

        success = validate_response(response, 200)
        return success
