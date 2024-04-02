import random
import string
import uuid
from typing import Callable

from checklib import *
import grpc
from contextlib import contextmanager
from proto.bluwal.bluwal_pb2 import (
    Contest,
    EnrollmentFilter,
    ContestCreateRequest,
    ContestCreateResponse,
    ContestGetRequest,
    ContestGetResponse,
    Challenge,
    FactorChallenge,
    FactorChallengeSubmission,
    ChallengeSubmitRequest,
    ChallengeSubmitResponse,
    ContestEnrollRequest,
    ContestEnrollResponse,
    CheckGoalRequest,
    CheckGoalResponse,
    ClaimRewardRequest,
    ClaimRewardResponse,
)
from Crypto.Util.number import getPrime, isPrime
from proto.bluwal.bluwal_service_pb2_grpc import BluwalServiceStub

PORT = 9090


class CheckMachine:
    def __init__(self, c: BaseChecker):
        self.c = c
        self.conn_pool: list[(BluwalServiceStub, grpc.Channel)] = []

    def connect(self) -> (grpc.Channel, BluwalServiceStub):
        addr = f"{self.c.host}:{PORT}"
        channel = grpc.insecure_channel(addr)
        return channel, BluwalServiceStub(channel)

    def create_contest(self, stub: BluwalServiceStub, contest: Contest) -> Contest:
        resp: ContestCreateResponse = stub.ContestCreate(
            ContestCreateRequest(contest=contest)
        )
        self.c.assert_(self.is_uuid(resp.contest.id), "contest id is not uuid")
        return resp.contest

    def get_contest(
        self,
        stub: BluwalServiceStub,
        contest_id: str,
        author: str = "",
    ) -> Contest:
        resp: ContestGetResponse = stub.ContestGet(
            ContestGetRequest(id=contest_id, author=author)
        )
        self.c.assert_eq(resp.contest.id, contest_id, "contest id mismatch")
        return resp.contest

    def enroll(
        self,
        stub: BluwalServiceStub,
        enrollment_filter: EnrollmentFilter,
    ) -> EnrollmentFilter:
        resp: ContestEnrollResponse = stub.ContestEnroll(
            ContestEnrollRequest(enrollment_filter=enrollment_filter)
        )
        self.c.assert_(resp.enrollment_filter is not None, "enrollment filter is empty")
        self.c.assert_eq(
            enrollment_filter.user_id, resp.enrollment_filter.user_id, "bad user id"
        )
        self.c.assert_eq(
            enrollment_filter.contest_id,
            resp.enrollment_filter.contest_id,
            "bad contest id",
        )
        self.c.assert_eq(
            enrollment_filter.current_state,
            resp.enrollment_filter.current_state,
            "bad current state",
        )
        return resp.enrollment_filter

    @staticmethod
    def submit(
        stub: BluwalServiceStub,
        enrollment_filter: EnrollmentFilter,
        request: ChallengeSubmitRequest,
    ) -> (int, EnrollmentFilter):
        request.enrollment_filter.CopyFrom(enrollment_filter)
        resp: ChallengeSubmitResponse = stub.ChallengeSubmit(request)
        return resp.current_challenge, resp.enrollment_filter

    @staticmethod
    def check_goal(
        stub: BluwalServiceStub,
        enrollment_filter: EnrollmentFilter,
    ) -> (int, list[int]):
        resp: CheckGoalResponse = stub.CheckGoal(
            CheckGoalRequest(enrollment_filter=enrollment_filter)
        )
        return resp.current_challenge, list(resp.current_state)

    @staticmethod
    def claim_reward(
        stub: BluwalServiceStub, enrollment_filter: EnrollmentFilter
    ) -> str:
        resp: ClaimRewardResponse = stub.ClaimReward(
            ClaimRewardRequest(enrollment_filter=enrollment_filter)
        )
        return resp.reward

    @contextmanager
    def handle_grpc_error(self, status=Status.MUMBLE):
        try:
            yield
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                raise
            else:
                self.c.cquit(status, f"grpc error: {e.code()}", f"grpc error: {e}")

    def rotating_connection(self) -> BluwalServiceStub:
        if not self.conn_pool or random.randint(0, 1):
            self.conn_pool.append(self.connect())
        if len(self.conn_pool) > 1 and random.randint(0, 1):
            self.conn_pool[0], self.conn_pool[-1] = (
                self.conn_pool[-1],
                self.conn_pool[0],
            )
            channel, _ = self.conn_pool[-1]
            self.conn_pool = self.conn_pool[:-1]
            channel.close()
        return random.choice(self.conn_pool)[1]

    @staticmethod
    def is_uuid(s: str) -> bool:
        try:
            uuid.UUID(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def fake_flag() -> str:
        return (
            "B" + rnd_string(31, alphabet=string.ascii_uppercase + string.digits) + "="
        )

    @staticmethod
    def next_prime(n: int) -> int:
        while True:
            n += 1
            if isPrime(n):
                return n

    @staticmethod
    def safe_get_prime(rnd: random.Random, bits: int) -> int:
        return getPrime(bits, randfunc=rnd.randbytes)

    def generate_factor_challenge(
        self, rnd: random.Random, possible: bool
    ) -> (Challenge, ChallengeSubmitRequest):
        if possible:
            challenge_type = rnd.choice(["simple", "fermat"])
            if challenge_type == "simple":
                factors_count = rnd.randint(2, 10)
                factors = [
                    self.safe_get_prime(rnd, rnd.randint(10, 30))
                    for _ in range(factors_count)
                ]

                n = 1
                for factor in factors:
                    n *= factor

                return (
                    Challenge(
                        factor_challenge=FactorChallenge(
                            n=str(n),
                        ),
                    ),
                    ChallengeSubmitRequest(
                        factor_challenge_submission=FactorChallengeSubmission(
                            factors=[str(factor) for factor in factors]
                        ),
                    ),
                )

            elif challenge_type == "fermat":
                factor1 = self.safe_get_prime(rnd, 512)
                factor2 = self.next_prime(self.next_prime(factor1))
                n = factor1 * factor2
                return (
                    Challenge(
                        factor_challenge=FactorChallenge(
                            n=str(n),
                        ),
                    ),
                    ChallengeSubmitRequest(
                        factor_challenge_submission=FactorChallengeSubmission(
                            factors=[str(factor1), str(factor2)]
                        ),
                    ),
                )
        else:
            p, q = self.safe_get_prime(rnd, 512), self.safe_get_prime(rnd, 512)
            n = p * q
            return (
                Challenge(
                    factor_challenge=FactorChallenge(
                        n=str(n),
                    ),
                ),
                ChallengeSubmitRequest(
                    factor_challenge_submission=FactorChallengeSubmission(
                        factors=[str(p), str(q)]
                    ),
                ),
            )

        raise Exception("impossible")

    def generate_challenge(
        self, rnd: random.Random, possible: bool
    ) -> (Challenge, ChallengeSubmitRequest):
        challenge_type = rnd.choice(["factor"])
        if challenge_type == "factor":
            return self.generate_factor_challenge(rnd, possible)

    def generate_contest(
        self,
        seed: str,
        author: str,
        reward: str,
        possible: Callable[[random.Random], bool],
        max_characteristic=1000,
    ) -> (Contest, list[ChallengeSubmitRequest]):
        rnd = random.Random(seed)

        characteristics_count = rnd.randint(10, 100)
        threshold = rnd.choices(range(0, max_characteristic), k=characteristics_count)
        goal = threshold.copy()

        challenges_count = rnd.randint(2, 10)
        challenges = []
        answers = []
        for _ in range(challenges_count):
            challenge, answer = self.generate_challenge(rnd, possible=possible(rnd))

            char = rnd.choice(range(1, characteristics_count))
            delta = rnd.randint(1, 5)
            goal[char] += delta

            challenge.characteristic = char
            challenge.delta = delta

            challenges.append(challenge)
            answers.append(answer)

        return (
            Contest(
                threshold=threshold,
                challenges=challenges,
                goal=goal,
                reward=reward,
                author=author,
            ),
            answers,
        )
