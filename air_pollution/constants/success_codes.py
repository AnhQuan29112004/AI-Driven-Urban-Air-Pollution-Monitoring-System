class SuccessCodes:
    # Default
    DEFAULT = (0, "")
    

    # User
    LOGIN = ("AU_S_001", "Login successfully!")
    GET_USER = ("GET_USER", "Get user successfully!")
    USER_INFOR = ("USER_INFOR", "User infor")
    GET_USER = ("GET_USER", "Get user successfully!")
    LOGOUT = ("AU_S_002", "Loogut successfully!")
    REGISTER = ("AU_S_003", "Register successfully!")
    ADMIN_CREATE_USER = ("CREATE_USER", "Register user successfully!")
    UPDATE_USER_PROFILE = ("UPDATE_USER_PROFILE", "Update User profile successfully!")
    LIST_USER = ("LIST_USER", "users")
    CREATE_USER = ("CREATE_USER", "User create successfully!")
    UPDATE_USER = ("UPDATE_USER", "User update successfully!")
    UPLOAD_AVATAR = ("UPLOAD_AVATAR", "Upload avatar successfully!")
    DELETE_USER = ("DELETE_USER", "User delete successfully!")
    CHANGE_PASSWORD = ("CHANGE_PASSWORD", "Change Password successfully!")
    ADMIN_INFOR = ("ADMIN_INFOR", "admin_infor")

    # token
    REFRESH_TOKEN = ("AU_S_003", "Token refreshed successfully")

    # Permission
    ASSIGN_PERMISSION = ("AU_S_004", "Permission assigned successfully")
    LIST_PERMISSION = ("LIST_PERMISSION", "Permissions")
    CREATE_PERMISSION = ("CREATE_PERMISSION", "Permission create successfully!")
    UPDATE_PERMISSION = ("UPDATE_PERMISSION", "Permission update successfully!")
    DELETE_PERMISSION = ("DELETE_PERMISSION", "Permission delete successfully!")

    # Group
    LIST_GROUP = ("LIST_GROUP", "groups")
    CREATE_GROUP = ("CREATE_GROUP", "Group create successfully!")
    UPDATE_GROUP = ("UPDATE_GROUP", "Group update successfully!")
    DELETE_GROUP = ("DELETE_GROUP", "Group delete successfully!")

    # File
    LIST_FILE = ("LIST_FILE", "Files")
    CREATE_FILE = ("CREATE_FILE", "File create successfully!")
    UPDATE_FILE = ("UPDATE_FILE", "File update successfully!")
    DELETE_FILE = ("DELETE_FILE", "File delete successfully!")

    # Template
    DELETE_TEMPLATE = ("CF_S_006", "Successfully deleted the contact customer template")
    # EMail
    SEND_EMAIL_CHANGE_PASSWORD = (
        "SEND_EMAIL_CHANGE_PASSWORD",
        "Successfully send email!",
    )
    SEND_EMAIL_REGISTER_USER = (
        "SEND_EMAIL_REGISTER_USER",
        "Send email register to user successfully!",
    )
    RE_SEND_EMAIL_REGISTER_USER = (
        "RE_SEND_EMAIL_REGISTER_USER",
        "Re send email register to user!",
    )
    # TABLE
    TABLE_TYPE_AND_RELATION = ("TABLE_TYPE_AND_RELATION", "Table type and relation")
    LIST_TABLE = ("LIST_TABLE", "List table")
    ALL_TABLE = ("ALL_TABLE", "All table")
    CUSTOMER_TABLE = ("CUSTOMER_TABLE", "Customer table")
    CREATE_TABLE = ("CREATE_TABLE", "Table create successfully!")
    UPDATE_TABLE = ("UPDATE_TABLE", "Table update successfully!")
    DELETE_TABLE = ("DELETE_TABLE", "Table delete successfully!")
    
    # COMPANY
    LIST_COMPANY = ("LIST_COMPANY", "List Company")
    CREATE_COMPANY = ("CREATE_COMPANY", "Company create successfully!")
    UPDATE_COMPANY = ("UPDATE_COMPANY", "Company update successfully!")
    DELETE_COMPANY = ("DELETE_COMPANY", "Company delete successfully!")

    # RECORD
    ALL_RECORDS = ("ALL_RECORDS", "Get all records successfully!")
    GET_RECORD = ("GET_RECORD", "Get record successfully!")
    CREATE_RECORD = ("CREATE_RECORD", "Record create successfully!")
    UPDATE_RECORD = ("UPDATE_RECORD", "Record update successfully!")
    DELETE_RECORD = ("DELETE_RECORD", "Record delete successfully!")

    # FIELD
    LIST_FIELD = ("LIST_FIELD", "List field")
    CREATE_FIELD = ("CREATE_FIELD", "Field create successfully!")
    ASSIGN_FIELD = ("ASSIGN_FIELD", "Field assign successfully!")
    UPDATE_FIELD = ("UPDATE_FIELD", "Field update successfully!")
    DELETE_FIELD = ("DELETE_FIELD", "Field delete successfully!")

    # SECTION
    CREATE_SECTION = ("CREATE_SECTION", "Section create successfully!")
    UPDATE_SECTION = ("UPDATE_SECTION", "Section update successfully!")
    DELETE_SECTION = ("DELETE_SECTION", "Section delete successfully!")

    # Excel
    IMPORT_EXCEL = ("IMPORT_EXCEL", "Import excel successfully!")
    EXPORT_EXCEL = ("EXPORT_EXCEL", "Export excel successfully!")



    # SOURCE
    CREATE_SOURCE = ("CREATE_SOURCE", "Source create successfully!")
    UPDATE_SOURCE = ("UPDATE_SOURCE", "Source update successfully!")
    DELETE_SOURCE = ("DELETE_SOURCE", "Source delete successfully!")
    LIST_SOURCE = ("LIST_SOURCE", "List source")
    
    # BUSINESS TYPE
    CREATE_BUSINESS_TYPE = ("CREATE_BUSINESS_TYPE", "Business type create successfully!")
    UPDATE_BUSINESS_TYPE = ("UPDATE_BUSINESS_TYPE", "Business type update successfully!")
    DELETE_BUSINESS_TYPE = ("DELETE_BUSINESS_TYPE", "Business type delete successfully!")
    LIST_BUSINESS_TYPE = ("LIST_BUSINESS_TYPE", "List Business type")

    # LOCATIOH
    VIETNAM_LOCATION = ("VIETNAM_LOCATION", "VietNam Location")
    #

    #LOGIN HISTORY
    LOGIN_HISTORY_SUCCESS = ("LOGIN_HISTORY_SUCCESS","Loading login history successfully!")
    
    @classmethod
    def get_success(cls, message):
        return getattr(cls, message, cls.DEFAULT)
