from redis5 import StrictRedis

HOST = '31.128.44.113'
PORT = 6379
redis = StrictRedis(host=HOST, port=PORT, db=0)


def support_mode(_id: int) -> bool:
    return bool(redis.get(f'sm:{_id}'))


def get_user_id_by_invoice(invoice: str) -> int:
    return int(redis.get(f'invoice:{invoice}'))


def set_registrated(user_id: int) -> None:
    redis.hset(str(user_id), "registrated", str(1))


def is_registrated(user_id: int) -> bool:
    return bool(redis.hget(str(user_id), "registrated"))


def clear_registrated(user_id: int) -> None:
    redis.hdel(str(user_id), "registrated")


def set_policy(user_id: int) -> None:
    redis.hset(str(user_id), "policy", str(1))


def get_policy(user_id: int) -> bool:
    return bool(redis.hget(str(user_id), "policy"))


def clear_policy(user_id: int) -> None:
    redis.hdel(str(user_id), "policy")


def get_temp_ea_cookie() -> str:
    cookie = redis.get("ea_cookie")
    return cookie if cookie is not None else ""


def set_temp_ea_cookie(cookie: str) -> None:
    redis.set("ea_cookie", cookie)
