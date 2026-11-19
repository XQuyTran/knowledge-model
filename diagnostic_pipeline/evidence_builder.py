from typing import Iterable, List

from .models import EvidenceInstance


EVIDENCE_TO_CONCEPTS = {
    'ev.loop.boundary.le_length': ['concept.c.array', 'concept.c.for', 'concept.cpp.vector', 'concept.cpp.range_for'],
    'ev.loop.boundary.starts_one': ['concept.c.array', 'concept.c.for', 'concept.cpp.array', 'concept.cpp.vector'],
    'ev.loop.timeout': ['concept.c.for', 'concept.c.while', 'concept.cpp.for', 'concept.cpp.while'],
    'ev.loop.no_progress': ['concept.c.while', 'concept.c.for', 'concept.cpp.loop'],
    'ev.cross.edge_only_failure': ['concept.c.array', 'concept.cpp.vector', 'concept.cpp.range_for'],
    'ev.array.index.size_access': ['concept.c.array', 'concept.cpp.array', 'concept.cpp.vector'],
    'ev.array.bounds.crash': ['concept.c.array', 'concept.cpp.array', 'concept.cpp.vector'],
    'ev.pointer.null_check_missing': ['concept.c.pointer', 'concept.cpp.pointer', 'concept.cpp.smart_pointer'],
    'ev.pointer.clang_null': ['concept.c.pointer', 'concept.cpp.pointer'],
    'ev.memory.release_then_use': ['concept.c.free', 'concept.cpp.new_delete', 'concept.c.pointer', 'concept.cpp.pointer'],
    'ev.memory.sanitizer_uaf': ['concept.c.pointer', 'concept.cpp.pointer'],
    'ev.memory.sanitizer_leak': ['concept.c.malloc', 'concept.cpp.new_delete'],
    'ev.memory.alloc_without_release': ['concept.c.malloc', 'concept.cpp.new_delete', 'concept.cpp.raii'],
    'ev.function.warn_nonvoid': ['concept.c.function_def', 'concept.cpp.function_decl', 'concept.cpp.return'],
    'ev.recursion.no_progress': ['concept.c.function_def', 'concept.cpp.function_decl'],
    'ev.move.use_after_move': ['concept.cpp.move_semantics', 'concept.cpp.unique_ptr', 'concept.cpp.vector'],
    'ev.oop.delete_base_no_virtual': ['concept.cpp.class', 'concept.cpp.virtual_function', 'concept.cpp.destructor'],
    'ev.format.printf_type_mismatch': ['concept.c.formatted_io', 'concept.cpp.format', 'concept.cpp.print_functions'],
    'ev.compile.error': ['concept.c.syntax', 'concept.cpp.compilation'],
    'ev.uninitialized.value': ['concept.c.variable', 'concept.cpp.initialization'],
    'ev.memory.static_leak': ['concept.memory', 'concept.resource_lifecycle'],
    'ev.loop.timeout': ['concept.loop.control'],
    'ev.recursion.stack_overflow': ['concept.recursion', 'concept.recursion.base_case'],
    'ev.sort.insertion.pattern': ['algorithm.insertion_sort', 'concept.sort.insertion', 'concept.loop.nested'],
    'ev.sort.insertion.missed_zero_index': ['algorithm.insertion_sort', 'concept.loop.boundary'],
    'ev.sort.insertion.wrong_insert_position': ['algorithm.insertion_sort', 'concept.array.indexing'],
    'ev.sort.insertion.missing_decrement': ['algorithm.insertion_sort', 'concept.loop.control'],
    'ev.sort.bubble.pattern': ['algorithm.bubble_sort', 'concept.sort.bubble', 'concept.loop.nested'],
    'ev.sort.bubble.wrong_order': ['algorithm.bubble_sort', 'concept.sort.ordering'],
    'ev.search.binary.pattern': ['algorithm.tim_kiem_nhi_phan', 'concept.search.binary']
}


class EvidenceBuilder:
    def merge(self, evidence_sets: Iterable[Iterable[EvidenceInstance]]) -> List[EvidenceInstance]:
        best_by_key = {}
        for evidence_set in evidence_sets:
            for item in evidence_set:
                key = (item.evidence_id, item.location.line_start if item.location else None)
                previous = best_by_key.get(key)
                if previous is None or item.confidence > previous.confidence:
                    best_by_key[key] = item
        merged = list(best_by_key.values())
        return sorted(merged, key=lambda e: (e.location.line_start if e.location and e.location.line_start else 999999, e.evidence_id))

    def infer_concepts(self, evidence: Iterable[EvidenceInstance]) -> List[str]:
        seen = set()
        concepts: List[str] = []
        for item in evidence:
            for concept_id in EVIDENCE_TO_CONCEPTS.get(item.evidence_id, []):
                if concept_id not in seen:
                    concepts.append(concept_id)
                    seen.add(concept_id)
        return concepts
