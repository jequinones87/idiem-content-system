#!/bin/bash
# Inicio de sesión (cloud): dependencias de Python + verificación previa de producción.
# La salida queda en el contexto de la sesión: avisa de ramas con trabajo no integrado,
# siguientes IDs libres y dónde está el playbook (docs/14_PLAYBOOK_PRODUCCION.md).
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

# pip al Python del sistema: no llena un directorio ignorado por git, así que corre siempre
# (es idempotente y rápido cuando ya está instalado).
python3 -m pip install -q --disable-pip-version-check --root-user-action=ignore -r requirements.txt >/dev/null

echo 'export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"' >> "${CLAUDE_ENV_FILE:-/dev/null}"

# Verificación previa: no debe bloquear la sesión si la red falla.
timeout 60 env PYTHONPATH=src python3 -m idiem.preflight --brief || \
  echo "IDIEM: no se pudo correr la verificación previa; correr 'PYTHONPATH=src python3 -m idiem.preflight' antes de producir."
