import typing
import subprocess
import sys
import io
import os
from contextlib import contextmanager

from kubernetes import client
from kubernetes.client import Configuration, ApiClient


@contextmanager
def run(
    *args, check=False, return_stdout=False, env=None
) -> typing.Union[typing.NoReturn, io.TextIOBase]:
    kwargs = {"stdout": sys.stderr, "stderr": subprocess.STDOUT}
    if env is not None:
        kwargs["env"] = env
    if return_stdout:
        kwargs["stderr"] = sys.stderr
        kwargs["stdout"] = subprocess.PIPE
    args = [str(a) for a in args]
    print(
        "** Running",
        " ".join(map(lambda a: repr(a) if " " in a else a, args)),
        kwargs,
        file=sys.stderr,
        flush=True,
    )
    proc = None
    try:
        proc = subprocess.Popen(args, **kwargs)
        yield proc
    finally:
        if proc is not None:
            proc.terminate()
            proc.kill()

    if return_stdout:
        return proc.stdout

@contextmanager
def kube_proxy(kubeconfig):
    with run(
        "kubectl",
        "proxy",
        "--port=8080",
        env={"KUBECONFIG": kubeconfig, "PATH": os.environ["PATH"]},
    ) as proc:
        print("Kubectl proxy started")
        print("Waiting for kubectl proxy to start")
        while True:
            try:
                kubeconfig = Configuration()
                kubeconfig.host = "http://127.0.0.1:8080"
                api_client = ApiClient(configuration=kubeconfig)
                kubectl = client.CoreV1Api(api_client=api_client)
                kubectl.list_node()
                print("Kubectl proxy is ready")
                break
            except Exception as e:
                print("Kubectl proxy is not ready yet")
                pass
        yield proc
        proc.terminate()
        proc.kill()