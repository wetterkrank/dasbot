from dynaconf import Dynaconf

# TODO: support test environment
settings = Dynaconf(
    environments=["default", "production", "development"],
    settings_file="settings.toml",
    load_dotenv=True,
)
