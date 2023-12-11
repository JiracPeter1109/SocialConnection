"""
config
"""
from pathlib import Path

from dynaconf import Dynaconf

_settings_files = [
    Path(__file__).parent / 'settings.yml',
]

# 变量在项目中传递
settings = Dynaconf(
    envvar_prefix=False,
    settings_files=_settings_files,
    load_dotenv=False,
    lowercase_read=False
)
