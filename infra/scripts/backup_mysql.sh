#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# AURUM QUANT - MYSQL BACKUP SCRIPT WITH 14-DAY ROTATION
# ==============================================================================

BACKUP_DIR="${BACKUP_DIR:-/backups/mysql}"
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%SZ")
BACKUP_FILE="${BACKUP_DIR}/gold_predict_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=14

MYSQL_HOST="${MYSQL_HOST:-localhost}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_USER="${MYSQL_USER:-gold_user}"
MYSQL_PWD="${MYSQL_PASSWORD:-SecureGoldPassword2026!}"
MYSQL_DB="${MYSQL_DATABASE:-gold_predict}"

mkdir -p "${BACKUP_DIR}"

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Bắt đầu sao lưu cơ sở dữ liệu ${MYSQL_DB}..."

export MYSQL_PWD
mysqldump \
  --host="${MYSQL_HOST}" \
  --port="${MYSQL_PORT}" \
  --user="${MYSQL_USER}" \
  --single-transaction \
  --routines \
  --triggers \
  --default-character-set=utf8mb4 \
  "${MYSQL_DB}" | gzip -c > "${BACKUP_FILE}"

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Sao lưu thành công: ${BACKUP_FILE} ($(du -h "${BACKUP_FILE}" | cut -f1))"

# Tự động xoay vòng xóa bản sao lưu cũ hơn 14 ngày
echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Dọn dẹp bản sao lưu cũ hơn ${RETENTION_DAYS} ngày..."
find "${BACKUP_DIR}" -name "gold_predict_*.sql.gz" -mtime +${RETENTION_DAYS} -exec rm -f {} \;

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Hoàn tất sao lưu."
