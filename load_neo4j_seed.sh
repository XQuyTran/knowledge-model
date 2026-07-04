#!/usr/bin/env bash
set -Eeuo pipefail

NEO4J_URI="${NEO4J_URI:-bolt://neo4j:7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-password}"
NEO4J_DATABASE="${NEO4J_DATABASE:-neo4j}"
WORKSPACE_DIR="${WORKSPACE_DIR:-/workspace}"

SEED_FILES=(
  "neo4j_latest_concepts_seed.cypher"
  "neo4j_bug_ontology_seed.cypher"
  "neo4j_diagnostic_rules_seed.cypher"
  "neo4j_explanation_feedback_seed.cypher"
  "neo4j_repair_ontology_seed.cypher"
)

function wait_for_neo4j() {
  echo "[seed] Waiting for Neo4j at ${NEO4J_URI} ..."
  for attempt in $(seq 1 60); do
    if cypher-shell -a "${NEO4J_URI}" -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" -d "${NEO4J_DATABASE}" "RETURN 1;" >/dev/null 2>&1; then
      echo "[seed] Neo4j is ready."
      return 0
    fi
    sleep 2
  done
  echo "[seed] Neo4j did not become ready in time." >&2
  return 1
}

function assert_seed_files_exist() {
  local missing=0
  for file in "${SEED_FILES[@]}"; do
    if [[ ! -f "${WORKSPACE_DIR}/${file}" ]]; then
      echo "[seed] Missing seed file: ${WORKSPACE_DIR}/${file}" >&2
      missing=1
    fi
  done
  if [[ "${missing}" -ne 0 ]]; then
    echo "[seed] One or more required seed files are missing." >&2
    echo "[seed] Place all generated *.cypher seed files next to docker-compose.yml before running the seed profile." >&2
    return 1
  fi
}

function apply_seed_file() {
  local file_path="$1"
  echo "[seed] Applying ${file_path} ..."
  cypher-shell     -a "${NEO4J_URI}"     -u "${NEO4J_USER}"     -p "${NEO4J_PASSWORD}"     -d "${NEO4J_DATABASE}"     --fail-fast     -f "${file_path}"
  echo "[seed] Applied ${file_path}"
}

wait_for_neo4j
assert_seed_files_exist

for file in "${SEED_FILES[@]}"; do
  apply_seed_file "${WORKSPACE_DIR}/${file}"
done

echo "[seed] All Neo4j seed files have been loaded successfully."
