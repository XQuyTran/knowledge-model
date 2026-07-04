"""Build the Neo4j Repair Ontology dataset.

This builder implements a reusable repair ontology layer that attaches to the
existing Concept, Bug, Diagnostic Rules, and Explanation/Feedback graphs.

Outputs:
- neo4j_repair_ontology_nodes.csv
- neo4j_repair_ontology_relationships.csv
- neo4j_repair_ontology_seed.cypher
- neo4j_repair_ontology_summary.json

Design goals:
- Keep repair plans reusable across many bug types.
- Separate "what to fix" from "where to fix it".
- Represent repair as high-level plans, reusable steps, atomic actions,
  constraints, and examples.
- Attach repair plans to existing bug.*, rule.*, fix.*, concept.*, and view.* IDs.
"""



from pathlib import Path
import csv
import json
from typing import Any, Dict, Iterable, List

OUTPUT_DIR = Path(".")

nodes: List[Dict[str, Any]] = []
relationships: List[Dict[str, Any]] = []
node_index: Dict[str, Dict[str, Any]] = {}
external_refs = set()

EXTERNAL_PREFIXES = (
    "bug.",
    "rule.",
    "fix.",
    "concept.",
    "view.",
    "mis.",
)


def add_node(node_id: str, label: str, **props: Any) -> None:
    """Add a node to the in-memory dataset."""
    if node_id in node_index:
        raise ValueError(f"Duplicate node id: {node_id}")
    row = {"id": node_id, "label": label}
    row.update(props)
    node_index[node_id] = row
    nodes.append(row)


def add_relationship(start_id: str, rel_type: str, end_id: str, **props: Any) -> None:
    """Add a relationship, allowing references to nodes from existing graph layers."""
    if start_id not in node_index:
        raise ValueError(f"Unknown start node: {start_id}")
    if end_id not in node_index:
        if end_id.startswith(EXTERNAL_PREFIXES):
            external_refs.add(end_id)
        else:
            raise ValueError(f"Unknown end node: {end_id}")
    row = {"start_id": start_id, "type": rel_type, "end_id": end_id}
    row.update(props)
    relationships.append(row)


def add_category(node_id: str, name: str, description: str, parent_id: str | None = None) -> None:
    add_node(node_id, "RepairCategory", name=name, description=description, status="active")
    if parent_id:
        add_relationship(node_id, "SUBCATEGORY_OF", parent_id)


def add_plan(node_id: str, name: str, strategy_type: str, description: str) -> None:
    add_node(
        node_id,
        "RepairPlan",
        name=name,
        strategyType=strategy_type,
        description=description,
        status="active",
    )


def add_step(node_id: str, name: str, step_type: str, description: str, default_order: int) -> None:
    add_node(
        node_id,
        "RepairStepTemplate",
        name=name,
        stepType=step_type,
        description=description,
        defaultOrder=str(default_order),
        status="active",
    )


def add_action(node_id: str, name: str, action_type: str, description: str, auto_fixable: bool) -> None:
    add_node(
        node_id,
        "RepairAction",
        name=name,
        actionType=action_type,
        description=description,
        autoFixable=str(auto_fixable).lower(),
        status="active",
    )


def add_constraint(node_id: str, name: str, constraint_type: str, description: str) -> None:
    add_node(
        node_id,
        "RepairConstraint",
        name=name,
        constraintType=constraint_type,
        description=description,
        status="active",
    )


def add_example(node_id: str, name: str, before: str, after: str, explanation: str) -> None:
    add_node(
        node_id,
        "RepairExample",
        name=name,
        beforeCode=before,
        afterCode=after,
        explanation=explanation,
        status="active",
    )


