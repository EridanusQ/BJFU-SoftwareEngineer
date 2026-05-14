#!/usr/bin/env sh
set -eu
ENVIRONMENT="${1:-staging}"
NAMESPACE="nekocafe-${ENVIRONMENT}"
RELEASE="nekocafe"
echo "Rolling back ${RELEASE} in ${NAMESPACE}"
helm history "${RELEASE}" -n "${NAMESPACE}" || true
helm rollback "${RELEASE}" -n "${NAMESPACE}"
kubectl rollout status deploy/nekocafe-reservation -n "${NAMESPACE}" --timeout=120s
kubectl rollout status deploy/nekocafe-member -n "${NAMESPACE}" --timeout=120s
