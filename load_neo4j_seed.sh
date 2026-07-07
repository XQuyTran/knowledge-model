#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE_DIR="${WORKSPACE_DIR:-/workspace}"

SEED_FILES=(
  "concepts/neo4j_latest_concepts_seed.cypher"
  "bugs/neo4j_bug_ontology_seed.cypher"
  "diagnostic/neo4j_diagnostic_rules_seed.cypher"
  "explanation/neo4j_explanation_feedback_seed.cypher"
  "repairs/neo4j_repair_ontology_seed.cypher"
  "problems/neo4j_problem_rules_seed.cypher"
  "problems/neo4j_algorithm_specific_rules_seed.cypher"
)

function wait_for_neo4j() {
  echo "[seed] Waiting for Neo4j at ${NEO4J_URI} ..."
  for attempt in $(seq 1 30); do
    if cypher-shell --format verbose -d system "SHOW DATABASES"; then
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
  cypher-shell -d "${NEO4J_DATABASE}" --fail-fast --file "${file_path}"
  echo "[seed] Applied ${file_path}"
}

wait_for_neo4j
assert_seed_files_exist

for file in "${SEED_FILES[@]}"; do
  apply_seed_file "${WORKSPACE_DIR}/${file}"
done

echo "[seed] All Neo4j seed files have been loaded successfully."
