from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from django.conf import settings


def verify_google_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        if idinfo.get('iss') not in (
            'accounts.google.com',
            'https://accounts.google.com',
        ):
            raise ValueError('Invalid Google token issuer.')

        if not idinfo.get('sub'):
            raise ValueError(
                'Google token does not contain a subject.'
            )

        if not idinfo.get('email'):
            raise ValueError(
                'Google token does not contain an email.'
            )

        if idinfo.get('email_verified') is not True:
            raise ValueError(
                'Google email is not verified.'
            )

        return idinfo

    except ValueError:
        raise
    except Exception:
        raise ValueError(
            'Unable to verify Google token.'
        )