import jwt
import aiohttp


class EsiaError(Exception):
    pass


class IncorrectJsonError(EsiaError, ValueError):
    pass


class IncorrectMarkerError(EsiaError, jwt.InvalidTokenError):
    pass


class HttpError(EsiaError, aiohttp.ClientError):
    pass
