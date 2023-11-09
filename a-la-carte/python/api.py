import asyncio
import json
import uvicorn

from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse


async def exec_command_async(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    # io streams are returned as unicode bytes, so decode to get strings
    stdout = stdout.decode("utf8", errors="ignore")
    stderr = stderr.decode("utf8", errors="ignore")

    return proc.returncode, stdout, stderr


api = Starlette()


@api.route("/")
async def index(request):
    return JSONResponse({"status": "ok", "version": "0.0.1"})


@api.route("/sample-endpoint")
class SampleEndpoint(HTTPEndpoint):
    async def get(self, request):
        return JSONResponse({"a": 1})

    async def put(self, request):
        body = await request.json()
        try:
            pass
        except Exception:
            return JSONResponse({"a": 1}, status_code=500)
        else:
            return JSONResponse({"a": 1}, status_code=200)


@api.route("/simple-endpoint")
async def simple(request):
    return JSONResponse({"target": "stress"})


@api.route("/command", methods=["PUT"])
async def put_command(request):
    body = await request.json()
    command = body.get("command")
    if not command:
        return JSONResponse(
            'Expected "command" key in JSON request body.', status_code=400
        )

    status, stdout, stderr = await exec_command_async(command)

    return JSONResponse(
        {
            "status": status,
            "stdout": stdout,
            "stderr": stderr,
        },
        status_code=200,
    )


def main():
    host = "0.0.0.0"
    port = 5000
    uvicorn.run(api, host=host, port=port, logger=None)


if __name__ == "__main__":
    main()
