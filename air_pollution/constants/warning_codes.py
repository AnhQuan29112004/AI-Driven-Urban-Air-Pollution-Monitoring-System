class WarningCodes:
    # Default
    DEFAULT = (0, "")

    @classmethod
    def get_warning(cls, message):
        return getattr(cls, message, cls.DEFAULT)