# 아르켄 — 부서진 하늘 아래의 일곱 맹약

맹약력 312년 초여름. 하늘이 갈라진 뒤 세워진 도시들은 서로 다른 법으로 살지만, 구조 요청과 약속 앞에서는 연결된다. 배울 수 있는 마법, 관계를 맺어 얻는 가호, 좁은 법칙을 집행하는 권능이 공존한다. 영웅도 물·노동·치료·신뢰를 혼자 만들 수 없다.

**[세계 개요](world/overview.md) · [분류별 위키](world/indexes/README.md) · [연표](world/indexes/timeline.md) · [세계 헌장](world/constitution.md)**

## 먼저 읽을 문서

- [아르켄 대륙](world/wiki/LOC-ARKEN.md): 지리·정치·생활
- [술식마법](world/wiki/SYS-MAGIC.md) / [가호](world/wiki/SYS-BLESSING.md) / [권능](world/wiki/SYS-AUTHORITY.md): 힘과 대가
- [세린](world/wiki/HERO-SERIN.md)과 [토마](world/wiki/NPC-TOMA.md): 구조 영웅과 뱃사공
- [수리](world/wiki/NPC-SURI.md)와 [바르카](world/wiki/NPC-VARKA.md): 물 공급과 독점 계약
- [은각 사슴](world/wiki/BEA-HART.md), [네므](world/wiki/SPI-NEM.md), [유리굴착충](world/wiki/MON-WORM.md): 영물·정령·몬스터
- [구명 등불](world/wiki/ITM-LANTERN.md): 소유·보관·사용이 다른 유일물

## 이어 쓰는 에이전트에게

[AGENTS.md](AGENTS.md) → [SKILLS.md](SKILLS.md) → [작업 목록](work/tasks/README.md) 순서로 읽는다. 채팅 기록 없이도 정사·미정 영역·변경 의도·검토 근거를 파일에서 확인한다.

기본 브랜치에 병합된 world가 정사다. 작업 브랜치는 초안이다. 승인된 Claim도 내용 자체가 참이라는 뜻은 아니다. 초기 세계는 사용자가 요청한 고급 모델의 부트스트랩이며 독립 합의체 승인으로 위장하지 않는다.

## 검사

Python 3.11 이상, 외부 패키지 없이 실행한다.

```bash
python tools/validate.py
python tools/index.py --check
python -m unittest discover -s tests -v
```

[운영 절차](docs/OPERATIONS.md) · [구조와 승인 경계](docs/ARCHITECTURE.md) · [검증 기록](docs/VALIDATION.md) · [이전 경험](docs/LESSONS.md)

키는 환경 변수로 전달한다. 로컬 실행 로그는 Git에서 제외한 .runtime에 보관한다. 자동 검토에는 LLM 연결과 운영자 서명 키가 필요하다. 자동 병합은 제공하지 않는다.
