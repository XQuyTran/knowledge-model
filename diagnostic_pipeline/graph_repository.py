from typing import List, Optional

from .exercise_knowledge_base import find_matching_problems
from .interfaces import GraphRepository
from .models import (
    ExplanationSelection,
    ExplanationStep,
    ProblemKnowledge,
    RepairPlanSelection,
    RepairStep,
    RuleHit,
)


class InMemoryGraphRepository(GraphRepository):
    RULES = {
        'ev.loop.boundary.le_length': [('rule.loop.off_by_one.leq_length', ['bug.off_by_one', 'bug.array_out_of_bounds'], 0.91)],
        'ev.cross.edge_only_failure': [('rule.meta.edge_case_boundary', ['bug.off_by_one', 'bug.array_out_of_bounds', 'bug.wrong_loop_condition'], 0.71)],
        'ev.array.index.size_access': [('rule.array.out_of_bounds.size_index', ['bug.array_out_of_bounds', 'bug.vector_out_of_range'], 0.90)],
        'ev.array.bounds.crash': [('rule.array.out_of_bounds.size_index', ['bug.array_out_of_bounds', 'bug.vector_out_of_range'], 0.96)],
        'ev.pointer.null_check_missing': [('rule.pointer.null_deref.ast', ['bug.null_dereference'], 0.83)],
        'ev.pointer.clang_null': [('rule.pointer.null_deref.clang', ['bug.null_dereference'], 0.97)],
        'ev.memory.release_then_use': [('rule.memory.use_after_free.flow', ['bug.use_after_free', 'bug.dangling_pointer'], 0.96)],
        'ev.memory.sanitizer_uaf': [('rule.memory.uaf.sanitizer', ['bug.use_after_free'], 0.99)],
        'ev.memory.sanitizer_leak': [('rule.memory.leak.sanitizer', ['bug.memory_leak'], 0.99)],
        'ev.memory.static_leak': [('rule.memory.leak.static', ['bug.memory_leak'], 0.93)],
        'ev.memory.alloc_without_release': [('rule.memory.leak.alloc_no_release', ['bug.memory_leak'], 0.87)],
        'ev.function.warn_nonvoid': [('rule.function.missing_return.compiler', ['bug.missing_return'], 0.98)],
        'ev.recursion.no_progress': [('rule.recursion.no_progress', ['bug.no_recursive_progress'], 0.93)],
        'ev.recursion.stack_overflow': [('rule.recursion.stack_overflow', ['bug.no_recursive_progress'], 0.97)],
        'ev.move.use_after_move': [('rule.move.use_after_move', ['bug.use_after_move'], 0.85)],
        'ev.oop.delete_base_no_virtual': [('rule.oop.delete_base_no_virtual', ['bug.missing_virtual_destructor'], 0.96)],
        'ev.format.printf_type_mismatch': [('rule.format.specifier_mismatch', ['bug.format_specifier_mismatch'], 0.95)],
        'ev.uninitialized.value': [('rule.memory.uninitialized', ['bug.uninitialized_value'], 0.85)],
        'ev.compile.error': [('rule.compile.error', ['bug.compile_error'], 0.99)],
        'ev.loop.no_progress': [('rule.loop.no_progress', ['bug.wrong_loop_condition', 'bug.infinite_loop'], 0.88)],
        'ev.loop.timeout': [('rule.loop.timeout', ['bug.infinite_loop', 'bug.wrong_loop_condition'], 0.90)],
        'ev.sort.insertion.missed_zero_index': [('rule.sort.insertion.off_by_one', ['bug.off_by_one', 'bug.wrong_loop_condition'], 0.88)],
        'ev.sort.insertion.wrong_insert_position': [('rule.sort.insertion.wrong_insert', ['bug.array_out_of_bounds', 'bug.wrong_loop_condition'], 0.78)],
        'ev.sort.insertion.missing_decrement': [('rule.sort.insertion.infinite_loop', ['bug.infinite_loop', 'bug.wrong_loop_condition'], 0.90)],
        'ev.sort.bubble.wrong_order': [('rule.sort.bubble.wrong_order', ['bug.wrong_loop_condition'], 0.72)],
    }

    PROBLEM_RULES = {
        'ex_array_sum': {'algorithm': 'algorithm.duyet_mang_tuan_tu', 'bugs': ['bug.off_by_one', 'bug.array_out_of_bounds']},
        'ex_array_max': {'algorithm': 'algorithm.duyet_mang_tim_max', 'bugs': ['bug.off_by_one', 'bug.uninitialized_value']},
        'ex_array_reverse': {'algorithm': 'algorithm.dao_nguoc_tai_cho', 'bugs': ['bug.off_by_one', 'bug.array_out_of_bounds']},
        'ex_loop_factorial': {'algorithm': 'algorithm.vong_lap_tich_luy', 'bugs': ['bug.off_by_one', 'bug.wrong_loop_condition']},
        'ex_loop_prime': {'algorithm': 'algorithm.kiem_tra_uoc_so', 'bugs': ['bug.wrong_loop_condition', 'bug.off_by_one']},
        'ex_loop_fibonacci': {'algorithm': 'algorithm.vong_lap_bo_nho_dem', 'bugs': ['bug.off_by_one', 'bug.uninitialized_value']},
        'ex_rec_factorial': {'algorithm': 'algorithm.de_quy_tuyen_tinh', 'bugs': ['bug.no_recursive_progress', 'bug.missing_return']},
        'ex_rec_fibonacci': {'algorithm': 'algorithm.de_quy_nhi_phan', 'bugs': ['bug.no_recursive_progress', 'bug.missing_return', 'bug.off_by_one']},
        'ex_rec_hanoi': {'algorithm': 'algorithm.de_quy_chia_de_tri', 'bugs': ['bug.no_recursive_progress', 'bug.wrong_loop_condition']},
        'ex_ds_linked_list': {'algorithm': 'algorithm.thao_tac_danh_sach_lien_ket', 'bugs': ['bug.null_dereference', 'bug.memory_leak', 'bug.dangling_pointer']},
        'ex_ds_stack_array': {'algorithm': 'algorithm.ngan_xep_lifo', 'bugs': ['bug.array_out_of_bounds', 'bug.off_by_one']},
        'ex_sort_bubble': {'algorithm': 'algorithm.bubble_sort', 'bugs': ['bug.off_by_one', 'bug.array_out_of_bounds', 'bug.wrong_loop_condition']},
        'ex_sort_selection': {'algorithm': 'algorithm.selection_sort', 'bugs': ['bug.off_by_one', 'bug.array_out_of_bounds']},
        'ex_sort_insertion': {'algorithm': 'algorithm.insertion_sort', 'bugs': ['bug.array_out_of_bounds', 'bug.off_by_one']},
        'ex_search_linear': {'algorithm': 'algorithm.tim_kiem_tuyen_tinh', 'bugs': ['bug.off_by_one', 'bug.wrong_loop_condition']},
        'ex_search_binary': {'algorithm': 'algorithm.tim_kiem_nhi_phan', 'bugs': ['bug.off_by_one', 'bug.wrong_loop_condition', 'bug.infinite_loop']},
    }

    def match_rules(self, evidence_ids: List[str], concept_ids: List[str]) -> List[RuleHit]:
        hits: List[RuleHit] = []
        for evidence_id in evidence_ids:
            for rule_id, bug_ids, confidence in self.RULES.get(evidence_id, []):
                hits.append(RuleHit(rule_id, bug_ids, [evidence_id], concept_ids[:4], confidence))
        return hits

    def match_problem_rules(self, problem_id: str) -> List[RuleHit]:
        info = self.PROBLEM_RULES.get(problem_id)
        if not info:
            return []
        return [
            RuleHit(
                rule_id=f'rule.problem.{info["algorithm"]}',
                bug_ids=info['bugs'],
                matched_evidence_ids=[],
                matched_concept_ids=[info['algorithm']],
                confidence=0.75,
            )
        ]

    def match_problems(self, statement: str, top_n: int = 3) -> List[ProblemKnowledge]:
        return find_matching_problems(statement, top_n)

    def select_explanation(self, bug_id: str, rule_ids: List[str], concept_ids: List[str]) -> Optional[ExplanationSelection]:
        return ExplanationSelection(
            template_id=f'expl.auto.{bug_id}',
            name=f'Explanation for {bug_id}',
            steps=[
                ExplanationStep('LocateEvidence', 'Locate the statement that produced the strongest diagnostic evidence.', 'locate'),
                ExplanationStep('ExplainSemanticMismatch', 'Explain how the observed behavior conflicts with the problem requirement.', 'concept'),
                ExplanationStep('ConnectRepair', 'Connect the diagnosis to the smallest safe source-code repair.', 'repair'),
            ],
        )

    def select_repair_plan(self, bug_id: str, rule_ids: List[str], concept_ids: List[str]) -> Optional[RepairPlanSelection]:
        plan_by_bug = {
            'bug.off_by_one': ('repair.boundary_validation', 'BoundaryValidation', ['Inspect the loop boundary and decide whether the upper bound should be exclusive.', 'Verify the valid index range for the accessed sequence.', 'Change the smallest condition or index expression and rerun the boundary test.']),
            'bug.array_out_of_bounds': ('repair.boundary_validation', 'BoundaryValidation', ['Locate the index expression that can exceed the sequence range.', 'Constrain the index to the valid range.', 'Rerun the smallest failing boundary case.']),
            'bug.vector_out_of_range': ('repair.boundary_validation', 'BoundaryValidation', ['Locate the vector access.', 'Verify size-based boundaries.', 'Use a safe boundary condition and rerun tests.']),
            'bug.null_dereference': ('repair.pointer_safety', 'PointerSafetyRepair', ['Locate the dereference.', 'Trace assignments to determine whether null is possible.', 'Add a guard or redesign ownership before dereference.']),
            'bug.use_after_free': ('repair.resource_lifecycle', 'ResourceLifecycleRepair', ['Trace the release operation.', 'Locate later access through the released handle.', 'Remove the later access or transfer ownership safely.']),
            'bug.memory_leak': ('repair.resource_lifecycle', 'ResourceLifecycleRepair', ['Locate the allocation site.', 'Find all exit paths from the owner scope.', 'Release exactly once or replace manual ownership with RAII.']),
            'bug.missing_return': ('repair.control_flow_completion', 'ControlFlowCompletionRepair', ['Find the non-void function path with no return.', 'Choose the correct value for that path.', 'Add the return without changing unrelated logic.']),
            'bug.no_recursive_progress': ('repair.recursion_progress', 'RecursionProgressRepair', ['Locate the recursive call.', 'Verify the argument changes toward the base case.', 'Rewrite the recursive call to reduce the problem size.']),
            'bug.use_after_move': ('repair.move_semantic_safety', 'MoveSemanticSafetyRepair', ['Locate the move operation.', 'Find later reads of the moved-from object.', 'Reinitialize the object or avoid depending on its old value.']),
            'bug.missing_virtual_destructor': ('repair.polymorphic_lifetime', 'PolymorphicLifetimeRepair', ['Locate deletion through a base pointer.', 'Check whether the base class is polymorphic.', 'Add a virtual destructor to the base class.']),
            'bug.format_specifier_mismatch': ('repair.format_type_safety', 'FormatTypeSafetyRepair', ['Locate the formatting call.', 'Match each placeholder to its argument type.', 'Correct the specifier or use type-safe formatting.']),
            'bug.wrong_loop_condition': ('repair.loop_condition', 'LoopConditionRepair', ['Identify the loop condition that causes incorrect iteration.', 'Determine the correct bound, comparator, or update.', 'Fix the condition and verify with test cases.']),
            'bug.infinite_loop': ('repair.infinite_loop', 'InfiniteLoopRepair', ['Locate the loop that does not terminate.', 'Check whether the loop variable is updated correctly.', 'Add or fix the update statement inside the loop.']),
            'bug.uninitialized_value': ('repair.initialize_variable', 'InitializeVariableRepair', ['Locate the variable read before initialization.', 'Assign a default value at declaration.', 'Verify the value is correct for all code paths.']),
            'bug.compile_error': ('repair.fix_syntax', 'FixSyntaxRepair', ['Read the compiler error message.', 'Fix the reported line.', 'Recompile and verify.']),
        }
        plan = plan_by_bug.get(bug_id)
        if not plan:
            return None
        plan_id, name, descriptions = plan
        steps = [RepairStep(f'step.auto.{idx}', f'Step{idx}', description, idx) for idx, description in enumerate(descriptions, start=1)]
        return RepairPlanSelection(plan_id, name, steps)


