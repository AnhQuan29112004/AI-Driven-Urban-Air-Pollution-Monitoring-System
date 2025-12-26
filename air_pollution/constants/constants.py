class Constants:
    PATH_DB_MAP = {
        "/api/user/": "user",
        "/api/sp/": "user",
        "/api/excel/": "user",
        "/api/token/": "user",
        "/api/companies/": "user",
        "/api/social-media/": "user",
        "/api/department/": "user",
        "/api/permission/": "user",
        "/api/group/": "user",
        "/api/email/": "email",
        "/api/file/": "file",
        "/api/address/": "address",
        "/api/customer/": "customer",
        "/api/tables/": "dynamic_field",
        # "/api/tables/": "user",
    }

    LEVEL_LOG_CHOICES = [
        ("DEBUG", "Debug"),
        ("INFO", "Info"),
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
        ("CRITICAL", "Critical"),
    ]

    APP_LABEL_DB_MAP = {
        "user": "user",
        "email_integrated": "email",
        "file": "file",
        "address": "address",
        "customer": "customer",
        "dynamic_field": "dynamic_field",
    }
    USER_STATUS = (
        (1, "Active"),
        (2, "Inactive"),
        (3, "Waiting"),
    )
    NEWS_STATUS = (
        (1, "Waiting"),
        (2, "Accept"),
        (3, "Reject"),
    )
    ROLE = (
        (1, "Admin"),
        (2, "Mod"),
        (3, "User"),
    )
    APP_TYPE = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    APP_STATUS = (
        (1, "Active"),
        (2, "Inactive"),
        (3, "Disconnect"),
    )
    INDUSTRIES = [
        (1, "Finance"),
        (2, "Expand"),
        
    ]
    PRODCUT_CATEGORY_STATUS = (
        (1, "Display"),
        (2, "Hide"),
    )
    USER_RANK = (
        (1, "Silver"),
        (2, "Gold"),
        (3, "Platinum"),
        (4, "Diamond"),
        (5, "White"),

    )

    DATA_TYPES = [
        ("char", "Text"),
        ("varchar", "Variable Character"),
        ("integer", "Integer"),
        ("bigint", "Big Integer"),
        ("smallint", "Small Integer"),
        ("float", "Float"),
        ("double", "Double Precision Float"),
        ("decimal", "Decimal"),
        ("numeric", "Numeric"),
        ("boolean", "Boolean"),
        ("datetime", "DateTime"),
        ("timestamp", "Timestamp"),
        ("enum", "Enum"),
        ("array", "Array"),
    ]

    RELATION_TYPES = [
        ("foreignkey", "Foreign Key"),
        ("manytoone", "Many-to-One"),
        ("onetoone", "One-to-One"),
        ("manytomany", "Many-to-Many"),
        ("social_media", "Social-Media"),
    ]
    
    PRODUCT_STATUS = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out Of Stock'),
    ]


    CHANGE_PASSWORD = "CHANGE_PASSWORD"
    ADMIN_REGISTER_USER = "ADMIN_REGISTER_USER"
    USER_CREATE_NEWS = "USER_CREATE_NEWS"
    USER_UPDATE_NEWS = "USER_UPDATE_NEWS"
    USER_DELETE_NEWS = "USER_DELETE_NEWS"
    USER_UPDATE_NEWS_CATEGORY = "USER_UPDATE_NEWS_CATEGORY"
    USER_CREATE_NEWS_CATEGORY = "USER_CREATE_NEWS_CATEGORY"
    USER_DELETE_NEWS_CATEGORY = "USER_DELETE_NEWS_CATEGORY"
    USER_UPDATE_PRODUCT_CATEGORY = "USER_UPDATE_PRODUCT_CATEGORY"
    USER_CREATE_FEEDBACK = "USER_CREATE_FEEDBACK"
    USER_UPDATE_FEEDBACK = "USER_UPDATE_FEEDBACK"
    USER_DELETE_FEEDBACK = "USER_DELETE_FEEDBACK"
    USER_REGISTER = "USER_REGISTER"
    REGISTER = "REGISTER"
    EDIT_USER_PROFILE = "EDIT_USER_PROFILE"
    EMAIL_DEFAULT_TEMPLATE_ADMIN_REGISTER_USER = "Default Admin Register User Template"
    EMAIL_DEFAULT_FORGOT_PASSWORD_TEMPLATE = "Default Forgot Password Template"
    CHANGE_PASSWORD_TIME = 1800
    ATTEMPT_BLOCK_USER = 1800
    ADMIN_REGISTER_USER_TIME = 259200
    ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc", ".xlsx", ".xls"]
    MAX_FILE_SIZE_MB = 20
    ALLOWED_AVATAR_TYPES = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/bmp",
    "image/tiff",
    "image/webp",
    "image/svg+xml",  
    "image/apng"      
    ]
    ALLOWED_FILE_EXTENSIONS = ["pdf", "doc", "docx", "xls", "xlsx", "txt", "zip", "rar"]
    MAX_AVATAR_SIZE_MB = 5
    JWT_EXPIRATION = 1800
    