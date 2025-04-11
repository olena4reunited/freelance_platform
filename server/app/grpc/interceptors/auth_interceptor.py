import grpc

from server.app.controllers.user_controller import UserController


class AuthInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        meta = dict(handler_call_details.invocation_metadata)
        auth_headers = meta.get("Authorization")

        if not auth_headers:
            context = grpc.ServicerContext()
            context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Missing authentication token",
            )

        try:
            token = auth_headers.decode("utf-8").split(" ")[1]
            user = UserController.get_user_by_token(token)
            handler_call_details.invocation_metadata.append(
                ("user_username", str(user["username"])),
                ("user_plan", str(user["plan_name"])),
            )
            return continuation(handler_call_details)
        except Exception as e:
            context = grpc.ServicerContext()
            context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Invalid authentication token",
            )