class Neo4jGraphRepository(GraphRepository):
    def __init__(self, driver, database: str = 'neo4j'):
        self.driver = driver
        self.database = database

    def _session(self):
        return self.driver.session(database=self.database)

    def match_rules(self, evidence_ids: List[str], concept_ids: List[str]) -> List[RuleHit]:
        query = """
        MATCH (r:DiagnosticRule)-[:USES_EVIDENCE]->(e:EvidencePattern)
        WHERE e.id IN $evidence_ids
        MATCH (r)-[:DETECTS_BUG]->(b:ProgrammingBug)
        OPTIONAL MATCH (r)-[:APPLIES_TO_CONCEPT]->(c:ProgrammingConcept)
        WHERE c.id IN $concept_ids
        RETURN r.id AS rule_id,
               collect(DISTINCT b.id) AS bug_ids,
               collect(DISTINCT e.id) AS evidence_ids,
               collect(DISTINCT c.id) AS concept_ids,
               coalesce(r.confidenceBase, 0.7) AS confidence
        """
        with self._session() as session:
            records = session.run(query, evidence_ids=evidence_ids, concept_ids=concept_ids)
            return [RuleHit(record['rule_id'], list(record['bug_ids']), list(record['evidence_ids']), list(record['concept_ids']), float(record['confidence'])) for record in records]

    def match_problem_rules(self, problem_id: str) -> List[RuleHit]:
        query = """
        MATCH (p {id: $problem_id})
        OPTIONAL MATCH (p)-[algorithm_rel]->(algo)
        WHERE type(algorithm_rel) = 'HAS_ALGORITHM'
        WITH p, head(collect(DISTINCT algo.id)) AS algorithm_id
        OPTIONAL MATCH (p)-[bug_rel]->(bug)
        WHERE type(bug_rel) = 'HAS_COMMON_BUG'
        RETURN algorithm_id AS algorithm_id,
               [bug_id IN collect(DISTINCT bug.id) WHERE bug_id IS NOT NULL] AS bug_ids
        """
        with self._session() as session:
            record = session.run(query, problem_id=problem_id).single()
        if record and record['algorithm_id']:
            algorithm_id = record['algorithm_id']
            bug_ids = list(record['bug_ids'] or [])
            if bug_ids:
                return [RuleHit(f'rule.problem.{algorithm_id}', bug_ids, [], [algorithm_id], 0.75)]
        info = InMemoryGraphRepository.PROBLEM_RULES.get(problem_id)
        if not info:
            return []
        return [RuleHit(f'rule.problem.{info["algorithm"]}', list(info['bugs']), [], [info['algorithm']], 0.75)]

    def select_explanation(self, bug_id: str, rule_ids: List[str], concept_ids: List[str]) -> Optional[ExplanationSelection]:
        query = """
        MATCH (t:ExplanationTemplate)-[:EXPLAINS_BUG]->(:ProgrammingBug {id: $bug_id})
        OPTIONAL MATCH (t)-[:TRIGGERED_BY_RULE]->(r:DiagnosticRule)
        WHERE r.id IN $rule_ids
        OPTIONAL MATCH (t)-[:CONSISTS_OF_STEP]->(s:ExplanationStep)
        RETURN t.id AS template_id, t.name AS name,
               collect(DISTINCT {name: s.name, text: s.text, kind: s.stepKind}) AS steps,
               count(DISTINCT r) AS matched_rules
        ORDER BY matched_rules DESC
        LIMIT 1
        """
        with self._session() as session:
            record = session.run(query, bug_id=bug_id, rule_ids=rule_ids).single()
            if not record:
                return None
            steps = [ExplanationStep(x['name'] or 'Step', x['text'] or '', x['kind'] or 'repair') for x in record['steps'] if x.get('text')]
            return ExplanationSelection(record['template_id'], record['name'], steps)

    def select_repair_plan(self, bug_id: str, rule_ids: List[str], concept_ids: List[str]) -> Optional[RepairPlanSelection]:
        query = """
        MATCH (p:RepairPlan)-[:REPAIRS_BUG]->(:ProgrammingBug {id: $bug_id})
        OPTIONAL MATCH (p)-[cs:CONSISTS_OF_STEP]->(s:RepairStepTemplate)
        OPTIONAL MATCH (p)-[:USES_ACTION]->(a:RepairAction)
        OPTIONAL MATCH (p)-[:MUST_SATISFY]->(c:RepairConstraint)
        RETURN p.id AS plan_id, p.name AS name,
               collect(DISTINCT {id: s.id, name: s.name, description: s.description, order: coalesce(cs.order, s.defaultOrder)}) AS steps,
               collect(DISTINCT a.name) AS actions,
               collect(DISTINCT c.name) AS constraints
        LIMIT 1
        """
        with self._session() as session:
            record = session.run(query, bug_id=bug_id).single()
            if not record:
                return None
            steps = [RepairStep(x['id'], x['name'], x['description'], int(x['order'] or 999)) for x in record['steps'] if x.get('id')]
            return RepairPlanSelection(record['plan_id'], record['name'], steps, list(record['actions']), list(record['constraints']))
