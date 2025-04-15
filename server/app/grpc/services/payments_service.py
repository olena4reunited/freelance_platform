from google.protobuf import empty_pb2

from server.app.grpc.generated.payments_pb2_grpc import PaymentsServiceServicer
from server.app.grpc.generated import payments_pb2
from server.app.grpc.utils.dependencies import required_permissions
from server.app.controllers.payment_controller import PaymentController
from server.app.validators.payment_validators import PaymentValidator
from server.app.grpc.utils.context import user_id_var
from server.app.grpc.utils.exception_handler import handle_exceptions


class PaymentsService(PaymentsServiceServicer):
    @handle_exceptions
    @required_permissions(["create_payment", "read_own_payment_list", "read_own_payment_details"])
    async def CreatePayment(self, request: payments_pb2.CreatePaymentRequest, context):
        user_id = int(user_id_var.get())
        result = PaymentController.create_payment(user_id=user_id, payment_data=request.payment)
        
        return payments_pb2.PaymentResponse(**result)
    
    @handle_exceptions
    @required_permissions(["read_own_payment_list"])
    async def GetAllUserPayments(self, request: empty_pb2.Empty, context):
        user_id = int(user_id_var.get())
        result = PaymentController.get_user_payments(user_id=user_id)

        return payments_pb2.PaymentListResponsePerUser(payments=result)

    @handle_exceptions
    @required_permissions(["read_own_payment_list", "read_own_payment_details"])
    async def GetPayment(self, request: payments_pb2.PaymentRequest, context):
        user_id = int(user_id_var.get())
        
        PaymentValidator(payment_id=request.payment_id) \
        .validate_payment_ownership(user_id=user_id)
        
        result = PaymentController.get_payment(payment_id=request.payment_id)

        return payments_pb2.PaymentResponse(**result)
    
    @handle_exceptions
    @required_permissions(["read_own_payment_details", "delete_own_payment"])
    async def DeletePayment(self, request: payments_pb2.PaymentRequest, context):  
        user_id = int(user_id_var.get())
        
        PaymentValidator(payment_id=request.payment_id) \
        .validate_payment_ownership(user_id=user_id)
        
        PaymentController.delete_payment(payment_id=request.payment_id)

        return empty_pb2.Empty()
    
    @handle_exceptions
    @required_permissions(["read_all_users_payments"])
    async def AdminGetAllUsersPayments(self, request: empty_pb2, context):
        result = PaymentController.get_all_users_payments()

        return payments_pb2.PaymentListResponse(payments=result)
    
    @handle_exceptions
    @required_permissions(["read_all_users_payments", "read_user_payments"])
    async def AdminGetAllUserPayments(self, request: payments_pb2.UserRequest, context):
        result = PaymentController.get_user_payments(user_id=request.user_id)

        return payments_pb2.PaymentListResponsePerUser(payments=result)
    
    @handle_exceptions
    @required_permissions(["read_all_users_payments", "read_user_payments", "read_user_payment_details"])
    async def AdminGetUserPayment(self, request: payments_pb2.UserPaymentRequest, context):
        PaymentValidator(payment_id=request.payment_id) \
        .validate_payment_ownership(user_id=request.user_id)

        result = PaymentController.get_user_payment_details(payment_id=request.payment_id)

        return payments_pb2.PaymentDetailResponse(**result)
    
    @handle_exceptions
    @required_permissions(["read_all_users_payments", "read_user_payments", "read_user_payment_details", "delete_user_payment"])
    async def AdminDeleteUserPayment(self, request: payments_pb2.UserPaymentRequest, context):
        PaymentValidator(payment_id=request.payment_id) \
        .validate_payment_ownership(user_id=request.user_id)
        
        PaymentController.delete_payment(payment_id=request.payment_id)

        return empty_pb2.Empty()
