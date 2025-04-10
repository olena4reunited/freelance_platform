from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreatePaymentRequest(_message.Message):
    __slots__ = ("payment",)
    PAYMENT_FIELD_NUMBER: _ClassVar[int]
    payment: str
    def __init__(self, payment: _Optional[str] = ...) -> None: ...

class PaymentRequest(_message.Message):
    __slots__ = ("payment_id",)
    PAYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    payment_id: int
    def __init__(self, payment_id: _Optional[int] = ...) -> None: ...

class UserRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    def __init__(self, user_id: _Optional[int] = ...) -> None: ...

class UserPaymentRequest(_message.Message):
    __slots__ = ("user_id", "payment_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    payment_id: int
    def __init__(self, user_id: _Optional[int] = ..., payment_id: _Optional[int] = ...) -> None: ...

class PaymentResponse(_message.Message):
    __slots__ = ("id", "payment")
    ID_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_FIELD_NUMBER: _ClassVar[int]
    id: int
    payment: str
    def __init__(self, id: _Optional[int] = ..., payment: _Optional[str] = ...) -> None: ...

class PaymentDetailResponse(_message.Message):
    __slots__ = ("id", "payment", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    payment: str
    user_id: int
    def __init__(self, id: _Optional[int] = ..., payment: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

class PaymentListResponse(_message.Message):
    __slots__ = ("payments",)
    PAYMENTS_FIELD_NUMBER: _ClassVar[int]
    payments: _containers.RepeatedCompositeFieldContainer[PaymentDetailResponse]
    def __init__(self, payments: _Optional[_Iterable[_Union[PaymentDetailResponse, _Mapping]]] = ...) -> None: ...

class PaymentListResponsePerUser(_message.Message):
    __slots__ = ("payments",)
    PAYMENTS_FIELD_NUMBER: _ClassVar[int]
    payments: _containers.RepeatedCompositeFieldContainer[PaymentResponse]
    def __init__(self, payments: _Optional[_Iterable[_Union[PaymentResponse, _Mapping]]] = ...) -> None: ...
