class Rediskeys:
    # USER
    def RESET_PASSWORD_EMAIL(email):
        return f"reset_password_email:{email}"

    def ADMIN_REGISTER_USER_EMAIL(email):
        return f"admin_register_user_email:{email}"

    def LOGIN_ATTEMPT(identifier):
        return f"login_attempt:{identifier}"

    def LOGIN_BLOCK(identifier):
        return f"login_block:{identifier}"

    #Admin Access Token
    def ADMIN_ACCESS_TOKEN_KEYCLOAK():
        return "admin_access_token"
    
    def USER(user_id):
        return f"user:{user_id}"