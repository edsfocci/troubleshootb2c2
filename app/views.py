"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        context_instance = RequestContext(request,
        {
            'title':'Home Page',
            'year':datetime.now().year,
        })
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        context_instance = RequestContext(request,
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        })
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        context_instance = RequestContext(request,
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        })
    )

def auth(request):
    from django.shortcuts import redirect

    # Validate query string
    if request.GET.get('code') == None or request.GET.get('id_token') == None:
        return redirect('/')

    import jwt

    id_dict = jwt.decode(request.GET['id_token'], verify=False)

    aad_meta_request = requests.get('https://login.microsoftonline.com/leddesignproauth.onmicrosoft.com/v2.0/.well-known/openid-configuration?p=' + id_dict['acr'])

    token_request = requests.post(aad_meta_request.json()['token_endpoint'], data={
        'grant_type': 'authorization_code',
        'client_id': '7b1a7b46-25d4-4379-8426-00a40795e06b',
        'scope': 'openid offline_access',
        'code': request.GET['code'],
        'redirect_uri': 'https://troubleshootb2c2.azurewebsites.net/auth',
        'client_secret': '7ss+5U2LYb2F-~9['
    })

    if token_request.status_code == 200:
        token_dict = token_request.json()

        id_dict = jwt.decode(token_dict['id_token'], verify=False)

        # Define ALGLO Users endpoint
        ALGLO_USERS_ENDPOINT = 'https://leddesignpro-api.azurewebsites.net/alglo-users/'

        user_request = requests.get(ALGLO_USERS_ENDPOINT + id_dict['oid'] + '/')

        if user_request.status_code != 200:
            user_request = requests.post(constants.ALGLO_USERS_ENDPOINT, data={
                'aad_id': id_dict['oid'],
                'email': id_dict['emails'][0],
            })

        # Define ALGLO Sessions endpoint
        ALGLO_SESSIONS_ENDPOINT = 'https://leddesignpro-api.azurewebsites.net/alglo-sessions/'

        session_request = requests.patch(ALGLO_SESSIONS_ENDPOINT +
            request.session['alglo_sessiontoken'] + '/', data={
                'owner': ALGLO_USERS_ENDPOINT + id_dict['oid'] + '/',
                'refresh_token': token_dict['refresh_token'],
                'last_aad_policy': id_dict['acr']
            })

    return redirect('/')
