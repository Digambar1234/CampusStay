from slowapi import Limiter
from slowapi.util import get_remote_address


def rate_limit_key(request):
    user_id = getattr(request.state, "user_id", None)
    return str(user_id) if user_id else get_remote_address(request)


limiter = Limiter(key_func=rate_limit_key)
