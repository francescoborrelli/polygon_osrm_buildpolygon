#  Copyright (c) 2020. AV Connect Inc.
# WSData client that auto-gets jwt tokens.
#
import requests
import json

class JWTClient(object):
    def __init__(self, host_url, username, password):
        """
        :param host_url: Root url of WSData server
        :param username:  Username on WSData server
        :param password:  Password on WSData server
        """
        self.token = None
        self.host_url = host_url
        self.username = username
        self.password = password

    def json_post(self, path, json_message):
        """
        POST to server, reloading token if necessary
        :param path: path from root url of WSData server to the requested resource
        :param json_message: message to be posted in json format
        :return:
        """
        if self.token is None:
            self.get_token()

        response = self._post_it(json_message, path)

        if response.status_code >= 400:
            """ Get token and retry """
            self.get_token()
            response = self._post_it(json_message, path)
        return response

    def get(self, url):
        if self.token is None:
            self.get_token()
        response = requests.get(self.host_url + url,
                                headers={"Authorization": "Bearer " + self.token,
                                         "Content-Type": "application/json"}
                                )
        return response

    def _post_it(self, json_message, url):
        response = requests.post(self.host_url + url,
                                 data=json_message,
                                 headers={"Authorization": "Bearer " + self.token,
                                          "Content-Type": "application/json"})
        return response

    def get_token(self):
        """ Refresh the jwt token"""
        response = requests.post(self.host_url + '/auth',
                                 data=json.dumps({
                                     "username": self.username,
                                     "password": self.password}),
                                 headers={"Content-Type": "application/json"})
        self.token = response.json()["access_token"]
        print(self.token)
