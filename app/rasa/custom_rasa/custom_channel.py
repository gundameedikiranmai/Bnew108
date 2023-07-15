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
        metadata = request.json.get("metadata", None)
        print(metadata)
        return metadata