try:
    import celery
    print("celery: OK")
except ImportError:
    print("celery: MISSING")

try:
    import sqlalchemy
    print("sqlalchemy: OK")
except ImportError:
    print("sqlalchemy: MISSING")

try:
    import geoalchemy2
    print("geoalchemy2: OK")
except ImportError:
    print("geoalchemy2: MISSING")

try:
    import asyncpg
    print("asyncpg: OK")
except ImportError:
    print("asyncpg: MISSING")

try:
    import passlib
    print("passlib: OK")
except ImportError:
    print("passlib: MISSING")

try:
    import jose
    print("python-jose: OK")
except ImportError:
    print("python-jose: MISSING")

try:
    import bcrypt
    print("bcrypt: OK")
except ImportError:
    print("bcrypt: MISSING")
