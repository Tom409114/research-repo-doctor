from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

DEFAULT_TIMEOUT_SECONDS = 20


@dataclass(frozen=True)
class DemoCheck:
    ok: bool
    message: str


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def check_demo_url(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> DemoCheck:
    request = Request(url, headers={"User-Agent": "rrdoctor-live-demo-check/1.0"})
    opener = build_opener(NoRedirect)
    try:
        with opener.open(request, timeout=timeout) as response:
            status = response.status
            if 200 <= status < 300:
                return DemoCheck(True, f"Demo is anonymously reachable: HTTP {status}.")
            return DemoCheck(False, f"Unexpected demo response: HTTP {status}.")
    except HTTPError as exc:
        location = exc.headers.get("Location", "")
        if exc.code in {301, 302, 303, 307, 308}:
            if "share.streamlit.io/-/auth" in location:
                return DemoCheck(
                    False,
                    "Demo redirects anonymous visitors to Streamlit auth. "
                    "Set the app sharing/visibility to public and redeploy.",
                )
            return DemoCheck(False, f"Demo redirects before loading: HTTP {exc.code} -> {location}")
        return DemoCheck(False, f"Demo returned HTTP {exc.code}.")
    except URLError as exc:
        return DemoCheck(False, f"Could not reach demo URL: {exc.reason}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that a hosted rrdoctor demo is reachable without Streamlit auth."
    )
    parser.add_argument("url", help="Hosted Streamlit or Spaces demo URL")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    args = parser.parse_args(argv)

    result = check_demo_url(args.url, timeout=args.timeout)
    print(result.message)
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
