from constants.status_codes import StatusCodes


class ErrorCodes:
    # Default
    INVALID_NAME = (
        "INVALID_NAME",
        "INVALID_NAME",
        StatusCodes.BAD_REQUEST
    )
    INVALID_SIGNATURE = (
        "INVALID_SIGNATURE",
        "INVALID_SIGNATURE",
        StatusCodes.BAD_REQUEST
    )
    INVALID_PARAMS = (
        'INVALID_PARAMS',
        'INVALID_PARAMS',
        StatusCodes.BAD_REQUEST
    )
    UNKNOWN_ERROR = (
        "UNKNOWN_ERROR",
        "Unknown error occurred",
        StatusCodes.INTERNAL_SERVER_ERROR,
    )
    
    INVALID_FILTER_FIELD_CHOICE = (
        "INVALID_FILTER_FIELD_CHOICE",
        "Invalid filter field choice",
        StatusCodes.INTERNAL_SERVER_ERROR,
    )
    
    INVALID_REQUEST = (
        "INVALID_REQUEST",
        "Invalid request",
        StatusCodes.BAD_REQUEST,
    )
    INTERNAL_SERVER_ERROR = (
        "INTERNAL_SERVER_ERROR",
        "Internal server error",
        StatusCodes.INTERNAL_SERVER_ERROR,
    )

    # Common
    VALIDATION_ERROR = (
        "VALIDATION_ERROR",
        "Invalid input data",
        StatusCodes.BAD_REQUEST,
    )
    NOT_FOUND = (
        "NOT_FOUND",
        "Requested resource not found",
        StatusCodes.NOT_FOUND_STATUS,
    )
    PERMISSION_DENIED = (
        "PERMISSION_DENIED",
        "Operation not permitted",
        StatusCodes.FORBIDDEN,
    )
    PERMISSION_NOT_EXISTS = (
        "PERMISSION_NOT_EXISTS",
        "Permission not exists",
        StatusCodes.NOT_FOUND_STATUS,
    )
    AUTHENTICATION_FAILED = (
        "AU_E_006",
        "Authentication error",
        StatusCodes.UNAUTHORIZED,
    )
    UNAUTHORIZED = (
        "UNAUTHORIZED",
        "Unauthorized access",
        StatusCodes.UNAUTHORIZED,
    )
    METHOD_NOT_SUPORT = (
        "METHOD_NOT_SUPORT",
        "HTTP method not supported",
        StatusCodes.METHOD_NOT_ALLOWED,
    )
    RATE_LIMITED = ("RATE_LIMITED", "Too many requests", StatusCodes.BAD_REQUEST)
    ARRAY_ONLY = ("ARRAY_ONLY", "Value must be an array", StatusCodes.BAD_REQUEST)
    TYPE_ERROR = (
        "TYPE_ERROR",
        "The provided type not match with the required type.",
        StatusCodes.BAD_REQUEST,
    )
    METHOD_DOES_NOT_EXISTS = ("METHOD_DOES_NOT_EXISTS", "This method does not exist !")

    # field
    REQUEST_MISSING_REQUIRED_FIELDS = (
        "US_E_008",
        "The request is missing required field(s).",
        StatusCodes.BAD_REQUEST,
    )
    
    
    # User
    VALIDATION_NEW_PASSWORD = (
        "NEW_PASSWORD_NOT_VALID",
        "New password is not valid",
        StatusCodes.BAD_REQUEST,
    )
    CANNOT_CHANGE_PASSWORD = (
        "CANNOT_CHANGE_PASSWORD",
        "An error occurred while changing password",
        StatusCodes.INTERNAL_SERVER_ERROR
    )
    USER_NOT_FOUND = ("AU_E_005", "User not found", StatusCodes.NOT_FOUND_STATUS)
    CAN_NOT_DELETE_SUPER_UER = (
        "CAN_NOT_DELETE_SUPER_UER",
        "Cannot delete superuser(s).",
        StatusCodes.FORBIDDEN,
    )
    USER_ALREADY_EXISTS = (
        "USER_ALREADY_EXISTS",
        "User already exists",
        StatusCodes.BAD_REQUEST,
    )
    INVALID_PASSWORD = (
        "INVALID_PASSWORD",
        "Incorrect password",
        StatusCodes.BAD_REQUEST,
    )
    CURRENT_PASSWORD_REQUIRED = (
        "CURRENT_PASSWORD_REQUIRED",
        "Current password is required",
        StatusCodes.BAD_REQUEST,
    )

    INVALID_CURRENT_PASSWORD = (
        "INVALID_CURRENT_PASSWORD",
        "Incorrect current password",
        StatusCodes.BAD_REQUEST,
    )
    UPDATE_PROFILE_FAIL = (
        "UPDATE_PROFILE_FAIL",
        "Update profile fail",
        StatusCodes.BAD_REQUEST,
    )
    PASSWORD_ALREADY_USED = (
        "PASSWORD_ALREADY_USED",
        "Password already used. Please login now!",
        StatusCodes.BAD_REQUEST,
    )
    INVALID_USERNAME = ("INVALID_USERNAME", "Invalid username", StatusCodes.BAD_REQUEST)
    EMAIL_OR_USERNAME_REQUIRED = (
        "USER_ERROR_01",
        "Email or username and password are required",
        StatusCodes.BAD_REQUEST,
    )
    INCORRECT_UE_OR_PASSWORD = (
        "AU_E_001",
        "Invalid username or password",
        StatusCodes.BAD_REQUEST,
    )
    USER_INACTIVE = (
        "USER_INACTIVE",
        "User account is inactive",
        StatusCodes.BAD_REQUEST,
    )
    EDIT_PROFILE_FAIL = (
        "EDIT_PROFILE_FAIL",
        "Edit profile fail",
        StatusCodes.BAD_REQUEST,
    )
    ERROR_REGISTER_USER = (
        "ERROR_REGISTER_USER",
        "Error registeruser",
        StatusCodes.BAD_REQUEST,
    )
    LOGOUT_FAIL = ("LOGOUT_FAIL", "Loogut fail", StatusCodes.BAD_REQUEST)
    LOGIN_TOO_MANY_ATTEMPTS = (
        "LOGIN_TOO_MANY_ATTEMPTS",
        "Account temporarily locked due to too many incorrect entries.",
        StatusCodes.BAD_REQUEST,
    )
    USER_ALREADY_REGISTER = (
        "USER_ALREADY_REGISTER",
        "Your account is already registered. Please login now.",
        StatusCodes.BAD_REQUEST,
    )
    USERNAME_ALREADY_EXISTS = (
        "US_E_012",
        "Username already exists",
        StatusCodes.BAD_REQUEST,
    )
    EMAIL_ALREADY_EXISTS = ("US_E_014", "Email already exists", StatusCodes.BAD_REQUEST)
    PHONE_ALREADY_EXISTS = (
        "PHONE_ALREADY_EXISTS",
        "Phone number already exists",
        StatusCodes.BAD_REQUEST,
    )
    MISSING_REQUIRED_FIELD = (
        "MISSING_REQUIRED_FIELD",
        "A required field is missing",
        StatusCodes.BAD_REQUEST,
    )
    BLANK_NOT_ALLOWED = (
        "BLANK_NOT_ALLOWED",
        "Field cannot be blank",
        StatusCodes.BAD_REQUEST,
    )
    NULL_NOT_ALLOWED = (
        "NULL_NOT_ALLOWED",
        "Field cannot be null",
        StatusCodes.BAD_REQUEST,
    )
    INVALID_TYPE = ("INVALID_TYPE", "Invalid type for field", StatusCodes.BAD_REQUEST)
    INVALID_CHOICE = ("INVALID_CHOICE", "Invalid choice", StatusCodes.BAD_REQUEST)
    REGEX_VALIDATION_FAILED = (
        "REGEX_VALIDATION_FAILED",
        "Field does not match required format",
        StatusCodes.BAD_REQUEST,
    )
    INVALID_EMAIL = ("INVALID_EMAIL", "Email is invalid", StatusCodes.BAD_REQUEST)
    INVALID_PHONE = (
        "INVALID_PHONE",
        "Phone number is invalid",
        StatusCodes.BAD_REQUEST,
    )
    INVALID_AVATAR = (
        "INVALID_AVATAR",
        "Avatar is invalid. Only jpg, jpeg, png, gif, bmp, tiff, webp are allowed.",
        StatusCodes.BAD_REQUEST,
    )
    WEAK_PASSWORD = ("WEAK_PASSWORD", "Password is too weak", StatusCodes.BAD_REQUEST)
    MAX_AVATAR_SIZE_MB_EXCEEDED = (
        "MAX_AVATAR_SIZE_MB_EXCEEDED",
        "File size is too large",
        StatusCodes.BAD_REQUEST,
    )
    MAX_LENGTH_EXCEEDED = (
        "MAX_LENGTH_EXCEEDED",
        "Maximum length exceeded",
        StatusCodes.BAD_REQUEST,
    )
    MIN_LENGTH_NOT_MET = (
        "MIN_LENGTH_NOT_MET",
        "Minimum length not met",
        StatusCodes.BAD_REQUEST,
    )
    NEW_PASSWORD_REQUIRED = (
        "NEW_PASSWORD_REQUIRED",
        "New password are required",
        StatusCodes.BAD_REQUEST,
    )
    EMAIL_RESET_TOKEN_EXPIRED = (
        "EMAIL_RESET_TOKEN_EXPIRED",
        "Password reset link has expired",
        StatusCodes.BAD_REQUEST,
    )
    USER_REGISTER_FAILED = (
        "USER_REGISTER_FAILED",
        "Register Fail",
        StatusCodes.BAD_REQUEST,
    )
    PASSWORD_REQUIRED = (
        "PASSWORD_REQUIRED",
        "Password required",
        StatusCodes.BAD_REQUEST,
    )
    EMAIL_REGISTER_TOKEN_EXPIRED_OR_USED = (
        "EMAIL_REGISTER_TOKEN_EXPIRED_OR_USED",
        "Register link has expired or has already been used",
        StatusCodes.BAD_REQUEST,
    )
    RESET_EMAIL_ALREADY_SENT = (
        "RESET_EMAIL_ALREADY_SENT",
        "Password reset email has been sent. Please check your email (Sent every 30 minutes!)",
        StatusCodes.BAD_REQUEST,
    )
    OPERATION_FAILED = (
        "OPERATION_FAILED",
        "Failed to generate registration links for all users!",
        StatusCodes.BAD_REQUEST,
    )
    
    NOT_VERIFY_EMAIL_GOOGLE = (
        'Not_VERIFY_EMAIL_GOOGLE',
        "Email not verified by Google",
        StatusCodes.BAD_REQUEST,
    )
    

    # Kafka
    KAFKA_CONNECTION_ERROR = (
        "KAFKA_CONNECTION_ERROR",
        "Failed to connect to Kafka",
        StatusCodes.SERVICE_UNAVAILABLE,
    )
    KAFKA_CONSUME_ERROR = (
        "KAFKA_CONSUME_ERROR",
        "Error consuming Kafka message",
        StatusCodes.INTERNAL_SERVER_ERROR,
    )

    # JWT / Token
    TOKEN_EXPIRED = ("AU_E_003", "Token expired", StatusCodes.UNAUTHORIZED)
    INVALID_TOKEN = ("AU_E_002", "Invalid token", StatusCodes.UNAUTHORIZED)
    REFRESH_TOKEN_REQUIRED = (
        "REFRESH_TOKEN_REQUIRED",
        "Refresh token required",
        StatusCodes.BAD_REQUEST,
    )
    REFRESH_TOKEN_ERROR = (
        "REFRESH_TOKEN_ERROR",
        "Refresh token processing failed",
        StatusCodes.BAD_REQUEST,
    )

    @classmethod
    def get_error(cls, error_name):
        return getattr(cls, error_name, cls.UNKNOWN_ERROR)  






    # Department
    DEPARTMENT_EXITS = (
        "DEPARTMENT_EXITS",
        "Department with this name already exists.",
        StatusCodes.BAD_REQUEST,
    )
    DEPARTMENT_NOT_EXITS = (
        "DEPARTMENT_NOT_EXITS",
        "Department dont not Exits",
        StatusCodes.BAD_REQUEST,
    )
    DEPARTMENT_CREATE_ERROR = (
        "DEPARTMENT_CREATE_ERROR",
        "Department create fail",
        StatusCodes.BAD_REQUEST,
    )

    # Perrmission
    PERMISSION_REQUIRED = (
        "PERMISSION_REQUIRED",
        "Permission are required",
        StatusCodes.BAD_REQUEST,
    )

    # Group
    GROUP_NAME_REQUIRED = (
        "GROUP_NAME_REQUIRED",
        "Group name is required",
        StatusCodes.BAD_REQUEST,
    )
    GROUP_NOT_FOUND = (
        "GROUP_NOT_FOUND",
        "Group not found",
        StatusCodes.NOT_FOUND_STATUS,
    )
    GROUP_EXISTS = ("GROUP_EXISTS", "Group already exists.", StatusCodes.BAD_REQUEST)

    # Table
    TABLE_NOT_FOUND = (
        "TABLE_NOT_FOUND",
        "Table not found",
        StatusCodes.NOT_FOUND_STATUS,
    )
    TABLE_EXISTS = ("TABLE_EXISTS", "Table already exists.", StatusCodes.BAD_REQUEST)
    CREATE_TABLE = ("CREATE_TABLE", "Error create table!", StatusCodes.BAD_REQUEST)
    TABLE_NAME_AND_TYPE_AND_FIELDS_REQUIRED = (
        "TABLE_NAME_AND_TYPE_AND_FIELDS_REQUIRED",
        "Table name and type, fields is required!",
        StatusCodes.BAD_REQUEST,
    )
    TABLE_NAME_AND_TYPE_REQUIRED = (
        "TABLE_NAME_AND_TYPE_REQUIRED",
        "Table name and type is required!",
        StatusCodes.BAD_REQUEST,
    )
    INVALID_TEMPLATE_TYPE = (
        "INVALID_TEMPLATE_TYPE", "Template type invalid", StatusCodes.BAD_REQUEST
    )
    
    # Record
    DELETE_RECORD_FAIL = (
        "DELETE_RECORD_FAIL",
        "Delete record fail",
        StatusCodes.BAD_REQUEST,
    )
    RECORD_NOT_FOUND = (
        "RECORD_NOT_FOUND",
        "Record not foud",
        StatusCodes.BAD_REQUEST,
    )

    # Section
    DELETE_SECTION_FAIL = (
        "DELETE_SECTION_FAIL",
        "Delete Section fail",
        StatusCodes.BAD_REQUEST,
    )
    SECTION_NOT_FOUND = (
        "SECTION_NOT_FOUND",
        "Section not foud",
        StatusCodes.BAD_REQUEST,
    )

    # Field
    DELETE_FIELD_FAIL = (
        "DELETE_FIELD_FAIL",
        "Delete Field fail",
        StatusCodes.BAD_REQUEST,
    )
    CREATE_FIELD_FAIL = (
        "CREATE_FIELD_FAIL",
        "Create fields fail",
        StatusCodes.BAD_REQUEST,
    )
    FIELD_NOT_FOUND = (
        "FIELD_NOT_FOUND",
        "Field not foud",
        StatusCodes.BAD_REQUEST,
    )

    # Section
    CONTENT_TYPE_NOT_FOUND = (
        "CONTENT_TYPE_NOT_FOUND",
        "Content type not foud",
        StatusCodes.BAD_REQUEST,
    )
    SECTION_HAVE_FIELD = (
        "SECTION_HAVE_FIELD",
        "Each section must have at least one field",
        StatusCodes.BAD_REQUEST,
    )

    # Source
    CREATE_SOURCE_FAIL = (
        "CREATE_SOURCE_FAIL",
        "Create Source Fail",
        StatusCodes.BAD_REQUEST,
    )
    UPDATE_SOURCE_FAIL = (
        "UPDATE_SOURCE_FAIL",
        "Update Source Fail",
        StatusCodes.BAD_REQUEST,
    )
    DELETE_SOURCE_FAIL = (
        "DELETE_SOURCE_FAIL",
        "Delete Source Fail",
        StatusCodes.BAD_REQUEST,
    )
    
    # Business type
    CREATE_BUSINESS_TYPE_FAIL = (
        "CREATE_BUSINESS_TYPE_FAIL",
        "Create Business Type Fail",
        StatusCodes.BAD_REQUEST,
    )
    UPDATE_BUSINESS_TYPE_FAIL = (
        "UPDATE_BUSINESS_TYPE_FAIL",
        "Update Business Type Fail",
        StatusCodes.BAD_REQUEST,
    )
    DELETE_BUSINESS_TYPE_FAIL = (
        "DELETE_BUSINESS_TYPE_FAIL",
        "Delete Business Type Fail",
        StatusCodes.BAD_REQUEST,
    )


    #SSO user info
    MISSING_HEADER = (
        "MISSING_REQUIRED_HEADER",
        "Missing required headers.",
        StatusCodes.FORBIDDEN
    )

    INVALID_CLIENT_ID = (
        "INVALID_CLIENT_ID",
        "Invalid client ID.",
        StatusCodes.FORBIDDEN
    )
    HMAC_VERIFY = (
        "HMAC_VERIFY",
        "HMAC verify errors",
        StatusCodes.FORBIDDEN
    )

    @classmethod
    def get_error(cls, error_name):
        return getattr(cls, error_name, cls.UNKNOWN_ERROR)
