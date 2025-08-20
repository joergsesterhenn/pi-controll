from fastapi import FastAPI, Depends, HTTPException, status, Header
from typing import Annotated
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.exceptions import FirebaseError
import os
import json

SERVICE_ACCOUNT_PATH = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY_PATH", "path/to/your-key-file.json")

# Ensure the service account key file exists before trying to initialize.
if not os.path.exists(SERVICE_ACCOUNT_PATH):
    raise FileNotFoundError(
        f"Firebase service account key file not found at: {SERVICE_ACCOUNT_PATH}. "
        "Please provide the correct path."
    )

try:
    # Initialize the Firebase Admin SDK with the service account credentials.
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)
except ValueError as e:
    raise ValueError(f"Error initializing Firebase Admin SDK: {e}")


# --- Dependency to Verify Firebase Token ---
async def verify_firebase_token(authorization: Annotated[str, Header()]):
    """
    A FastAPI dependency function that verifies the Firebase ID token.
    It's used on endpoints to ensure the user is authenticated.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be provided with 'Bearer' schema."
        )
    
    # Extract the token from the "Bearer <token>" string.
    id_token = authorization.split(" ")[1]

    try:
        # Use the Firebase Admin SDK to verify the token.
        # This checks the token's signature, expiration, and other claims.
        decoded_token = auth.verify_id_token(id_token)
        # The decoded_token is a dictionary containing the user's information.
        return decoded_token
    except ValueError as e:
        # The token is invalid, e.g., malformed.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}"
        )
    except FirebaseError as e:
        # The token is expired, revoked, etc.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {e}"
        )

