import json
from bson import json_util


def decodeResponse(data):
    raw_data = data.read()
    encoding = data.info().get_content_charset('utf8')
    data = json.loads(raw_data.decode(encoding))
    return data

def parse_json(data):
    return json.loads(json_util.dumps(data))