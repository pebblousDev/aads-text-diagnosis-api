# Diagnosis Engine Text Dataset API

FastAPI 기반의 텍스트 데이터셋 진단 스크립트 실행 API 서버입니다.

## 기능

- POST `/diagnosis/application`: 진단 스크립트를 비동기로 실행
- 입력값 검증
- 로그 및 에러 처리

## 요구사항

- Python 3.11+
- Docker (선택사항)

## 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python main.py
```

서버는 `http://localhost:8000`에서 실행됩니다.

## Docker Compose 실행 (권장)

### 초기 설정

```bash
# .env 파일 생성
cp .env.example .env
# .env 파일 편집하여 SCRIPT_PATH 설정
```

### Setup 스크립트 사용

```bash
# 전체 업데이트 및 재시작 (git pull + rebuild + restart)
./setup.sh

# 재시작만 (빌드 없이)
./setup.sh restart
```

### 수동 실행

```bash
# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down

# 서비스 재시작
docker-compose restart
```

서버는 `http://192.168.0.24:13321`에서 접근 가능합니다.
(포트포워딩: 외부포트 13032 -> 서버포트 13321 -> 컨테이너포트 8000)

## Docker 실행 (대안)

```bash
# 이미지 빌드
docker build -t aads-text-diagnosis-api:latest .

# 컨테이너 실행 (볼륨 마운트 포함)
docker run -d \
  -p 13321:8000 \
  -v /storage_data/projects:/storage_data/projects \
  -v /pbls_data/projects:/pbls_data/projects \
  --name aads-text-diagnosis-api \
  aads-text-diagnosis-api:latest
```

## API 사용법

### Health Check

```bash
# 로컬
curl http://localhost:8000/health

# 서버 (포트포워딩 후)
curl http://192.168.0.24:13321/health
```

### 진단 신청

```bash
# 로컬
curl -X POST http://localhost:8000/diagnosis/application \
  -H "Content-Type: application/json" \
  -d '{"dataset": "my_dataset"}'

# 서버 (포트포워딩 후)
curl -X POST http://192.168.0.24:13321/diagnosis/application \
  -H "Content-Type: application/json" \
  -d '{"dataset": "my_dataset"}'
```

**응답 예시:**
```json
{
  "message": "Diagnosis application submitted for my_dataset"
}
```

## API 문서

서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- Swagger UI: `http://192.168.0.24:13321/docs`
- ReDoc: `http://192.168.0.24:13321/redoc`

## 입력값 검증

`dataset` 파라미터는 다음 규칙을 따라야 합니다:
- 알파벳, 숫자, 언더스코어(`_`), 하이픈(`-`)만 허용
- 최대 100자

## 실행 프로세스

1. API 호출 수신
2. 입력값 검증
3. 백그라운드에서 `bash command_text.sh <dataset>` 실행
4. 즉시 "신청 완료" 응답 반환
5. 스크립트는 백그라운드에서 계속 실행됨

## 볼륨 마운트

다음 경로가 컨테이너에 마운트되어야 합니다:
- `/storage_data/projects` - 데이터 및 결과 저장
- `/pbls_data/projects/dataclinic-diagnosis-engine/diagnosis` - 스크립트 위치

## 로그

애플리케이션 로그는 표준 출력으로 출력되며, Docker 환경에서는 다음 명령으로 확인할 수 있습니다:

```bash
docker logs aads-text-diagnosis-api
```
