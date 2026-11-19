// ============================================================================
// SAFE SEED: Algorithm-Specific Diagnostic Rules
// - Idempotent (can run multiple times)
// - No conflicts with problem seed
// - Uses MERGE correctly with named variables
// ============================================================================


// ---------------------------------------------------------------------------
// SECTION 1: Ensure EvidencePattern nodes (safe MERGE)
// ---------------------------------------------------------------------------

MERGE (e1:EvidencePattern {id: "ev.memory.static_leak"})
ON CREATE SET e1.name = "Static memory leak evidence"

MERGE (e2:EvidencePattern {id: "ev.loop.timeout"})
ON CREATE SET e2.name = "Loop timeout evidence"

MERGE (e3:EvidencePattern {id: "ev.recursion.stack_overflow"})
ON CREATE SET e3.name = "Stack overflow recursion evidence"

MERGE (e4:EvidencePattern {id: "ev.sort.insertion.missed_zero_index"})
MERGE (e5:EvidencePattern {id: "ev.sort.insertion.wrong_insert_position"})
MERGE (e6:EvidencePattern {id: "ev.sort.insertion.missing_decrement"})

MERGE (e7:EvidencePattern {id: "ev.sort.bubble.wrong_order"})


// ---------------------------------------------------------------------------
// SECTION 2: Ensure Bug nodes (shared with problem seed)
// (SAFE: MERGE only, no override)
// ---------------------------------------------------------------------------

MERGE (b1:ProgrammingBug {id: "bug.memory_leak"})
MERGE (b2:ProgrammingBug {id: "bug.infinite_loop"})
MERGE (b3:ProgrammingBug {id: "bug.no_recursive_progress"})
MERGE (b4:ProgrammingBug {id: "bug.off_by_one"})
MERGE (b5:ProgrammingBug {id: "bug.wrong_loop_condition"})
MERGE (b6:ProgrammingBug {id: "bug.array_out_of_bounds"})


// ---------------------------------------------------------------------------
// SECTION 3: Ensure Algorithm nodes exist (already created by problem seed)
// SAFE: MERGE only
// ---------------------------------------------------------------------------

MERGE (algoInsertion:Algorithm {id: "algorithm.insertion_sort"})
MERGE (algoBubble:Algorithm {id: "algorithm.bubble_sort"})


// ---------------------------------------------------------------------------
// SECTION 4: Diagnostic Rules
// ---------------------------------------------------------------------------

// 4.1 Static memory leak
MERGE (r1:DiagnosticRule {id: "rule.memory.leak.static"})
ON CREATE SET r1.confidenceBase = 0.93
MERGE (r1)-[:USES_EVIDENCE]->(e1)
MERGE (r1)-[:DETECTS_BUG]->(b1)


// 4.2 Loop timeout → infinite loop
MERGE (r2:DiagnosticRule {id: "rule.loop.timeout"})
ON CREATE SET r2.confidenceBase = 0.90
MERGE (r2)-[:USES_EVIDENCE]->(e2)
MERGE (r2)-[:DETECTS_BUG]->(b2)
MERGE (r2)-[:DETECTS_BUG]->(b5)


// 4.3 Recursion stack overflow
MERGE (r3:DiagnosticRule {id: "rule.recursion.stack_overflow"})
ON CREATE SET r3.confidenceBase = 0.97
MERGE (r3)-[:USES_EVIDENCE]->(e3)
MERGE (r3)-[:DETECTS_BUG]->(b3)


// 4.4 Insertion sort: off-by-one
MERGE (r4:DiagnosticRule {id: "rule.sort.insertion.off_by_one"})
ON CREATE SET r4.confidenceBase = 0.88
MERGE (r4)-[:USES_EVIDENCE]->(e4)
MERGE (r4)-[:DETECTS_BUG]->(b4)
MERGE (r4)-[:DETECTS_BUG]->(b5)
MERGE (r4)-[:APPLIES_TO_CONCEPT]->(algoInsertion)


// 4.5 Insertion sort: wrong insert
MERGE (r5:DiagnosticRule {id: "rule.sort.insertion.wrong_insert"})
ON CREATE SET r5.confidenceBase = 0.78
MERGE (r5)-[:USES_EVIDENCE]->(e5)
MERGE (r5)-[:DETECTS_BUG]->(b6)
MERGE (r5)-[:DETECTS_BUG]->(b5)
MERGE (r5)-[:APPLIES_TO_CONCEPT]->(algoInsertion)


// 4.6 Insertion sort: infinite loop
MERGE (r6:DiagnosticRule {id: "rule.sort.insertion.infinite_loop"})
ON CREATE SET r6.confidenceBase = 0.90
MERGE (r6)-[:USES_EVIDENCE]->(e6)
MERGE (r6)-[:DETECTS_BUG]->(b2)
MERGE (r6)-[:DETECTS_BUG]->(b5)
MERGE (r6)-[:APPLIES_TO_CONCEPT]->(algoInsertion)


// 4.7 Bubble sort wrong order
MERGE (r7:DiagnosticRule {id: "rule.sort.bubble.wrong_order"})
ON CREATE SET r7.confidenceBase = 0.72
MERGE (r7)-[:USES_EVIDENCE]->(e7)
MERGE (r7)-[:DETECTS_BUG]->(b5)
MERGE (r7)-[:APPLIES_TO_CONCEPT]->(algoBubble)
