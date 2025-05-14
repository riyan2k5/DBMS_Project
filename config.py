import configparser
import os


def load_config():
    config = configparser.ConfigParser()
    config_file = 'config.ini'

    if not os.path.exists(config_file):
        config['DATABASE'] = {
            'dbname': 'ProjectDB',
            'user': 'postgres',
            'password': '2023494',
            'host': 'localhost'
        }

        with open(config_file, 'w') as f:
            config.write(f)
        print(f"Created default config file: {config_file}")

    config.read(config_file)

    return {
        'dbname': config.get('DATABASE', 'dbname'),
        'user': config.get('DATABASE', 'user'),
        'password': config.get('DATABASE', 'password'),
        'host': config.get('DATABASE', 'host')
    }


DB_PARAMS = load_config()