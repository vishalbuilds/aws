import json
from datetime import datetime
from typing import Optional, Dict, Any


class ResponseBuilder(dict):
    SUCCESS_RESULT = "success"
    ERROR_RESULT = "error"

    def __init__(
        self,
        result: str,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        include_timestamp: bool = True
    ):
        if result not in [self.SUCCESS_RESULT, self.ERROR_RESULT]:
            raise ValueError(f"Invalid result: {result}")

        body = {
            "status": result
        }

        if message:
            body["message"] = message

        if data:
            body["data"] = data

        if meta is None:
            meta = {}

        if include_timestamp:
            meta["timestamp"] = datetime.utcnow().isoformat() + "Z"

        if meta:
            body["meta"] = meta

        response = {
            "statusCode": status_code or (200 if result == self.SUCCESS_RESULT else 500),
            "headers": headers or {"Content-Type": "application/json"},
            "body": json.dumps(body)
        }
        super().__init__(response)
