from __future__ import annotations

import base64
import gzip
import hashlib
import io
import random
import tarfile
import tempfile
import time
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

import websocket
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, AES
from pydantic import BaseModel, Field
from checklib import *

if TYPE_CHECKING:
    from checker import Checker

PORT = 5555

CAPTCHA_DIFFICULTY = 6
CAPTCHA_ITERATIONS = 3

W = websocket.WebSocket


class Artifact(BaseModel):
    source_project: str = Field(default="")
    source: str
    destination: str


class Step(BaseModel):
    name: str
    artifacts: list[Artifact]


class Job(BaseModel):
    steps: list[Step]


class JobRequest(BaseModel):
    job: Job


class CheckMachine:
    def __init__(self, c: Checker):
        self.c = c

        privkey_path = Path(__file__).parent / "checker-priv.pem"
        captcha_key = RSA.import_key(privkey_path.read_text())
        self.cipher = PKCS1_v1_5.new(captcha_key)

    def connect(self) -> W:
        return websocket.create_connection(
            f"ws://{self.c.host}:{PORT}/ws/",
            header={"User-Agent": "CTF"},
        )

    def create_project(self, conn: W, project_id: str) -> str:
        conn.send(f"project {project_id} {rnd_bytes(16).hex()}")
        self.c.assert_eq("project created", conn.recv(), "bad project msg")
        pass_msg = conn.recv().split(" ")
        self.c.assert_eq(len(pass_msg), 2, "bad project msg")
        self.c.assert_eq(pass_msg[0], "project-password", "bad project msg")
        return pass_msg[1]

    def enter_project(
        self, conn: W, project_id: str, project_pass: str, st=Status.MUMBLE
    ):
        conn.send(f"project {project_id} {project_pass}")
        self.c.assert_eq("project set", conn.recv(), "bad project msg", status=st)

    def solve_captcha(self, conn: W):
        conn.send("captcha")
        captcha_msg = conn.recv().split(" ")
        self.c.assert_eq(len(captcha_msg), 2, "bad captcha msg")
        self.c.assert_eq(captcha_msg[0], "captcha", "bad captcha msg")

        challenge = captcha_msg[1].split(":")
        self.c.assert_eq(len(challenge), 3, "bad captcha challenge")

        captcha_nonce = b"".fromhex(challenge[0])
        captcha_hash = challenge[1]
        captcha_ans = b"".fromhex(challenge[2])

        self.c.assert_eq(len(captcha_hash), CAPTCHA_DIFFICULTY, "bad captcha challenge")

        ans = self.cipher.decrypt(captcha_ans, None)

        got_hash = captcha_nonce + ans
        for i in range(CAPTCHA_ITERATIONS):
            got_hash = hashlib.md5(got_hash).digest()

        self.c.assert_eq(
            got_hash.hex()[: len(captcha_hash)],
            captcha_hash,
            "bad captcha challenge",
        )
        conn.send(f"{ans.hex()}")
        self.c.assert_eq("captcha ok", conn.recv(), "could not solve captcha")

    def upload(self, conn: W, name: str, fmt: str, files: list[tuple[str, bytes]]):
        self.solve_captcha(conn)

        with tempfile.NamedTemporaryFile(delete=True) as f:
            if self.is_tar(fmt):
                with tarfile.open(f.name, "w") as tf:
                    for filename, content in files:
                        tarinfo = tarfile.TarInfo(filename)
                        tarinfo.size = len(content)
                        tarinfo.mtime = int(time.time())
                        tf.addfile(tarinfo, fileobj=io.BytesIO(content))

                content = f.read()
                if fmt == "targz":
                    content = gzip.compress(content)

            else:
                with zipfile.ZipFile(
                    f.name, "w", compression=zipfile.ZIP_DEFLATED
                ) as zf:
                    for filename, content in files:
                        zipinfo = zipfile.ZipInfo(
                            filename=filename,
                            date_time=time.localtime(time.time())[:6],
                        )
                        zf.writestr(zipinfo, content)
                content = f.read()

            conn.send(f"upload {name}.{fmt} {self.compress(content)}")

        res = conn.recv()
        self.c.assert_eq(
            f"upload ok: remote directory `{name}` created", res, "bad upload response"
        )

        return content

    def list_files(
        self,
        conn: W,
        name: str,
        prefix: str,
        st=Status.MUMBLE,
    ) -> list[str]:
        conn.send(f"list {name}/{prefix}")
        res = conn.recv()

        self.c.assert_(res.startswith("files "), "could not list files", status=st)
        self.c.assert_in("files ", res, "could not list files", status=st)
        return list(filter(lambda x: x, res.split(" ")[1:]))

    def download(self, conn: W, name: str, file: str, st=Status.MUMBLE) -> bytes:
        conn.send(f"download {name}/{file}")
        res = conn.recv()

        tokens = res.split(" ")
        self.c.assert_eq(len(tokens), 3, "bad download response", status=st)
        self.c.assert_eq(tokens[0], "file", "bad download response", status=st)
        self.c.assert_eq(
            tokens[1], f"{name}/{file}", "bad download response", status=st
        )
        return self.decompress(tokens[2])

    def job(self, conn: W, job: JobRequest, st=Status.MUMBLE):
        self.solve_captcha(conn)
        conn.send(f"job {self.compress(job.json().encode())}")
        self.c.assert_eq("job ok", conn.recv(), "could not send job", status=st)

    def cleanup_job(self, conn: W, name: str):
        conn.send(f"delete .{name}.tar")
        self.c.assert_eq("delete ok", conn.recv(), "could not cleanup job")

    @staticmethod
    def random_format() -> str:
        return random.choice(["targz", "zip"])

    def decrypt(self, data: bytes, project_pass: str, st=Status.MUMBLE) -> bytes:
        self.c.assert_eq(len(data) % AES.block_size, 0, "bad encrypted data", status=st)
        self.c.assert_gt(len(data), 2 * AES.block_size, "bad encrypted data", status=st)

        iv = data[: AES.block_size]
        cipher = AES.new(b"".fromhex(project_pass), AES.MODE_CBC, iv=iv)
        decrypted = cipher.decrypt(data[AES.block_size:])
        return CheckMachine.unpad(decrypted)

    @staticmethod
    def compress(data: bytes) -> str:
        return base64.urlsafe_b64encode(gzip.compress(data)).decode()

    @staticmethod
    def decompress(data: str) -> bytes:
        return gzip.decompress(base64.urlsafe_b64decode(data))

    @staticmethod
    def is_tar(fmt: str) -> bool:
        return fmt in ["tar", "targz"]

    @staticmethod
    def unpad(data: bytes) -> bytes:
        assert len(data) >= data[-1]
        return data[: -data[-1]]

    def check_encrypted_zip_archive_files(
        self,
        conn: W,
        name: str,
        filename: str,
        password: str,
        need_files: list[tuple[str, bytes]],
        st=Status.MUMBLE,
    ):
        content = self.download(conn, name, filename, st=st)
        content = self.decrypt(content, password, st=st)
        with tempfile.NamedTemporaryFile(delete=True) as f:
            f.write(content)
            f.flush()
            with zipfile.ZipFile(f.name, "r") as zf:
                for filename, content in need_files:
                    self.c.assert_in(filename, zf.namelist(), "bad archive", status=st)
                    self.c.assert_eq(
                        content,
                        zf.read(filename),
                        "bad archive",
                        status=st,
                    )

    def check_encrypted_tar_archive_files(
        self,
        conn: W,
        name: str,
        filename: str,
        password: str,
        fmt: str,
        need_files: list[tuple[str, bytes]],
        st=Status.MUMBLE,
    ):
        assert self.is_tar(fmt)

        content = self.download(conn, name, filename, st=st)
        content = self.decrypt(content, password, st=st)

        if fmt == "targz":
            content = gzip.decompress(content)

        with tempfile.NamedTemporaryFile(delete=True) as f:
            f.write(content)
            f.flush()
            with tarfile.open(f.name, "r") as zf:
                for filename, content in need_files:
                    self.c.assert_in(filename, zf.getnames(), "bad archive", status=st)
                    self.c.assert_eq(
                        content,
                        zf.extractfile(filename).read(),
                        "bad archive",
                        status=st,
                    )
