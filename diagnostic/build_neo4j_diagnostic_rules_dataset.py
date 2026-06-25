"""Recreate the Neo4j Diagnostic Rules dataset attached to the latest concept and bug graphs.

Outputs:
- neo4j_diagnostic_rules_nodes.csv
- neo4j_diagnostic_rules_relationships.csv
- neo4j_diagnostic_rules_seed.cypher
- neo4j_diagnostic_rules_summary.json
"""

from pathlib import Path

NODES_CSV = r"""confidenceBase,description,id,isAutoApplicable,label,level,mode,name,patternType,requiresExecution,status
,Root category for all diagnostic rules,rulecat.root,,RuleCategory,top,,DiagnosticRuleRoot,,,active
,"Rules for loops, boundaries, and progress",rulecat.loop,,RuleCategory,top,,LoopDiagnosis,,,active
,"Rules for arrays, indexing, and traversal",rulecat.array,,RuleCategory,top,,ArrayAndIndexDiagnosis,,,active
,"Rules for pointer validity, ownership, and memory lifetime",rulecat.pointer,,RuleCategory,top,,PointerAndMemoryDiagnosis,,,active
,Rules for return behavior and function-level obligations,rulecat.function,,RuleCategory,top,,FunctionContractDiagnosis,,,active
,Rules for base case and recursive progress,rulecat.recursion,,RuleCategory,top,,RecursionDiagnosis,,,active
,"Rules for iterators, ranges, and container invalidation",rulecat.iterator,,RuleCategory,top,,IteratorAndRangeDiagnosis,,,active
,"Rules for virtual dispatch, polymorphic destruction, and RAII",rulecat.oop,,RuleCategory,top,,OOPLifetimeDiagnosis,,,active
,Rules for formatted input/output and printing APIs,rulecat.io,,RuleCategory,top,,IOFormattingDiagnosis,,,active
,"Rules for threads, mutexes, atomics, and condition variables",rulecat.concurrency,,RuleCategory,top,,ConcurrencyDiagnosis,,,active
,Cross-cutting rules that combine multiple evidence types,rulecat.meta,,RuleCategory,top,,MetaAndCrossChecks,,,active
,Pattern extracted from abstract syntax tree shape or syntax form.,tool.ast,,ToolSignature,,static,ASTInspection,,,active
,Pattern extracted from control-flow graph shape.,tool.cfg,,ToolSignature,,static,CFGInspection,,,active
,"Pattern extracted from value, alias, or lifetime flow.",tool.dataflow,,ToolSignature,,static,DataFlowInspection,,,active
,Derived from Clang Static Analyzer findings or equivalent path-sensitive analyzers.,tool.clangsa,,ToolSignature,,static,ClangStaticAnalyzer,,,active
,Derived from compiler diagnostics and warnings.,tool.compiler,,ToolSignature,,static,CompilerWarning,,,active
,Derived from failed edge-case or specification tests.,tool.unittest,,ToolSignature,,dynamic,UnitTestFailure,,,active
,"Derived from observed crash, timeout, hang, or anomalous runtime behavior.",tool.runtime,,ToolSignature,,dynamic,RuntimeObservation,,,active
,"Derived from tools such as AddressSanitizer, UBSan, or thread sanitizers.",tool.sanitizer,,ToolSignature,,dynamic,Sanitizer,,,active
,Derived from linting or best-practice checks for modern C++.,tool.style,,ToolSignature,,static,ModernCppLinter,,,active
,Loop condition uses <= length or <= size while indexing from zero.,ev.loop.boundary.le_length,,EvidencePattern,,,LoopBoundaryUsesLessEqualLength,ast-pattern,,active
,Traversal over zero-indexed storage starts at 1 and misses or shifts valid positions.,ev.loop.boundary.starts_one,,EvidencePattern,,,LoopStartsAtOneForZeroIndexedTraversal,ast-pattern,,active
,Loop variable or termination state is never updated toward exit.,ev.loop.progress.no_update,,EvidencePattern,,,LoopVariableNotUpdated,ast-pattern,,active
,Loop variable update moves away from satisfying exit condition.,ev.loop.progress.wrong_direction,,EvidencePattern,,,LoopVariableMovesAwayFromExit,ast-pattern,,active
,Tests fail only on the final boundary element or exact-size edge case.,ev.loop.test.last_case_only,,EvidencePattern,,,FailsOnlyOnLastElementCase,test-pattern,,active
,Observed timeout or hang in a loop-heavy region.,ev.loop.timeout,,EvidencePattern,,,RuntimeTimeoutInLoopRegion,runtime-pattern,,active
,Array or vector is directly indexed by its length/size result.,ev.array.index.size_access,,EvidencePattern,,,ArrayIndexedBySizeValue,ast-pattern,,active
,Logic mixes roles of array element values and positions.,ev.array.index.value_misuse,,EvidencePattern,,,ArrayValueUsedAsIndexOrViceVersa,ast-pattern,,active
,Boundary test triggers crash or invalid access symptom.,ev.array.bounds.crash,,EvidencePattern,,,OutOfBoundsCrashOnBoundaryTest,runtime-pattern,,active
,Pointer is dereferenced on a path lacking a guard or ownership guarantee.,ev.pointer.null_check_missing,,EvidencePattern,,,PointerDereferencedWithoutGuard,ast-pattern,,active
,Static analyzer reports null dereference possibility.,ev.pointer.clang_null,,EvidencePattern,,,ClangNullDereferenceFinding,static-finding,,active
,Ownership path contains allocation but no matching release or RAII handoff.,ev.memory.alloc_without_release,,EvidencePattern,,,AllocationWithoutMatchingRelease,dataflow-pattern,,active
,Data-flow shows pointer/resource used after free/delete.,ev.memory.release_then_use,,EvidencePattern,,,ReleaseThenUseAccess,dataflow-pattern,,active
,Lifetime path contains duplicated release of the same resource.,ev.memory.double_release,,EvidencePattern,,,ResourceReleasedTwice,dataflow-pattern,,active
,Sanitizer reports heap-use-after-free or invalid lifetime access.,ev.memory.sanitizer_uaf,,EvidencePattern,,,SanitizerUseAfterFreeFinding,dynamic-finding,,active
,Leak sanitizer or instrumentation shows unreleased allocations.,ev.memory.sanitizer_leak,,EvidencePattern,,,SanitizerLeakFinding,dynamic-finding,,active
,Compiler warns that control reaches end of non-void function.,ev.function.warn_nonvoid,,EvidencePattern,,,CompilerWarnsControlReachesEndNonVoid,static-finding,,active
,At least one control-flow path exits without a return in non-void function.,ev.function.path_no_return,,EvidencePattern,,,NonVoidPathMissingReturn,cfg-pattern,,active
,Recursive function lacks a valid base case branch.,ev.recursion.no_base_case,,EvidencePattern,,,RecursiveFunctionWithoutBaseCase,ast-pattern,,active
,A base case exists syntactically but cannot be reached for relevant inputs.,ev.recursion.base_unreachable,,EvidencePattern,,,RecursiveBaseCaseUnreachable,cfg-pattern,,active
,Recursive call fails to reduce problem size toward a base case.,ev.recursion.no_progress,,EvidencePattern,,,RecursiveCallDoesNotReduceProblem,ast-pattern,,active
,Iterator/reference survives a modification that invalidates it.,ev.iterator.modified_container,,EvidencePattern,,,IteratorUsedAfterContainerModification,dataflow-pattern,,active
,Iterator is used after erase/pop/reallocation-like operations.,ev.iterator.erase_then_use,,EvidencePattern,,,IteratorUsedAfterErase,dataflow-pattern,,active
,Non-owning range/view outlives or outscopes its underlying source.,ev.iterator.view_lifetime,,EvidencePattern,,,ViewOrRangeOutlivesSource,dataflow-pattern,,active
,Object is read as though unchanged after move operation.,ev.move.use_after_move,,EvidencePattern,,,MovedFromObjectUsedAsIfUnchanged,dataflow-pattern,,active
,Delete is applied through base pointer lacking virtual destructor.,ev.oop.delete_base_no_virtual,,EvidencePattern,,,DeleteThroughBaseWithoutVirtualDestructor,ast-pattern,,active
,Resource-owning class defines only some copy/move/destructor members.,ev.oop.rule_of_five_partial,,EvidencePattern,,,CustomOwnerDefinesPartialSpecialMembers,ast-pattern,,active
,Exceptional path can bypass manual cleanup or leave partial state.,ev.oop.exception_cleanup,,EvidencePattern,,,ManualCleanupOnExceptionalPath,cfg-pattern,,active
,Format specifier and actual argument type do not match.,ev.format.printf_type_mismatch,,EvidencePattern,,,PrintfSpecifierTypeMismatch,ast-pattern,,active
,Unsafe legacy formatting is used where safer type-aware formatting is expected.,ev.format.mixed_print_api,,EvidencePattern,,,UnsafeCFormattingPreferredOverTypeSafeFormatting,style-pattern,,active
,Condition variable wait is not wrapped in a predicate-checking loop.,ev.concurrent.wait_without_predicate,,EvidencePattern,,,ConditionWaitWithoutPredicateLoop,ast-pattern,,active
,Shared state and notify/wait protocol are not synchronized consistently.,ev.concurrent.notify_without_lock_protocol,,EvidencePattern,,,NotifyAndStateProtocolBroken,dataflow-pattern,,active
,Shared mutable state accessed across threads without evident synchronization.,ev.concurrent.thread_shared_state_no_sync,,EvidencePattern,,,SharedStateAccessWithoutSynchronization,dataflow-pattern,,active
,"Most tests pass but edge cases fail, suggesting boundary or contract issue.",ev.cross.edge_only_failure,,EvidencePattern,,,FailsOnlyOnEdgeCaseTests,test-pattern,,active
0.91,Detect off-by-one traversal logic when a loop uses <= length while indexing from zero.,rule.loop.off_by_one.leq_length,true,DiagnosticRule,,,DetectOffByOneFromLessEqualLength,,false,active
0.79,Detect off-by-one behavior when traversal starts at one in zero-indexed structures.,rule.loop.off_by_one.start_one,true,DiagnosticRule,,,DetectOffByOneFromStartOne,,false,active
0.95,Detect infinite loop caused by missing progress update.,rule.loop.infinite.missing_update,true,DiagnosticRule,,,DetectInfiniteLoopFromMissingUpdate,,false,active
0.88,Detect infinite loop when progress moves away from exit condition.,rule.loop.infinite.wrong_direction,true,DiagnosticRule,,,DetectInfiniteLoopFromWrongDirection,,false,active
0.74,Infer boundary bug from failure isolated to last/edge element tests.,rule.loop.boundary.edge_case,true,DiagnosticRule,,,DetectBoundaryLogicFromEdgeCaseFailure,,true,active
0.90,Detect out-of-bounds access where array/container is indexed by its size directly.,rule.array.out_of_bounds.size_index,true,DiagnosticRule,,,DetectArrayOutOfBoundsFromSizeIndex,,false,active
0.72,Detect confusion between index and value roles in traversal/update logic.,rule.array.index_value_confusion,true,DiagnosticRule,,,DetectIndexValueRoleConfusion,,false,active
0.83,Detect possible null dereference from an unsafe dereference pattern.,rule.pointer.null_deref.ast,true,DiagnosticRule,,,DetectNullDereferenceFromUnsafeDereference,,false,active
0.97,Attach null dereference diagnosis when the static analyzer reports it.,rule.pointer.null_deref.clang,true,DiagnosticRule,,,DetectNullDereferenceFromAnalyzer,,false,active
0.87,Detect memory leak from ownership flow missing a release or RAII handoff.,rule.memory.leak.alloc_no_release,true,DiagnosticRule,,,DetectMemoryLeakFromMissingRelease,,false,active
0.96,Detect use-after-free when data-flow shows access after release.,rule.memory.use_after_free.flow,true,DiagnosticRule,,,DetectUseAfterFreeFromDataFlow,,false,active
0.95,Detect double release of the same ownership resource.,rule.memory.double_free.flow,true,DiagnosticRule,,,DetectDoubleFreeFromDataFlow,,false,active
0.99,Trust sanitizer evidence for use-after-free diagnosis.,rule.memory.uaf.sanitizer,true,DiagnosticRule,,,DetectUseAfterFreeFromSanitizer,,true,active
0.99,Trust sanitizer or leak instrumentation for memory leak diagnosis.,rule.memory.leak.sanitizer,true,DiagnosticRule,,,DetectMemoryLeakFromSanitizer,,true,active
0.98,Detect missing return in non-void function from compiler diagnostic.,rule.function.missing_return.compiler,true,DiagnosticRule,,,DetectMissingReturnFromCompilerWarning,,false,active
0.86,Detect missing return by finding a control-flow path with no return.,rule.function.missing_return.cfg,true,DiagnosticRule,,,DetectMissingReturnFromCFG,,false,active
0.89,Detect recursion bug when no valid base case is present.,rule.recursion.no_base_case,true,DiagnosticRule,,,DetectWrongBaseCaseFromMissingBase,,false,active
0.84,Detect recursion bug when base case exists but is unreachable.,rule.recursion.unreachable_base,true,DiagnosticRule,,,DetectWrongBaseCaseFromUnreachableBase,,false,active
0.93,Detect recursive non-progress when recursive calls do not reduce problem size.,rule.recursion.no_progress,true,DiagnosticRule,,,DetectNoRecursiveProgress,,false,active
0.94,Detect iterator invalidation caused by modify-then-use pattern.,rule.iterator.invalidation.modify_then_use,true,DiagnosticRule,,,DetectIteratorInvalidationAfterModification,,false,active
0.82,Detect view or range lifetime misuse when source outlives assumptions fail.,rule.iterator.view_lifetime,true,DiagnosticRule,,,DetectRangeViewLifetimeIssue,,false,active
0.85,Detect invalid dependence on moved-from object state.,rule.move.use_after_move,true,DiagnosticRule,,,DetectUseAfterMove,,false,active
0.96,Detect missing virtual destructor when deleting through base pointer.,rule.oop.delete_base_no_virtual,true,DiagnosticRule,,,DetectMissingVirtualDestructor,,false,active
0.81,Detect a likely Rule of Five violation in a resource-owning type.,rule.oop.rule_of_five,true,DiagnosticRule,,,DetectRuleOfFiveViolation,,false,active
0.77,Detect likely exception-safety issue from manual cleanup on exceptional path.,rule.oop.exception_safety,true,DiagnosticRule,,,DetectExceptionSafetyViolation,,false,active
0.95,Detect mismatch between formatting specifier and argument type.,rule.format.specifier_mismatch,true,DiagnosticRule,,,DetectFormatSpecifierMismatch,,false,active
0.64,Recommend upgrading from unsafe formatting to type-safe modern formatting APIs.,rule.format.modern_cpp_upgrade,false,DiagnosticRule,,,RecommendTypeSafeFormatting,,false,active
0.88,Detect condition variable wait misuse without predicate-based waiting.,rule.concurrent.wait_protocol,true,DiagnosticRule,,,DetectConditionVariableProtocolMisuse,,false,active
0.76,Detect unsafe shared-state access with insufficient synchronization evidence.,rule.concurrent.missing_sync,true,DiagnosticRule,,,DetectSharedStateWithoutSynchronization,,false,active
0.71,Use cross-evidence from edge-case failures to strengthen boundary-related diagnoses.,rule.meta.edge_case_boundary,true,DiagnosticRule,,,CrossCheckBoundaryBugFromEdgeCasePattern,,true,active
"""
RELATIONSHIPS_CSV = r"""end_id,start_id,type
rulecat.root,rulecat.loop,SUBCATEGORY_OF
rulecat.root,rulecat.array,SUBCATEGORY_OF
rulecat.root,rulecat.pointer,SUBCATEGORY_OF
rulecat.root,rulecat.function,SUBCATEGORY_OF
rulecat.root,rulecat.recursion,SUBCATEGORY_OF
rulecat.root,rulecat.iterator,SUBCATEGORY_OF
rulecat.root,rulecat.oop,SUBCATEGORY_OF
rulecat.root,rulecat.io,SUBCATEGORY_OF
rulecat.root,rulecat.concurrency,SUBCATEGORY_OF
rulecat.root,rulecat.meta,SUBCATEGORY_OF
rulecat.loop,rule.loop.off_by_one.leq_length,BELONGS_TO_CATEGORY
rulecat.loop,rule.loop.off_by_one.start_one,BELONGS_TO_CATEGORY
rulecat.loop,rule.loop.infinite.missing_update,BELONGS_TO_CATEGORY
rulecat.loop,rule.loop.infinite.wrong_direction,BELONGS_TO_CATEGORY
rulecat.loop,rule.loop.boundary.edge_case,BELONGS_TO_CATEGORY
rulecat.array,rule.array.out_of_bounds.size_index,BELONGS_TO_CATEGORY
rulecat.array,rule.array.index_value_confusion,BELONGS_TO_CATEGORY
rulecat.pointer,rule.pointer.null_deref.ast,BELONGS_TO_CATEGORY
rulecat.pointer,rule.pointer.null_deref.clang,BELONGS_TO_CATEGORY
rulecat.pointer,rule.memory.leak.alloc_no_release,BELONGS_TO_CATEGORY
rulecat.pointer,rule.memory.use_after_free.flow,BELONGS_TO_CATEGORY
rulecat.pointer,rule.memory.double_free.flow,BELONGS_TO_CATEGORY
rulecat.pointer,rule.memory.uaf.sanitizer,BELONGS_TO_CATEGORY
rulecat.pointer,rule.memory.leak.sanitizer,BELONGS_TO_CATEGORY
rulecat.function,rule.function.missing_return.compiler,BELONGS_TO_CATEGORY
rulecat.function,rule.function.missing_return.cfg,BELONGS_TO_CATEGORY
rulecat.recursion,rule.recursion.no_base_case,BELONGS_TO_CATEGORY
rulecat.recursion,rule.recursion.unreachable_base,BELONGS_TO_CATEGORY
rulecat.recursion,rule.recursion.no_progress,BELONGS_TO_CATEGORY
rulecat.iterator,rule.iterator.invalidation.modify_then_use,BELONGS_TO_CATEGORY
rulecat.iterator,rule.iterator.view_lifetime,BELONGS_TO_CATEGORY
rulecat.oop,rule.move.use_after_move,BELONGS_TO_CATEGORY
rulecat.oop,rule.oop.delete_base_no_virtual,BELONGS_TO_CATEGORY
rulecat.oop,rule.oop.rule_of_five,BELONGS_TO_CATEGORY
rulecat.oop,rule.oop.exception_safety,BELONGS_TO_CATEGORY
rulecat.io,rule.format.specifier_mismatch,BELONGS_TO_CATEGORY
rulecat.io,rule.format.modern_cpp_upgrade,BELONGS_TO_CATEGORY
rulecat.concurrency,rule.concurrent.wait_protocol,BELONGS_TO_CATEGORY
rulecat.concurrency,rule.concurrent.missing_sync,BELONGS_TO_CATEGORY
rulecat.meta,rule.meta.edge_case_boundary,BELONGS_TO_CATEGORY
bug.off_by_one,rule.loop.off_by_one.leq_length,DETECTS_BUG
bug.array_out_of_bounds,rule.loop.off_by_one.leq_length,DETECTS_BUG
bug.off_by_one,rule.loop.off_by_one.start_one,DETECTS_BUG
bug.index_value_confusion,rule.loop.off_by_one.start_one,DETECTS_BUG
bug.infinite_loop,rule.loop.infinite.missing_update,DETECTS_BUG
bug.missing_loop_update,rule.loop.infinite.missing_update,DETECTS_BUG
bug.infinite_loop,rule.loop.infinite.wrong_direction,DETECTS_BUG
bug.off_by_one,rule.loop.boundary.edge_case,DETECTS_BUG
bug.wrong_loop_condition,rule.loop.boundary.edge_case,DETECTS_BUG
bug.array_out_of_bounds,rule.array.out_of_bounds.size_index,DETECTS_BUG
bug.vector_out_of_range,rule.array.out_of_bounds.size_index,DETECTS_BUG
bug.index_value_confusion,rule.array.index_value_confusion,DETECTS_BUG
bug.null_dereference,rule.pointer.null_deref.ast,DETECTS_BUG
bug.null_dereference,rule.pointer.null_deref.clang,DETECTS_BUG
bug.memory_leak,rule.memory.leak.alloc_no_release,DETECTS_BUG
bug.use_after_free,rule.memory.use_after_free.flow,DETECTS_BUG
bug.dangling_pointer,rule.memory.use_after_free.flow,DETECTS_BUG
bug.double_free,rule.memory.double_free.flow,DETECTS_BUG
bug.use_after_free,rule.memory.uaf.sanitizer,DETECTS_BUG
bug.memory_leak,rule.memory.leak.sanitizer,DETECTS_BUG
bug.missing_return,rule.function.missing_return.compiler,DETECTS_BUG
bug.missing_return,rule.function.missing_return.cfg,DETECTS_BUG
bug.wrong_base_case,rule.recursion.no_base_case,DETECTS_BUG
bug.wrong_base_case,rule.recursion.unreachable_base,DETECTS_BUG
bug.no_recursive_progress,rule.recursion.no_progress,DETECTS_BUG
bug.iterator_invalidation,rule.iterator.invalidation.modify_then_use,DETECTS_BUG
bug.vector_out_of_range,rule.iterator.invalidation.modify_then_use,DETECTS_BUG
bug.iterator_invalidation,rule.iterator.view_lifetime,DETECTS_BUG
bug.use_after_move,rule.move.use_after_move,DETECTS_BUG
bug.missing_virtual_destructor,rule.oop.delete_base_no_virtual,DETECTS_BUG
bug.rule_of_five,rule.oop.rule_of_five,DETECTS_BUG
bug.exception_safety,rule.oop.exception_safety,DETECTS_BUG
bug.format_specifier_mismatch,rule.format.specifier_mismatch,DETECTS_BUG
bug.format_specifier_mismatch,rule.format.modern_cpp_upgrade,DETECTS_BUG
bug.condition_variable_misuse,rule.concurrent.wait_protocol,DETECTS_BUG
bug.condition_variable_misuse,rule.concurrent.missing_sync,DETECTS_BUG
bug.off_by_one,rule.meta.edge_case_boundary,DETECTS_BUG
bug.array_out_of_bounds,rule.meta.edge_case_boundary,DETECTS_BUG
bug.wrong_loop_condition,rule.meta.edge_case_boundary,DETECTS_BUG
ev.loop.boundary.le_length,rule.loop.off_by_one.leq_length,USES_EVIDENCE
ev.loop.test.last_case_only,rule.loop.off_by_one.leq_length,USES_EVIDENCE
ev.loop.boundary.starts_one,rule.loop.off_by_one.start_one,USES_EVIDENCE
ev.loop.test.last_case_only,rule.loop.off_by_one.start_one,USES_EVIDENCE
ev.loop.progress.no_update,rule.loop.infinite.missing_update,USES_EVIDENCE
ev.loop.timeout,rule.loop.infinite.missing_update,USES_EVIDENCE
ev.loop.progress.wrong_direction,rule.loop.infinite.wrong_direction,USES_EVIDENCE
ev.loop.timeout,rule.loop.infinite.wrong_direction,USES_EVIDENCE
ev.loop.test.last_case_only,rule.loop.boundary.edge_case,USES_EVIDENCE
ev.cross.edge_only_failure,rule.loop.boundary.edge_case,USES_EVIDENCE
ev.array.index.size_access,rule.array.out_of_bounds.size_index,USES_EVIDENCE
ev.array.bounds.crash,rule.array.out_of_bounds.size_index,USES_EVIDENCE
ev.array.index.value_misuse,rule.array.index_value_confusion,USES_EVIDENCE
ev.pointer.null_check_missing,rule.pointer.null_deref.ast,USES_EVIDENCE
ev.pointer.clang_null,rule.pointer.null_deref.clang,USES_EVIDENCE
ev.memory.alloc_without_release,rule.memory.leak.alloc_no_release,USES_EVIDENCE
ev.memory.release_then_use,rule.memory.use_after_free.flow,USES_EVIDENCE
ev.memory.double_release,rule.memory.double_free.flow,USES_EVIDENCE
ev.memory.sanitizer_uaf,rule.memory.uaf.sanitizer,USES_EVIDENCE
ev.memory.sanitizer_leak,rule.memory.leak.sanitizer,USES_EVIDENCE
ev.function.warn_nonvoid,rule.function.missing_return.compiler,USES_EVIDENCE
ev.function.path_no_return,rule.function.missing_return.cfg,USES_EVIDENCE
ev.recursion.no_base_case,rule.recursion.no_base_case,USES_EVIDENCE
ev.recursion.base_unreachable,rule.recursion.unreachable_base,USES_EVIDENCE
ev.recursion.no_progress,rule.recursion.no_progress,USES_EVIDENCE
ev.iterator.modified_container,rule.iterator.invalidation.modify_then_use,USES_EVIDENCE
ev.iterator.erase_then_use,rule.iterator.invalidation.modify_then_use,USES_EVIDENCE
ev.iterator.view_lifetime,rule.iterator.view_lifetime,USES_EVIDENCE
ev.move.use_after_move,rule.move.use_after_move,USES_EVIDENCE
ev.oop.delete_base_no_virtual,rule.oop.delete_base_no_virtual,USES_EVIDENCE
ev.oop.rule_of_five_partial,rule.oop.rule_of_five,USES_EVIDENCE
ev.oop.exception_cleanup,rule.oop.exception_safety,USES_EVIDENCE
ev.format.printf_type_mismatch,rule.format.specifier_mismatch,USES_EVIDENCE
ev.format.mixed_print_api,rule.format.modern_cpp_upgrade,USES_EVIDENCE
ev.concurrent.wait_without_predicate,rule.concurrent.wait_protocol,USES_EVIDENCE
ev.concurrent.notify_without_lock_protocol,rule.concurrent.missing_sync,USES_EVIDENCE
ev.concurrent.thread_shared_state_no_sync,rule.concurrent.missing_sync,USES_EVIDENCE
ev.cross.edge_only_failure,rule.meta.edge_case_boundary,USES_EVIDENCE
ev.loop.test.last_case_only,rule.meta.edge_case_boundary,USES_EVIDENCE
tool.ast,rule.loop.off_by_one.leq_length,SUPPORTED_BY_TOOL
tool.unittest,rule.loop.off_by_one.leq_length,SUPPORTED_BY_TOOL
tool.ast,rule.loop.off_by_one.start_one,SUPPORTED_BY_TOOL
tool.unittest,rule.loop.off_by_one.start_one,SUPPORTED_BY_TOOL
tool.ast,rule.loop.infinite.missing_update,SUPPORTED_BY_TOOL
tool.runtime,rule.loop.infinite.missing_update,SUPPORTED_BY_TOOL
tool.ast,rule.loop.infinite.wrong_direction,SUPPORTED_BY_TOOL
tool.runtime,rule.loop.infinite.wrong_direction,SUPPORTED_BY_TOOL
tool.unittest,rule.loop.boundary.edge_case,SUPPORTED_BY_TOOL
tool.ast,rule.array.out_of_bounds.size_index,SUPPORTED_BY_TOOL
tool.runtime,rule.array.out_of_bounds.size_index,SUPPORTED_BY_TOOL
tool.ast,rule.array.index_value_confusion,SUPPORTED_BY_TOOL
tool.ast,rule.pointer.null_deref.ast,SUPPORTED_BY_TOOL
tool.clangsa,rule.pointer.null_deref.clang,SUPPORTED_BY_TOOL
tool.dataflow,rule.memory.leak.alloc_no_release,SUPPORTED_BY_TOOL
tool.dataflow,rule.memory.use_after_free.flow,SUPPORTED_BY_TOOL
tool.dataflow,rule.memory.double_free.flow,SUPPORTED_BY_TOOL
tool.sanitizer,rule.memory.uaf.sanitizer,SUPPORTED_BY_TOOL
tool.sanitizer,rule.memory.leak.sanitizer,SUPPORTED_BY_TOOL
tool.compiler,rule.function.missing_return.compiler,SUPPORTED_BY_TOOL
tool.cfg,rule.function.missing_return.cfg,SUPPORTED_BY_TOOL
tool.ast,rule.recursion.no_base_case,SUPPORTED_BY_TOOL
tool.cfg,rule.recursion.unreachable_base,SUPPORTED_BY_TOOL
tool.ast,rule.recursion.no_progress,SUPPORTED_BY_TOOL
tool.dataflow,rule.iterator.invalidation.modify_then_use,SUPPORTED_BY_TOOL
tool.dataflow,rule.iterator.view_lifetime,SUPPORTED_BY_TOOL
tool.dataflow,rule.move.use_after_move,SUPPORTED_BY_TOOL
tool.style,rule.move.use_after_move,SUPPORTED_BY_TOOL
tool.ast,rule.oop.delete_base_no_virtual,SUPPORTED_BY_TOOL
tool.ast,rule.oop.rule_of_five,SUPPORTED_BY_TOOL
tool.style,rule.oop.rule_of_five,SUPPORTED_BY_TOOL
tool.cfg,rule.oop.exception_safety,SUPPORTED_BY_TOOL
tool.style,rule.oop.exception_safety,SUPPORTED_BY_TOOL
tool.ast,rule.format.specifier_mismatch,SUPPORTED_BY_TOOL
tool.compiler,rule.format.specifier_mismatch,SUPPORTED_BY_TOOL
tool.style,rule.format.modern_cpp_upgrade,SUPPORTED_BY_TOOL
tool.ast,rule.concurrent.wait_protocol,SUPPORTED_BY_TOOL
tool.dataflow,rule.concurrent.missing_sync,SUPPORTED_BY_TOOL
tool.runtime,rule.concurrent.missing_sync,SUPPORTED_BY_TOOL
tool.unittest,rule.meta.edge_case_boundary,SUPPORTED_BY_TOOL
concept.c.array,rule.loop.off_by_one.leq_length,APPLIES_TO_CONCEPT
concept.c.for,rule.loop.off_by_one.leq_length,APPLIES_TO_CONCEPT
concept.cpp.vector,rule.loop.off_by_one.leq_length,APPLIES_TO_CONCEPT
concept.cpp.range_for,rule.loop.off_by_one.leq_length,APPLIES_TO_CONCEPT
concept.c.array,rule.loop.off_by_one.start_one,APPLIES_TO_CONCEPT
concept.c.for,rule.loop.off_by_one.start_one,APPLIES_TO_CONCEPT
concept.cpp.array,rule.loop.off_by_one.start_one,APPLIES_TO_CONCEPT
concept.cpp.vector,rule.loop.off_by_one.start_one,APPLIES_TO_CONCEPT
concept.c.for,rule.loop.infinite.missing_update,APPLIES_TO_CONCEPT
concept.c.while,rule.loop.infinite.missing_update,APPLIES_TO_CONCEPT
concept.cpp.for,rule.loop.infinite.missing_update,APPLIES_TO_CONCEPT
concept.cpp.while,rule.loop.infinite.missing_update,APPLIES_TO_CONCEPT
concept.c.for,rule.loop.infinite.wrong_direction,APPLIES_TO_CONCEPT
concept.cpp.for,rule.loop.infinite.wrong_direction,APPLIES_TO_CONCEPT
concept.c.array,rule.loop.boundary.edge_case,APPLIES_TO_CONCEPT
concept.cpp.vector,rule.loop.boundary.edge_case,APPLIES_TO_CONCEPT
concept.cpp.range_for,rule.loop.boundary.edge_case,APPLIES_TO_CONCEPT
concept.c.array,rule.array.out_of_bounds.size_index,APPLIES_TO_CONCEPT
concept.cpp.array,rule.array.out_of_bounds.size_index,APPLIES_TO_CONCEPT
concept.cpp.vector,rule.array.out_of_bounds.size_index,APPLIES_TO_CONCEPT
concept.c.array,rule.array.index_value_confusion,APPLIES_TO_CONCEPT
concept.cpp.array,rule.array.index_value_confusion,APPLIES_TO_CONCEPT
concept.cpp.vector,rule.array.index_value_confusion,APPLIES_TO_CONCEPT
concept.c.pointer,rule.pointer.null_deref.ast,APPLIES_TO_CONCEPT
concept.cpp.pointer,rule.pointer.null_deref.ast,APPLIES_TO_CONCEPT
concept.cpp.smart_pointer,rule.pointer.null_deref.ast,APPLIES_TO_CONCEPT
concept.c.pointer,rule.pointer.null_deref.clang,APPLIES_TO_CONCEPT
concept.cpp.pointer,rule.pointer.null_deref.clang,APPLIES_TO_CONCEPT
concept.c.malloc,rule.memory.leak.alloc_no_release,APPLIES_TO_CONCEPT
concept.c.calloc,rule.memory.leak.alloc_no_release,APPLIES_TO_CONCEPT
concept.c.realloc,rule.memory.leak.alloc_no_release,APPLIES_TO_CONCEPT
concept.cpp.new_delete,rule.memory.leak.alloc_no_release,APPLIES_TO_CONCEPT
concept.cpp.raii,rule.memory.leak.alloc_no_release,APPLIES_TO_CONCEPT
concept.c.free,rule.memory.use_after_free.flow,APPLIES_TO_CONCEPT
concept.cpp.new_delete,rule.memory.use_after_free.flow,APPLIES_TO_CONCEPT
concept.c.pointer,rule.memory.use_after_free.flow,APPLIES_TO_CONCEPT
concept.cpp.pointer,rule.memory.use_after_free.flow,APPLIES_TO_CONCEPT
concept.c.free,rule.memory.double_free.flow,APPLIES_TO_CONCEPT
concept.cpp.new_delete,rule.memory.double_free.flow,APPLIES_TO_CONCEPT
concept.cpp.smart_pointer,rule.memory.double_free.flow,APPLIES_TO_CONCEPT
concept.c.pointer,rule.memory.uaf.sanitizer,APPLIES_TO_CONCEPT
concept.cpp.pointer,rule.memory.uaf.sanitizer,APPLIES_TO_CONCEPT
concept.c.malloc,rule.memory.leak.sanitizer,APPLIES_TO_CONCEPT
concept.cpp.new_delete,rule.memory.leak.sanitizer,APPLIES_TO_CONCEPT
concept.c.function_def,rule.function.missing_return.compiler,APPLIES_TO_CONCEPT
concept.cpp.function_decl,rule.function.missing_return.compiler,APPLIES_TO_CONCEPT
concept.c.function_def,rule.function.missing_return.cfg,APPLIES_TO_CONCEPT
concept.cpp.function_decl,rule.function.missing_return.cfg,APPLIES_TO_CONCEPT
concept.c.function_def,rule.recursion.no_base_case,APPLIES_TO_CONCEPT
concept.cpp.function_decl,rule.recursion.no_base_case,APPLIES_TO_CONCEPT
concept.c.function_def,rule.recursion.unreachable_base,APPLIES_TO_CONCEPT
concept.cpp.function_decl,rule.recursion.unreachable_base,APPLIES_TO_CONCEPT
concept.c.function_def,rule.recursion.no_progress,APPLIES_TO_CONCEPT
concept.cpp.function_decl,rule.recursion.no_progress,APPLIES_TO_CONCEPT
concept.cpp.iterator,rule.iterator.invalidation.modify_then_use,APPLIES_TO_CONCEPT
concept.cpp.vector,rule.iterator.invalidation.modify_then_use,APPLIES_TO_CONCEPT
concept.cpp.map,rule.iterator.invalidation.modify_then_use,APPLIES_TO_CONCEPT
concept.cpp.unordered_map,rule.iterator.invalidation.modify_then_use,APPLIES_TO_CONCEPT
concept.cpp.ranges,rule.iterator.view_lifetime,APPLIES_TO_CONCEPT
concept.cpp.views,rule.iterator.view_lifetime,APPLIES_TO_CONCEPT
concept.cpp.string_view,rule.iterator.view_lifetime,APPLIES_TO_CONCEPT
concept.cpp.span,rule.iterator.view_lifetime,APPLIES_TO_CONCEPT
concept.cpp.move_semantics,rule.move.use_after_move,APPLIES_TO_CONCEPT
concept.cpp.unique_ptr,rule.move.use_after_move,APPLIES_TO_CONCEPT
concept.cpp.string,rule.move.use_after_move,APPLIES_TO_CONCEPT
concept.cpp.vector,rule.move.use_after_move,APPLIES_TO_CONCEPT
concept.cpp.class,rule.oop.delete_base_no_virtual,APPLIES_TO_CONCEPT
concept.cpp.inheritance,rule.oop.delete_base_no_virtual,APPLIES_TO_CONCEPT
concept.cpp.virtual_function,rule.oop.delete_base_no_virtual,APPLIES_TO_CONCEPT
concept.cpp.destructor,rule.oop.delete_base_no_virtual,APPLIES_TO_CONCEPT
concept.cpp.class,rule.oop.rule_of_five,APPLIES_TO_CONCEPT
concept.cpp.destructor,rule.oop.rule_of_five,APPLIES_TO_CONCEPT
concept.cpp.copy_semantics,rule.oop.rule_of_five,APPLIES_TO_CONCEPT
concept.cpp.move_semantics,rule.oop.rule_of_five,APPLIES_TO_CONCEPT
concept.cpp.raii,rule.oop.rule_of_five,APPLIES_TO_CONCEPT
concept.cpp.try_catch,rule.oop.exception_safety,APPLIES_TO_CONCEPT
concept.cpp.noexcept,rule.oop.exception_safety,APPLIES_TO_CONCEPT
concept.cpp.raii,rule.oop.exception_safety,APPLIES_TO_CONCEPT
concept.c.formatted_io,rule.format.specifier_mismatch,APPLIES_TO_CONCEPT
concept.cpp.format,rule.format.specifier_mismatch,APPLIES_TO_CONCEPT
concept.cpp.print_functions,rule.format.specifier_mismatch,APPLIES_TO_CONCEPT
concept.cpp.format,rule.format.modern_cpp_upgrade,APPLIES_TO_CONCEPT
concept.cpp.print_functions,rule.format.modern_cpp_upgrade,APPLIES_TO_CONCEPT
concept.cpp.thread,rule.concurrent.wait_protocol,APPLIES_TO_CONCEPT
concept.cpp.mutex,rule.concurrent.wait_protocol,APPLIES_TO_CONCEPT
concept.cpp.condition_variable,rule.concurrent.wait_protocol,APPLIES_TO_CONCEPT
concept.cpp.thread,rule.concurrent.missing_sync,APPLIES_TO_CONCEPT
concept.cpp.mutex,rule.concurrent.missing_sync,APPLIES_TO_CONCEPT
concept.cpp.atomic,rule.concurrent.missing_sync,APPLIES_TO_CONCEPT
concept.c.array,rule.meta.edge_case_boundary,APPLIES_TO_CONCEPT
concept.cpp.vector,rule.meta.edge_case_boundary,APPLIES_TO_CONCEPT
concept.cpp.range_for,rule.meta.edge_case_boundary,APPLIES_TO_CONCEPT
fix.loop.bound,rule.loop.off_by_one.leq_length,RECOMMENDS_FIX
fix.array.bound,rule.loop.off_by_one.leq_length,RECOMMENDS_FIX
fix.loop.bound,rule.loop.off_by_one.start_one,RECOMMENDS_FIX
fix.loop.progress,rule.loop.infinite.missing_update,RECOMMENDS_FIX
fix.loop.progress,rule.loop.infinite.wrong_direction,RECOMMENDS_FIX
fix.loop.bound,rule.loop.boundary.edge_case,RECOMMENDS_FIX
fix.array.bound,rule.array.out_of_bounds.size_index,RECOMMENDS_FIX
fix.array.index_value,rule.array.index_value_confusion,RECOMMENDS_FIX
fix.null.check,rule.pointer.null_deref.ast,RECOMMENDS_FIX
fix.null.check,rule.pointer.null_deref.clang,RECOMMENDS_FIX
fix.release.once,rule.memory.leak.alloc_no_release,RECOMMENDS_FIX
fix.use_raii,rule.memory.leak.alloc_no_release,RECOMMENDS_FIX
fix.smart_pointer,rule.memory.leak.alloc_no_release,RECOMMENDS_FIX
fix.no_use_after_release,rule.memory.use_after_free.flow,RECOMMENDS_FIX
fix.smart_pointer,rule.memory.use_after_free.flow,RECOMMENDS_FIX
fix.release.once,rule.memory.double_free.flow,RECOMMENDS_FIX
fix.no_use_after_release,rule.memory.uaf.sanitizer,RECOMMENDS_FIX
fix.release.once,rule.memory.leak.sanitizer,RECOMMENDS_FIX
fix.return,rule.function.missing_return.compiler,RECOMMENDS_FIX
fix.return,rule.function.missing_return.cfg,RECOMMENDS_FIX
fix.recursion.base,rule.recursion.no_base_case,RECOMMENDS_FIX
fix.recursion.base,rule.recursion.unreachable_base,RECOMMENDS_FIX
fix.recursion.progress,rule.recursion.no_progress,RECOMMENDS_FIX
fix.iterator.refresh,rule.iterator.invalidation.modify_then_use,RECOMMENDS_FIX
fix.iterator.refresh,rule.iterator.view_lifetime,RECOMMENDS_FIX
fix.move.use_state,rule.move.use_after_move,RECOMMENDS_FIX
fix.virtual_destructor,rule.oop.delete_base_no_virtual,RECOMMENDS_FIX
fix.use_raii,rule.oop.rule_of_five,RECOMMENDS_FIX
fix.smart_pointer,rule.oop.rule_of_five,RECOMMENDS_FIX
fix.use_raii,rule.oop.exception_safety,RECOMMENDS_FIX
fix.format.match,rule.format.specifier_mismatch,RECOMMENDS_FIX
fix.format.match,rule.format.modern_cpp_upgrade,RECOMMENDS_FIX
fix.condition_wait,rule.concurrent.wait_protocol,RECOMMENDS_FIX
fix.condition_wait,rule.concurrent.missing_sync,RECOMMENDS_FIX
fix.array.bound,rule.meta.edge_case_boundary,RECOMMENDS_FIX
fix.loop.bound,rule.meta.edge_case_boundary,RECOMMENDS_FIX
view.intro_c,rule.loop.off_by_one.leq_length,VISIBLE_IN
view.algorithms,rule.loop.off_by_one.leq_length,VISIBLE_IN
view.intro_c,rule.loop.off_by_one.start_one,VISIBLE_IN
view.algorithms,rule.loop.off_by_one.start_one,VISIBLE_IN
view.intro_c,rule.loop.infinite.missing_update,VISIBLE_IN
view.algorithms,rule.loop.infinite.missing_update,VISIBLE_IN
view.intro_c,rule.loop.infinite.wrong_direction,VISIBLE_IN
view.algorithms,rule.loop.infinite.wrong_direction,VISIBLE_IN
view.intro_c,rule.loop.boundary.edge_case,VISIBLE_IN
view.algorithms,rule.loop.boundary.edge_case,VISIBLE_IN
view.intro_c,rule.array.out_of_bounds.size_index,VISIBLE_IN
view.algorithms,rule.array.out_of_bounds.size_index,VISIBLE_IN
view.cpp_stl,rule.array.out_of_bounds.size_index,VISIBLE_IN
view.intro_c,rule.array.index_value_confusion,VISIBLE_IN
view.algorithms,rule.array.index_value_confusion,VISIBLE_IN
view.c_pointers,rule.pointer.null_deref.ast,VISIBLE_IN
view.c_pointers,rule.pointer.null_deref.clang,VISIBLE_IN
view.c_pointers,rule.memory.leak.alloc_no_release,VISIBLE_IN
view.cpp_modern,rule.memory.leak.alloc_no_release,VISIBLE_IN
view.c_pointers,rule.memory.use_after_free.flow,VISIBLE_IN
view.c_pointers,rule.memory.double_free.flow,VISIBLE_IN
view.c_pointers,rule.memory.uaf.sanitizer,VISIBLE_IN
view.c_pointers,rule.memory.leak.sanitizer,VISIBLE_IN
view.cpp_modern,rule.memory.leak.sanitizer,VISIBLE_IN
view.intro_c,rule.function.missing_return.compiler,VISIBLE_IN
view.intro_c,rule.function.missing_return.cfg,VISIBLE_IN
view.algorithms,rule.recursion.no_base_case,VISIBLE_IN
view.algorithms,rule.recursion.unreachable_base,VISIBLE_IN
view.algorithms,rule.recursion.no_progress,VISIBLE_IN
view.cpp_stl,rule.iterator.invalidation.modify_then_use,VISIBLE_IN
view.cpp_modern,rule.iterator.invalidation.modify_then_use,VISIBLE_IN
view.cpp_stl,rule.iterator.view_lifetime,VISIBLE_IN
view.cpp_modern,rule.iterator.view_lifetime,VISIBLE_IN
view.cpp_modern,rule.move.use_after_move,VISIBLE_IN
view.cpp_oop,rule.oop.delete_base_no_virtual,VISIBLE_IN
view.cpp_oop,rule.oop.rule_of_five,VISIBLE_IN
view.cpp_modern,rule.oop.rule_of_five,VISIBLE_IN
view.cpp_oop,rule.oop.exception_safety,VISIBLE_IN
view.cpp_modern,rule.oop.exception_safety,VISIBLE_IN
view.intro_c,rule.format.specifier_mismatch,VISIBLE_IN
view.cpp_modern,rule.format.modern_cpp_upgrade,VISIBLE_IN
view.cpp_modern,rule.concurrent.wait_protocol,VISIBLE_IN
view.cpp_modern,rule.concurrent.missing_sync,VISIBLE_IN
view.algorithms,rule.meta.edge_case_boundary,VISIBLE_IN
"""
SEED_CYPHER = r"""CREATE CONSTRAINT rule_category_id_unique IF NOT EXISTS FOR (n:RuleCategory) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT diagnostic_rule_id_unique IF NOT EXISTS FOR (n:DiagnosticRule) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT evidence_pattern_id_unique IF NOT EXISTS FOR (n:EvidencePattern) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT tool_signature_id_unique IF NOT EXISTS FOR (n:ToolSignature) REQUIRE n.id IS UNIQUE;

// Diagnostic rule nodes
MERGE (n:RuleCategory {id: 'rulecat.root'}) SET n += {id: 'rulecat.root', name: 'DiagnosticRuleRoot', description: 'Root category for all diagnostic rules', level: 'top', status: 'active'};
MERGE (n:RuleCategory {id: 'rulecat.loop'}) SET n += {id: 'rulecat.loop', name: 'LoopDiagnosis', description: 'Rules for loops, boundaries, and progress', level: 'top', status: 'active'};
MERGE (n:RuleCategory {id: 'rulecat.array'}) SET n += {id: 'rulecat.array', name: 'ArrayAndIndexDiagnosis', description: 'Rules for arrays, indexing, and traversal', level: 'top', status: 'active'};
MERGE (n:RuleCategory {id: 'rulecat.pointer'}) SET n += {id: 'rulecat.pointer', name: 'PointerAndMemoryDiagnosis', description: 'Rules for pointer validity, ownership, and memory lifetime', level: 'top', status: 'active'};
MERGE (n:RuleCategory {id: 'rulecat.function'}) SET n += {id: 'rulecat.function', name: 'FunctionContractDiagnosis', description: 'Rules for return behavior and function-level obligations', level: 'top', status: 'active'};
MERGE (n:RuleCategory {id: 'rulecat.recursion'}) SET n += {id: 'rulecat.recursion', name: 'RecursionDiagnosis', description: 'Rules for base case and recursive progress', level: 'top', status: 'active'};
MERGE (n:RuleCategory {id: 'rulecat.iterator'}) SET n += {id: 'rulecat.iterator', name: 'IteratorAndRangeDiagnosis', description: 'Rules for iterators, ranges, and container invalidation', level: 'top', status: 'active'};
MERGE (n:RuleCategory {id: 'rulecat.oop'}) SET n += {id: 'rulecat.oop', name: 'OOPLifetimeDiagnosis', description: 'Rules for virtual dispatch, polymorphic destruction, and RAII', level: 'top', status: 'active'};
MERGE (n:RuleCategory {id: 'rulecat.io'}) SET n += {id: 'rulecat.io', name: 'IOFormattingDiagnosis', description: 'Rules for formatted input/output and printing APIs', level: 'top', status: 'active'};
MERGE (n:RuleCategory {id: 'rulecat.concurrency'}) SET n += {id: 'rulecat.concurrency', name: 'ConcurrencyDiagnosis', description: 'Rules for threads, mutexes, atomics, and condition variables', level: 'top', status: 'active'};
MERGE (n:RuleCategory {id: 'rulecat.meta'}) SET n += {id: 'rulecat.meta', name: 'MetaAndCrossChecks', description: 'Cross-cutting rules that combine multiple evidence types', level: 'top', status: 'active'};
MERGE (n:ToolSignature {id: 'tool.ast'}) SET n += {id: 'tool.ast', name: 'ASTInspection', mode: 'static', description: 'Pattern extracted from abstract syntax tree shape or syntax form.', status: 'active'};
MERGE (n:ToolSignature {id: 'tool.cfg'}) SET n += {id: 'tool.cfg', name: 'CFGInspection', mode: 'static', description: 'Pattern extracted from control-flow graph shape.', status: 'active'};
MERGE (n:ToolSignature {id: 'tool.dataflow'}) SET n += {id: 'tool.dataflow', name: 'DataFlowInspection', mode: 'static', description: 'Pattern extracted from value, alias, or lifetime flow.', status: 'active'};
MERGE (n:ToolSignature {id: 'tool.clangsa'}) SET n += {id: 'tool.clangsa', name: 'ClangStaticAnalyzer', mode: 'static', description: 'Derived from Clang Static Analyzer findings or equivalent path-sensitive analyzers.', status: 'active'};
MERGE (n:ToolSignature {id: 'tool.compiler'}) SET n += {id: 'tool.compiler', name: 'CompilerWarning', mode: 'static', description: 'Derived from compiler diagnostics and warnings.', status: 'active'};
MERGE (n:ToolSignature {id: 'tool.unittest'}) SET n += {id: 'tool.unittest', name: 'UnitTestFailure', mode: 'dynamic', description: 'Derived from failed edge-case or specification tests.', status: 'active'};
MERGE (n:ToolSignature {id: 'tool.runtime'}) SET n += {id: 'tool.runtime', name: 'RuntimeObservation', mode: 'dynamic', description: 'Derived from observed crash, timeout, hang, or anomalous runtime behavior.', status: 'active'};
MERGE (n:ToolSignature {id: 'tool.sanitizer'}) SET n += {id: 'tool.sanitizer', name: 'Sanitizer', mode: 'dynamic', description: 'Derived from tools such as AddressSanitizer, UBSan, or thread sanitizers.', status: 'active'};
MERGE (n:ToolSignature {id: 'tool.style'}) SET n += {id: 'tool.style', name: 'ModernCppLinter', mode: 'static', description: 'Derived from linting or best-practice checks for modern C++.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.loop.boundary.le_length'}) SET n += {id: 'ev.loop.boundary.le_length', name: 'LoopBoundaryUsesLessEqualLength', patternType: 'ast-pattern', description: 'Loop condition uses <= length or <= size while indexing from zero.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.loop.boundary.starts_one'}) SET n += {id: 'ev.loop.boundary.starts_one', name: 'LoopStartsAtOneForZeroIndexedTraversal', patternType: 'ast-pattern', description: 'Traversal over zero-indexed storage starts at 1 and misses or shifts valid positions.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.loop.progress.no_update'}) SET n += {id: 'ev.loop.progress.no_update', name: 'LoopVariableNotUpdated', patternType: 'ast-pattern', description: 'Loop variable or termination state is never updated toward exit.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.loop.progress.wrong_direction'}) SET n += {id: 'ev.loop.progress.wrong_direction', name: 'LoopVariableMovesAwayFromExit', patternType: 'ast-pattern', description: 'Loop variable update moves away from satisfying exit condition.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.loop.test.last_case_only'}) SET n += {id: 'ev.loop.test.last_case_only', name: 'FailsOnlyOnLastElementCase', patternType: 'test-pattern', description: 'Tests fail only on the final boundary element or exact-size edge case.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.loop.timeout'}) SET n += {id: 'ev.loop.timeout', name: 'RuntimeTimeoutInLoopRegion', patternType: 'runtime-pattern', description: 'Observed timeout or hang in a loop-heavy region.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.array.index.size_access'}) SET n += {id: 'ev.array.index.size_access', name: 'ArrayIndexedBySizeValue', patternType: 'ast-pattern', description: 'Array or vector is directly indexed by its length/size result.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.array.index.value_misuse'}) SET n += {id: 'ev.array.index.value_misuse', name: 'ArrayValueUsedAsIndexOrViceVersa', patternType: 'ast-pattern', description: 'Logic mixes roles of array element values and positions.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.array.bounds.crash'}) SET n += {id: 'ev.array.bounds.crash', name: 'OutOfBoundsCrashOnBoundaryTest', patternType: 'runtime-pattern', description: 'Boundary test triggers crash or invalid access symptom.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.pointer.null_check_missing'}) SET n += {id: 'ev.pointer.null_check_missing', name: 'PointerDereferencedWithoutGuard', patternType: 'ast-pattern', description: 'Pointer is dereferenced on a path lacking a guard or ownership guarantee.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.pointer.clang_null'}) SET n += {id: 'ev.pointer.clang_null', name: 'ClangNullDereferenceFinding', patternType: 'static-finding', description: 'Static analyzer reports null dereference possibility.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.memory.alloc_without_release'}) SET n += {id: 'ev.memory.alloc_without_release', name: 'AllocationWithoutMatchingRelease', patternType: 'dataflow-pattern', description: 'Ownership path contains allocation but no matching release or RAII handoff.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.memory.release_then_use'}) SET n += {id: 'ev.memory.release_then_use', name: 'ReleaseThenUseAccess', patternType: 'dataflow-pattern', description: 'Data-flow shows pointer/resource used after free/delete.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.memory.double_release'}) SET n += {id: 'ev.memory.double_release', name: 'ResourceReleasedTwice', patternType: 'dataflow-pattern', description: 'Lifetime path contains duplicated release of the same resource.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.memory.sanitizer_uaf'}) SET n += {id: 'ev.memory.sanitizer_uaf', name: 'SanitizerUseAfterFreeFinding', patternType: 'dynamic-finding', description: 'Sanitizer reports heap-use-after-free or invalid lifetime access.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.memory.sanitizer_leak'}) SET n += {id: 'ev.memory.sanitizer_leak', name: 'SanitizerLeakFinding', patternType: 'dynamic-finding', description: 'Leak sanitizer or instrumentation shows unreleased allocations.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.function.warn_nonvoid'}) SET n += {id: 'ev.function.warn_nonvoid', name: 'CompilerWarnsControlReachesEndNonVoid', patternType: 'static-finding', description: 'Compiler warns that control reaches end of non-void function.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.function.path_no_return'}) SET n += {id: 'ev.function.path_no_return', name: 'NonVoidPathMissingReturn', patternType: 'cfg-pattern', description: 'At least one control-flow path exits without a return in non-void function.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.recursion.no_base_case'}) SET n += {id: 'ev.recursion.no_base_case', name: 'RecursiveFunctionWithoutBaseCase', patternType: 'ast-pattern', description: 'Recursive function lacks a valid base case branch.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.recursion.base_unreachable'}) SET n += {id: 'ev.recursion.base_unreachable', name: 'RecursiveBaseCaseUnreachable', patternType: 'cfg-pattern', description: 'A base case exists syntactically but cannot be reached for relevant inputs.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.recursion.no_progress'}) SET n += {id: 'ev.recursion.no_progress', name: 'RecursiveCallDoesNotReduceProblem', patternType: 'ast-pattern', description: 'Recursive call fails to reduce problem size toward a base case.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.iterator.modified_container'}) SET n += {id: 'ev.iterator.modified_container', name: 'IteratorUsedAfterContainerModification', patternType: 'dataflow-pattern', description: 'Iterator/reference survives a modification that invalidates it.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.iterator.erase_then_use'}) SET n += {id: 'ev.iterator.erase_then_use', name: 'IteratorUsedAfterErase', patternType: 'dataflow-pattern', description: 'Iterator is used after erase/pop/reallocation-like operations.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.iterator.view_lifetime'}) SET n += {id: 'ev.iterator.view_lifetime', name: 'ViewOrRangeOutlivesSource', patternType: 'dataflow-pattern', description: 'Non-owning range/view outlives or outscopes its underlying source.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.move.use_after_move'}) SET n += {id: 'ev.move.use_after_move', name: 'MovedFromObjectUsedAsIfUnchanged', patternType: 'dataflow-pattern', description: 'Object is read as though unchanged after move operation.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.oop.delete_base_no_virtual'}) SET n += {id: 'ev.oop.delete_base_no_virtual', name: 'DeleteThroughBaseWithoutVirtualDestructor', patternType: 'ast-pattern', description: 'Delete is applied through base pointer lacking virtual destructor.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.oop.rule_of_five_partial'}) SET n += {id: 'ev.oop.rule_of_five_partial', name: 'CustomOwnerDefinesPartialSpecialMembers', patternType: 'ast-pattern', description: 'Resource-owning class defines only some copy/move/destructor members.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.oop.exception_cleanup'}) SET n += {id: 'ev.oop.exception_cleanup', name: 'ManualCleanupOnExceptionalPath', patternType: 'cfg-pattern', description: 'Exceptional path can bypass manual cleanup or leave partial state.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.format.printf_type_mismatch'}) SET n += {id: 'ev.format.printf_type_mismatch', name: 'PrintfSpecifierTypeMismatch', patternType: 'ast-pattern', description: 'Format specifier and actual argument type do not match.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.format.mixed_print_api'}) SET n += {id: 'ev.format.mixed_print_api', name: 'UnsafeCFormattingPreferredOverTypeSafeFormatting', patternType: 'style-pattern', description: 'Unsafe legacy formatting is used where safer type-aware formatting is expected.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.concurrent.wait_without_predicate'}) SET n += {id: 'ev.concurrent.wait_without_predicate', name: 'ConditionWaitWithoutPredicateLoop', patternType: 'ast-pattern', description: 'Condition variable wait is not wrapped in a predicate-checking loop.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.concurrent.notify_without_lock_protocol'}) SET n += {id: 'ev.concurrent.notify_without_lock_protocol', name: 'NotifyAndStateProtocolBroken', patternType: 'dataflow-pattern', description: 'Shared state and notify/wait protocol are not synchronized consistently.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.concurrent.thread_shared_state_no_sync'}) SET n += {id: 'ev.concurrent.thread_shared_state_no_sync', name: 'SharedStateAccessWithoutSynchronization', patternType: 'dataflow-pattern', description: 'Shared mutable state accessed across threads without evident synchronization.', status: 'active'};
MERGE (n:EvidencePattern {id: 'ev.cross.edge_only_failure'}) SET n += {id: 'ev.cross.edge_only_failure', name: 'FailsOnlyOnEdgeCaseTests', patternType: 'test-pattern', description: 'Most tests pass but edge cases fail, suggesting boundary or contract issue.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.loop.off_by_one.leq_length'}) SET n += {id: 'rule.loop.off_by_one.leq_length', name: 'DetectOffByOneFromLessEqualLength', confidenceBase: '0.91', requiresExecution: false, isAutoApplicable: true, description: 'Detect off-by-one traversal logic when a loop uses <= length while indexing from zero.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.loop.off_by_one.start_one'}) SET n += {id: 'rule.loop.off_by_one.start_one', name: 'DetectOffByOneFromStartOne', confidenceBase: '0.79', requiresExecution: false, isAutoApplicable: true, description: 'Detect off-by-one behavior when traversal starts at one in zero-indexed structures.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.loop.infinite.missing_update'}) SET n += {id: 'rule.loop.infinite.missing_update', name: 'DetectInfiniteLoopFromMissingUpdate', confidenceBase: '0.95', requiresExecution: false, isAutoApplicable: true, description: 'Detect infinite loop caused by missing progress update.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.loop.infinite.wrong_direction'}) SET n += {id: 'rule.loop.infinite.wrong_direction', name: 'DetectInfiniteLoopFromWrongDirection', confidenceBase: '0.88', requiresExecution: false, isAutoApplicable: true, description: 'Detect infinite loop when progress moves away from exit condition.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.loop.boundary.edge_case'}) SET n += {id: 'rule.loop.boundary.edge_case', name: 'DetectBoundaryLogicFromEdgeCaseFailure', confidenceBase: '0.74', requiresExecution: true, isAutoApplicable: true, description: 'Infer boundary bug from failure isolated to last/edge element tests.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.array.out_of_bounds.size_index'}) SET n += {id: 'rule.array.out_of_bounds.size_index', name: 'DetectArrayOutOfBoundsFromSizeIndex', confidenceBase: '0.90', requiresExecution: false, isAutoApplicable: true, description: 'Detect out-of-bounds access where array/container is indexed by its size directly.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.array.index_value_confusion'}) SET n += {id: 'rule.array.index_value_confusion', name: 'DetectIndexValueRoleConfusion', confidenceBase: '0.72', requiresExecution: false, isAutoApplicable: true, description: 'Detect confusion between index and value roles in traversal/update logic.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.pointer.null_deref.ast'}) SET n += {id: 'rule.pointer.null_deref.ast', name: 'DetectNullDereferenceFromUnsafeDereference', confidenceBase: '0.83', requiresExecution: false, isAutoApplicable: true, description: 'Detect possible null dereference from an unsafe dereference pattern.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.pointer.null_deref.clang'}) SET n += {id: 'rule.pointer.null_deref.clang', name: 'DetectNullDereferenceFromAnalyzer', confidenceBase: '0.97', requiresExecution: false, isAutoApplicable: true, description: 'Attach null dereference diagnosis when the static analyzer reports it.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.memory.leak.alloc_no_release'}) SET n += {id: 'rule.memory.leak.alloc_no_release', name: 'DetectMemoryLeakFromMissingRelease', confidenceBase: '0.87', requiresExecution: false, isAutoApplicable: true, description: 'Detect memory leak from ownership flow missing a release or RAII handoff.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.memory.use_after_free.flow'}) SET n += {id: 'rule.memory.use_after_free.flow', name: 'DetectUseAfterFreeFromDataFlow', confidenceBase: '0.96', requiresExecution: false, isAutoApplicable: true, description: 'Detect use-after-free when data-flow shows access after release.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.memory.double_free.flow'}) SET n += {id: 'rule.memory.double_free.flow', name: 'DetectDoubleFreeFromDataFlow', confidenceBase: '0.95', requiresExecution: false, isAutoApplicable: true, description: 'Detect double release of the same ownership resource.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.memory.uaf.sanitizer'}) SET n += {id: 'rule.memory.uaf.sanitizer', name: 'DetectUseAfterFreeFromSanitizer', confidenceBase: '0.99', requiresExecution: true, isAutoApplicable: true, description: 'Trust sanitizer evidence for use-after-free diagnosis.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.memory.leak.sanitizer'}) SET n += {id: 'rule.memory.leak.sanitizer', name: 'DetectMemoryLeakFromSanitizer', confidenceBase: '0.99', requiresExecution: true, isAutoApplicable: true, description: 'Trust sanitizer or leak instrumentation for memory leak diagnosis.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.function.missing_return.compiler'}) SET n += {id: 'rule.function.missing_return.compiler', name: 'DetectMissingReturnFromCompilerWarning', confidenceBase: '0.98', requiresExecution: false, isAutoApplicable: true, description: 'Detect missing return in non-void function from compiler diagnostic.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.function.missing_return.cfg'}) SET n += {id: 'rule.function.missing_return.cfg', name: 'DetectMissingReturnFromCFG', confidenceBase: '0.86', requiresExecution: false, isAutoApplicable: true, description: 'Detect missing return by finding a control-flow path with no return.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.recursion.no_base_case'}) SET n += {id: 'rule.recursion.no_base_case', name: 'DetectWrongBaseCaseFromMissingBase', confidenceBase: '0.89', requiresExecution: false, isAutoApplicable: true, description: 'Detect recursion bug when no valid base case is present.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.recursion.unreachable_base'}) SET n += {id: 'rule.recursion.unreachable_base', name: 'DetectWrongBaseCaseFromUnreachableBase', confidenceBase: '0.84', requiresExecution: false, isAutoApplicable: true, description: 'Detect recursion bug when base case exists but is unreachable.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.recursion.no_progress'}) SET n += {id: 'rule.recursion.no_progress', name: 'DetectNoRecursiveProgress', confidenceBase: '0.93', requiresExecution: false, isAutoApplicable: true, description: 'Detect recursive non-progress when recursive calls do not reduce problem size.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.iterator.invalidation.modify_then_use'}) SET n += {id: 'rule.iterator.invalidation.modify_then_use', name: 'DetectIteratorInvalidationAfterModification', confidenceBase: '0.94', requiresExecution: false, isAutoApplicable: true, description: 'Detect iterator invalidation caused by modify-then-use pattern.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.iterator.view_lifetime'}) SET n += {id: 'rule.iterator.view_lifetime', name: 'DetectRangeViewLifetimeIssue', confidenceBase: '0.82', requiresExecution: false, isAutoApplicable: true, description: 'Detect view or range lifetime misuse when source outlives assumptions fail.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.move.use_after_move'}) SET n += {id: 'rule.move.use_after_move', name: 'DetectUseAfterMove', confidenceBase: '0.85', requiresExecution: false, isAutoApplicable: true, description: 'Detect invalid dependence on moved-from object state.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.oop.delete_base_no_virtual'}) SET n += {id: 'rule.oop.delete_base_no_virtual', name: 'DetectMissingVirtualDestructor', confidenceBase: '0.96', requiresExecution: false, isAutoApplicable: true, description: 'Detect missing virtual destructor when deleting through base pointer.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.oop.rule_of_five'}) SET n += {id: 'rule.oop.rule_of_five', name: 'DetectRuleOfFiveViolation', confidenceBase: '0.81', requiresExecution: false, isAutoApplicable: true, description: 'Detect a likely Rule of Five violation in a resource-owning type.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.oop.exception_safety'}) SET n += {id: 'rule.oop.exception_safety', name: 'DetectExceptionSafetyViolation', confidenceBase: '0.77', requiresExecution: false, isAutoApplicable: true, description: 'Detect likely exception-safety issue from manual cleanup on exceptional path.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.format.specifier_mismatch'}) SET n += {id: 'rule.format.specifier_mismatch', name: 'DetectFormatSpecifierMismatch', confidenceBase: '0.95', requiresExecution: false, isAutoApplicable: true, description: 'Detect mismatch between formatting specifier and argument type.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.format.modern_cpp_upgrade'}) SET n += {id: 'rule.format.modern_cpp_upgrade', name: 'RecommendTypeSafeFormatting', confidenceBase: '0.64', requiresExecution: false, isAutoApplicable: false, description: 'Recommend upgrading from unsafe formatting to type-safe modern formatting APIs.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.concurrent.wait_protocol'}) SET n += {id: 'rule.concurrent.wait_protocol', name: 'DetectConditionVariableProtocolMisuse', confidenceBase: '0.88', requiresExecution: false, isAutoApplicable: true, description: 'Detect condition variable wait misuse without predicate-based waiting.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.concurrent.missing_sync'}) SET n += {id: 'rule.concurrent.missing_sync', name: 'DetectSharedStateWithoutSynchronization', confidenceBase: '0.76', requiresExecution: false, isAutoApplicable: true, description: 'Detect unsafe shared-state access with insufficient synchronization evidence.', status: 'active'};
MERGE (n:DiagnosticRule {id: 'rule.meta.edge_case_boundary'}) SET n += {id: 'rule.meta.edge_case_boundary', name: 'CrossCheckBoundaryBugFromEdgeCasePattern', confidenceBase: '0.71', requiresExecution: true, isAutoApplicable: true, description: 'Use cross-evidence from edge-case failures to strengthen boundary-related diagnoses.', status: 'active'};

// Diagnostic rule relationships
MATCH (a {id: 'rulecat.loop'}), (b {id: 'rulecat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'rulecat.array'}), (b {id: 'rulecat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'rulecat.pointer'}), (b {id: 'rulecat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'rulecat.function'}), (b {id: 'rulecat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'rulecat.recursion'}), (b {id: 'rulecat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'rulecat.iterator'}), (b {id: 'rulecat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'rulecat.oop'}), (b {id: 'rulecat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'rulecat.io'}), (b {id: 'rulecat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'rulecat.concurrency'}), (b {id: 'rulecat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'rulecat.meta'}), (b {id: 'rulecat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'rulecat.loop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.loop.off_by_one.start_one'}), (b {id: 'rulecat.loop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.loop.infinite.missing_update'}), (b {id: 'rulecat.loop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.loop.infinite.wrong_direction'}), (b {id: 'rulecat.loop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.loop.boundary.edge_case'}), (b {id: 'rulecat.loop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.array.out_of_bounds.size_index'}), (b {id: 'rulecat.array'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.array.index_value_confusion'}), (b {id: 'rulecat.array'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.pointer.null_deref.ast'}), (b {id: 'rulecat.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.pointer.null_deref.clang'}), (b {id: 'rulecat.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.memory.leak.alloc_no_release'}), (b {id: 'rulecat.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.memory.use_after_free.flow'}), (b {id: 'rulecat.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.memory.double_free.flow'}), (b {id: 'rulecat.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.memory.uaf.sanitizer'}), (b {id: 'rulecat.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.memory.leak.sanitizer'}), (b {id: 'rulecat.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.function.missing_return.compiler'}), (b {id: 'rulecat.function'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.function.missing_return.cfg'}), (b {id: 'rulecat.function'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.recursion.no_base_case'}), (b {id: 'rulecat.recursion'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.recursion.unreachable_base'}), (b {id: 'rulecat.recursion'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.recursion.no_progress'}), (b {id: 'rulecat.recursion'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.iterator.invalidation.modify_then_use'}), (b {id: 'rulecat.iterator'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.iterator.view_lifetime'}), (b {id: 'rulecat.iterator'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.move.use_after_move'}), (b {id: 'rulecat.oop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.oop.delete_base_no_virtual'}), (b {id: 'rulecat.oop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.oop.rule_of_five'}), (b {id: 'rulecat.oop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.oop.exception_safety'}), (b {id: 'rulecat.oop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.format.specifier_mismatch'}), (b {id: 'rulecat.io'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.format.modern_cpp_upgrade'}), (b {id: 'rulecat.io'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.concurrent.wait_protocol'}), (b {id: 'rulecat.concurrency'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.concurrent.missing_sync'}), (b {id: 'rulecat.concurrency'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.meta.edge_case_boundary'}), (b {id: 'rulecat.meta'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'bug.off_by_one'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'bug.array_out_of_bounds'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.loop.off_by_one.start_one'}), (b {id: 'bug.off_by_one'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.loop.off_by_one.start_one'}), (b {id: 'bug.index_value_confusion'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.loop.infinite.missing_update'}), (b {id: 'bug.infinite_loop'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.loop.infinite.missing_update'}), (b {id: 'bug.missing_loop_update'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.loop.infinite.wrong_direction'}), (b {id: 'bug.infinite_loop'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.loop.boundary.edge_case'}), (b {id: 'bug.off_by_one'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.loop.boundary.edge_case'}), (b {id: 'bug.wrong_loop_condition'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.array.out_of_bounds.size_index'}), (b {id: 'bug.array_out_of_bounds'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.array.out_of_bounds.size_index'}), (b {id: 'bug.vector_out_of_range'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.array.index_value_confusion'}), (b {id: 'bug.index_value_confusion'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.pointer.null_deref.ast'}), (b {id: 'bug.null_dereference'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.pointer.null_deref.clang'}), (b {id: 'bug.null_dereference'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.memory.leak.alloc_no_release'}), (b {id: 'bug.memory_leak'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.memory.use_after_free.flow'}), (b {id: 'bug.use_after_free'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.memory.use_after_free.flow'}), (b {id: 'bug.dangling_pointer'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.memory.double_free.flow'}), (b {id: 'bug.double_free'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.memory.uaf.sanitizer'}), (b {id: 'bug.use_after_free'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.memory.leak.sanitizer'}), (b {id: 'bug.memory_leak'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.function.missing_return.compiler'}), (b {id: 'bug.missing_return'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.function.missing_return.cfg'}), (b {id: 'bug.missing_return'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.recursion.no_base_case'}), (b {id: 'bug.wrong_base_case'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.recursion.unreachable_base'}), (b {id: 'bug.wrong_base_case'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.recursion.no_progress'}), (b {id: 'bug.no_recursive_progress'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.iterator.invalidation.modify_then_use'}), (b {id: 'bug.iterator_invalidation'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.iterator.invalidation.modify_then_use'}), (b {id: 'bug.vector_out_of_range'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.iterator.view_lifetime'}), (b {id: 'bug.iterator_invalidation'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.move.use_after_move'}), (b {id: 'bug.use_after_move'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.oop.delete_base_no_virtual'}), (b {id: 'bug.missing_virtual_destructor'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.oop.rule_of_five'}), (b {id: 'bug.rule_of_five'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.oop.exception_safety'}), (b {id: 'bug.exception_safety'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.format.specifier_mismatch'}), (b {id: 'bug.format_specifier_mismatch'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.format.modern_cpp_upgrade'}), (b {id: 'bug.format_specifier_mismatch'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.concurrent.wait_protocol'}), (b {id: 'bug.condition_variable_misuse'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.concurrent.missing_sync'}), (b {id: 'bug.condition_variable_misuse'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.meta.edge_case_boundary'}), (b {id: 'bug.off_by_one'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.meta.edge_case_boundary'}), (b {id: 'bug.array_out_of_bounds'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.meta.edge_case_boundary'}), (b {id: 'bug.wrong_loop_condition'}) MERGE (a)-[r:DETECTS_BUG]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'ev.loop.boundary.le_length'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'ev.loop.test.last_case_only'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.loop.off_by_one.start_one'}), (b {id: 'ev.loop.boundary.starts_one'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.loop.off_by_one.start_one'}), (b {id: 'ev.loop.test.last_case_only'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.loop.infinite.missing_update'}), (b {id: 'ev.loop.progress.no_update'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.loop.infinite.missing_update'}), (b {id: 'ev.loop.timeout'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.loop.infinite.wrong_direction'}), (b {id: 'ev.loop.progress.wrong_direction'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.loop.infinite.wrong_direction'}), (b {id: 'ev.loop.timeout'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.loop.boundary.edge_case'}), (b {id: 'ev.loop.test.last_case_only'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.loop.boundary.edge_case'}), (b {id: 'ev.cross.edge_only_failure'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.array.out_of_bounds.size_index'}), (b {id: 'ev.array.index.size_access'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.array.out_of_bounds.size_index'}), (b {id: 'ev.array.bounds.crash'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.array.index_value_confusion'}), (b {id: 'ev.array.index.value_misuse'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.pointer.null_deref.ast'}), (b {id: 'ev.pointer.null_check_missing'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.pointer.null_deref.clang'}), (b {id: 'ev.pointer.clang_null'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.memory.leak.alloc_no_release'}), (b {id: 'ev.memory.alloc_without_release'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.memory.use_after_free.flow'}), (b {id: 'ev.memory.release_then_use'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.memory.double_free.flow'}), (b {id: 'ev.memory.double_release'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.memory.uaf.sanitizer'}), (b {id: 'ev.memory.sanitizer_uaf'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.memory.leak.sanitizer'}), (b {id: 'ev.memory.sanitizer_leak'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.function.missing_return.compiler'}), (b {id: 'ev.function.warn_nonvoid'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.function.missing_return.cfg'}), (b {id: 'ev.function.path_no_return'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.recursion.no_base_case'}), (b {id: 'ev.recursion.no_base_case'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.recursion.unreachable_base'}), (b {id: 'ev.recursion.base_unreachable'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.recursion.no_progress'}), (b {id: 'ev.recursion.no_progress'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.iterator.invalidation.modify_then_use'}), (b {id: 'ev.iterator.modified_container'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.iterator.invalidation.modify_then_use'}), (b {id: 'ev.iterator.erase_then_use'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.iterator.view_lifetime'}), (b {id: 'ev.iterator.view_lifetime'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.move.use_after_move'}), (b {id: 'ev.move.use_after_move'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.oop.delete_base_no_virtual'}), (b {id: 'ev.oop.delete_base_no_virtual'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.oop.rule_of_five'}), (b {id: 'ev.oop.rule_of_five_partial'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.oop.exception_safety'}), (b {id: 'ev.oop.exception_cleanup'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.format.specifier_mismatch'}), (b {id: 'ev.format.printf_type_mismatch'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.format.modern_cpp_upgrade'}), (b {id: 'ev.format.mixed_print_api'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.concurrent.wait_protocol'}), (b {id: 'ev.concurrent.wait_without_predicate'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.concurrent.missing_sync'}), (b {id: 'ev.concurrent.notify_without_lock_protocol'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.concurrent.missing_sync'}), (b {id: 'ev.concurrent.thread_shared_state_no_sync'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.meta.edge_case_boundary'}), (b {id: 'ev.cross.edge_only_failure'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.meta.edge_case_boundary'}), (b {id: 'ev.loop.test.last_case_only'}) MERGE (a)-[r:USES_EVIDENCE]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'tool.ast'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'tool.unittest'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.loop.off_by_one.start_one'}), (b {id: 'tool.ast'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.loop.off_by_one.start_one'}), (b {id: 'tool.unittest'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.loop.infinite.missing_update'}), (b {id: 'tool.ast'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.loop.infinite.missing_update'}), (b {id: 'tool.runtime'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.loop.infinite.wrong_direction'}), (b {id: 'tool.ast'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.loop.infinite.wrong_direction'}), (b {id: 'tool.runtime'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.loop.boundary.edge_case'}), (b {id: 'tool.unittest'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.array.out_of_bounds.size_index'}), (b {id: 'tool.ast'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.array.out_of_bounds.size_index'}), (b {id: 'tool.runtime'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.array.index_value_confusion'}), (b {id: 'tool.ast'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.pointer.null_deref.ast'}), (b {id: 'tool.ast'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.pointer.null_deref.clang'}), (b {id: 'tool.clangsa'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.memory.leak.alloc_no_release'}), (b {id: 'tool.dataflow'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.memory.use_after_free.flow'}), (b {id: 'tool.dataflow'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.memory.double_free.flow'}), (b {id: 'tool.dataflow'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.memory.uaf.sanitizer'}), (b {id: 'tool.sanitizer'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.memory.leak.sanitizer'}), (b {id: 'tool.sanitizer'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.function.missing_return.compiler'}), (b {id: 'tool.compiler'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.function.missing_return.cfg'}), (b {id: 'tool.cfg'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.recursion.no_base_case'}), (b {id: 'tool.ast'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.recursion.unreachable_base'}), (b {id: 'tool.cfg'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.recursion.no_progress'}), (b {id: 'tool.ast'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.iterator.invalidation.modify_then_use'}), (b {id: 'tool.dataflow'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.iterator.view_lifetime'}), (b {id: 'tool.dataflow'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.move.use_after_move'}), (b {id: 'tool.dataflow'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.move.use_after_move'}), (b {id: 'tool.style'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.oop.delete_base_no_virtual'}), (b {id: 'tool.ast'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.oop.rule_of_five'}), (b {id: 'tool.ast'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.oop.rule_of_five'}), (b {id: 'tool.style'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.oop.exception_safety'}), (b {id: 'tool.cfg'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.oop.exception_safety'}), (b {id: 'tool.style'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.format.specifier_mismatch'}), (b {id: 'tool.ast'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.format.specifier_mismatch'}), (b {id: 'tool.compiler'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.format.modern_cpp_upgrade'}), (b {id: 'tool.style'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.concurrent.wait_protocol'}), (b {id: 'tool.ast'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.concurrent.missing_sync'}), (b {id: 'tool.dataflow'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.concurrent.missing_sync'}), (b {id: 'tool.runtime'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.meta.edge_case_boundary'}), (b {id: 'tool.unittest'}) MERGE (a)-[r:SUPPORTED_BY_TOOL]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'concept.c.array'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'concept.c.for'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'concept.cpp.range_for'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.off_by_one.start_one'}), (b {id: 'concept.c.array'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.off_by_one.start_one'}), (b {id: 'concept.c.for'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.off_by_one.start_one'}), (b {id: 'concept.cpp.array'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.off_by_one.start_one'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.infinite.missing_update'}), (b {id: 'concept.c.for'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.infinite.missing_update'}), (b {id: 'concept.c.while'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.infinite.missing_update'}), (b {id: 'concept.cpp.for'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.infinite.missing_update'}), (b {id: 'concept.cpp.while'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.infinite.wrong_direction'}), (b {id: 'concept.c.for'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.infinite.wrong_direction'}), (b {id: 'concept.cpp.for'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.boundary.edge_case'}), (b {id: 'concept.c.array'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.boundary.edge_case'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.boundary.edge_case'}), (b {id: 'concept.cpp.range_for'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.array.out_of_bounds.size_index'}), (b {id: 'concept.c.array'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.array.out_of_bounds.size_index'}), (b {id: 'concept.cpp.array'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.array.out_of_bounds.size_index'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.array.index_value_confusion'}), (b {id: 'concept.c.array'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.array.index_value_confusion'}), (b {id: 'concept.cpp.array'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.array.index_value_confusion'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.pointer.null_deref.ast'}), (b {id: 'concept.c.pointer'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.pointer.null_deref.ast'}), (b {id: 'concept.cpp.pointer'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.pointer.null_deref.ast'}), (b {id: 'concept.cpp.smart_pointer'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.pointer.null_deref.clang'}), (b {id: 'concept.c.pointer'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.pointer.null_deref.clang'}), (b {id: 'concept.cpp.pointer'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.leak.alloc_no_release'}), (b {id: 'concept.c.malloc'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.leak.alloc_no_release'}), (b {id: 'concept.c.calloc'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.leak.alloc_no_release'}), (b {id: 'concept.c.realloc'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.leak.alloc_no_release'}), (b {id: 'concept.cpp.new_delete'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.leak.alloc_no_release'}), (b {id: 'concept.cpp.raii'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.use_after_free.flow'}), (b {id: 'concept.c.free'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.use_after_free.flow'}), (b {id: 'concept.cpp.new_delete'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.use_after_free.flow'}), (b {id: 'concept.c.pointer'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.use_after_free.flow'}), (b {id: 'concept.cpp.pointer'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.double_free.flow'}), (b {id: 'concept.c.free'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.double_free.flow'}), (b {id: 'concept.cpp.new_delete'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.double_free.flow'}), (b {id: 'concept.cpp.smart_pointer'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.uaf.sanitizer'}), (b {id: 'concept.c.pointer'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.uaf.sanitizer'}), (b {id: 'concept.cpp.pointer'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.leak.sanitizer'}), (b {id: 'concept.c.malloc'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.memory.leak.sanitizer'}), (b {id: 'concept.cpp.new_delete'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.function.missing_return.compiler'}), (b {id: 'concept.c.function_def'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.function.missing_return.compiler'}), (b {id: 'concept.cpp.function_decl'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.function.missing_return.cfg'}), (b {id: 'concept.c.function_def'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.function.missing_return.cfg'}), (b {id: 'concept.cpp.function_decl'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.recursion.no_base_case'}), (b {id: 'concept.c.function_def'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.recursion.no_base_case'}), (b {id: 'concept.cpp.function_decl'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.recursion.unreachable_base'}), (b {id: 'concept.c.function_def'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.recursion.unreachable_base'}), (b {id: 'concept.cpp.function_decl'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.recursion.no_progress'}), (b {id: 'concept.c.function_def'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.recursion.no_progress'}), (b {id: 'concept.cpp.function_decl'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.iterator.invalidation.modify_then_use'}), (b {id: 'concept.cpp.iterator'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.iterator.invalidation.modify_then_use'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.iterator.invalidation.modify_then_use'}), (b {id: 'concept.cpp.map'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.iterator.invalidation.modify_then_use'}), (b {id: 'concept.cpp.unordered_map'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.iterator.view_lifetime'}), (b {id: 'concept.cpp.ranges'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.iterator.view_lifetime'}), (b {id: 'concept.cpp.views'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.iterator.view_lifetime'}), (b {id: 'concept.cpp.string_view'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.iterator.view_lifetime'}), (b {id: 'concept.cpp.span'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.move.use_after_move'}), (b {id: 'concept.cpp.move_semantics'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.move.use_after_move'}), (b {id: 'concept.cpp.unique_ptr'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.move.use_after_move'}), (b {id: 'concept.cpp.string'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.move.use_after_move'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.oop.delete_base_no_virtual'}), (b {id: 'concept.cpp.class'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.oop.delete_base_no_virtual'}), (b {id: 'concept.cpp.inheritance'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.oop.delete_base_no_virtual'}), (b {id: 'concept.cpp.virtual_function'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.oop.delete_base_no_virtual'}), (b {id: 'concept.cpp.destructor'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.oop.rule_of_five'}), (b {id: 'concept.cpp.class'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.oop.rule_of_five'}), (b {id: 'concept.cpp.destructor'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.oop.rule_of_five'}), (b {id: 'concept.cpp.copy_semantics'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.oop.rule_of_five'}), (b {id: 'concept.cpp.move_semantics'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.oop.rule_of_five'}), (b {id: 'concept.cpp.raii'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.oop.exception_safety'}), (b {id: 'concept.cpp.try_catch'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.oop.exception_safety'}), (b {id: 'concept.cpp.noexcept'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.oop.exception_safety'}), (b {id: 'concept.cpp.raii'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.format.specifier_mismatch'}), (b {id: 'concept.c.formatted_io'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.format.specifier_mismatch'}), (b {id: 'concept.cpp.format'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.format.specifier_mismatch'}), (b {id: 'concept.cpp.print_functions'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.format.modern_cpp_upgrade'}), (b {id: 'concept.cpp.format'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.format.modern_cpp_upgrade'}), (b {id: 'concept.cpp.print_functions'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.concurrent.wait_protocol'}), (b {id: 'concept.cpp.thread'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.concurrent.wait_protocol'}), (b {id: 'concept.cpp.mutex'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.concurrent.wait_protocol'}), (b {id: 'concept.cpp.condition_variable'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.concurrent.missing_sync'}), (b {id: 'concept.cpp.thread'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.concurrent.missing_sync'}), (b {id: 'concept.cpp.mutex'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.concurrent.missing_sync'}), (b {id: 'concept.cpp.atomic'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.meta.edge_case_boundary'}), (b {id: 'concept.c.array'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.meta.edge_case_boundary'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.meta.edge_case_boundary'}), (b {id: 'concept.cpp.range_for'}) MERGE (a)-[r:APPLIES_TO_CONCEPT]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'fix.loop.bound'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'fix.array.bound'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.loop.off_by_one.start_one'}), (b {id: 'fix.loop.bound'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.loop.infinite.missing_update'}), (b {id: 'fix.loop.progress'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.loop.infinite.wrong_direction'}), (b {id: 'fix.loop.progress'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.loop.boundary.edge_case'}), (b {id: 'fix.loop.bound'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.array.out_of_bounds.size_index'}), (b {id: 'fix.array.bound'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.array.index_value_confusion'}), (b {id: 'fix.array.index_value'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.pointer.null_deref.ast'}), (b {id: 'fix.null.check'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.pointer.null_deref.clang'}), (b {id: 'fix.null.check'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.memory.leak.alloc_no_release'}), (b {id: 'fix.release.once'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.memory.leak.alloc_no_release'}), (b {id: 'fix.use_raii'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.memory.leak.alloc_no_release'}), (b {id: 'fix.smart_pointer'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.memory.use_after_free.flow'}), (b {id: 'fix.no_use_after_release'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.memory.use_after_free.flow'}), (b {id: 'fix.smart_pointer'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.memory.double_free.flow'}), (b {id: 'fix.release.once'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.memory.uaf.sanitizer'}), (b {id: 'fix.no_use_after_release'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.memory.leak.sanitizer'}), (b {id: 'fix.release.once'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.function.missing_return.compiler'}), (b {id: 'fix.return'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.function.missing_return.cfg'}), (b {id: 'fix.return'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.recursion.no_base_case'}), (b {id: 'fix.recursion.base'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.recursion.unreachable_base'}), (b {id: 'fix.recursion.base'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.recursion.no_progress'}), (b {id: 'fix.recursion.progress'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.iterator.invalidation.modify_then_use'}), (b {id: 'fix.iterator.refresh'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.iterator.view_lifetime'}), (b {id: 'fix.iterator.refresh'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.move.use_after_move'}), (b {id: 'fix.move.use_state'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.oop.delete_base_no_virtual'}), (b {id: 'fix.virtual_destructor'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.oop.rule_of_five'}), (b {id: 'fix.use_raii'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.oop.rule_of_five'}), (b {id: 'fix.smart_pointer'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.oop.exception_safety'}), (b {id: 'fix.use_raii'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.format.specifier_mismatch'}), (b {id: 'fix.format.match'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.format.modern_cpp_upgrade'}), (b {id: 'fix.format.match'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.concurrent.wait_protocol'}), (b {id: 'fix.condition_wait'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.concurrent.missing_sync'}), (b {id: 'fix.condition_wait'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.meta.edge_case_boundary'}), (b {id: 'fix.array.bound'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.meta.edge_case_boundary'}), (b {id: 'fix.loop.bound'}) MERGE (a)-[r:RECOMMENDS_FIX]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.loop.off_by_one.leq_length'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.loop.off_by_one.start_one'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.loop.off_by_one.start_one'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.loop.infinite.missing_update'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.loop.infinite.missing_update'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.loop.infinite.wrong_direction'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.loop.infinite.wrong_direction'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.loop.boundary.edge_case'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.loop.boundary.edge_case'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.array.out_of_bounds.size_index'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.array.out_of_bounds.size_index'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.array.out_of_bounds.size_index'}), (b {id: 'view.cpp_stl'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.array.index_value_confusion'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.array.index_value_confusion'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.pointer.null_deref.ast'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.pointer.null_deref.clang'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.memory.leak.alloc_no_release'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.memory.leak.alloc_no_release'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.memory.use_after_free.flow'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.memory.double_free.flow'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.memory.uaf.sanitizer'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.memory.leak.sanitizer'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.memory.leak.sanitizer'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.function.missing_return.compiler'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.function.missing_return.cfg'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.recursion.no_base_case'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.recursion.unreachable_base'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.recursion.no_progress'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.iterator.invalidation.modify_then_use'}), (b {id: 'view.cpp_stl'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.iterator.invalidation.modify_then_use'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.iterator.view_lifetime'}), (b {id: 'view.cpp_stl'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.iterator.view_lifetime'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.move.use_after_move'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.oop.delete_base_no_virtual'}), (b {id: 'view.cpp_oop'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.oop.rule_of_five'}), (b {id: 'view.cpp_oop'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.oop.rule_of_five'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.oop.exception_safety'}), (b {id: 'view.cpp_oop'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.oop.exception_safety'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.format.specifier_mismatch'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.format.modern_cpp_upgrade'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.concurrent.wait_protocol'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.concurrent.missing_sync'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'rule.meta.edge_case_boundary'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);"""
SUMMARY_JSON = r"""{
  "node_count": 84,
  "relationship_count": 330,
  "label_breakdown": {
    "RuleCategory": 11,
    "ToolSignature": 9,
    "EvidencePattern": 34,
    "DiagnosticRule": 30
  },
  "relationship_breakdown": {
    "SUBCATEGORY_OF": 10,
    "BELONGS_TO_CATEGORY": 30,
    "DETECTS_BUG": 39,
    "USES_EVIDENCE": 39,
    "SUPPORTED_BY_TOOL": 40,
    "APPLIES_TO_CONCEPT": 92,
    "RECOMMENDS_FIX": 36,
    "VISIBLE_IN": 44
  },
  "external_refs": [
    "bug.array_out_of_bounds",
    "bug.condition_variable_misuse",
    "bug.dangling_pointer",
    "bug.double_free",
    "bug.exception_safety",
    "bug.format_specifier_mismatch",
    "bug.index_value_confusion",
    "bug.infinite_loop",
    "bug.iterator_invalidation",
    "bug.memory_leak",
    "bug.missing_loop_update",
    "bug.missing_return",
    "bug.missing_virtual_destructor",
    "bug.no_recursive_progress",
    "bug.null_dereference",
    "bug.off_by_one",
    "bug.rule_of_five",
    "bug.use_after_free",
    "bug.use_after_move",
    "bug.vector_out_of_range",
    "bug.wrong_base_case",
    "bug.wrong_loop_condition",
    "concept.c.array",
    "concept.c.calloc",
    "concept.c.for",
    "concept.c.formatted_io",
    "concept.c.free",
    "concept.c.function_def",
    "concept.c.malloc",
    "concept.c.pointer",
    "concept.c.realloc",
    "concept.c.while",
    "concept.cpp.array",
    "concept.cpp.atomic",
    "concept.cpp.class",
    "concept.cpp.condition_variable",
    "concept.cpp.copy_semantics",
    "concept.cpp.destructor",
    "concept.cpp.for",
    "concept.cpp.format",
    "concept.cpp.function_decl",
    "concept.cpp.inheritance",
    "concept.cpp.iterator",
    "concept.cpp.map",
    "concept.cpp.move_semantics",
    "concept.cpp.mutex",
    "concept.cpp.new_delete",
    "concept.cpp.noexcept",
    "concept.cpp.pointer",
    "concept.cpp.print_functions",
    "concept.cpp.raii",
    "concept.cpp.range_for",
    "concept.cpp.ranges",
    "concept.cpp.smart_pointer",
    "concept.cpp.span",
    "concept.cpp.string",
    "concept.cpp.string_view",
    "concept.cpp.thread",
    "concept.cpp.try_catch",
    "concept.cpp.unique_ptr",
    "concept.cpp.unordered_map",
    "concept.cpp.vector",
    "concept.cpp.views",
    "concept.cpp.virtual_function",
    "concept.cpp.while",
    "fix.array.bound",
    "fix.array.index_value",
    "fix.condition_wait",
    "fix.format.match",
    "fix.iterator.refresh",
    "fix.loop.bound",
    "fix.loop.progress",
    "fix.move.use_state",
    "fix.no_use_after_release",
    "fix.null.check",
    "fix.recursion.base",
    "fix.recursion.progress",
    "fix.release.once",
    "fix.return",
    "fix.smart_pointer",
    "fix.use_raii",
    "fix.virtual_destructor",
    "view.algorithms",
    "view.c_pointers",
    "view.cpp_modern",
    "view.cpp_oop",
    "view.cpp_stl",
    "view.intro_c"
  ],
  "files": [
    "neo4j_diagnostic_rules_nodes.csv",
    "neo4j_diagnostic_rules_relationships.csv",
    "neo4j_diagnostic_rules_seed.cypher",
    "build_neo4j_diagnostic_rules_dataset.py"
  ]
}"""


def main() -> None:
    out_dir = Path('.')
    (out_dir / 'neo4j_diagnostic_rules_nodes.csv').write_text(NODES_CSV, encoding='utf-8')
    (out_dir / 'neo4j_diagnostic_rules_relationships.csv').write_text(RELATIONSHIPS_CSV, encoding='utf-8')
    (out_dir / 'neo4j_diagnostic_rules_seed.cypher').write_text(SEED_CYPHER, encoding='utf-8')
    (out_dir / 'neo4j_diagnostic_rules_summary.json').write_text(SUMMARY_JSON, encoding='utf-8')
    print('Diagnostic rules dataset files created successfully.')


if __name__ == '__main__':
    main()
