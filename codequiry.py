"""
Codequiry's SDK was broken, so we built our own.
Pass in the API key to create a new session like so:
codecheck = Codechecker("1234567890")

After that, you can call each of the methods as outlined
in their individual docstrings.

Matt Rudge
December 2019
"""

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import os
import json
import socketio

class Codechecker(object):
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key is required")

        self.api_key = api_key

        self.BASE_URL = "https://codequiry.com/api/v1/"
        self.API_UPLOAD_URL = "https://codequiry.com/api/v1/check/upload"
        self.SOCKS_BASE_URL = "https://api.codequiry.com/"

        self.HEADERS = {
            "apikey": api_key,
            "Content-Type": "application/json"
        }

        session = requests.Session()
        self.session = session

    def get_account_details(self):
        """
        Lists the account details. Handy for testing if the API is
        working properly
        """
        url = self.BASE_URL + "account"

        return self._send(url)

    def create_check(self, check_name, lang):
        """
        Creates a new check on Codequiry. You must specify the check name
        and language code.
        Valid language codes are:

        13: Java
        14: Python
        16: C
        17: C++
        18: C#
        20: Perl
        21: PHP
        22: SQL
        23: VB
        24: XML
        28: Haskell
        29: Pascal
        30: Go
        31: Matlab
        32: Lisp
        33: Ruby
        34: Assembly
        38: HTML containing JavaScript
        39: JavaScript
        40: HTML
        41: Text by word
        42: Text by character
        """

        url = self.BASE_URL + "check/create?name=" + check_name + "&language=" + str(lang)

        return self._send(url)

    def list_checks(self):
        """
        Lists all the checks on our account
        """

        url = self.BASE_URL + "checks"

        return self._send(url)

    def upload(self, check_id, file_path):
        """
        Uploads a file. The check_id must be supplied from a
        pre-existing check.
        The file_path must be a path to a zip file.
        """

        _,file_name = os.path.split(file_path)

        mp = MultipartEncoder(
            fields={
                "file": (file_name, open(file_path, "rb")),
                "check_id": str(check_id)
            }
        )

        headers = self.HEADERS
        headers["Content-Type"] = mp.content_type
        
        response = self.session.post(self.API_UPLOAD_URL, data=mp, headers=headers)
        
        return response.status_code if response.status_code != 200 else \
               json.loads(response.content)
    
    def run_check(self, check_id):
        """
        Runs a check after the file has been uploaded.
        Supply the check_id
        """

        url = self.BASE_URL + "check/start?check_id=" + str(check_id) + "?webcheck=1?dbcheck=1"

        return self._send(url)
    
    def check_status(self, check_id):
        """
        Checks take some time to run. Supply the check_id to poll
        if the checks have finished.
        """

        url = self.BASE_URL + "check/get?check_id=" + str(check_id)

        return self._send(url)
    
    def job_listen(self, check_id, callback):
        """
        Uses socketsio to listen for when a job is finished.
        Supply the check_id and a callback function to run when the
        checks are complete.
        """

        if not check_id:
            return

        sio = socketio.Client()
        sio.connect(self.SOCKS_BASE_URL)

        @sio.event
        def connect():
            sio.emit('job-check', {'jobid': check_id})

        @sio.on('job-status')
        def on_message(data):
            callback(data)
            if data.error == 1 or data.percent == 100:
                sio.disconnect()

    def get_overview(self, check_id):
        """
        Gets a basic overview of the results for a given
        check_id
        """

        url = self.BASE_URL + "check/overview?check_id=" + str(check_id)

        return self._send(url)

    def get_detailed_results(self, check_id, submission_id):
        """
        Supplies detailed results of a given check_id and
        submission_id.
        The submission_id can be found in the overview.
        """

        url = self.BASE_URL + "check/results?check_id=" + str(check_id) + "&submission_id=" + str(submission_id)

        return self._send(url)

    def _send(self, url):
        """
        Private method to actually post the data to Codequiry
        """

        try:
            response = self.session.post(url, headers=self.HEADERS)
        except requests.ConnectionError:
            raise Exception("Cannot connect to Codequiry")
        
        try:
            return json.loads(response.content)
        except ValueError as e:
            raise Exception("Cannot decode JSON")
