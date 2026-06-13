#!/usr/bin/env python3
"""
로또명당 로컬 서버 실행기
==========================
이 파일을 실행하면 브라우저가 자동으로 열립니다.

실행:
    python serve.py

종료:
    Ctrl+C
"""

import http.server
import socketserver
import webbrowser
import threading
import os
from pathlib import Path

PORT = 8080
HERE = Path(__file__).parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HERE), **kwargs)

    # 정적 파일 캐시 비활성화 (새로고침 시 항상 최신 JSON 로드)
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    # 로그 간소화
    def log_message(self, format, *args):
        if any(x in args[0] for x in [".json", ".html", ".js"]):
            print(f"  [{args[1]}] {args[0].split()[1]}")

def main():
    # lotto_stores.json 존재 확인
    json_file = HERE / "lotto_stores.json"
    if not json_file.exists():
        print("⚠  lotto_stores.json 이 없습니다.")
        print("   crawl_all.py 를 먼저 실행하세요.\n")

    print("=" * 48)
    print("  🍀 로또명당 로컬 서버")
    print(f"  http://localhost:{PORT}/lotto-myungdang.html")
    print("=" * 48)
    print("  종료: Ctrl+C\n")

    # 브라우저 자동 오픈 (1초 딜레이)
    url = f"http://localhost:{PORT}/lotto-myungdang.html"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    # 서버 실행
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.allow_reuse_address = True
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n서버를 종료합니다.")

if __name__ == "__main__":
    main()
