import requests

ALGLO_SESSIONS_ENDPOINT = 'https://leddesignpro-api.azurewebsites.net/alglo-sessions/'


class ALGLOSessionMiddleware(object):
    def process_request(self, request):
        request.session.load()
        alglo_sessiontoken = request.session.get('alglo_sessiontoken')

        # Sessiontoken must be a string (must not be None or a list)
        # Also True if User wants to logout
        if type(alglo_sessiontoken) != str or request.GET.get('logout') != None:
            alglo_sessiontoken = self.new_session(request)['sessiontoken']
        else:
            # Check if the sessiontoken exists in the API
            session_request = requests.get(ALGLO_SESSIONS_ENDPOINT +
                alglo_sessiontoken + '/')
            if session_request.status_code != 200:
                alglo_sessiontoken = self.new_session(request)['sessiontoken']

        # Set sessiontoken
        request.session['alglo_sessiontoken'] = alglo_sessiontoken


    # Helper: Get new session (and sessiontoken with it)
    def new_session(self, request):
        from ipware.ip import get_real_ip

        # Get user's IP address
        ip_address = get_real_ip(request)
        if ip_address == None:
            from ipware.ip import get_ip

            ip_address = get_ip(request)

        if ip_address != None:
            # Deal with IP address edge case which won't work with my API
            # Looks like ###.###.###.###:#####
            # (I think my API doesn't like ports in IPv4 addresses)
            import re

            if re.match(r'^\d{,3}\.\d{,3}\.\d{,3}\.\d{,3}:\d+$', ip_address) != None:
                ip_address = ip_address.split(':')[0]

            session_data = { 'ip_address': ip_address }

        # Save session; obtain sessiontoken
        session_request = requests.post(ALGLO_SESSIONS_ENDPOINT,
            data=session_data)

        # Return session info

        # session_request.json() # This breaks Azure
        # Azure-specific hack to get this to work:
        # http://stackoverflow.com/questions/23661008/html-before-json-when-using-post
        import json

        return json.loads(session_request.text.split('</body>')[1])
