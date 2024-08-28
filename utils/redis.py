from redis5 import StrictRedis

HOST = '31.128.44.113'
PORT = 6379
redis = StrictRedis(host=HOST, port=PORT, db=0, password='px9TWv5uQI&2')


def get_user_id_by_invoice(invoice: str) -> int:
    user_id = int(redis.get(f'invoice:{invoice}'))
    redis.delete(f'invoice:{invoice}')
    return user_id


def set_registered(user_id: int) -> None:
    redis.hset(str(user_id), "registered", str(1))


def is_registered(user_id: int) -> bool:
    return bool(redis.hget(str(user_id), "registered"))


def clear_registered(user_id: int) -> None:
    redis.hdel(str(user_id), "registered")  # Неверная типизация библиотеки


def set_policy(user_id: int) -> None:
    redis.hset(str(user_id), "policy", "1")


def get_policy(user_id: int) -> bool:
    return bool(redis.hget(str(user_id), "policy"))


def clear_policy(user_id: int) -> None:
    redis.hdel(str(user_id), "policy")  # Неверная типизация библиотеки


def get_temp_ea_cookie() -> str:
    cookie = redis.get("ea_cookie")
    return cookie if cookie is not None else ""


def set_temp_ea_cookie(cookie: str) -> None:
    redis.set("ea_cookie", cookie)


def set_support_mode(user_id: int, mode: bool = True) -> None:
    if mode:
        redis.hset(str(user_id), "sm", "1")
    else:
        redis.hdel(str(user_id), "sm")  # Неверная типизация библиотеки


def set_validate_mode(user_id: int, mode: bool = True) -> None:
    if mode:
        redis.hset(str(user_id), "vm", "1")
    else:
        redis.hdel(str(user_id), "vm")  # Неверная типизация библиотеки


def get_support_mode(user_id: int) -> bool:
    return bool(redis.hget(str(user_id), "sm"))


def get_validate_mode(user_id: int) -> bool:
    return bool(redis.hget(str(user_id), "vm"))


def clear_support_mode(user_id: int) -> None:
    redis.hdel(str(user_id), "sm")  # Неверная типизация библиотеки


def clear_validate_mode(user_id: int) -> None:
    redis.hdel(str(user_id), "vm")  # Неверная типизация библиотеки


def get_next_emoji() -> str:
    if not redis.exists("emoji_id"):
        redis.set("emoji_id", 0)

    emoji_id = int(redis.get("emoji_id"))
    redis.incr("emoji_id")

    with open("utils/emoji.txt", "r", encoding="utf-8") as f:
        emoji_list = list(f.read())

    emoji = emoji_list[emoji_id % len(emoji_list)]
    return str(emoji)
