from fastapi import Header, HTTPException

def require_token(
    authorization: str | None = Header(default=None)
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid format. Use 'Bearer ...'"
        )
    token = authorization.removeprefix("Bearer ").strip()
    return {"token": token, "user_id": 123}  # Dummy