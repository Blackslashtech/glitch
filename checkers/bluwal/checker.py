#!/usr/bin/env python3

import random
import secrets
import sys
import uuid

import grpc
from checklib import *

from bluwal_lib import CheckMachine
from proto.bluwal.bluwal_pb2 import Contest, ChallengeSubmitRequest, EnrollmentFilter


class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 10
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.c = CheckMachine(self)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except self.get_check_finished_exception():
            raise
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                self.cquit(Status.DOWN, "unavailable", f"grpc error: {e}")
            else:
                self.cquit(Status.MUMBLE, f"grpc error: {e.code()}", f"grpc error: {e}")
        except ConnectionRefusedError:
            self.cquit(Status.DOWN, "Connection refused", "Connection refused")

    def check(self):
        seed = secrets.token_hex(32)
        author = str(uuid.uuid4())
        reward = uuid.uuid4().hex if random.randint(0, 1) else self.c.fake_flag()
        contest, answers = self.c.generate_contest(
            seed=seed,
            author=author,
            reward=reward,
            possible=lambda rnd: bool(rnd.randint(0, 1)),
        )
        created_contest = self.c.create_contest(self.c.rotating_connection(), contest)
        got_contest = self.c.get_contest(
            self.c.rotating_connection(), created_contest.id, author=author
        )

        # set for comparison.
        contest.id = created_contest.id
        self.assert_eq(contest, got_contest, "contest mismatch")

        self.complete_contest(contest, answers)

        self.cquit(Status.OK)

    def put(self, _: str, flag: str, vuln: str):
        author = str(uuid.uuid4())
        seed = secrets.token_hex(32)
        contest, _ = self.c.generate_contest(
            seed=seed,
            author=author,
            reward=flag,
            possible=lambda _: False,
            max_characteristic=80,
        )
        created_contest = self.c.create_contest(self.c.rotating_connection(), contest)

        self.cquit(
            Status.OK,
            f"{created_contest.id}",
            f"{created_contest.id}:{author}:{seed}",
        )

    def get(self, flag_id: str, flag: str, vuln: str):
        contest_id, author, seed = flag_id.split(":")

        with self.c.handle_grpc_error(status=Status.CORRUPT):
            contest = self.c.get_contest(
                self.c.rotating_connection(), contest_id, author=author
            )
            self.assert_eq(
                contest.reward, flag, "missing reward", status=Status.CORRUPT
            )

            generated_contest, answers = self.c.generate_contest(
                seed=seed,
                author=author,
                reward=flag,
                possible=lambda _: False,
                max_characteristic=80,
            )
            self.assert_eq(
                contest.challenges,
                generated_contest.challenges,
                "challenges mismatch",
                status=Status.CORRUPT,
            )

            contest.reward = flag
            self.complete_contest(contest, answers, status=Status.CORRUPT)

        self.cquit(Status.OK)

    def complete_contest(
        self,
        contest: Contest,
        answers: list[ChallengeSubmitRequest],
        status=Status.MUMBLE,
    ):
        initial_state = list(contest.threshold)
        # try to add some delta to some characteristics.
        for i in range(10):
            char = random.choice(range(len(initial_state)))
            delta = random.randint(1, 5)
            new_state = initial_state.copy()
            new_state[char] += delta
            if new_state >= list(contest.goal):
                continue
            initial_state = new_state

        contest_goal = list(contest.goal)

        user_id = str(uuid.uuid4())

        enrollment_filter = EnrollmentFilter(
            contest_id=contest.id,
            user_id=user_id,
            current_state=initial_state.copy(),
        )
        got_enrollment_filter = self.c.enroll(
            self.c.rotating_connection(),
            enrollment_filter,
        )
        self.assert_eq(
            enrollment_filter, got_enrollment_filter, "enrollment filter mismatch"
        )

        expected_challenge = 0
        for challenge, answer in zip(contest.challenges, answers):
            current_challenge, new_enrollment_filter = self.c.submit(
                self.c.rotating_connection(), enrollment_filter, answer
            )
            new_enrollment_filter: EnrollmentFilter

            expected_challenge += 1
            initial_state[challenge.characteristic] += challenge.delta

            self.assert_eq(
                current_challenge, expected_challenge, "wrong challenge", status=status
            )
            self.assert_eq(
                new_enrollment_filter.current_state,
                initial_state,
                "wrong state",
                status=status,
            )

            enrollment_filter = new_enrollment_filter

            if random.randint(0, 1):
                current_challenge, current_state = self.c.check_goal(
                    self.c.rotating_connection(), enrollment_filter
                )
                self.assert_eq(
                    current_challenge,
                    expected_challenge,
                    "wrong challenge",
                    status=status,
                )
                self.assert_eq(
                    current_state, initial_state, "wrong state", status=status
                )

            if list(enrollment_filter.current_state) < contest_goal and random.randint(
                0, 1
            ):
                try:
                    self.c.claim_reward(self.c.rotating_connection(), enrollment_filter)
                except grpc.RpcError as e:
                    if e.code() == grpc.StatusCode.FAILED_PRECONDITION:
                        pass
                    else:
                        raise
                else:
                    self.cquit(Status.CORRUPT, "reward claimed too soon")

        final_challenge, final_state = self.c.check_goal(
            self.c.rotating_connection(), enrollment_filter
        )
        self.assert_eq(
            final_challenge, len(contest.challenges), "wrong challenge", status=status
        )
        self.assert_gte(final_state, contest_goal, "wrong state", status=status)

        reward = self.c.claim_reward(self.c.rotating_connection(), enrollment_filter)
        self.assert_eq(reward, contest.reward, "wrong reward", status=status)


if __name__ == "__main__":
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
