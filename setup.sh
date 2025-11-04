#!/bin/bash
#
# AADS Text Diagnosis API Setup Script
# 서버 배포 시 Git 업데이트 및 컨테이너 재시작
#
# Usage:
#   ./setup.sh           - 전체 재시작 (git pull + rebuild + restart)
#   ./setup.sh restart   - 재시작만 (빌드 없이)
#

set -e  # 에러 발생 시 중단

ACTION=$1

if [ "$ACTION" == "restart" ]; then
  echo "🔄 AADS Text Diagnosis API 재시작 중..."

  docker compose restart

  echo ""
  echo "✅ 재시작 완료!"
  echo ""
  echo "📊 상태 확인:"
  docker compose ps
  echo ""

else
  echo "🚀 AADS Text Diagnosis API 전체 업데이트 시작..."

  # 1. Git pull
  echo "📥 Git 최신 변경사항 가져오기..."
  git pull

  # 2. .env 파일 존재 확인
  if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다!"
    echo "📝 .env.example을 참고하여 .env 파일을 생성하세요."
    exit 1
  fi

  # 3. Docker Compose 재빌드 및 재시작
  echo "🐳 Docker 컨테이너 재빌드 및 재시작 중..."
  docker compose down
  docker compose build --no-cache
  docker compose up -d

  echo ""
  echo "✅ 전체 업데이트 및 재시작 완료!"
  echo ""
  echo "📊 상태 확인:"
  docker compose ps
  echo ""
  echo "📋 로그 확인: docker compose logs -f"
  echo ""
fi
