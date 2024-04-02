from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FactorChallenge(_message.Message):
    __slots__ = ["n"]
    N_FIELD_NUMBER: _ClassVar[int]
    n: str
    def __init__(self, n: _Optional[str] = ...) -> None: ...

class FactorChallengeSubmission(_message.Message):
    __slots__ = ["factors"]
    FACTORS_FIELD_NUMBER: _ClassVar[int]
    factors: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, factors: _Optional[_Iterable[str]] = ...) -> None: ...

class Challenge(_message.Message):
    __slots__ = ["factor_challenge", "characteristic", "delta"]
    FACTOR_CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    CHARACTERISTIC_FIELD_NUMBER: _ClassVar[int]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    factor_challenge: FactorChallenge
    characteristic: int
    delta: int
    def __init__(self, factor_challenge: _Optional[_Union[FactorChallenge, _Mapping]] = ..., characteristic: _Optional[int] = ..., delta: _Optional[int] = ...) -> None: ...

class Contest(_message.Message):
    __slots__ = ["id", "author", "goal", "threshold", "challenges", "reward"]
    ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    GOAL_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    CHALLENGES_FIELD_NUMBER: _ClassVar[int]
    REWARD_FIELD_NUMBER: _ClassVar[int]
    id: str
    author: str
    goal: _containers.RepeatedScalarFieldContainer[int]
    threshold: _containers.RepeatedScalarFieldContainer[int]
    challenges: _containers.RepeatedCompositeFieldContainer[Challenge]
    reward: str
    def __init__(self, id: _Optional[str] = ..., author: _Optional[str] = ..., goal: _Optional[_Iterable[int]] = ..., threshold: _Optional[_Iterable[int]] = ..., challenges: _Optional[_Iterable[_Union[Challenge, _Mapping]]] = ..., reward: _Optional[str] = ...) -> None: ...

class EnrollmentFilter(_message.Message):
    __slots__ = ["contest_id", "user_id", "current_state"]
    CONTEST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_STATE_FIELD_NUMBER: _ClassVar[int]
    contest_id: str
    user_id: str
    current_state: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, contest_id: _Optional[str] = ..., user_id: _Optional[str] = ..., current_state: _Optional[_Iterable[int]] = ...) -> None: ...

class ContestCreateRequest(_message.Message):
    __slots__ = ["contest"]
    CONTEST_FIELD_NUMBER: _ClassVar[int]
    contest: Contest
    def __init__(self, contest: _Optional[_Union[Contest, _Mapping]] = ...) -> None: ...

class ContestCreateResponse(_message.Message):
    __slots__ = ["contest"]
    CONTEST_FIELD_NUMBER: _ClassVar[int]
    contest: Contest
    def __init__(self, contest: _Optional[_Union[Contest, _Mapping]] = ...) -> None: ...

class ContestGetRequest(_message.Message):
    __slots__ = ["id", "author"]
    ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    id: str
    author: str
    def __init__(self, id: _Optional[str] = ..., author: _Optional[str] = ...) -> None: ...

class ContestGetResponse(_message.Message):
    __slots__ = ["contest"]
    CONTEST_FIELD_NUMBER: _ClassVar[int]
    contest: Contest
    def __init__(self, contest: _Optional[_Union[Contest, _Mapping]] = ...) -> None: ...

class ContestEnrollRequest(_message.Message):
    __slots__ = ["enrollment_filter"]
    ENROLLMENT_FILTER_FIELD_NUMBER: _ClassVar[int]
    enrollment_filter: EnrollmentFilter
    def __init__(self, enrollment_filter: _Optional[_Union[EnrollmentFilter, _Mapping]] = ...) -> None: ...

class ContestEnrollResponse(_message.Message):
    __slots__ = ["enrollment_filter"]
    ENROLLMENT_FILTER_FIELD_NUMBER: _ClassVar[int]
    enrollment_filter: EnrollmentFilter
    def __init__(self, enrollment_filter: _Optional[_Union[EnrollmentFilter, _Mapping]] = ...) -> None: ...

class ChallengeSubmitRequest(_message.Message):
    __slots__ = ["enrollment_filter", "factor_challenge_submission"]
    ENROLLMENT_FILTER_FIELD_NUMBER: _ClassVar[int]
    FACTOR_CHALLENGE_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    enrollment_filter: EnrollmentFilter
    factor_challenge_submission: FactorChallengeSubmission
    def __init__(self, enrollment_filter: _Optional[_Union[EnrollmentFilter, _Mapping]] = ..., factor_challenge_submission: _Optional[_Union[FactorChallengeSubmission, _Mapping]] = ...) -> None: ...

class ChallengeSubmitResponse(_message.Message):
    __slots__ = ["enrollment_filter", "current_challenge"]
    ENROLLMENT_FILTER_FIELD_NUMBER: _ClassVar[int]
    CURRENT_CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    enrollment_filter: EnrollmentFilter
    current_challenge: int
    def __init__(self, enrollment_filter: _Optional[_Union[EnrollmentFilter, _Mapping]] = ..., current_challenge: _Optional[int] = ...) -> None: ...

class CheckGoalRequest(_message.Message):
    __slots__ = ["enrollment_filter"]
    ENROLLMENT_FILTER_FIELD_NUMBER: _ClassVar[int]
    enrollment_filter: EnrollmentFilter
    def __init__(self, enrollment_filter: _Optional[_Union[EnrollmentFilter, _Mapping]] = ...) -> None: ...

class CheckGoalResponse(_message.Message):
    __slots__ = ["current_challenge", "current_state"]
    CURRENT_CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_STATE_FIELD_NUMBER: _ClassVar[int]
    current_challenge: int
    current_state: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, current_challenge: _Optional[int] = ..., current_state: _Optional[_Iterable[int]] = ...) -> None: ...

class ClaimRewardRequest(_message.Message):
    __slots__ = ["enrollment_filter"]
    ENROLLMENT_FILTER_FIELD_NUMBER: _ClassVar[int]
    enrollment_filter: EnrollmentFilter
    def __init__(self, enrollment_filter: _Optional[_Union[EnrollmentFilter, _Mapping]] = ...) -> None: ...

class ClaimRewardResponse(_message.Message):
    __slots__ = ["reward"]
    REWARD_FIELD_NUMBER: _ClassVar[int]
    reward: str
    def __init__(self, reward: _Optional[str] = ...) -> None: ...

class ContestListRequest(_message.Message):
    __slots__ = ["author", "limit", "offset"]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    author: str
    limit: int
    offset: int
    def __init__(self, author: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class ContestListResponse(_message.Message):
    __slots__ = ["contests"]
    CONTESTS_FIELD_NUMBER: _ClassVar[int]
    contests: _containers.RepeatedCompositeFieldContainer[Contest]
    def __init__(self, contests: _Optional[_Iterable[_Union[Contest, _Mapping]]] = ...) -> None: ...