def build_dataset() -> None:
    """Build all Repair Ontology nodes and relationships."""

    # Categories
    add_category("repaircat.root", "RepairRoot", "Root category for all repair strategies.")
    add_category("repaircat.boundary_loop", "BoundaryAndLoopRepair", "Boundary, loop progress, and termination repairs.", "repaircat.root")
    add_category("repaircat.pointer_memory", "PointerAndMemoryRepair", "Pointer safety, ownership, and memory lifecycle repairs.", "repaircat.root")
    add_category("repaircat.function_flow", "FunctionAndControlFlowRepair", "Function contract and control-flow completion repairs.", "repaircat.root")
    add_category("repaircat.recursion", "RecursionRepair", "Recursive base case and progress repairs.", "repaircat.root")
    add_category("repaircat.iterator_range", "IteratorAndRangeRepair", "Iterator validity, range lifetime, and STL traversal repairs.", "repaircat.root")
    add_category("repaircat.modern_cpp", "ModernCppRepair", "Move semantics, RAII, polymorphic lifetime, and exception safety repairs.", "repaircat.root")
    add_category("repaircat.concurrency", "ConcurrencyRepair", "Lock discipline, condition protocols, and shared state protection repairs.", "repaircat.root")
    add_category("repaircat.io", "IOFormattingRepair", "Formatting and type-safe I/O repairs.", "repaircat.root")

    # Reusable repair plans
    plans = [
        ("repair.boundary_validation", "BoundaryValidation", "boundary", "Validate loop boundaries, index ranges, and edge-case behavior."),
        ("repair.loop_progress", "LoopProgressRepair", "loop", "Ensure loop state changes toward termination on every iteration."),
        ("repair.loop_termination", "LoopTerminationRepair", "loop", "Repair loop conditions so execution eventually reaches an exit state."),
        ("repair.pointer_safety", "PointerSafetyRepair", "pointer", "Guard pointer use and prove dereference validity before access."),
        ("repair.resource_lifecycle", "ResourceLifecycleRepair", "memory", "Match allocation, ownership transfer, use, and release paths."),
        ("repair.ownership_management", "OwnershipManagementRepair", "memory", "Clarify ownership and prevent double release or dangling references."),
        ("repair.control_flow_completion", "ControlFlowCompletionRepair", "control-flow", "Ensure all required control-flow paths complete their contract."),
        ("repair.function_contract", "FunctionContractRepair", "function", "Align function behavior with its return type and specification."),
        ("repair.recursion_termination", "RecursionTerminationRepair", "recursion", "Define and verify a reachable recursive base case."),
        ("repair.recursion_progress", "RecursionProgressRepair", "recursion", "Ensure recursive calls reduce problem size toward the base case."),
        ("repair.iterator_validity", "IteratorValidityRepair", "iterator", "Avoid use of invalidated iterators, references, and views."),
        ("repair.range_lifetime", "RangeLifetimeRepair", "range", "Ensure non-owning views and ranges do not outlive their sources."),
        ("repair.move_semantic_safety", "MoveSemanticSafetyRepair", "modern-cpp", "Avoid relying on moved-from object values unless reinitialized."),
        ("repair.polymorphic_lifetime", "PolymorphicLifetimeRepair", "oop", "Repair polymorphic cleanup, especially base class destruction."),
        ("repair.exception_safety", "ExceptionSafetyRepair", "modern-cpp", "Move cleanup into exception-safe ownership boundaries."),
        ("repair.lock_discipline", "LockDisciplineRepair", "concurrency", "Protect shared mutable state with consistent locking."),
        ("repair.condition_protocol", "ConditionProtocolRepair", "concurrency", "Use predicate-based condition variable waiting and notification protocol."),
        ("repair.shared_state_protection", "SharedStateProtectionRepair", "concurrency", "Prevent unsynchronized cross-thread shared state access."),
        ("repair.format_type_safety", "FormatTypeSafetyRepair", "io", "Match formatting placeholders with argument types or use type-safe formatting."),
    ]
    for plan in plans:
        add_plan(*plan)

    # Plan categories
    plan_category = {
        "repair.boundary_validation": "repaircat.boundary_loop",
        "repair.loop_progress": "repaircat.boundary_loop",
        "repair.loop_termination": "repaircat.boundary_loop",
        "repair.pointer_safety": "repaircat.pointer_memory",
        "repair.resource_lifecycle": "repaircat.pointer_memory",
        "repair.ownership_management": "repaircat.pointer_memory",
        "repair.control_flow_completion": "repaircat.function_flow",
        "repair.function_contract": "repaircat.function_flow",
        "repair.recursion_termination": "repaircat.recursion",
        "repair.recursion_progress": "repaircat.recursion",
        "repair.iterator_validity": "repaircat.iterator_range",
        "repair.range_lifetime": "repaircat.iterator_range",
        "repair.move_semantic_safety": "repaircat.modern_cpp",
        "repair.polymorphic_lifetime": "repaircat.modern_cpp",
        "repair.exception_safety": "repaircat.modern_cpp",
        "repair.lock_discipline": "repaircat.concurrency",
        "repair.condition_protocol": "repaircat.concurrency",
        "repair.shared_state_protection": "repaircat.concurrency",
        "repair.format_type_safety": "repaircat.io",
    }
    for plan_id, category_id in plan_category.items():
        add_relationship(plan_id, "BELONGS_TO_CATEGORY", category_id)

    # Reusable step templates
    steps = [
        ("step.locate_fault_region", "LocateFaultRegion", "locate", "Locate the smallest code region related to the failing behavior.", 1),
        ("step.inspect_loop_condition", "InspectLoopCondition", "analysis", "Inspect loop condition and decide whether it should be inclusive or exclusive.", 2),
        ("step.verify_index_range", "VerifyIndexRange", "analysis", "Verify that every index stays inside the valid range.", 3),
        ("step.run_boundary_case", "RunBoundaryCase", "validation", "Run the smallest edge cases that expose boundary mistakes.", 4),
        ("step.verify_loop_progress", "VerifyLoopProgress", "analysis", "Verify that loop state changes toward termination.", 2),
        ("step.repair_loop_update", "RepairLoopUpdate", "repair", "Change or add the loop update so progress is guaranteed.", 3),
        ("step.trace_pointer_assignment", "TracePointerAssignment", "analysis", "Trace all assignments and ownership transfers of the pointer or handle.", 2),
        ("step.check_nullability", "CheckNullability", "analysis", "Check whether the pointer may be null or invalid before dereference.", 3),
        ("step.insert_validity_guard", "InsertValidityGuard", "repair", "Add a guard or invariant that prevents invalid dereference.", 4),
        ("step.verify_resource_owner", "VerifyResourceOwner", "analysis", "Identify who owns each resource at each program point.", 2),
        ("step.verify_release_path", "VerifyReleasePath", "analysis", "Verify that each allocated resource is released exactly once.", 3),
        ("step.replace_manual_ownership", "ReplaceManualOwnership", "repair", "Prefer RAII or smart pointers for resource ownership when available.", 4),
        ("step.trace_release_then_use", "TraceReleaseThenUse", "analysis", "Trace whether a resource is accessed after release.", 2),
        ("step.invalidate_after_release", "InvalidateAfterRelease", "repair", "Stop using handles after release or reset them to a safe state.", 3),
        ("step.verify_all_return_paths", "VerifyAllReturnPaths", "analysis", "Check every control-flow path in non-void functions for a return value.", 2),
        ("step.add_missing_return", "AddMissingReturn", "repair", "Add a valid return value or redesign the function contract.", 3),
        ("step.identify_base_case", "IdentifyBaseCase", "analysis", "Identify the recursive base case and when it should apply.", 2),
        ("step.verify_base_case_reachable", "VerifyBaseCaseReachable", "analysis", "Verify that recursive execution can reach the base case.", 3),
        ("step.verify_recursive_progress", "VerifyRecursiveProgress", "analysis", "Verify that each recursive call reduces the problem size.", 3),
        ("step.rewrite_recursive_call", "RewriteRecursiveCall", "repair", "Rewrite recursive arguments so they progress toward the base case.", 4),
        ("step.locate_container_modification", "LocateContainerModification", "locate", "Locate the operation that can invalidate iterators or references.", 2),
        ("step.refresh_iterator", "RefreshIterator", "repair", "Refresh or reacquire iterators after invalidating operations.", 3),
        ("step.check_view_source_lifetime", "CheckViewSourceLifetime", "analysis", "Check whether a view or range outlives its source object.", 2),
        ("step.extend_source_lifetime", "ExtendSourceLifetime", "repair", "Extend source lifetime or use an owning object instead of a dangling view.", 3),
        ("step.locate_move_operation", "LocateMoveOperation", "locate", "Locate the move operation and later use of the moved-from object.", 2),
        ("step.reinitialize_moved_from", "ReinitializeMovedFromObject", "repair", "Reinitialize moved-from objects before relying on their semantic value.", 3),
        ("step.locate_polymorphic_delete", "LocatePolymorphicDelete", "locate", "Locate deletion through a base pointer or owner.", 2),
        ("step.add_virtual_destructor", "AddVirtualDestructor", "repair", "Add a virtual destructor to a polymorphic base class.", 3),
        ("step.identify_exception_path", "IdentifyExceptionPath", "analysis", "Locate paths where exceptions may bypass cleanup or break invariants.", 2),
        ("step.apply_raii_boundary", "ApplyRAIIBoundary", "repair", "Move cleanup into RAII-managed objects or scope-bound ownership.", 3),
        ("step.locate_format_call", "LocateFormatCall", "locate", "Locate the formatting call and its arguments.", 1),
        ("step.match_format_type", "MatchFormatType", "analysis", "Match placeholders against actual argument types.", 2),
        ("step.use_type_safe_format", "UseTypeSafeFormatting", "repair", "Use type-safe formatting APIs where available.", 3),
        ("step.locate_shared_state", "LocateSharedState", "locate", "Locate mutable state shared across threads.", 1),
        ("step.verify_lock_coverage", "VerifyLockCoverage", "analysis", "Check whether all shared-state accesses use the same synchronization discipline.", 2),
        ("step.use_predicate_wait", "UsePredicateWait", "repair", "Use predicate-based wait loops for condition variables.", 3),
        ("step.rerun_targeted_tests", "RerunTargetedTests", "validation", "Rerun the smallest tests that validate the repair.", 99),
    ]
    for step in steps:
        add_step(*step)

    # Atomic repair actions
    actions = [
        ("action.replace_less_equal_with_less", "ReplaceLessEqualWithLess", "edit", "Replace <= with < when iterating over zero-indexed ranges of length n.", True),
        ("action.replace_less_with_less_equal", "ReplaceLessWithLessEqual", "edit", "Replace < with <= when the upper bound is meant to be included.", True),
        ("action.change_loop_start_to_zero", "ChangeLoopStartToZero", "edit", "Change loop start value to zero for zero-indexed traversal.", True),
        ("action.add_loop_update", "AddLoopUpdate", "edit", "Add a missing update statement to a loop.", True),
        ("action.change_update_direction", "ChangeUpdateDirection", "edit", "Change increment to decrement or vice versa when loop progress is reversed.", True),
        ("action.insert_bounds_check", "InsertBoundsCheck", "edit", "Insert a condition that prevents out-of-range access.", False),
        ("action.insert_null_guard", "InsertNullGuard", "edit", "Insert a null check before pointer dereference.", True),
        ("action.initialize_pointer", "InitializePointer", "edit", "Initialize pointer variables to a safe value.", True),
        ("action.add_missing_free", "AddMissingFree", "edit", "Add a missing resource release on the owning path.", False),
        ("action.remove_duplicate_free", "RemoveDuplicateFree", "edit", "Remove or restructure duplicated release operations.", False),
        ("action.set_pointer_null_after_free", "SetPointerNullAfterFree", "edit", "Set pointer to null after release when ownership remains in scope.", True),
        ("action.convert_raw_pointer_to_unique_ptr", "ConvertRawPointerToUniquePtr", "refactor", "Replace raw owning pointer with std::unique_ptr.", False),
        ("action.add_return_statement", "AddReturnStatement", "edit", "Add a valid return statement on paths that currently miss one.", True),
        ("action.add_base_case", "AddBaseCase", "edit", "Add a recursive base case.", False),
        ("action.reduce_recursive_argument", "ReduceRecursiveArgument", "edit", "Modify recursive arguments to reduce problem size.", False),
        ("action.reacquire_iterator", "ReacquireIterator", "edit", "Reacquire iterators after operations that may invalidate them.", False),
        ("action.avoid_view_to_temporary", "AvoidViewToTemporary", "edit", "Avoid creating non-owning views to temporary or short-lived objects.", False),
        ("action.reinitialize_after_move", "ReinitializeAfterMove", "edit", "Assign a new valid value to a moved-from object before semantic use.", True),
        ("action.add_virtual_destructor", "AddVirtualDestructor", "edit", "Add virtual destructor to a polymorphic base class.", True),
        ("action.wrap_resource_in_raii", "WrapResourceInRAII", "refactor", "Move manual resource cleanup into RAII objects.", False),
        ("action.fix_printf_specifier", "FixPrintfSpecifier", "edit", "Replace incorrect printf-style specifier with the correct one.", True),
        ("action.use_std_format_or_print", "UseStdFormatOrPrint", "refactor", "Use std::format or std::print for type-safe formatting when available.", False),
        ("action.wrap_access_with_mutex", "WrapAccessWithMutex", "edit", "Protect shared-state access with a mutex.", False),
        ("action.rewrite_condition_wait", "RewriteConditionWait", "edit", "Rewrite condition variable waiting as a predicate-based loop.", False),
    ]
    for action in actions:
        add_action(*action)

    # Constraints
    constraints = [
        ("constraint.preserve_semantics", "PreserveProblemSemantics", "semantic", "Repair must preserve the problem statement semantics."),
        ("constraint.minimal_patch", "PreferMinimalPatch", "style", "Prefer the smallest repair that fixes the diagnosed issue."),
        ("constraint.no_unrelated_refactor", "AvoidUnrelatedRefactor", "style", "Avoid changing unrelated code while repairing the bug."),
        ("constraint.keep_public_api", "KeepPublicAPIStable", "interface", "Do not change function signatures unless the function contract is the issue."),
        ("constraint.valid_index_range", "MaintainValidIndexRange", "safety", "All index expressions must stay within valid range."),
        ("constraint.single_release", "ReleaseEachResourceExactlyOnce", "ownership", "Each owned resource must be released exactly once."),
        ("constraint.no_use_after_release", "NoUseAfterRelease", "ownership", "Do not read or write through a released resource handle."),
        ("constraint.return_all_paths", "ReturnOnAllRequiredPaths", "control-flow", "Every non-void function path must return a value."),
        ("constraint.recursive_progress", "RecursiveCallsMustProgress", "algorithm", "Recursive calls must move toward the base case."),
        ("constraint.iterator_validity", "IteratorMustRemainValid", "stl", "Do not use invalidated iterators, references, or views."),
        ("constraint.moved_from_safe_use", "MovedFromObjectSafeUseOnly", "modern-cpp", "Use moved-from objects only in documented safe ways or reinitialize them."),
        ("constraint.virtual_base_cleanup", "PolymorphicBaseRequiresVirtualDestructor", "oop", "Polymorphic base deletion requires a virtual destructor."),
        ("constraint.exception_safe_cleanup", "CleanupMustBeExceptionSafe", "exception", "Cleanup must happen correctly on normal and exceptional paths."),
        ("constraint.format_type_match", "FormatSpecifierMustMatchType", "io", "Format specifiers must match argument types."),
        ("constraint.synchronized_shared_state", "SharedStateMustBeSynchronized", "concurrency", "Shared mutable state must be protected consistently."),
        ("constraint.wait_predicate", "ConditionWaitNeedsPredicate", "concurrency", "Condition variable waiting must re-check the predicate under lock."),
    ]
    for constraint in constraints:
        add_constraint(*constraint)

    # Examples
    examples = [
        (
            "example.off_by_one.less_equal",
            "OffByOneLessEqualExample",
            "for (int i = 0; i <= n; ++i) { sum += a[i]; }",
            "for (int i = 0; i < n; ++i) { sum += a[i]; }",
            "When a has n elements, the last valid index is n - 1, so the loop must stop before i reaches n.",
        ),
        (
            "example.null_guard",
            "NullGuardExample",
            "int value = *p;",
            "if (p != nullptr) { int value = *p; }",
            "Dereference is only safe when the pointer is known to refer to a valid object.",
        ),
        (
            "example.missing_return",
            "MissingReturnExample",
            "int f(bool ok) { if (ok) return 1; }",
            "int f(bool ok) { if (ok) return 1; return 0; }",
            "Every path in a non-void function must return a value.",
        ),
        (
            "example.recursive_progress",
            "RecursiveProgressExample",
            "int f(int n) { if (n == 0) return 0; return f(n); }",
            "int f(int n) { if (n == 0) return 0; return f(n - 1); }",
            "The recursive call must reduce the input toward the base case.",
        ),
        (
            "example.virtual_destructor",
            "VirtualDestructorExample",
            "struct Base { virtual void f(); };",
            "struct Base { virtual ~Base() = default; virtual void f(); };",
            "A polymorphic base class should have a virtual destructor if objects may be deleted through base pointers.",
        ),
        (
            "example.condition_wait",
            "ConditionVariablePredicateWaitExample",
            "cv.wait(lock);",
            "cv.wait(lock, [&] { return ready; });",
            "Condition variable waiting should re-check a predicate under the lock.",
        ),
    ]
    for example in examples:
        add_example(*example)

    # Plan -> steps
    plan_steps = {
        "repair.boundary_validation": [
            "step.locate_fault_region",
            "step.inspect_loop_condition",
            "step.verify_index_range",
            "step.run_boundary_case",
            "step.rerun_targeted_tests",
        ],
        "repair.loop_progress": [
            "step.locate_fault_region",
            "step.verify_loop_progress",
            "step.repair_loop_update",
            "step.rerun_targeted_tests",
        ],
        "repair.loop_termination": [
            "step.locate_fault_region",
            "step.inspect_loop_condition",
            "step.verify_loop_progress",
            "step.rerun_targeted_tests",
        ],
        "repair.pointer_safety": [
            "step.locate_fault_region",
            "step.trace_pointer_assignment",
            "step.check_nullability",
            "step.insert_validity_guard",
            "step.rerun_targeted_tests",
        ],
        "repair.resource_lifecycle": [
            "step.locate_fault_region",
            "step.verify_resource_owner",
            "step.verify_release_path",
            "step.replace_manual_ownership",
            "step.rerun_targeted_tests",
        ],
        "repair.ownership_management": [
            "step.locate_fault_region",
            "step.verify_resource_owner",
            "step.trace_release_then_use",
            "step.invalidate_after_release",
            "step.rerun_targeted_tests",
        ],
        "repair.control_flow_completion": [
            "step.locate_fault_region",
            "step.verify_all_return_paths",
            "step.add_missing_return",
            "step.rerun_targeted_tests",
        ],
        "repair.function_contract": [
            "step.locate_fault_region",
            "step.verify_all_return_paths",
            "step.add_missing_return",
            "step.rerun_targeted_tests",
        ],
        "repair.recursion_termination": [
            "step.locate_fault_region",
            "step.identify_base_case",
            "step.verify_base_case_reachable",
            "step.rerun_targeted_tests",
        ],
        "repair.recursion_progress": [
            "step.locate_fault_region",
            "step.verify_recursive_progress",
            "step.rewrite_recursive_call",
            "step.rerun_targeted_tests",
        ],
        "repair.iterator_validity": [
            "step.locate_fault_region",
            "step.locate_container_modification",
            "step.refresh_iterator",
            "step.rerun_targeted_tests",
        ],
        "repair.range_lifetime": [
            "step.locate_fault_region",
            "step.check_view_source_lifetime",
            "step.extend_source_lifetime",
            "step.rerun_targeted_tests",
        ],
        "repair.move_semantic_safety": [
            "step.locate_fault_region",
            "step.locate_move_operation",
            "step.reinitialize_moved_from",
            "step.rerun_targeted_tests",
        ],
        "repair.polymorphic_lifetime": [
            "step.locate_fault_region",
            "step.locate_polymorphic_delete",
            "step.add_virtual_destructor",
            "step.rerun_targeted_tests",
        ],
        "repair.exception_safety": [
            "step.locate_fault_region",
            "step.identify_exception_path",
            "step.apply_raii_boundary",
            "step.rerun_targeted_tests",
        ],
        "repair.lock_discipline": [
            "step.locate_shared_state",
            "step.verify_lock_coverage",
            "step.rerun_targeted_tests",
        ],
        "repair.condition_protocol": [
            "step.locate_shared_state",
            "step.use_predicate_wait",
            "step.rerun_targeted_tests",
        ],
        "repair.shared_state_protection": [
            "step.locate_shared_state",
            "step.verify_lock_coverage",
            "step.rerun_targeted_tests",
        ],
        "repair.format_type_safety": [
            "step.locate_format_call",
            "step.match_format_type",
            "step.use_type_safe_format",
            "step.rerun_targeted_tests",
        ],
    }
    for plan_id, step_ids in plan_steps.items():
        for order, step_id in enumerate(step_ids, start=1):
            add_relationship(plan_id, "CONSISTS_OF_STEP", step_id, order=str(order))

    # Plan -> actions
    plan_actions = {
        "repair.boundary_validation": ["action.replace_less_equal_with_less", "action.replace_less_with_less_equal", "action.change_loop_start_to_zero", "action.insert_bounds_check"],
        "repair.loop_progress": ["action.add_loop_update", "action.change_update_direction"],
        "repair.loop_termination": ["action.replace_less_equal_with_less", "action.add_loop_update", "action.change_update_direction"],
        "repair.pointer_safety": ["action.insert_null_guard", "action.initialize_pointer"],
        "repair.resource_lifecycle": ["action.add_missing_free", "action.convert_raw_pointer_to_unique_ptr", "action.wrap_resource_in_raii"],
        "repair.ownership_management": ["action.remove_duplicate_free", "action.set_pointer_null_after_free", "action.convert_raw_pointer_to_unique_ptr"],
        "repair.control_flow_completion": ["action.add_return_statement"],
        "repair.function_contract": ["action.add_return_statement"],
        "repair.recursion_termination": ["action.add_base_case"],
        "repair.recursion_progress": ["action.reduce_recursive_argument"],
        "repair.iterator_validity": ["action.reacquire_iterator"],
        "repair.range_lifetime": ["action.avoid_view_to_temporary"],
        "repair.move_semantic_safety": ["action.reinitialize_after_move"],
        "repair.polymorphic_lifetime": ["action.add_virtual_destructor"],
        "repair.exception_safety": ["action.wrap_resource_in_raii"],
        "repair.lock_discipline": ["action.wrap_access_with_mutex"],
        "repair.condition_protocol": ["action.rewrite_condition_wait"],
        "repair.shared_state_protection": ["action.wrap_access_with_mutex"],
        "repair.format_type_safety": ["action.fix_printf_specifier", "action.use_std_format_or_print"],
    }
    for plan_id, action_ids in plan_actions.items():
        for action_id in action_ids:
            add_relationship(plan_id, "USES_ACTION", action_id)

    # Plan -> constraints
    plan_constraints = {
        "repair.boundary_validation": ["constraint.preserve_semantics", "constraint.minimal_patch", "constraint.valid_index_range"],
        "repair.loop_progress": ["constraint.preserve_semantics", "constraint.minimal_patch"],
        "repair.loop_termination": ["constraint.preserve_semantics", "constraint.minimal_patch"],
        "repair.pointer_safety": ["constraint.no_use_after_release", "constraint.minimal_patch"],
        "repair.resource_lifecycle": ["constraint.single_release", "constraint.no_use_after_release"],
        "repair.ownership_management": ["constraint.single_release", "constraint.no_use_after_release"],
        "repair.control_flow_completion": ["constraint.return_all_paths", "constraint.keep_public_api"],
        "repair.function_contract": ["constraint.return_all_paths", "constraint.keep_public_api"],
        "repair.recursion_termination": ["constraint.recursive_progress", "constraint.preserve_semantics"],
        "repair.recursion_progress": ["constraint.recursive_progress", "constraint.preserve_semantics"],
        "repair.iterator_validity": ["constraint.iterator_validity", "constraint.preserve_semantics"],
        "repair.range_lifetime": ["constraint.iterator_validity", "constraint.preserve_semantics"],
        "repair.move_semantic_safety": ["constraint.moved_from_safe_use", "constraint.no_unrelated_refactor"],
        "repair.polymorphic_lifetime": ["constraint.virtual_base_cleanup", "constraint.keep_public_api"],
        "repair.exception_safety": ["constraint.exception_safe_cleanup", "constraint.no_unrelated_refactor"],
        "repair.lock_discipline": ["constraint.synchronized_shared_state", "constraint.no_unrelated_refactor"],
        "repair.condition_protocol": ["constraint.wait_predicate", "constraint.synchronized_shared_state"],
        "repair.shared_state_protection": ["constraint.synchronized_shared_state"],
        "repair.format_type_safety": ["constraint.format_type_match", "constraint.minimal_patch"],
    }
    for plan_id, constraint_ids in plan_constraints.items():
        for constraint_id in constraint_ids:
            add_relationship(plan_id, "MUST_SATISFY", constraint_id)

    # Examples to plans
    example_plan_map = {
        "example.off_by_one.less_equal": ["repair.boundary_validation"],
        "example.null_guard": ["repair.pointer_safety"],
        "example.missing_return": ["repair.control_flow_completion", "repair.function_contract"],
        "example.recursive_progress": ["repair.recursion_progress"],
        "example.virtual_destructor": ["repair.polymorphic_lifetime"],
        "example.condition_wait": ["repair.condition_protocol"],
    }
    for example_id, plan_ids in example_plan_map.items():
        for plan_id in plan_ids:
            add_relationship(plan_id, "HAS_EXAMPLE", example_id)

    # Bug -> repair plan mapping
    bug_plan_map = {
        "bug.off_by_one": ["repair.boundary_validation"],
        "bug.array_out_of_bounds": ["repair.boundary_validation"],
        "bug.vector_out_of_range": ["repair.boundary_validation", "repair.iterator_validity"],
        "bug.index_value_confusion": ["repair.boundary_validation"],
        "bug.infinite_loop": ["repair.loop_progress", "repair.loop_termination"],
        "bug.missing_loop_update": ["repair.loop_progress"],
        "bug.wrong_loop_init": ["repair.boundary_validation"],
        "bug.wrong_loop_condition": ["repair.loop_termination", "repair.boundary_validation"],
        "bug.null_dereference": ["repair.pointer_safety"],
        "bug.memory_leak": ["repair.resource_lifecycle", "repair.ownership_management"],
        "bug.use_after_free": ["repair.pointer_safety", "repair.resource_lifecycle", "repair.ownership_management"],
        "bug.double_free": ["repair.resource_lifecycle", "repair.ownership_management"],
        "bug.dangling_pointer": ["repair.pointer_safety", "repair.ownership_management"],
        "bug.uninitialized_value": ["repair.control_flow_completion"],
        "bug.missing_return": ["repair.control_flow_completion", "repair.function_contract"],
        "bug.wrong_base_case": ["repair.recursion_termination"],
        "bug.no_recursive_progress": ["repair.recursion_progress"],
        "bug.iterator_invalidation": ["repair.iterator_validity"],
        "bug.use_after_move": ["repair.move_semantic_safety"],
        "bug.missing_virtual_destructor": ["repair.polymorphic_lifetime"],
        "bug.rule_of_five": ["repair.resource_lifecycle", "repair.ownership_management", "repair.exception_safety"],
        "bug.exception_safety": ["repair.exception_safety"],
        "bug.format_specifier_mismatch": ["repair.format_type_safety"],
        "bug.condition_variable_misuse": ["repair.condition_protocol", "repair.lock_discipline", "repair.shared_state_protection"],
    }
    for bug_id, plan_ids in bug_plan_map.items():
        for plan_id in plan_ids:
            add_relationship(plan_id, "REPAIRS_BUG", bug_id)

    # Rule -> repair plan mapping
    rule_plan_map = {
        "rule.loop.off_by_one.leq_length": ["repair.boundary_validation"],
        "rule.loop.off_by_one.start_one": ["repair.boundary_validation"],
        "rule.loop.infinite.missing_update": ["repair.loop_progress"],
        "rule.loop.infinite.wrong_direction": ["repair.loop_progress", "repair.loop_termination"],
        "rule.loop.boundary.edge_case": ["repair.boundary_validation"],
        "rule.array.out_of_bounds.size_index": ["repair.boundary_validation"],
        "rule.array.index_value_confusion": ["repair.boundary_validation"],
        "rule.pointer.null_deref.ast": ["repair.pointer_safety"],
        "rule.pointer.null_deref.clang": ["repair.pointer_safety"],
        "rule.memory.leak.alloc_no_release": ["repair.resource_lifecycle"],
        "rule.memory.use_after_free.flow": ["repair.pointer_safety", "repair.resource_lifecycle"],
        "rule.memory.double_free.flow": ["repair.ownership_management"],
        "rule.memory.uaf.sanitizer": ["repair.pointer_safety"],
        "rule.memory.leak.sanitizer": ["repair.resource_lifecycle"],
        "rule.function.missing_return.compiler": ["repair.control_flow_completion"],
        "rule.function.missing_return.cfg": ["repair.control_flow_completion"],
        "rule.recursion.no_base_case": ["repair.recursion_termination"],
        "rule.recursion.unreachable_base": ["repair.recursion_termination"],
        "rule.recursion.no_progress": ["repair.recursion_progress"],
        "rule.iterator.invalidation.modify_then_use": ["repair.iterator_validity"],
        "rule.iterator.view_lifetime": ["repair.range_lifetime"],
        "rule.move.use_after_move": ["repair.move_semantic_safety"],
        "rule.oop.delete_base_no_virtual": ["repair.polymorphic_lifetime"],
        "rule.oop.rule_of_five": ["repair.ownership_management", "repair.exception_safety"],
        "rule.oop.exception_safety": ["repair.exception_safety"],
        "rule.format.specifier_mismatch": ["repair.format_type_safety"],
        "rule.format.modern_cpp_upgrade": ["repair.format_type_safety"],
        "rule.concurrent.wait_protocol": ["repair.condition_protocol"],
        "rule.concurrent.missing_sync": ["repair.lock_discipline", "repair.shared_state_protection"],
        "rule.meta.edge_case_boundary": ["repair.boundary_validation"],
    }
    for rule_id, plan_ids in rule_plan_map.items():
        for plan_id in plan_ids:
            add_relationship(plan_id, "RECOMMENDED_BY_RULE", rule_id)

    # FixStrategy -> plan mapping
    fix_plan_map = {
        "fix.loop.bound": ["repair.boundary_validation"],
        "fix.loop.progress": ["repair.loop_progress"],
        "fix.loop.init": ["repair.boundary_validation"],
        "fix.array.bound": ["repair.boundary_validation"],
        "fix.array.index_value": ["repair.boundary_validation"],
        "fix.null.check": ["repair.pointer_safety"],
        "fix.release.once": ["repair.resource_lifecycle", "repair.ownership_management"],
        "fix.no_use_after_release": ["repair.pointer_safety", "repair.ownership_management"],
        "fix.use_raii": ["repair.resource_lifecycle", "repair.exception_safety"],
        "fix.smart_pointer": ["repair.ownership_management", "repair.resource_lifecycle"],
        "fix.return": ["repair.control_flow_completion", "repair.function_contract"],
        "fix.recursion.base": ["repair.recursion_termination"],
        "fix.recursion.progress": ["repair.recursion_progress"],
        "fix.iterator.refresh": ["repair.iterator_validity"],
        "fix.move.use_state": ["repair.move_semantic_safety"],
        "fix.virtual_destructor": ["repair.polymorphic_lifetime"],
        "fix.format.match": ["repair.format_type_safety"],
        "fix.condition_wait": ["repair.condition_protocol"],
    }
    for fix_id, plan_ids in fix_plan_map.items():
        for plan_id in plan_ids:
            add_relationship(plan_id, "IMPLEMENTS_FIX_STRATEGY", fix_id)

    # Plan -> concepts
    plan_concepts = {
        "repair.boundary_validation": ["concept.c.array", "concept.c.for", "concept.cpp.vector", "concept.cpp.range_for"],
        "repair.loop_progress": ["concept.c.for", "concept.c.while", "concept.cpp.for", "concept.cpp.while"],
        "repair.loop_termination": ["concept.c.for", "concept.c.while", "concept.cpp.for", "concept.cpp.while"],
        "repair.pointer_safety": ["concept.c.pointer", "concept.cpp.pointer", "concept.cpp.smart_pointer"],
        "repair.resource_lifecycle": ["concept.c.malloc", "concept.c.free", "concept.cpp.new_delete", "concept.cpp.raii"],
        "repair.ownership_management": ["concept.c.pointer", "concept.cpp.smart_pointer", "concept.cpp.raii"],
        "repair.control_flow_completion": ["concept.c.function_def", "concept.cpp.function_decl", "concept.cpp.return"],
        "repair.function_contract": ["concept.c.function_def", "concept.cpp.function_decl", "concept.cpp.return"],
        "repair.recursion_termination": ["concept.c.function_def", "concept.cpp.function_decl"],
        "repair.recursion_progress": ["concept.c.function_def", "concept.cpp.function_decl"],
        "repair.iterator_validity": ["concept.cpp.iterator", "concept.cpp.vector", "concept.cpp.map", "concept.cpp.unordered_map"],
        "repair.range_lifetime": ["concept.cpp.ranges", "concept.cpp.views", "concept.cpp.string_view", "concept.cpp.span"],
        "repair.move_semantic_safety": ["concept.cpp.move_semantics", "concept.cpp.unique_ptr", "concept.cpp.string", "concept.cpp.vector"],
        "repair.polymorphic_lifetime": ["concept.cpp.class", "concept.cpp.inheritance", "concept.cpp.virtual_function", "concept.cpp.destructor"],
        "repair.exception_safety": ["concept.cpp.try_catch", "concept.cpp.noexcept", "concept.cpp.raii"],
        "repair.lock_discipline": ["concept.cpp.thread", "concept.cpp.mutex", "concept.cpp.atomic"],
        "repair.condition_protocol": ["concept.cpp.thread", "concept.cpp.mutex", "concept.cpp.condition_variable"],
        "repair.shared_state_protection": ["concept.cpp.thread", "concept.cpp.mutex", "concept.cpp.atomic"],
        "repair.format_type_safety": ["concept.c.formatted_io", "concept.cpp.format", "concept.cpp.print_functions"],
    }
    for plan_id, concept_ids in plan_concepts.items():
        for concept_id in concept_ids:
            add_relationship(plan_id, "APPLIES_TO_CONCEPT", concept_id)

    # Plan -> view
    plan_views = {
        "repair.boundary_validation": ["view.intro_c", "view.algorithms", "view.cpp_stl"],
        "repair.loop_progress": ["view.intro_c", "view.algorithms"],
        "repair.loop_termination": ["view.intro_c", "view.algorithms"],
        "repair.pointer_safety": ["view.c_pointers", "view.cpp_modern"],
        "repair.resource_lifecycle": ["view.c_pointers", "view.cpp_modern"],
        "repair.ownership_management": ["view.c_pointers", "view.cpp_modern"],
        "repair.control_flow_completion": ["view.intro_c"],
        "repair.function_contract": ["view.intro_c"],
        "repair.recursion_termination": ["view.algorithms"],
        "repair.recursion_progress": ["view.algorithms"],
        "repair.iterator_validity": ["view.cpp_stl", "view.cpp_modern"],
        "repair.range_lifetime": ["view.cpp_stl", "view.cpp_modern"],
        "repair.move_semantic_safety": ["view.cpp_modern", "view.cpp_stl"],
        "repair.polymorphic_lifetime": ["view.cpp_oop"],
        "repair.exception_safety": ["view.cpp_oop", "view.cpp_modern"],
        "repair.lock_discipline": ["view.cpp_modern"],
        "repair.condition_protocol": ["view.cpp_modern"],
        "repair.shared_state_protection": ["view.cpp_modern"],
        "repair.format_type_safety": ["view.intro_c", "view.cpp_modern"],
    }
    for plan_id, view_ids in plan_views.items():
        for view_id in view_ids:
            add_relationship(plan_id, "VISIBLE_IN", view_id)


