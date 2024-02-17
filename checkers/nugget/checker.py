#!/usr/bin/env python3
import binascii
import random
import traceback
import uuid
import sys
import zipfile

import websocket
from checklib import *

from nuggetlib import CheckMachine, JobRequest, Job, Step, Artifact


class Checker(BaseChecker):
    # tar, targz, zip.
    vulns: int = 3
    timeout: int = 20
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.c = CheckMachine(self)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except self.get_check_finished_exception():
            raise
        except websocket.WebSocketException as e:
            self.cquit(
                Status.MUMBLE,
                "Websocket exception",
                f"Websocket exception: {e}\n{traceback.format_exc()}",
            )
        except (binascii.Error, ValueError, zipfile.BadZipFile) as e:
            self.cquit(
                Status.MUMBLE,
                "Bad data returned",
                f"Bad data: {e}\n{traceback.format_exc()}",
            )
        except ConnectionRefusedError:
            self.cquit(Status.DOWN, "Connection refused", "Connection refused")

    def check(self):
        scenarios = [
            self.check_scenario1,
            self.check_scenario2,
        ]
        random.shuffle(scenarios)

        for scenario in scenarios:
            scenario()

        self.cquit(Status.OK)

    def put(self, _: str, flag: str, vuln: str):
        project_id = str(uuid.uuid4())

        conn1 = self.c.connect()
        project_pass = self.c.create_project(conn1, project_id)

        conn2 = self.c.connect()
        self.c.enter_project(conn2, project_id, project_pass)

        def random_conn():
            return random.choice([conn1, conn2])

        fmt = ["tar", "targz", "zip"][int(vuln) - 1]
        upload_name = rnd_string(random.randint(5, 20))
        flag_filename = rnd_string(random.randint(5, 20))
        files = [
            (
                flag_filename,
                flag.encode(),
            )
        ]
        self.c.upload(
            random_conn(),
            upload_name,
            fmt,
            files,
        )

        self.cquit(
            Status.OK,
            f"{project_id}/{upload_name}.{fmt}",
            f"{project_id}:{upload_name}:{fmt}:{flag_filename}:{project_pass}",
        )

    def get(self, flag_id: str, flag: str, vuln: str):
        project_id, upload_name, fmt, flag_filename, project_pass = flag_id.split(":")
        self.get_scenario1(project_id, project_pass, flag, upload_name, flag_filename)
        self.get_scenario2(
            project_id, project_pass, flag, upload_name, flag_filename, fmt
        )
        self.cquit(Status.OK)

    def check_scenario1(self):
        project_id = str(uuid.uuid4())

        conn1 = self.c.connect()
        project_pass = self.c.create_project(conn1, project_id)

        conn2 = self.c.connect()
        self.c.enter_project(conn2, project_id, project_pass)

        conn3 = self.c.connect()
        self.c.enter_project(conn3, project_id, project_pass)

        def random_conn():
            return random.choice([conn1, conn2, conn3])

        fmt = self.c.random_format()
        files = [
            (
                rnd_string(random.randint(5, 20)),
                rnd_bytes(random.randint(10, 100)),
            )
            for _ in range(random.randint(1, 10))
        ]

        upload_name = rnd_string(random.randint(5, 20))
        self.c.upload(
            random_conn(),
            upload_name,
            fmt,
            files,
        )

        need_prefix = ""
        if random.randint(0, 1):
            f = random.choice(files)
            need_prefix = f[0][: random.randint(1, len(f[0]) - 1)]

        got_files = sorted(self.c.list_files(random_conn(), upload_name, need_prefix))
        need_files = sorted(
            [f[0][len(need_prefix):] for f in files if f[0].startswith(need_prefix)]
        )

        self.assert_eq(need_files, got_files, "bad list files")

        for name, need_content in random.sample(files, random.randint(1, len(files))):
            content = self.c.download(random_conn(), upload_name, name)
            self.assert_eq(need_content, content, "bad download")

        job_name = rnd_string(random.randint(5, 20))
        destinations = [
            rnd_string(random.randint(5, 20)),
            rnd_string(random.randint(5, 20)),
        ]
        job = Job(
            steps=[
                Step(
                    name=job_name,
                    artifacts=[
                        Artifact(source=upload_name, destination=destinations[0]),
                        Artifact(
                            source=f"{upload_name}.{fmt}", destination=destinations[1]
                        ),
                    ],
                ),
            ],
        )
        self.c.job(random_conn(), JobRequest(job=job))
        self.c.cleanup_job(random_conn(), job_name)

        got_job_files = sorted(self.c.list_files(random_conn(), job_name, ""))
        need_job_files = sorted(destinations)
        self.assert_eq(need_job_files, got_job_files, "bad job files")

    def check_scenario2(self):
        first_project_id = str(uuid.uuid4())
        second_project_id = str(uuid.uuid4())

        conn1 = self.c.connect()
        first_project_pass = self.c.create_project(conn1, first_project_id)

        conn2 = self.c.connect()
        second_project_pass = self.c.create_project(conn2, second_project_id)

        upload_name1 = rnd_string(random.randint(5, 20))
        fmt1 = self.c.random_format()
        files1 = [
            (
                rnd_string(random.randint(5, 20)),
                rnd_bytes(random.randint(10, 100)),
            )
            for _ in range(random.randint(1, 10))
        ]

        upload_content1 = self.c.upload(
            conn1,
            upload_name1,
            fmt1,
            files1,
        )

        upload_name2 = rnd_string(random.randint(5, 20))
        fmt2 = self.c.random_format()
        files2 = [
            (
                rnd_string(random.randint(5, 20)),
                rnd_bytes(random.randint(10, 100)),
            )
            for _ in range(random.randint(1, 10))
        ]

        upload_content2 = self.c.upload(
            conn2,
            upload_name2,
            fmt2,
            files2,
        )

        job_name = rnd_string(random.randint(5, 20))
        destinations = [rnd_string(random.randint(5, 20)) for _ in range(4)]
        job = Job(
            steps=[
                Step(
                    name=job_name,
                    artifacts=[
                        Artifact(
                            source_project=first_project_id,
                            source=upload_name1,
                            destination=destinations[0],
                        ),
                        Artifact(
                            source_project=first_project_id,
                            source=f"{upload_name1}.{fmt1}",
                            destination=destinations[1],
                        ),
                        Artifact(
                            source_project=second_project_id,
                            source=upload_name2,
                            destination=destinations[2],
                        ),
                        Artifact(
                            source_project=second_project_id,
                            source=f"{upload_name2}.{fmt2}",
                            destination=destinations[3],
                        ),
                    ],
                ),
            ],
        )

        third_project_id = str(uuid.uuid4())
        conn3 = self.c.connect()
        self.c.create_project(conn3, third_project_id)

        self.c.job(conn3, JobRequest(job=job))
        self.c.cleanup_job(conn3, job_name)

        got_job_files = sorted(self.c.list_files(conn3, job_name, ""))
        need_job_files = sorted(destinations)
        self.assert_eq(need_job_files, got_job_files, "bad job files")

        if random.randint(0, 1):
            content = self.c.download(conn3, job_name, destinations[1])
            decrypted = self.c.decrypt(content, project_pass=first_project_pass)
            self.assert_eq(upload_content1, decrypted, "bad download")

        if random.randint(0, 1):
            content = self.c.download(conn3, job_name, destinations[3])
            decrypted = self.c.decrypt(content, project_pass=second_project_pass)
            self.assert_eq(upload_content2, decrypted, "bad download")

        if random.randint(0, 1):
            self.c.check_encrypted_zip_archive_files(
                conn3,
                job_name,
                destinations[0],
                first_project_pass,
                files1,
            )

        if random.randint(0, 1):
            self.c.check_encrypted_zip_archive_files(
                conn3,
                job_name,
                destinations[2],
                second_project_pass,
                files2,
            )

    def get_scenario1(
        self,
        project_id: str,
        project_pass: str,
        flag: str,
        upload_name: str,
        flag_name: str,
    ):
        conn1 = self.c.connect()
        self.c.enter_project(conn1, project_id, project_pass, st=Status.CORRUPT)

        conn2 = self.c.connect()
        self.c.enter_project(conn2, project_id, project_pass, st=Status.CORRUPT)

        def random_conn():
            return random.choice([conn1, conn2])

        files = self.c.list_files(random_conn(), upload_name, "", st=Status.CORRUPT)
        self.assert_eq([flag_name], files, "flag not found", status=Status.CORRUPT)

        content = self.c.download(
            random_conn(), upload_name, flag_name, st=Status.CORRUPT
        )
        self.assert_eq(flag.encode(), content, "bad flag", status=Status.CORRUPT)

    def get_scenario2(
        self,
        project_id: str,
        project_pass: str,
        flag: str,
        upload_name: str,
        flag_name: str,
        fmt: str,
    ):
        fake_project_id = str(uuid.uuid4())
        conn = self.c.connect()
        fake_project_pass = self.c.create_project(conn, fake_project_id)

        check_conn1 = self.c.connect()
        self.c.enter_project(check_conn1, fake_project_id, fake_project_pass)

        check_conn2 = self.c.connect()
        self.c.enter_project(check_conn2, fake_project_id, fake_project_pass)

        def random_conn():
            return random.choice([check_conn1, check_conn2])

        job_name = rnd_string(random.randint(5, 20))
        count_files = random.randint(100, 500)
        destinations = [
            rnd_string(random.randint(5, 20)) for _ in range(2 * count_files)
        ]
        job = Job(
            steps=[
                Step(
                    name=job_name,
                    artifacts=[
                                  Artifact(
                                      source_project=project_id,
                                      source=f"{upload_name}.{fmt}",
                                      destination=destinations[i],
                                  )
                                  for i in range(count_files)
                              ]
                              + [
                                  Artifact(
                                      source_project=project_id,
                                      source=upload_name,
                                      destination=destinations[count_files + i],
                                  )
                                  for i in range(count_files)
                              ],
                ),
            ],
        )

        self.c.job(conn, JobRequest(job=job), st=Status.CORRUPT)
        self.c.cleanup_job(conn, job_name)

        got_files = self.c.list_files(conn, job_name, "", st=Status.CORRUPT)
        self.assert_eq(
            sorted(destinations),
            sorted(got_files),
            "bad job files",
            status=Status.CORRUPT,
        )

        checks_variant1 = random.sample(
            range(count_files), random.randint(1, min(count_files, 5))
        )
        checks_variant2 = random.sample(
            range(count_files), random.randint(1, min(count_files, 5))
        )

        flag_files = [(flag_name, flag.encode())]

        for i in checks_variant1:
            if self.c.is_tar(fmt):
                self.c.check_encrypted_tar_archive_files(
                    random_conn(),
                    job_name,
                    destinations[i],
                    project_pass,
                    fmt,
                    flag_files,
                )
            else:
                self.c.check_encrypted_zip_archive_files(
                    random_conn(), job_name, destinations[i], project_pass, flag_files
                )

        for i in checks_variant2:
            self.c.check_encrypted_zip_archive_files(
                random_conn(),
                job_name,
                destinations[count_files + i],
                project_pass,
                flag_files,
            )


if __name__ == "__main__":
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
