from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from http.cookiejar import CookieJar
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPCookieProcessor, Request, build_opener

DEFAULT_TIMEOUT_SECONDS = 20


@dataclass(frozen=True)
class DemoCheck:
    ok: bool
    message: str


def check_demo_url(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> DemoCheck:
    request = Request(url, headers={"User-Agent": "rrdoctor-live-demo-check/1.0"})
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    try:
        with opener.open(request, timeout=timeout) as response:
            status = response.status
            if 200 <= status < 300:
                final_url = response.geturl()
                if _is_auth_url(final_url):
                    return DemoCheck(
                        False,
                        "Demo still lands on Streamlit auth after redirects. "
                        "Check app sharing/visibility and redeploy.",
                    )
                if not _same_host(url, final_url):
                    return DemoCheck(False, f"Demo ended on an unexpected URL: {final_url}")
                return DemoCheck(
                    True,
                    f"Demo is anonymously reachable after redirects: HTTP {status}.",
                )
            return DemoCheck(False, f"Unexpected demo response: HTTP {status}.")
    except HTTPError as exc:
        return DemoCheck(False, f"Demo returned HTTP {exc.code}.")
    except URLError as exc:
        return DemoCheck(False, f"Could not reach demo URL: {exc.reason}")


def _same_host(expected_url: str, actual_url: str) -> bool:
    return urlparse(expected_url).netloc.lower() == urlparse(actual_url).netloc.lower()


def _is_auth_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc.lower() == "share.streamlit.io" and parsed.path.startswith("/-/auth")


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
