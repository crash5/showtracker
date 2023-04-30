import hashlib
import secrets
import base64


ALGORITHM = "pbkdf2_sha256"
SALT_SIZE = 32

def hash_password(password, salt=None, iterations=260000):
    if salt is None:
        salt = secrets.token_hex(SALT_SIZE)
    assert salt and isinstance(salt, str) and "$" not in salt
    assert isinstance(password, str)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations
    )
    b64_hash = base64.b64encode(pw_hash).decode("ascii").strip()
    return "{}${}${}${}".format(ALGORITHM, iterations, salt, b64_hash)


def verify_password(password, password_hash):
    if (password_hash or "").count("$") != 3:
        return False
    algorithm, iterations, salt, _ = password_hash.split("$", 3)
    iterations = int(iterations)
    assert algorithm == ALGORITHM
    compare_hash = hash_password(password, salt, iterations)
    return secrets.compare_digest(password_hash, compare_hash)

if __name__ == '__main__':
    import sys
    password = hash_password(sys.argv[1])
    print(password)
