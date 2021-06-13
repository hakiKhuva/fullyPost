import os

# EMAIL AND PASSWORD TO SEND EMAILS TO USERS
MAIN_EMAIL = os.environ.get('main_email')
MAIN_PASSWORD = os.environ.get('main_pwd')

SECRET_KEY = os.environ.get('SECRET_KEY')
PERMANENT_SESSION_LIFETIME = 7

databaseURL = ""
if os.environ.get('DATABASE_URL'):
    if os.environ.get('DATABASE_URL').startswith("postgres://"):
        databaseURL = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
    else:
        databaseURL = os.environ.get('DATABASE_URL')
else:
    print("DATABASE_URL is None or not specified!")

SQLALCHEMY_DATABASE_URI = databaseURL
SQLALCHEMY_POOL_RECYCLE = 280
SQLALCHEMY_POOL_SIZE = 20

SQLALCHEMY_TRACK_MODIFICATIONS = False
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SEND_FILE_MAX_AGE_DEFAULT = 2592000

Strict_Transport_Security = "max-age=604800;"
X_XSS_Protection= "1; mode=block"
X_Frame_Options = "SAMEORIGIN"
X_Content_Type_Options = "nosniff"
Cache_Control = "no-store, no-transform, must-revalidate"

# DATABASE CONFIG

LENGTH = {
    'EMAIL' : 200,
    'USER_ID' : 50,
    'RANDOM_NAME': 5,
    'NAME' : 23,
    'DESCRIPTION' : 1000,
    'RANDOM_USERNAME': 8,
    'USERNAME' : 18,
    'POST_ID' : 30,
    'POST_FILE_TYPE' : 100,
    
}

#   AUTHENTICATION

TIME_LIMITED_FOR_AUTHENTICATION = 180
MINIMUM_PASSWORD_LENGTH = 8
MAXIMUM_PASSWORD_LENGTH = 50

# Allow all emails
# EMAIL = "ALL"
# REGEX_EMAIL = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

# Allow only gmails
EMAIL = "GMAIL"
REGEX_EMAIL = '^[a-z0-9](\.?[a-z0-9]){5,}@g(oogle)?mail\.com$'

REGEX_PASSWORD = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{"+str(MINIMUM_PASSWORD_LENGTH)+","+str(MAXIMUM_PASSWORD_LENGTH)+"}$"

#   PROFILE
MIN_PROFILE_NAME_LEN = 3
MAX_PROFILE_NAME_LEN = LENGTH['NAME']

MIN_PROFILE_USERNAME_LEN = 3
MAX_PROFILE_USERNAME_LEN = LENGTH['USERNAME']

MAX_DESCRIPTION_LEN = LENGTH['DESCRIPTION']

MAX_PROFILE_IMAGE_SIZE_KB = 1024
PROFILE_IMAGE_PATH = os.path.join("userProfileImages")
STORE_PROFILE_IMAGE_PATH = os.path.join("fullyPost","static",PROFILE_IMAGE_PATH)
UPLOAD_PROFILE_IMAGE_PATH = os.path.join("static",PROFILE_IMAGE_PATH)

#for profile Image
MAX_CACHE_CONTROL = "max-age=600000, no-transform, must-revalidate"


#   POSTS
POST_TEXT_MAX_CHAR = 200            # MAXIMUM 200 CHARACTERS
POST_FILE_SIZE_KB = 5*1024         # 5 MB(s)

UPLOAD_FILES_FOLDER = os.path.join("userUploadedFiles")
STORE_UPLOAD_FILES_FOLDER_PATH = os.path.join("fullyPost","static",UPLOAD_FILES_FOLDER)
FILES_UPLOAD_FOLDER_PATH = os.path.join("static",UPLOAD_FILES_FOLDER)

RANDOM_STRING_LEN_TO_SAVE_UPLOADED_FILE = 30

COMMENT_LENGTH = 75               # MAXIMUM COMMENT LENGTH


# PASSWORD

PASSWORD_SALT = os.environ.get('PASSWORD_SALT')

# CREATE FOLDER TO SAVE PROFILE IMAGE IN
if not os.path.exists(STORE_PROFILE_IMAGE_PATH):
    os.mkdir(STORE_PROFILE_IMAGE_PATH)

if not os.path.exists(STORE_UPLOAD_FILES_FOLDER_PATH):
    os.mkdir(STORE_UPLOAD_FILES_FOLDER_PATH)
