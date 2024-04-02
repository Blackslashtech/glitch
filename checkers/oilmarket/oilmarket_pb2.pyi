from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SignRequest(_message.Message):
    __slots__ = ("api_key", "request")
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    api_key: str
    request: bytes
    def __init__(self, api_key: _Optional[str] = ..., request: _Optional[bytes] = ...) -> None: ...

class SignResponse(_message.Message):
    __slots__ = ("signature",)
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    signature: bytes
    def __init__(self, signature: _Optional[bytes] = ...) -> None: ...

class SellRequest(_message.Message):
    __slots__ = ("api_key", "buyer", "attester", "request", "signature")
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    BUYER_FIELD_NUMBER: _ClassVar[int]
    ATTESTER_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    api_key: str
    buyer: str
    attester: str
    request: bytes
    signature: bytes
    def __init__(self, api_key: _Optional[str] = ..., buyer: _Optional[str] = ..., attester: _Optional[str] = ..., request: _Optional[bytes] = ..., signature: _Optional[bytes] = ...) -> None: ...

class SellResponse(_message.Message):
    __slots__ = ("flag",)
    FLAG_FIELD_NUMBER: _ClassVar[int]
    flag: str
    def __init__(self, flag: _Optional[str] = ...) -> None: ...

class CreateBuyerRequest(_message.Message):
    __slots__ = ("name", "flag", "attesters")
    NAME_FIELD_NUMBER: _ClassVar[int]
    FLAG_FIELD_NUMBER: _ClassVar[int]
    ATTESTERS_FIELD_NUMBER: _ClassVar[int]
    name: str
    flag: str
    attesters: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., flag: _Optional[str] = ..., attesters: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateAttesterRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class CreateSellerRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class ApiKeyResponse(_message.Message):
    __slots__ = ("api_key",)
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    api_key: str
    def __init__(self, api_key: _Optional[str] = ...) -> None: ...

class AddBarrelRequest(_message.Message):
    __slots__ = ("api_key",)
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    api_key: str
    def __init__(self, api_key: _Optional[str] = ...) -> None: ...

class AddBarrelResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...
