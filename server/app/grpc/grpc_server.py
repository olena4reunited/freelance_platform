import asyncio

import grpc

from server.app.grpc.generated import payments_pb2_grpc
from server.app.grpc.interceptors.auth_interceptor import AuthInterceptor
from server.app.grpc.services.payments_service import PaymentsService
from server.app.utils.logger import logger


async def serve():
    server = grpc.aio.server(interceptors=[AuthInterceptor()])

    payments_pb2_grpc.add_PaymentsServiceServicer_to_server(
        PaymentsService(), 
        server
    )

    server.add_insecure_port('[::]:50051')
    logger.info("gRPC AsyncIO server started on port 50051")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
