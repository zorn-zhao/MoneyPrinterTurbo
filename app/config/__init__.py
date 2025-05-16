import os
import sys
from loguru import logger

_config_ready = False
_logger_initialized = False

def _init_config():
    global _config_ready, config
    if not _config_ready:
        from .config import config as _config  # 延迟导入
        config = _config
        _config_ready = True
    return config

def __init_logger():
    global _logger_initialized
    if _logger_initialized:
        return
        
    try:
        conf = _init_config()
        _lvl = getattr(conf, "log_level", "INFO")  # 安全访问属性
        
        root_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        )

        def format_record(record):
            file_path = record["file"].path
            relative_path = os.path.relpath(file_path, root_dir)
            record["file"].path = f"./{relative_path}"
            _format = (
                "<green>{time:%Y-%m-%d %H:%M:%S}</> | "
                + "<level>{level}</> | "
                + '"{file.path}:{line}":<blue> {function}</> '
                + "- <level>{message}</>"
                + "\n"
            )
            return _format

        logger.remove()
        logger.add(
            sys.stdout,
            level=_lvl,
            format=format_record,
            colorize=True,
        )
        _logger_initialized = True
    except Exception as e:
        logger.error(f"Logger init failed: {str(e)}")
        raise

# 显式初始化接口
def init_all():
    _init_config()
    __init_logger()

# 默认初始化（旧代码兼容）
init_all()
