import json
import os
from typing import Any, Optional

import boto3
import jwt
from jwt import PyJWKClient
from botocore.exceptions import ClientError


class AuthenticationError(Exception):
    """認証エラー"""
    pass


class AuthHelper:
    """Cognito JWT認証ヘルパークラス"""
    
    def __init__(self):
        self.user_pool_id = os.environ.get("USER_POOL_ID")
        self.app_client_id = os.environ.get("APP_CLIENT_ID")
        self.region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        
        if not self.user_pool_id or not self.app_client_id:
            raise ValueError("USER_POOL_ID and APP_CLIENT_ID must be set")
            
        # LocalStack環境の場合
        self.cognito_endpoint = os.environ.get("COGNITO_ENDPOINT")
        if self.cognito_endpoint:
            # LocalStackではJWKSエンドポイントが利用できないため、JWT検証をスキップ
            self.is_localstack = True
        else:
            self.is_localstack = False
            # JWKSクライアントの初期化
            jwks_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
            self.jwks_client = PyJWKClient(jwks_url)

    def verify_token(self, token: str) -> dict[str, Any]:
        """JWTトークンを検証し、ユーザー情報を返す"""
        try:
            if self.is_localstack:
                # LocalStack環境では簡易検証
                return self._verify_token_localstack(token)
            else:
                # AWS環境での正式なJWT検証
                return self._verify_token_aws(token)
        except Exception as e:
            raise AuthenticationError(f"Token verification failed: {str(e)}")

    def _verify_token_localstack(self, token: str) -> dict[str, Any]:
        """LocalStack環境での簡易トークン検証"""
        try:
            # LocalStackでは署名検証をスキップして、ペイロードのみをデコード
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            # 基本的な検証
            if decoded.get("aud") != self.app_client_id:
                raise AuthenticationError("Invalid audience")
                
            return {
                "user_id": decoded.get("sub"),
                "email": decoded.get("email"),
                "name": decoded.get("name", ""),
                "token_use": decoded.get("token_use", "access")
            }
        except jwt.DecodeError:
            raise AuthenticationError("Invalid token format")

    def _verify_token_aws(self, token: str) -> dict[str, Any]:
        """AWS環境での正式なJWT検証"""
        try:
            # JWTヘッダーからkidを取得
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header["kid"]
            
            # JWKSから公開鍵を取得
            signing_key = self.jwks_client.get_signing_key(kid)
            
            # JWTを検証
            decoded = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.app_client_id,
                issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"
            )
            
            return {
                "user_id": decoded.get("sub"),
                "email": decoded.get("email"),
                "name": decoded.get("name", ""),
                "token_use": decoded.get("token_use", "access")
            }
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")

    def extract_user_from_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Lambdaイベントからユーザー情報を抽出"""
        # API GatewayオーソライザーがセットしたrequestContextから取得
        request_context = event.get("requestContext", {})
        authorizer = request_context.get("authorizer", {})
        
        if authorizer:
            # Cognitoオーソライザーがセットした情報を使用
            claims = authorizer.get("claims", {})
            return {
                "user_id": claims.get("sub"),
                "email": claims.get("email"),
                "name": claims.get("name", "")
            }
        
        # フォールバック: Authorizationヘッダーから手動検証
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization") or headers.get("authorization")
        
        if not auth_header:
            raise AuthenticationError("No authorization header found")
            
        if not auth_header.startswith("Bearer "):
            raise AuthenticationError("Invalid authorization header format")
            
        token = auth_header[7:]  # "Bearer " を除去
        return self.verify_token(token)


def get_user_from_event(event: dict[str, Any]) -> dict[str, Any]:
    """Lambdaイベントからユーザー情報を取得するヘルパー関数"""
    # LocalStack環境では認証をスキップ
    environment = os.environ.get("ENVIRONMENT", "local")
    if environment == "local":
        return {
            "user_id": "local-user-123",
            "email": "test@example.com",
            "name": "Test User"
        }
    
    auth_helper = AuthHelper()
    return auth_helper.extract_user_from_event(event)


def require_auth(func):
    """認証が必要なLambda関数用のデコレーター"""
    def wrapper(event: dict[str, Any], context: Any) -> dict[str, Any]:
        try:
            user = get_user_from_event(event)
            event["user"] = user
            return func(event, context)
        except AuthenticationError as e:
            return {
                "statusCode": 401,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({
                    "error": str(e),
                    "code": "UNAUTHORIZED"
                })
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({
                    "error": "Authentication error",
                    "code": "INTERNAL_ERROR"
                })
            }
    
    return wrapper