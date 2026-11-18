# 아르켄 오프라인 위키 뷰어

문서 ID: ARKEN-VIEWER-001 · 버전:1.0 · 기준일:2026-11-18

## 열기

`arken-wiki.html` 파일을 다운로드하고 Chrome, Edge, Firefox 같은 브라우저로 연다. 서버 설치·Python 실행·호스팅·API 키는 열람에 필요하지 않다. 저장소 폴더 전체를 내려받은 경우에도 이 HTML 하나만 열면 된다. GitHub 파일 미리보기는 HTML을 실행하지 않으므로 파일 화면의 Download raw file을 사용한다.

문서75개와 세계 개요·헌장·연표3개, 스타일과 JavaScript를 파일 내부에 포함한다. 외부 글꼴·라이브러리·fetch·서버 API를 사용하지 않는다. 검색·분류·관련 문서·목차·임의 문서·뒤로가기·Markdown 저장·어두운 테마를 제공한다. 브라우저가 로컬 저장을 허용할 때만 최근 문서와 테마를 기억하며, 저장이 차단되어도 열람은 계속된다.

이 파일은 생성 시점의 읽기 전용 스냅샷이다. Markdown 저장은 로컬 사본 내려받기이며 정사 수정이나 Git 커밋이 아니다. 새로운 정사를 보려면 갱신된 HTML을 내려받는다.

## 재생성

개발 환경 Python3.11 이상에서 실행한다.

```bash
python tools/build_viewer.py
python tools/build_viewer.py --check
```

원본은 world/wiki, world/records, world/overview.md, world/constitution.md, world/indexes/timeline.md다. 수정 전 정적 검사를 통과해야 한다. 구현 파일은 viewer/src에 있다. 제한된 Markdown(제목·목록·표·강조·코드·내부 링크)을 지원하며 임의 HTML은 실행하지 않는다.

## 검증 결과

75개 본문+안내3개 전체 탐색, 검색, 내부 링크, 뒤로가기, 재접속, 목차, 다운로드, 분류, 연표, HTML/위험 링크 이스케이프, 모바일 폭을 Chromium에서 확인했다. 외부 네트워크 요청0·JavaScript 오류0.

관리 환경의 Chromium 정책이 file:// 및 data: 직접 탐색을 차단하여 해당 경로의 직접 실행 검증은 하지 못했다. 검증에는 임시 localhost를 사용했으며 최종 뷰어에 서버 의존성을 추가하지 않았다. 실제 로컬 파일 열기는 사용자 브라우저에서 확인할 항목이다.