def quote_cypher(value: Any) -> str:
    """Convert a Python value to a Cypher literal."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value)
    if text.lower() in {"true", "false"}:
        return text.lower()
    escaped = text.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def write_csv(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    rows = list(rows)
    fields = sorted({key for row in rows for key in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_cypher() -> str:
    constraints = [
        "CREATE CONSTRAINT repair_category_id_unique IF NOT EXISTS FOR (n:RepairCategory) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT repair_plan_id_unique IF NOT EXISTS FOR (n:RepairPlan) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT repair_step_template_id_unique IF NOT EXISTS FOR (n:RepairStepTemplate) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT repair_action_id_unique IF NOT EXISTS FOR (n:RepairAction) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT repair_constraint_id_unique IF NOT EXISTS FOR (n:RepairConstraint) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT repair_example_id_unique IF NOT EXISTS FOR (n:RepairExample) REQUIRE n.id IS UNIQUE;",
    ]
    lines = list(constraints)
    lines.append("")
    lines.append("// Repair Ontology nodes")
    for row in nodes:
        props = ", ".join(f"{key}: {quote_cypher(value)}" for key, value in row.items() if key != "label")
        lines.append(f"MERGE (n:{row['label']} {{id: {quote_cypher(row['id'])}}}) SET n += {{{props}}};")
    lines.append("")
    lines.append("// Repair Ontology relationships")
    for row in relationships:
        rel_props = {k: v for k, v in row.items() if k not in {"start_id", "type", "end_id"}}
        prop_text = ""
        if rel_props:
            prop_text = " {" + ", ".join(f"{key}: {quote_cypher(value)}" for key, value in rel_props.items()) + "}"
        lines.append(
            f"MATCH (a {{id: {quote_cypher(row['start_id'])}}}), (b {{id: {quote_cypher(row['end_id'])}}}) "
            f"MERGE (a)-[r:{row['type']}{prop_text}]->(b);"
        )
    return "\n".join(lines)


def write_outputs() -> Dict[str, Any]:
    write_csv(OUTPUT_DIR / "neo4j_repair_ontology_nodes.csv", nodes)
    write_csv(OUTPUT_DIR / "neo4j_repair_ontology_relationships.csv", relationships)
    (OUTPUT_DIR / "neo4j_repair_ontology_seed.cypher").write_text(build_cypher(), encoding="utf-8")

    summary = {
        "node_count": len(nodes),
        "relationship_count": len(relationships),
        "label_breakdown": {},
        "relationship_breakdown": {},
        "external_refs": sorted(external_refs),
        "files": [
            "neo4j_repair_ontology_nodes.csv",
            "neo4j_repair_ontology_relationships.csv",
            "neo4j_repair_ontology_seed.cypher",
            "build_neo4j_repair_ontology_dataset.py",
        ],
    }
    for row in nodes:
        summary["label_breakdown"][row["label"]] = summary["label_breakdown"].get(row["label"], 0) + 1
    for row in relationships:
        summary["relationship_breakdown"][row["type"]] = summary["relationship_breakdown"].get(row["type"], 0) + 1
    (OUTPUT_DIR / "neo4j_repair_ontology_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return summary


def main() -> None:
    build_dataset()
    summary = write_outputs()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
