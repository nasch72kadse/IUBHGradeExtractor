import yaml
import re
from datetime import datetime, timedelta
from collections import Counter
import pandas as pd
from connection import GradeConnection


def parse_yaml(yaml_file):
    """
        Parse yaml file to object and return it
        :param: yaml_file: path to yaml file
        :return: yaml_object
    """
    with open(yaml_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return False


def create_connection_object(yaml_object):
    con = GradeConnection(
        yaml_object['username'],
        yaml_object['password'],
        yaml_object['telegram_token']
    )
    return con
