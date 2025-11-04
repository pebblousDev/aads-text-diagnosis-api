import subprocess
import logging
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
import re

# 환경 변수 설정
class Settings(BaseSettings):
    script_path: str  # 기본값 제거 - 필수 값으로 설정
    log_dir: str = "./logs"  # 로그 디렉토리 경로

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# 로그 디렉토리 생성
os.makedirs(settings.log_dir, exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Diagnosis Engine Text Dataset API",
    description="API for executing diagnosis scripts on text datasets",
    version="1.0.0"
)


class DiagnosisRequest(BaseModel):
    dataset: str = Field(..., description="Dataset name to process")

    @validator('dataset')
    def validate_dataset(cls, v):
        # 입력값 검증: 알파벳, 숫자, 언더스코어, 하이픈만 허용
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Dataset name must contain only alphanumeric characters, underscores, and hyphens')
        if len(v) > 100:
            raise ValueError('Dataset name must be less than 100 characters')
        return v


class DiagnosisResponse(BaseModel):
    message: str


@app.get("/")
async def root():
    return {"status": "healthy", "service": "Diagnosis Engine Text Dataset API"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/diagnosis/application", response_model=DiagnosisResponse)
async def diagnosis_application(request: DiagnosisRequest):
    """
    비동기로 진단 스크립트를 실행합니다.

    - **dataset**: 처리할 데이터셋 이름
    """
    dataset = request.dataset

    logger.info(f"Received diagnosis application request for dataset: {dataset}")

    # 환경 변수에서 쉘 스크립트 경로 가져오기
    script_path = settings.script_path

    try:
        # 로그 파일 경로 생성 (일별)
        date_str = datetime.now().strftime("%Y%m%d")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file_path = os.path.join(
            settings.log_dir,
            f"diagnosis_{date_str}.log"
        )

        # 로그 파일 열기 (append 모드)
        log_file = open(log_file_path, 'a')

        # 로그 구분을 위한 헤더 작성
        log_file.write(f"\n{'='*80}\n")
        log_file.write(f"[{timestamp}] Starting diagnosis for dataset: {dataset}\n")
        log_file.write(f"{'='*80}\n\n")
        log_file.flush()

        # 호스트 환경에서 스크립트 실행
        # nsenter로 호스트 네임스페이스에 진입하여 pbls_dev 사용자로 실행
        # --setuid, --setgid로 직접 UID/GID 지정
        # HOME 환경 변수를 설정하고 로그인 쉘로 실행
        env = os.environ.copy()
        env['HOME'] = '/home/pbls_dev'
        env['USER'] = 'pbls_dev'

        process = subprocess.Popen([
            "nsenter", "-t", "1", "-m", "-u", "-i", "-n", "-p",
            "--setuid", "100001", "--setgid", "1003",
            "bash", "-l", "-c",
            f"cd /pbls_data/projects/dataclinic-diagnosis-engine/diagnosis && bash {script_path} {dataset}"
        ], stdout=log_file, stderr=subprocess.STDOUT, text=True, env=env)

        logger.info(
            f"Started diagnosis script for dataset '{dataset}' with PID: {process.pid}. "
            f"Logs will be written to: {log_file_path}"
        )

        return DiagnosisResponse(
            message=f"Diagnosis application submitted for {dataset}. Check logs at: {log_file_path}"
        )

    except FileNotFoundError:
        logger.error(f"Script not found at path: {script_path}")
        raise HTTPException(
            status_code=500,
            detail=f"Diagnosis script not found at {script_path}"
        )
    except Exception as e:
        logger.error(f"Error executing diagnosis script: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute diagnosis script: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
