#!/usr/bin/env bash
# Gera o SealedSecret para a aplicação gt-dash contendo GH_PUSH_TOKEN

set -euo pipefail

APP_NAME="gt-dash"
NAMESPACE="gt-dash"
SEALED_NS="kube-system"
SEALED_SVC="sealed-secrets"
OUT_DIR="apps/${APP_NAME}/templates"
OUT_FILE="$OUT_DIR/sealedsecret-${APP_NAME}.yaml"

# Verificação da variável necessária
if [[ -z "${GH_PUSH_TOKEN:-}" ]]; then
  echo "❌ Variável de ambiente GH_PUSH_TOKEN não definida." >&2
  exit 1
fi

# Preparação do diretório de saída
mkdir -p "$OUT_DIR"
rm -f "$OUT_FILE" || true

# Obtém o certificado do controller Sealed Secrets
CERT_TMP=$(mktemp)
trap 'rm -f "$CERT_TMP"' EXIT
kubeseal --controller-namespace="$SEALED_NS" \
         --controller-name="$SEALED_SVC" \
         --fetch-cert > "$CERT_TMP"

# Criação do Secret temporário
kubectl create secret generic "${APP_NAME}-secrets" \
  --from-literal=GH_PUSH_TOKEN="$GH_PUSH_TOKEN" \
  -n "$NAMESPACE" --dry-run=client -o json > /tmp/secret.json

# Geração do SealedSecret
kubeseal -o yaml --cert "$CERT_TMP" \
  --controller-namespace="$SEALED_NS" \
  --controller-name="$SEALED_SVC" \
  < /tmp/secret.json > "$OUT_FILE"

echo "✅ SealedSecret gerado em: $OUT_FILE"
