from rasa.core.channels.rest import RestInput
from sanic.request import Request
from typing import (
    Text,
    Dict,
    Any,
    Optional,
)

class RestInputCustom(RestInput):

    def get_metadata(self, request: Request) -> Optional[Dict[Text, Any]]:
        code = request.json.get("metadata", None)
        print(code)
        return code