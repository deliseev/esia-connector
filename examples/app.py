import os

from aiohttp import web

from esia_connector_aiohttp.client import EsiaSettings, EsiaAuth


def get_test_file(name):
    return os.path.join(os.path.dirname(__file__), 'res', name)


TEST_SETTINGS = EsiaSettings(esia_client_id='YOUR SYSTEM ID',
                             redirect_uri='http://localhost:5000/info',
                             certificate_file=get_test_file('test.crt'),
                             private_key_file=get_test_file('test.key'),
                             esia_token_check_key=get_test_file('esia_pub.key'),
                             esia_service_url='https://esia-portal1.test.gosuslugi.ru',
                             esia_scope='openid fullname id_doc')

assert TEST_SETTINGS.esia_client_id != 'YOUR SYSTEM ID', "Please specify real system id!"

assert os.path.exists(TEST_SETTINGS.certificate_file), "Please place your certificate in res/test.crt !"
assert os.path.exists(TEST_SETTINGS.private_key_file), "Please place your private key in res/test.key!"
assert os.path.exists(TEST_SETTINGS.esia_token_check_key), "Please place ESIA public key in res/esia_pub.key !"


routes = web.RouteTableDef()

esia_auth = EsiaAuth(TEST_SETTINGS)


@routes.get('/')
async def hello(request) -> web.Response:
    url = esia_auth.get_auth_url()
    return 'Start here: <a href="{0}">{0}</a>'.format(url)


@routes.get('/info')
async def process(request) -> web.Response:
    code = request.query.get('code')
    state = request.query.get('state')
    esia_connector = esia_auth.complete_authorization(code, state)
    inf = esia_connector.get_person_main_info()
    return "%s" % inf


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)
