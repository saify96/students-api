import json
from typing import Any

from fastapi import Response
from fastapi.encoders import jsonable_encoder


class JSONResponse(Response):
    media_type = 'application/json'

    def render(self, content: Any) -> bytes:
        if not content:
            self.media_type = ''
            return b''

        return json.dumps(jsonable_encoder(content),
                          ensure_ascii=False,
                          allow_nan=False,
                          indent=None,
                          separators=(",", ":")).encode('utf8')
