import os
import shutil
import socket
import tempfile
import types
import toml
from loguru import logger

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
config_file = os.getenv('CONFIG_FILE', f"{root_dir}/config.toml")

def safe_config_load(config_path):
    """安全加载配置文件"""
    if not os.path.exists(config_path):
        return {}
    try:
        return toml.load(config_path)
    except Exception as e:
        logger.warning(f"Load config failed (first attempt): {str(e)}")
        try:
            with open(config_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
                return toml.loads(content)
        except Exception as e2:
            logger.error(f"Failed to load config: {str(e2)}")
            return {}

def load_or_create_config():
    """加载或创建默认配置文件"""
    os.makedirs(os.path.dirname(config_file), exist_ok=True, mode=0o777)
    
    if not os.path.exists(config_file):
        example_file = f"{root_dir}/config.example.toml"
        if os.path.exists(example_file):
            logger.info("Creating config from example file")
            try:
                with tempfile.NamedTemporaryFile(
                    mode='w', 
                    dir=os.path.dirname(config_file),
                    delete=False,
                    encoding='utf-8'
                ) as tmp:
                    with open(example_file, 'r', encoding='utf-8') as f:
                        tmp.write(f.read())
                    os.chmod(tmp.name, 0o777)
                    os.replace(tmp.name, config_file)
            except Exception as e:
                logger.error(f"Failed to create config file: {str(e)}")
    return safe_config_load(config_file)

# 初始化全局配置
try:
    _cfg = load_or_create_config()
except Exception as e:
    logger.critical(f"Config initialization failed: {str(e)}")
    _cfg = {}

# 确保所有必需的配置项存在
_cfg.setdefault("app", {})
_cfg.setdefault("whisper", {})
_cfg.setdefault("proxy", {})
_cfg.setdefault("azure", {})
_cfg.setdefault("siliconflow", {})
_cfg.setdefault("ui", {"hide_log": False, "language": "en-US"})
_cfg.setdefault("log_level", "INFO")       # 确保日志级别存在
_cfg.setdefault("project_version", "1.2.6")  # 确保项目版本存在

# 创建config对象
config = types.SimpleNamespace()
config.log_level = _cfg["log_level"]
config.app = _cfg["app"]
config.whisper = _cfg["whisper"]
config.proxy = _cfg["proxy"]
config.azure = _cfg["azure"]
config.siliconflow = _cfg["siliconflow"]
config.ui = _cfg["ui"]
config.project_version = _cfg["project_version"]  # 确保项目版本可用

def save_config():
    """安全保存配置到文件"""
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            dir=os.path.dirname(config_file),
            delete=False,
            encoding='utf-8'
        ) as tmp:
            toml.dump(_cfg, tmp)
            os.chmod(tmp.name, 0o777)
            os.replace(tmp.name, config_file)
            return True
    except Exception as e:
        logger.error(f"Failed to save config: {str(e)}")
        return False

config.save_config = save_config
