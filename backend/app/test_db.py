
from database import test_connection

try:
    version = test_connection()
    print("PostgreSQL connection successful!")
    print(version)
except Exception as error:
    print("PostgreSQL connection failed.")
    print(type(error).__name__, str(error))
