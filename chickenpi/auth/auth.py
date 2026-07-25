import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated

import firebase_admin
import sentry_sdk
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


def init_auth():
    SERVICE_ACCOUNT_PATH = os.environ.get(
        "FIREBASE_SERVICE_ACCOUNT_KEY_PATH", "path/to/your-key-file.json"
    )
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        logger.error("no service account")
        raise FileNotFoundError(
            f"Firebase service account key file not found at: {SERVICE_ACCOUNT_PATH}. "
            "Please provide the correct path."
        )

    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
    except ValueError as e:
        logger.exception()
        raise ValueError(f"Error initializing Firebase Admin SDK: {e}")


class FirebaseUser(BaseModel):
    uid: str
    name: str | None


bearer_scheme = HTTPBearer()


async def verify_firebase_token(
    creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> FirebaseUser:
    id_token = creds.credentials

    try:
        decoded = auth.verify_id_token(id_token)
        user = FirebaseUser(**decoded)
        sentry_sdk.set_user({"id": user.uid, "name": user.name})
        return user
    except (
        ValidationError,
        ValueError,
        auth.InvalidIdTokenError,
        auth.ExpiredIdTokenError,
        auth.RevokedIdTokenError,
        auth.CertificateFetchError,
        auth.UserDisabledError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {e}",
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    try:
        init_auth()
        logger.info("Firebase Admin initialized successfully.")
    except Exception:
        logger.exception("Failed to initialize Firebase Admin:")
        raise

    yield  # === app is now running ===

    # --- Shutdown (optional) ---
    logger.info("Shutting down application.")
