import grpc
from concurrent import futures

from generated import payments_pb2_grpc
from services.payments_service import PaymentsService
from server.app.utils.logger import logger


async def serve():
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=None
    )

    payments_pb2_grpc.add_PaymentsServiceServicer_to_server(
        PaymentsService(), 
        server
    )

    server.add_insecure_port('[::]:50051')
    logger.info("gRPC server started on port 50051")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    import asyncio
    asyncio.run(serve())
