import os
import importlib

# Lấy thư mục hiện tại (thư mục models)
models_dir = os.path.dirname(__file__)

# Lặp qua tất cả file .py trong folder models (trừ __init__.py)
for filename in os.listdir(models_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"{__package__}.{filename[:-3]}"  # -> app_name.models.user
        importlib.import_module(module_name)
