from starlette.types import ASGIApp, Receive, Scope, Send
from app.config.database import AsyncSessionLocal
from app.services.user_service import UserService
from app.utils.auth import verify_user_token
import http.cookies

class AuthMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Ensure "state" dictionary exists
        if "state" not in scope:
            scope["state"] = {}
        scope["state"]["user"] = None

        # Parse headers
        headers = dict(scope.get("headers", []))
        token = None

        # 1. Check Authorization: Bearer <token>
        auth_header = headers.get(b"authorization", b"").decode("utf-8")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

        # 2. Check Cookie: access_token=<token>
        if not token:
            cookie_header = headers.get(b"cookie", b"").decode("utf-8")
            if cookie_header:
                cookie = http.cookies.SimpleCookie(cookie_header)
                if "access_token" in cookie:
                    token = cookie["access_token"].value

        if token:
            try:
                payload = verify_user_token(token)
                user_id = payload.get("sub")
                if user_id:
                    async with AsyncSessionLocal() as db:
                        user_service = UserService(db)
                        user = await user_service.get(int(user_id))
                        if user:
                            scope["state"]["user"] = user
            except Exception:
                pass

        await self.app(scope, receive, send)
