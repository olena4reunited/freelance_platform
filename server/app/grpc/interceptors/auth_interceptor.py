import traceback

import grpc

from server.app.controllers.user_controller import UserController
from server.app.grpc.utils.context import (
    user_id_var, 
    user_username_var, 
    user_plan_var
)
from server.app.utils.logger import logger


class AuthInterceptor(grpc.aio.ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        meta = dict(handler_call_details.invocation_metadata)
        auth_headers = meta.get("authorization")

        try:
            if not auth_headers:
                logger.error("Missing authentication token")
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNAUTHENTICATED,
                    details="Auth token missing",
                    initial_metadata=None,
                    trailing_metadata=None
                )
                return await continuation(handler_call_details)

            token = auth_headers.split(" ")[1]
            user = UserController.get_user_by_token(token)
        
            if not user:
                logger.error("Invalid authentication token")
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNAUTHENTICATED,
                    details="Invalid auth token",
                    initial_metadata=None,
                    trailing_metadata=None
                )
                return await continuation(handler_call_details)

            user_id_var.set(user["id"])
            user_username_var.set(user["username"])
            user_plan_var.set(user["plan_name"])            
        except Exception as e:
            logger.error(f"Error during authentication: {e}")    
            grpc.aio.AioRpcError(
                code=grpc.StatusCode.UNAUTHENTICATED,
                details="Authentication processing failed",
                initial_metadata=None,
                trailing_metadata=None
            )
    
        return await continuation(handler_call_details)
