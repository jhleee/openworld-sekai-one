# 데이터 계약 v1

실행 기준은 tools/validate.py와 tools/governance.py다. 외부 JSON Schema 엔진은 필요하지 않다. 계약 변경은 인프라 변경이다.

공통: schema_version:1, id(파일명과 동일), kind, name, summary, references:[ID], details:[{heading,text}].

Article: id:ART-기록ID, record:기록ID, name, category:kind, tags:[최소2개], references:[대표ID 포함]. frontmatter 값은 한 줄 JSON인 YAML 부분집합이다. 본문240자(공백 제외), 제목2개, details 전체 포함.

Character: born 정수, death_status alive/dead/unknown, dead일 때 died 정수. alive는 as_of 시점의 관측이다.

Event: time 정수 또는 time:null,time_status:range,earliest,latest. after/before는 Event ID 배열. requires_alive는 Character ID 배열. 같은 연도의 죽음/행동은 더 세밀한 순서가 필요하다.

Fact: subject,target ID, temporal_kind:state, certainty:confirmed, start 정수,end 정수 또는 null. end는 제외 경계. 일반 술어 DSL과 공간 순환은 아직 미구현이다.

Power: holder Character, seat 일곱좌 중 하나, start/end. 좌의 중복 재임과 한 인물의 복수좌 동시 점유를 차단한다.

Item: unique:true, owner/keeper Character 또는 Organization, as_of. 다른 이름의 의미적 복제품은 별도 검토가 필요하다.

Claim: truth true/false/undecided 문자열. Belief: holder ID와 claim Claim ID. Thread: status open/resolved.

검토: role canon/knowledge/wiki, verdict approve/revise/reject, findings:[severity blocker/warning,ids,reason,evidence,suggestion]. 영수증: base_commit,world_digest,votes,created_at,model,signature.

작업 field_limits는 경로별 허용 메타데이터 키 목록이다. 지정하면 나머지 필드와 Markdown 본문 변경을 차단한다. 생성자가 임의로 추가하는 옵션이 아니라 운영자 작업 계약이다.

Culture는 장소와 구별하는 반복 관습·생활 문화다. 작업 expected_kinds는 ID별 요구 유형이며 본문이 있어도 유형이 다르면 재작성한다.
