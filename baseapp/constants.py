SUCCESS = 1
FAIL = 0

UNEXPECTED_METHOD = 4004

ERROR_UNIQUE_CONSTRAINT_USERNAME = 4010
ERROR_UNIQUE_CONSTRAINT_MAIL_TOKEN = 4011
ERROR_OVER_WHILE = 4012
ERROR_UNEXPECTED = 4013


USERNAME_MAX_LENGTH = 30
USERNAME_MIN_LENGTH = 4
USERNAME_DIGIT_MIN_LENGTH = 8

USER_FULL_NAME_MAX_LENGTH = 30
USER_FULL_NAME_MIN_LENGTH = 1

USER_EMAIL_MAX_LENGTH = 255

USER_PASSWORD_MIN_LENGTH = 6
USER_PASSWORD_MAX_LENGTH = 128

VALIDATE_OK = 1100
VALIDATE_FAILED = 1400

USER_USERNAME_VALIDATE_REGEX_PROBLEM = 1001
USER_USERNAME_VALIDATE_LENGTH_PROBLEM = 1002
USER_USERNAME_VALIDATE_DIGIT_PROBLEM = 1003
USER_USERNAME_VALIDATE_BANNED_PROBLEM = 1004

USER_FULL_NAME_VALIDATE_LENGTH_PROBLEM = 2002


USER_EMAIL_VALIDATE_REGEX_PROBLEM = 3001
USER_EMAIL_VALIDATE_LENGTH_PROBLEM = 3002
USER_EMAIL_EXIST_PROBLEM = 3007

USER_PASSWORD_VALIDATE_SELF_EQUAL_PROBLEM = 4005
USER_PASSWORD_VALIDATE_USERNAME_EQUAL_PROBLEM = 4006
USER_PASSWORD_VALIDATE_LENGTH_PROBLEM = 4002
USER_PASSWORD_VALIDATE_BANNED_PROBLEM = 4004


USERNAME_PREFIX_LIST = ["love", "hope", "brave", "cool", "great", "nice", "super", "wise"]

USER_CREATED = 1111
USER_CREATE_FAILED = 1444
EMAIL_SENT = 1112

# authentication

AUTH_EMAIL_NOT_EXIST = 20002
AUTH_USERNAME_NOT_EXIST = 20003
AUTH_USER_NOT_EXIST = 20004

# response pro con

SUCCEED_RESPONSE = 10002
FAILED_RESPONSE = 10004
INVALID_TOKEN = 10008


# post opts

DEFAULT_PING = 1
TO_CLICK = 2

# fcm push

FCM_OPT_NOTICE_REACT = "fcm_opt_notice_react"
FCM_OPT_NOTICE_COMMENT = "fcm_opt_notice_comment"
FCM_OPT_NOTICE_FOLLOW = "fcm_opt_notice_follow"
FCM_OPT_POST = "fcm_opt_post"

# log

LOG_POST = "log_post"
LOG_COMMENT = "log_post_comment"
LOG_REACT = "log_react"
LOG_FOLLOW = "log_follow"
LOG_GET_INIT_FEED = "log_get_init_feed"
LOG_GET_FOLLOWING_FEED = "log_get_following_feed"
LOG_GET_RECEIVED_FEED = "log_get_received_feed"

