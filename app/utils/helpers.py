from fastapi import Request

def is_api_request(request: Request) -> bool:
    return request.url.path.startswith("/api")