"""
Utils
"""
from bson import json_util
import json

from fastapi import Response

def JsonResponse(data, status):
    return Response(content=json.dumps(data, default=json_util.default), media_type="application/json", status_code=status)