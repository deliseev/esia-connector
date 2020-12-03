import asyncio
import base64
import datetime
import shlex
from subprocess import PIPE, Popen

import aiohttp
import pytz

from esia_connector_aiohttp.exceptions import HttpError, IncorrectJsonError, OpenSSLError


async def make_request(url, method='GET', headers=None, data=None, verify_ssl=False):
    """
    Makes request to given url and returns parsed response JSON
    :type url: str
    :type method: str
    :type headers: dict or None
    :type data: dict or None
    :rtype: dict
    :raises HttpError: if requests.HTTPError occurs
    :raises IncorrectJsonError: if response data cannot be parsed to JSON
    """

    try:
        # TODO: SSLCertVerificationError
        # https://github.com/aio-libs/aiohttp/issues/955
        connector=aiohttp.TCPConnector(verify_ssl=verify_ssl)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.request(method, url, headers=headers, data=data) as resp:
                return await resp.json()

    except Exception as e:
        raise HttpError(e)
    except ValueError as e:
        raise IncorrectJsonError(e)


async def sign_params(params, certificate_file, private_key_file):
    """
    Signs params adding client_secret key, containing signature based on `scope`, `timestamp`, `client_id` and `state`
    keys values.
    :param dict params: requests parameters
    :param str certificate_file: path to certificate file
    :param str private_key_file: path to private key file
    :return:signed request parameters
    :rtype: dict
    """
    plaintext = ''.join([
        params.get(key, '') for key in ['scope', 'timestamp', 'client_id', 'state']
    ])

    cmd = 'openssl smime  -sign -md md_gost12_256 -signer {cert} -inkey {key} -outform DER'.format(
        cert=certificate_file,
        key=private_key_file
    )
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    stdout, stderr = await proc.communicate(input=plaintext.encode())

    if proc.returncode != 0:
        raise OpenSSLError

    client_secret=base64.urlsafe_b64encode(stdout).decode('utf-8'),
    return {**params, 'client_secret': client_secret}


def get_timestamp():
    return datetime.datetime.now(pytz.utc).strftime('%Y.%m.%d %H:%M:%S %z').strip()

