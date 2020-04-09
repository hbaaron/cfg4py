import logging
import os
import sys

import fire
import yaml

from cfg4py import create_config, enable_logging

enable_logging()

resource_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'resources/'))


def build(config_dir: str):
    """
    Compile configuration files into a python class file, which is used by IDE's auto-complete function

    Args:
        config_dir: The folder where your configuration files located

    Returns:

    """
    import os
    import sys
    if not os.path.exists(config_dir):
        print(f"path {config_dir} not exists")
        sys.exit(-1)

    count = 0
    for f in os.listdir(config_dir):
        if f.startswith("default") or f.startswith("dev") or f.startswith("test") or f.startswith("production"):
            print(f"found {f}")
            count += 1

    if count > 0:
        print(f"{count} files found in total")
    else:
        print("the folder contains no valid configuration files")
        sys.exit(-1)

    try:
        # set server role temporarily
        os.environ["__cfg4py_server_role__"] = "DEV"

        create_config(config_dir)
        sys.path.insert(0, config_dir)
        # noinspection PyUnresolvedReferences
        from cfg4py_auto_gen import Config
        print(f"Config file is built with success and saved at {os.path.join(config_dir, 'cfg4py_auto_gen')}")
    except Exception as e:
        logging.exception(e)
        print("Config file built failure.")


def choose_dest_dir(dst):
    if dst is None:
        dst = input("Where should I save configuration files?\n")

    if os.path.exists(dst):
        for f in os.listdir(dst):
            if f in ['defaults.yaml', 'dev.yaml', 'test.yaml', 'production.yaml']:
                print(f"The folder provided already contains {f}, please choose clean one.")
                return None
        return dst
    else:
        create = input("Path not exists, create('Q' to exit)? [Y/n]")
        if create.upper() == 'Y':
            os.makedirs(dst, exist_ok=True)
            return dst
        elif create.upper() == 'Q':
            sys.exit(-1)
        else:
            return None


def scaffold(dst: str):
    print("Creating a configuration boilerplate:")
    dst = choose_dest_dir(dst)
    while dst is None:
        dst = choose_dest_dir(dst)

    with open(os.path.join(resource_path, 'template.yaml'), 'r') as f:
        templates = yaml.safe_load(f)

    print("Which flavors do you want?")
    print("-" * 20)
    prompt = """
    0  - console + rotating file logging
    10 - redis/redis-py (gh://andymccurdy/redis-py)
    11 - redis/aioredis (gh://aio-libs/aioredis)
    20 - mysql/PyMySQL (gh://PyMySQL/PyMySQL)
    30 - postgres/asyncpg (gh://MagicStack/asyncpg)
    31 - postgres/psycopg2 (gh://psycopg/psycopg2)
    40 - mq/pika (gh://pika/pika)
    50 - mongodb/pymongo (gh://mongodb/mongo-python-driver)
    """
    print(prompt)
    chooses = input("Please choose flavors by index, separated each by a comma(,):\n")
    flavors = {}
    mapping = {
        "0": "logging",
        "1": "redis",
        "2": "mysql",
        "3": "postgres",
        "4": "mq",
        "5": "mongodb"
    }
    for index in chooses.strip(' ').split(','):
        if index == "0":
            flavors["logging"] = templates["logging"]
            continue

        major = mapping[index[0]]
        try:
            minor = int(index[1])
            flavors[major] = list(templates[major][minor].values())[0]
        except (ValueError, IndexError):
            print(f"Wrong index {index}, skipped.")
            continue

    with open(os.path.join(dst, "defaults.yaml"), 'w') as f:
        f.writelines("#auto generated by Cfg4Py: https://github.com/jieyu-tech/cfg4py\n")
        yaml.dump(flavors, f)

    print(f"Cfg4Py has generated the following files under {dst}:")
    print("defaults.yaml")
    for name in ['dev.yaml', 'test.yaml', 'production.yaml']:
        with open(os.path.join(dst, name), 'w') as f:
            f.writelines("#auto generated by Cfg4Py: https://github.com/jieyu-tech/cfg4py\n")
            print(name)

    with open(os.path.join(dst, "defaults.yaml"), 'r') as f:
        print("Content in defaults.yaml")
        for line in f.readlines():
            print(line.replace('\n', ''))


def help():
    msg = """
    Welcome to Cfg4Py! Reach me at code@jieyu.ai for any suggestions/issues.

    support commands:
        [0] scaffold - generate basic settings, like logging, database access, etc.
        [1] build    - convert configuration into python code, for typing hinting.
        [2] help     - show this message
    """
    print(msg)

    commands = [scaffold, build, help]
    choose = input("Please input your command here(Q to quite):[2]")
    while choose.upper() != 'Q':
        try:
            idx = int(choose)
            cmd = commands[idx]
            cmd()
        except ValueError:
            print("Please give me the index number")
        except IndexError:
            print("The index number must be from 0 to 2!")


#if __name__ == "__main__":
def main():
    fire.Fire({
        "help":     help,
        "build":    build,
        "scaffold": scaffold
    })
