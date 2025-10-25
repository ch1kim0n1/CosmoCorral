def generate_access_code():
    import random
    import string

    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def generate_token():
    import uuid

    return uuid.uuid4().hex