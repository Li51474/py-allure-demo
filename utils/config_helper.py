import yaml, os, json
from jsonpath_ng import parse

_CONF = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
_CACHE = {}

def get_var(key):
    return _CACHE.setdefault(key, yaml.safe_load(open(_CONF, encoding='utf-8') or {}).get(key))

def save_var(key, value):
    _CACHE[key] = value
    yaml.dump(_CACHE, open(_CONF, 'w', encoding='utf-8'), allow_unicode=True)

def extract_by_json(resp, path):
    return next((x.value for x in parse(path).find(json.loads(resp))), None)