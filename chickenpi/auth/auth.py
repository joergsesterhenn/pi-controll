import os
from typing import Optional

import firebase_admin
from fastapi import Header, HTTPException, status
from firebase_admin import auth, credentials
from firebase_admin.exceptions import FirebaseError
from pydantic import BaseModel


def init_auth():
    SERVICE_ACCOUNT_PATH = os.environ.get(
        "FIREBASE_SERVICE_ACCOUNT_KEY_PATH", "path/to/your-key-file.json"
    )
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        raise FileNotFoundError(
            f"Firebase service account key file not found at: {SERVICE_ACCOUNT_PATH}. "
            "Please provide the correct path."
        )

    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
    except ValueError as e:
        raise ValueError(f"Error initializing Firebase Admin SDK: {e}")


class FirebaseUser(BaseModel):
    uid: str
    name: Optional[str]


async def verify_firebase_token(authorization: str = Header(...)) -> FirebaseUser:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be 'Bearer <token>'.",
        )

    id_token = authorization.split(" ", 1)[1]
    try:
        decoded = auth.verify_id_token(id_token)
        return FirebaseUser(**decoded)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    except FirebaseError as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {e}")
