# 운영 절차

문서 ID: ARKEN-OPS-001 · 버전:1.0 · 기준일:2026-11-17

## 시작

Python3.11 이상과 Git이 필요하다. AGENTS와 담당 스킬, 작업 JSON을 읽고 기준 커밋을 확인한다.

```bash
git worktree add ../arken-task -b task/example
python tools/context.py LOC-SAHEL NPC-SURI NPC-VARKA
python tools/validate.py
```

운영자 환경에 LLM_ENDPOINT(HTTPS chat completions URL), LLM_API_KEY, LLM_MODEL, REVIEW_SIGNING_KEY를 설정한다. 키를 명령 인수·문서·프롬프트에 적지 않는다.

```bash
python tools/agent_loop.py --task work/tasks/TASK-001.json --root ../arken-task
```

최초 초안과 최대3회 재작성, 정적 검사, 세 검토 요청을 수행한다. 승인 뒤 영수증을 저장하며 병합하지 않는다. 변경과 영수증을 커밋해 PR을 제출한다. 기준 정사가 바뀌면 재검토한다.

## 실패와 복구

.runtime/실행ID에 초안·검사·검토·handoff가 남는다. 408/429/5xx·네트워크·잘못된 JSON은 제한 재시도하고 인증 오류는 실패한다. 불완전 응답은 승인하지 않는다.

중단된 worktree를 보존한다. 새 자동 실행은 clean worktree를 요구하므로 기존 초안은 별도 브랜치에 보존하고 검토 후 새 작업 입력으로 정리한다. 단계 중간부터 자동 투명 재개는 아직 없다. lease는 최대2시간 뒤 만료된다.

검사·색인·테스트와 영수증의 기준/내용을 확인하고 PR의 실제 반영 후 completed로 기록한다. approved 필드를 쓰는 것만으로 완료하지 않는다.

중단된 세션의 실제 상태는 읽기 전용 명령으로 점검한다.

```bash
python tools/resume.py --root ../arken-task
```

커밋된 초안의 HEAD는 정사 기준 커밋과 다르므로 영수증 검증에는 기록된 base_commit과 현재 대상 브랜치를 함께 대조해야 한다. 이 명령은 작업 상태를 요약하며 자동 승인이나 강제 점유를 하지 않는다.
