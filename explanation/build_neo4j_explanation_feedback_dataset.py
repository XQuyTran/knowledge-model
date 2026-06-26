"""Recreate the Neo4j Explanation / Feedback Ontology dataset.

Outputs:
- neo4j_explanation_feedback_nodes.csv
- neo4j_explanation_feedback_relationships.csv
- neo4j_explanation_feedback_seed.cypher
- neo4j_explanation_feedback_summary.json
"""

from pathlib import Path

NODES_CSV = r"""anchorType,description,difficultyBand,explanationMode,id,label,language,level,maxHintDepth,name,patternType,planType,status,stepKind,stepOrder,text,toneLevel
,Root category for explanation and feedback templates,,,explcat.root,ExplanationCategory,,top,,ExplanationRoot,,,active,,,,
,Feedback templates for loop-related bugs,,,explcat.loop,ExplanationCategory,,top,,LoopFeedback,,,active,,,,
,"Feedback templates for arrays, indexing, and boundaries",,,explcat.array,ExplanationCategory,,top,,ArrayAndBoundaryFeedback,,,active,,,,
,Feedback templates for pointer and memory lifetime issues,,,explcat.pointer,ExplanationCategory,,top,,PointerAndMemoryFeedback,,,active,,,,
,Feedback templates for function return and contract violations,,,explcat.function,ExplanationCategory,,top,,FunctionContractFeedback,,,active,,,,
,Feedback templates for base case and recursive progress issues,,,explcat.recursion,ExplanationCategory,,top,,RecursionFeedback,,,active,,,,
,"Feedback templates for iterators, views, and invalidation",,,explcat.iterator,ExplanationCategory,,top,,IteratorAndRangeFeedback,,,active,,,,
,"Feedback templates for OOP lifetime, move, and exception safety",,,explcat.oop,ExplanationCategory,,top,,OOPAndLifetimeFeedback,,,active,,,,
,Feedback templates for formatting and API misuse,,,explcat.io,ExplanationCategory,,top,,IOFormattingFeedback,,,active,,,,
,Feedback templates for synchronization and waiting protocols,,,explcat.concurrent,ExplanationCategory,,top,,ConcurrencyFeedback,,,active,,,,
,Point to the likely code region and describe what is suspicious there.,,,fbp.locate_issue,FeedbackPattern,,,,LocateIssueInStudentCode,diagnostic,,active,,,,
,Restate the key programming rule in plain language.,,,fbp.restate_rule,FeedbackPattern,,,,RestateCoreRule,conceptual,,active,,,,
,Provide a minimal counterexample showing why the student logic fails.,,,fbp.counter_example,FeedbackPattern,,,,CounterExample,illustrative,,active,,,,
,Walk through one concrete execution trace or edge case.,,,fbp.trace_execution,FeedbackPattern,,,,TraceExecutionNarration,dynamic,,active,,,,
,Contrast the current code behavior with the corrected version.,,,fbp.compare_fix,FeedbackPattern,,,,CompareCurrentAndFixedLogic,repair,,active,,,,
,Recommend a modern safer alternative such as RAII or std::format.,,,fbp.modern_recommendation,FeedbackPattern,,,,ModernPracticeRecommendation,best-practice,,active,,,,
,Start with mild hints and become increasingly explicit only if needed.,,,fbp.hint_escalation,FeedbackPattern,,,,HintEscalation,pedagogical,,active,,,,
,Suggest next concepts or exercises for strengthening the weak area.,,,fbp.remediation_path,FeedbackPattern,,,,RemediationPath,pedagogical,,active,,,,
source-location,Anchor explanation to a specific line or range of lines.,,,ctx.line,ContextAnchorType,,,,LineNumberAnchor,,,active,,,,
syntax,"Anchor explanation to a concrete condition, expression, or statement.",,,ctx.expression,ContextAnchorType,,,,ExpressionAnchor,,,active,,,,
state,Anchor explanation to a variable whose value or lifetime is central.,,,ctx.variable,ContextAnchorType,,,,VariableAnchor,,,active,,,,
test,Anchor explanation to a failing boundary or counterexample test.,,,ctx.testcase,ContextAnchorType,,,,TestCaseAnchor,,,active,,,,
diagnostic,Anchor explanation to a compiler or analyzer finding.,,,ctx.finding,ContextAnchorType,,,,AnalyzerFindingAnchor,,,active,,,,
dynamic,Anchor explanation to a sequence of runtime states or steps.,,,ctx.trace,ContextAnchorType,,,,ExecutionTraceAnchor,,,active,,,,
,Revisit strict versus non-strict inequalities and zero-based iteration.,basic-intermediate,,plan.loop_boundary,RemediationPlan,,,,ReviewLoopBoundaryReasoning,,concept-remediation,active,,,,
,Practice indexing rules and traversal over fixed and dynamic sequences.,basic-intermediate,,plan.array_indexing,RemediationPlan,,,,ReviewArrayIndexingAndTraversal,,concept-remediation,active,,,,
,"Review pointer validity, ownership, free/delete semantics, and lifetime boundaries.",intermediate-advanced,,plan.pointer_lifetime,RemediationPlan,,,,ReviewPointerValidityAndLifetime,,concept-remediation,active,,,,
,Practice allocate-use-release reasoning and matching ownership operations.,intermediate-advanced,,plan.manual_memory,RemediationPlan,,,,ReviewManualMemoryLifecycle,,concept-remediation,active,,,,
,Reinforce the idea that every non-void path must produce a value.,basic,,plan.return_contract,RemediationPlan,,,,ReviewFunctionReturnContracts,,concept-remediation,active,,,,
,Train on defining precise base cases and shrinking recursive state.,intermediate,,plan.recursion,RemediationPlan,,,,ReviewRecursiveBaseCaseAndProgress,,concept-remediation,active,,,,
,"Study invalidation rules, view lifetimes, and non-owning range semantics.",advanced,,plan.iterator_range,RemediationPlan,,,,ReviewIteratorInvalidationAndRangeLifetimes,,concept-remediation,active,,,,
,"Study single ownership, shared ownership, moved-from states, and RAII design.",advanced,,plan.modern_cpp_ownership,RemediationPlan,,,,ReviewRAIIAndOwnershipModels,,concept-remediation,active,,,,
,"Review virtual destructors, base pointers, and polymorphic object cleanup.",advanced,,plan.oop_destruction,RemediationPlan,,,,ReviewPolymorphicDestruction,,concept-remediation,active,,,,
,Study strong/basic/no-throw guarantees and exception-safe cleanup design.,advanced,,plan.exception_safety,RemediationPlan,,,,ReviewExceptionSafetyAndCleanup,,concept-remediation,active,,,,
,Practice matching types to format specifiers and prefer type-safe formatting APIs.,basic-intermediate,,plan.formatting,RemediationPlan,,,,ReviewFormattingAndTypeSafeOutput,,concept-remediation,active,,,,
,"Study locking discipline, predicate waits, and shared-state synchronization.",advanced,,plan.concurrency_wait,RemediationPlan,,,,ReviewSynchronizationAndConditionProtocols,,concept-remediation,active,,,,
,Explain why a boundary that is one too small or too large breaks traversal logic.,,step-by-step,expl.off_by_one,ExplanationTemplate,en,,3,ExplainOffByOneBoundaryBug,,,active,,,,novice
,,,,expl.off_by_one.step1,ExplanationStep,en,,,LocateBoundaryCondition,,,active,locate,1,Point to the loop condition or index access that determines the last iteration.,
,,,,expl.off_by_one.step2,ExplanationStep,en,,,RestateValidIndexRange,,,active,concept,2,Explain that a sequence of length n is normally indexed from 0 to n-1.,
,,,,expl.off_by_one.step3,ExplanationStep,en,,,WalkEdgeCaseAndPatch,,,active,repair,3,Walk through the boundary test case and show the corrected strict or non-strict condition.,
,Explain why the loop never reaches its exit condition and how to restore progress.,,step-by-step,expl.infinite_loop,ExplanationTemplate,en,,3,ExplainInfiniteLoop,,,active,,,,novice
,,,,expl.infinite_loop.step1,ExplanationStep,en,,,FindProgressVariable,,,active,locate,1,Identify the variable or state that should move toward loop termination.,
,,,,expl.infinite_loop.step2,ExplanationStep,en,,,ShowWhyExitIsNeverReached,,,active,concept,2,Show that the condition stays true forever or moves in the wrong direction.,
,,,,expl.infinite_loop.step3,ExplanationStep,en,,,RepairUpdateOrCondition,,,active,repair,3,Adjust the update or condition so each iteration moves toward termination.,
,Explain why the current index can exceed valid sequence bounds.,,step-by-step,expl.array_out_of_bounds,ExplanationTemplate,en,,3,ExplainArrayOutOfBounds,,,active,,,,novice
,,,,expl.array_out_of_bounds.step1,ExplanationStep,en,,,IdentifyUnsafeIndex,,,active,locate,1,Point to the index expression that can become equal to or larger than the container length.,
,,,,expl.array_out_of_bounds.step2,ExplanationStep,en,,,RunBoundaryCounterExample,,,active,concept,2,Use the smallest failing boundary case to show the invalid access.,
,,,,expl.array_out_of_bounds.step3,ExplanationStep,en,,,ConstrainIndexRange,,,active,repair,3,Rewrite the logic so every access stays within valid bounds.,
,Explain the difference between index positions and the values stored at those positions.,,guided-hint,expl.index_value_confusion,ExplanationTemplate,en,,2,ExplainIndexValueConfusion,,,active,,,,novice
,,,,expl.index_value_confusion.step1,ExplanationStep,en,,,SeparateRoles,,,active,concept,1,Separate the variable representing the position from the value stored at that position.,
,,,,expl.index_value_confusion.step2,ExplanationStep,en,,,ShowCurrentMixUp,,,active,locate,2,Highlight where the code uses a value as if it were an index or vice versa.,
,,,,expl.index_value_confusion.step3,ExplanationStep,en,,,RefactorRoles,,,active,repair,3,Rename or restructure the variables so the two roles are not confused.,
,Explain why a nullable or invalid pointer must not be dereferenced without proof of validity.,,step-by-step,expl.null_dereference,ExplanationTemplate,en,,3,ExplainNullDereference,,,active,,,,intermediate
,,,,expl.null_dereference.step1,ExplanationStep,en,,,ShowUnsafeDereference,,,active,locate,1,Point to the dereference site and the missing validity guarantee.,
,,,,expl.null_dereference.step2,ExplanationStep,en,,,ExplainValidityRequirement,,,active,concept,2,Explain that dereference is only safe when the pointer definitely refers to a live object.,
,,,,expl.null_dereference.step3,ExplanationStep,en,,,GuardOrRedesignOwnership,,,active,repair,3,Add a guard or redesign the ownership model to make invalid states impossible.,
,Explain how allocation creates ownership obligations and why missing release causes leaks.,,step-by-step,expl.memory_leak,ExplanationTemplate,en,,3,ExplainMemoryLeak,,,active,,,,intermediate
,,,,expl.memory_leak.step1,ExplanationStep,en,,,LocateAllocationOwnership,,,active,locate,1,Point to the allocation site and ask who is responsible for releasing it.,
,,,,expl.memory_leak.step2,ExplanationStep,en,,,ShowMissingReleasePath,,,active,concept,2,Show the path where the resource is never released or returned safely.,
,,,,expl.memory_leak.step3,ExplanationStep,en,,,IntroduceLifecycleFix,,,active,repair,3,Add the missing release or replace manual ownership with RAII/smart pointers.,
,Explain why a handle becomes invalid immediately after its resource is released.,,step-by-step,expl.use_after_free,ExplanationTemplate,en,,3,ExplainUseAfterFree,,,active,,,,intermediate
,,,,expl.use_after_free.step1,ExplanationStep,en,,,TraceReleaseThenUse,,,active,locate,1,Trace the point where the resource is released and the later point where it is still used.,
,,,,expl.use_after_free.step2,ExplanationStep,en,,,ExplainEndedLifetime,,,active,concept,2,Explain that releasing the underlying storage ends the object lifetime for that handle.,
,,,,expl.use_after_free.step3,ExplanationStep,en,,,InvalidateOrTransferOwnership,,,active,repair,3,Stop using the handle after release or replace manual lifetime management with safer ownership.,
,Explain why the same resource must be released exactly once.,,step-by-step,expl.double_free,ExplanationTemplate,en,,3,ExplainDoubleFree,,,active,,,,intermediate
,,,,expl.double_free.step1,ExplanationStep,en,,,FindDuplicateReleasePath,,,active,locate,1,Locate the two paths that release the same resource.,
,,,,expl.double_free.step2,ExplanationStep,en,,,ExplainSingleOwnershipRule,,,active,concept,2,Explain that one owned resource must have one final release operation.,
,,,,expl.double_free.step3,ExplanationStep,en,,,RestructureOwnership,,,active,repair,3,Make ownership unique or centralize release so it happens only once.,
,Explain why reading a variable before valid initialization leads to unstable behavior.,,guided-hint,expl.uninitialized_value,ExplanationTemplate,en,,2,ExplainUninitializedValueUse,,,active,,,,novice
,,,,expl.uninitialized_value.step1,ExplanationStep,en,,,FindFirstRead,,,active,locate,1,Find the first read of the variable before any guaranteed assignment.,
,,,,expl.uninitialized_value.step2,ExplanationStep,en,,,ExplainInitializationRequirement,,,active,concept,2,Explain that a variable must be initialized before its value is used.,
,,,,expl.uninitialized_value.step3,ExplanationStep,en,,,InitializeBeforeUse,,,active,repair,3,Introduce an explicit meaningful initialization before the first read.,
,Explain that every non-void function path must return a valid value.,,guided-hint,expl.missing_return,ExplanationTemplate,en,,2,ExplainMissingReturnValue,,,active,,,,novice
,,,,expl.missing_return.step1,ExplanationStep,en,,,LocateMissingPath,,,active,locate,1,Locate the control-flow path that ends without returning a value.,
,,,,expl.missing_return.step2,ExplanationStep,en,,,ExplainContract,,,active,concept,2,Explain the contract of a non-void function: every path must produce a result.,
,,,,expl.missing_return.step3,ExplanationStep,en,,,AddReturnToAllPaths,,,active,repair,3,Make every branch return a valid value or redesign the function signature.,
,Explain that recursion needs a reachable stopping condition that matches the smallest solvable case.,,step-by-step,expl.wrong_base_case,ExplanationTemplate,en,,3,ExplainWrongRecursiveBaseCase,,,active,,,,intermediate
,,,,expl.wrong_base_case.step1,ExplanationStep,en,,,LocateBaseCaseCondition,,,active,locate,1,Highlight the stopping condition and check whether it can actually be reached.,
,,,,expl.wrong_base_case.step2,ExplanationStep,en,,,ShowFailingInput,,,active,concept,2,Run a small input where the recursion should stop but does not stop correctly.,
,,,,expl.wrong_base_case.step3,ExplanationStep,en,,,DefineReachableBaseCase,,,active,repair,3,Rewrite the stopping condition so the smallest case terminates correctly.,
,Explain why recursive calls must reduce the problem size toward the base case.,,step-by-step,expl.no_recursive_progress,ExplanationTemplate,en,,3,ExplainNoRecursiveProgress,,,active,,,,intermediate
,,,,expl.no_recursive_progress.step1,ExplanationStep,en,,,LocateRecursiveArgument,,,active,locate,1,Find the argument or state passed into the recursive call.,
,,,,expl.no_recursive_progress.step2,ExplanationStep,en,,,ShowLackOfReduction,,,active,concept,2,Show that the recursive input does not become simpler or smaller.,
,,,,expl.no_recursive_progress.step3,ExplanationStep,en,,,MakeProgressExplicit,,,active,repair,3,Change the recursive call so it moves toward the base case on every step.,
,"Explain why some container operations invalidate iterators, references, or views.",,step-by-step,expl.iterator_invalidation,ExplanationTemplate,en,,3,ExplainIteratorInvalidation,,,active,,,,advanced
,,,,expl.iterator_invalidation.step1,ExplanationStep,en,,,LocateModificationAndUse,,,active,locate,1,Locate the container modification and the later iterator or view use.,
,,,,expl.iterator_invalidation.step2,ExplanationStep,en,,,ExplainInvalidationRule,,,active,concept,2,Explain that some operations reallocate or erase elements and invalidate observers.,
,,,,expl.iterator_invalidation.step3,ExplanationStep,en,,,RefreshIteratorsOrChangePattern,,,active,repair,3,Reacquire iterators after modification or change to a safer traversal pattern.,
,Explain the valid but unspecified state of moved-from objects and how to use them safely.,,step-by-step,expl.use_after_move,ExplanationTemplate,en,,3,ExplainUseAfterMove,,,active,,,,advanced
,,,,expl.use_after_move.step1,ExplanationStep,en,,,LocateMoveAndLaterRead,,,active,locate,1,Locate the move operation and the subsequent read that assumes the old value is still there.,
,,,,expl.use_after_move.step2,ExplanationStep,en,,,ExplainMovedFromState,,,active,concept,2,Explain that moved-from objects remain valid but their value is not the old owned resource.,
,,,,expl.use_after_move.step3,ExplanationStep,en,,,ReinitializeOrAvoidDependence,,,active,repair,3,Reinitialize the object or avoid reading semantic value after the move.,
,Explain why deleting a derived object through a base pointer requires a virtual base destructor.,,step-by-step,expl.missing_virtual_destructor,ExplanationTemplate,en,,3,ExplainMissingVirtualDestructor,,,active,,,,advanced
,,,,expl.missing_virtual_destructor.step1,ExplanationStep,en,,,LocateDeleteThroughBase,,,active,locate,1,Locate the delete operation performed through a base-class pointer or reference-like owner.,
,,,,expl.missing_virtual_destructor.step2,ExplanationStep,en,,,ExplainPolymorphicDestructionRule,,,active,concept,2,Explain that the base destructor must be virtual for derived cleanup to run correctly.,
,,,,expl.missing_virtual_destructor.step3,ExplanationStep,en,,,AddVirtualDestructor,,,active,repair,3,Declare the base destructor virtual and verify derived cleanup now happens safely.,
,Explain why a resource-owning class must define consistent special member behavior or delegate ownership to RAII types.,,step-by-step,expl.rule_of_five,ExplanationTemplate,en,,4,ExplainRuleOfFiveViolation,,,active,,,,advanced
,,,,expl.rule_of_five.step1,ExplanationStep,en,,,IdentifyOwnedResourceClass,,,active,locate,1,Identify the class that manually manages a resource such as dynamic memory or a handle.,
,,,,expl.rule_of_five.step2,ExplanationStep,en,,,ExplainSpecialMemberConsistency,,,active,concept,2,"Explain why copy, move, destruction, and assignment must agree on ownership semantics.",
,,,,expl.rule_of_five.step3,ExplanationStep,en,,,PreferRAIIOrCompleteSpecialMembers,,,active,repair,3,Prefer composing RAII types or define the needed special members consistently.,
,Explain how exceptions can bypass manual cleanup and break invariants when ownership is not exception-safe.,,step-by-step,expl.exception_safety,ExplanationTemplate,en,,4,ExplainExceptionSafetyViolation,,,active,,,,advanced
,,,,expl.exception_safety.step1,ExplanationStep,en,,,LocateExceptionalPath,,,active,locate,1,Locate the operation that can throw and the cleanup that may be skipped.,
,,,,expl.exception_safety.step2,ExplanationStep,en,,,ExplainInvariantAndCleanupRisk,,,active,concept,2,Explain what resource or invariant becomes inconsistent if an exception interrupts the path.,
,,,,expl.exception_safety.step3,ExplanationStep,en,,,AdoptRAIIBoundaries,,,active,repair,3,Move resource cleanup into RAII objects so normal and exceptional exits behave the same.,
,Explain that formatting placeholders and argument types must agree.,,guided-hint,expl.format_specifier,ExplanationTemplate,en,,2,ExplainFormatSpecifierMismatch,,,active,,,,novice
,,,,expl.format_specifier.step1,ExplanationStep,en,,,LocateFormatMismatch,,,active,locate,1,Point to the formatting call where placeholder and argument type disagree.,
,,,,expl.format_specifier.step2,ExplanationStep,en,,,ExplainTypeAgreementRule,,,active,concept,2,Explain that formatting APIs interpret arguments according to the placeholder contract.,
,,,,expl.format_specifier.step3,ExplanationStep,en,,,CorrectSpecifierOrUpgradeAPI,,,active,repair,3,Choose the correct specifier or use a type-safe formatting API when available.,
,Explain the correct waiting protocol for condition variables and shared state synchronization.,,step-by-step,expl.condition_variable,ExplanationTemplate,en,,4,ExplainConditionVariableMisuse,,,active,,,,advanced
,,,,expl.condition_variable.step1,ExplanationStep,en,,,LocateWaitNotifyProtocol,,,active,locate,1,"Locate the shared state, the lock, and the wait/notify operations.",
,,,,expl.condition_variable.step2,ExplanationStep,en,,,ExplainPredicateWaitRule,,,active,concept,2,Explain that waiting should re-check the predicate while holding the correct lock.,
,,,,expl.condition_variable.step3,ExplanationStep,en,,,RepairSynchronizationProtocol,,,active,repair,3,Protect the shared state consistently and rewrite waiting as a predicate loop.,
"""
RELATIONSHIPS_CSV = r"""end_id,start_id,type
explcat.root,explcat.loop,SUBCATEGORY_OF
explcat.root,explcat.array,SUBCATEGORY_OF
explcat.root,explcat.pointer,SUBCATEGORY_OF
explcat.root,explcat.function,SUBCATEGORY_OF
explcat.root,explcat.recursion,SUBCATEGORY_OF
explcat.root,explcat.iterator,SUBCATEGORY_OF
explcat.root,explcat.oop,SUBCATEGORY_OF
explcat.root,explcat.io,SUBCATEGORY_OF
explcat.root,explcat.concurrent,SUBCATEGORY_OF
explcat.array,expl.off_by_one,BELONGS_TO_CATEGORY
bug.off_by_one,expl.off_by_one,EXPLAINS_BUG
rule.loop.off_by_one.leq_length,expl.off_by_one,TRIGGERED_BY_RULE
rule.loop.off_by_one.start_one,expl.off_by_one,TRIGGERED_BY_RULE
rule.meta.edge_case_boundary,expl.off_by_one,TRIGGERED_BY_RULE
mis.loop.bound,expl.off_by_one,TARGETS_MISCONCEPTION
mis.array.last_index,expl.off_by_one,TARGETS_MISCONCEPTION
fix.loop.bound,expl.off_by_one,SUGGESTS_FIX
fix.array.bound,expl.off_by_one,SUGGESTS_FIX
concept.c.array,expl.off_by_one,REINFORCES_CONCEPT
concept.c.for,expl.off_by_one,REINFORCES_CONCEPT
concept.cpp.vector,expl.off_by_one,REINFORCES_CONCEPT
concept.cpp.range_for,expl.off_by_one,REINFORCES_CONCEPT
view.intro_c,expl.off_by_one,VISIBLE_IN
view.algorithms,expl.off_by_one,VISIBLE_IN
view.cpp_stl,expl.off_by_one,VISIBLE_IN
fbp.locate_issue,expl.off_by_one,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.off_by_one,USES_FEEDBACK_PATTERN
fbp.trace_execution,expl.off_by_one,USES_FEEDBACK_PATTERN
fbp.compare_fix,expl.off_by_one,USES_FEEDBACK_PATTERN
fbp.remediation_path,expl.off_by_one,USES_FEEDBACK_PATTERN
ctx.line,expl.off_by_one,USES_CONTEXT_ANCHOR
ctx.expression,expl.off_by_one,USES_CONTEXT_ANCHOR
ctx.testcase,expl.off_by_one,USES_CONTEXT_ANCHOR
plan.loop_boundary,expl.off_by_one,RECOMMENDS_PLAN
expl.off_by_one.step1,expl.off_by_one,CONSISTS_OF_STEP
expl.off_by_one.step2,expl.off_by_one,CONSISTS_OF_STEP
expl.off_by_one.step3,expl.off_by_one,CONSISTS_OF_STEP
explcat.loop,expl.infinite_loop,BELONGS_TO_CATEGORY
bug.infinite_loop,expl.infinite_loop,EXPLAINS_BUG
bug.missing_loop_update,expl.infinite_loop,EXPLAINS_BUG
bug.wrong_loop_condition,expl.infinite_loop,EXPLAINS_BUG
rule.loop.infinite.missing_update,expl.infinite_loop,TRIGGERED_BY_RULE
rule.loop.infinite.wrong_direction,expl.infinite_loop,TRIGGERED_BY_RULE
mis.loop.progress,expl.infinite_loop,TARGETS_MISCONCEPTION
fix.loop.progress,expl.infinite_loop,SUGGESTS_FIX
fix.loop.bound,expl.infinite_loop,SUGGESTS_FIX
concept.c.for,expl.infinite_loop,REINFORCES_CONCEPT
concept.c.while,expl.infinite_loop,REINFORCES_CONCEPT
concept.cpp.for,expl.infinite_loop,REINFORCES_CONCEPT
concept.cpp.while,expl.infinite_loop,REINFORCES_CONCEPT
view.intro_c,expl.infinite_loop,VISIBLE_IN
view.algorithms,expl.infinite_loop,VISIBLE_IN
fbp.locate_issue,expl.infinite_loop,USES_FEEDBACK_PATTERN
fbp.trace_execution,expl.infinite_loop,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.infinite_loop,USES_FEEDBACK_PATTERN
fbp.compare_fix,expl.infinite_loop,USES_FEEDBACK_PATTERN
ctx.line,expl.infinite_loop,USES_CONTEXT_ANCHOR
ctx.variable,expl.infinite_loop,USES_CONTEXT_ANCHOR
ctx.trace,expl.infinite_loop,USES_CONTEXT_ANCHOR
plan.loop_boundary,expl.infinite_loop,RECOMMENDS_PLAN
expl.infinite_loop.step1,expl.infinite_loop,CONSISTS_OF_STEP
expl.infinite_loop.step2,expl.infinite_loop,CONSISTS_OF_STEP
expl.infinite_loop.step3,expl.infinite_loop,CONSISTS_OF_STEP
explcat.array,expl.array_out_of_bounds,BELONGS_TO_CATEGORY
bug.array_out_of_bounds,expl.array_out_of_bounds,EXPLAINS_BUG
bug.vector_out_of_range,expl.array_out_of_bounds,EXPLAINS_BUG
rule.array.out_of_bounds.size_index,expl.array_out_of_bounds,TRIGGERED_BY_RULE
mis.array.last_index,expl.array_out_of_bounds,TARGETS_MISCONCEPTION
fix.array.bound,expl.array_out_of_bounds,SUGGESTS_FIX
concept.c.array,expl.array_out_of_bounds,REINFORCES_CONCEPT
concept.cpp.array,expl.array_out_of_bounds,REINFORCES_CONCEPT
concept.cpp.vector,expl.array_out_of_bounds,REINFORCES_CONCEPT
view.intro_c,expl.array_out_of_bounds,VISIBLE_IN
view.algorithms,expl.array_out_of_bounds,VISIBLE_IN
view.cpp_stl,expl.array_out_of_bounds,VISIBLE_IN
fbp.locate_issue,expl.array_out_of_bounds,USES_FEEDBACK_PATTERN
fbp.counter_example,expl.array_out_of_bounds,USES_FEEDBACK_PATTERN
fbp.trace_execution,expl.array_out_of_bounds,USES_FEEDBACK_PATTERN
fbp.compare_fix,expl.array_out_of_bounds,USES_FEEDBACK_PATTERN
ctx.expression,expl.array_out_of_bounds,USES_CONTEXT_ANCHOR
ctx.testcase,expl.array_out_of_bounds,USES_CONTEXT_ANCHOR
ctx.trace,expl.array_out_of_bounds,USES_CONTEXT_ANCHOR
plan.array_indexing,expl.array_out_of_bounds,RECOMMENDS_PLAN
expl.array_out_of_bounds.step1,expl.array_out_of_bounds,CONSISTS_OF_STEP
expl.array_out_of_bounds.step2,expl.array_out_of_bounds,CONSISTS_OF_STEP
expl.array_out_of_bounds.step3,expl.array_out_of_bounds,CONSISTS_OF_STEP
explcat.array,expl.index_value_confusion,BELONGS_TO_CATEGORY
bug.index_value_confusion,expl.index_value_confusion,EXPLAINS_BUG
rule.array.index_value_confusion,expl.index_value_confusion,TRIGGERED_BY_RULE
mis.array.index_value,expl.index_value_confusion,TARGETS_MISCONCEPTION
fix.array.index_value,expl.index_value_confusion,SUGGESTS_FIX
concept.c.array,expl.index_value_confusion,REINFORCES_CONCEPT
concept.cpp.array,expl.index_value_confusion,REINFORCES_CONCEPT
concept.cpp.vector,expl.index_value_confusion,REINFORCES_CONCEPT
view.intro_c,expl.index_value_confusion,VISIBLE_IN
view.algorithms,expl.index_value_confusion,VISIBLE_IN
fbp.locate_issue,expl.index_value_confusion,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.index_value_confusion,USES_FEEDBACK_PATTERN
fbp.compare_fix,expl.index_value_confusion,USES_FEEDBACK_PATTERN
ctx.variable,expl.index_value_confusion,USES_CONTEXT_ANCHOR
ctx.expression,expl.index_value_confusion,USES_CONTEXT_ANCHOR
plan.array_indexing,expl.index_value_confusion,RECOMMENDS_PLAN
expl.index_value_confusion.step1,expl.index_value_confusion,CONSISTS_OF_STEP
expl.index_value_confusion.step2,expl.index_value_confusion,CONSISTS_OF_STEP
expl.index_value_confusion.step3,expl.index_value_confusion,CONSISTS_OF_STEP
explcat.pointer,expl.null_dereference,BELONGS_TO_CATEGORY
bug.null_dereference,expl.null_dereference,EXPLAINS_BUG
rule.pointer.null_deref.ast,expl.null_dereference,TRIGGERED_BY_RULE
rule.pointer.null_deref.clang,expl.null_dereference,TRIGGERED_BY_RULE
mis.pointer.null,expl.null_dereference,TARGETS_MISCONCEPTION
fix.null.check,expl.null_dereference,SUGGESTS_FIX
fix.smart_pointer,expl.null_dereference,SUGGESTS_FIX
concept.c.pointer,expl.null_dereference,REINFORCES_CONCEPT
concept.cpp.pointer,expl.null_dereference,REINFORCES_CONCEPT
concept.cpp.smart_pointer,expl.null_dereference,REINFORCES_CONCEPT
view.c_pointers,expl.null_dereference,VISIBLE_IN
view.cpp_modern,expl.null_dereference,VISIBLE_IN
fbp.locate_issue,expl.null_dereference,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.null_dereference,USES_FEEDBACK_PATTERN
fbp.counter_example,expl.null_dereference,USES_FEEDBACK_PATTERN
fbp.modern_recommendation,expl.null_dereference,USES_FEEDBACK_PATTERN
ctx.finding,expl.null_dereference,USES_CONTEXT_ANCHOR
ctx.line,expl.null_dereference,USES_CONTEXT_ANCHOR
ctx.variable,expl.null_dereference,USES_CONTEXT_ANCHOR
plan.pointer_lifetime,expl.null_dereference,RECOMMENDS_PLAN
expl.null_dereference.step1,expl.null_dereference,CONSISTS_OF_STEP
expl.null_dereference.step2,expl.null_dereference,CONSISTS_OF_STEP
expl.null_dereference.step3,expl.null_dereference,CONSISTS_OF_STEP
explcat.pointer,expl.memory_leak,BELONGS_TO_CATEGORY
bug.memory_leak,expl.memory_leak,EXPLAINS_BUG
rule.memory.leak.alloc_no_release,expl.memory_leak,TRIGGERED_BY_RULE
rule.memory.leak.sanitizer,expl.memory_leak,TRIGGERED_BY_RULE
mis.memory.auto_cleanup,expl.memory_leak,TARGETS_MISCONCEPTION
fix.release.once,expl.memory_leak,SUGGESTS_FIX
fix.use_raii,expl.memory_leak,SUGGESTS_FIX
fix.smart_pointer,expl.memory_leak,SUGGESTS_FIX
concept.c.malloc,expl.memory_leak,REINFORCES_CONCEPT
concept.c.realloc,expl.memory_leak,REINFORCES_CONCEPT
concept.cpp.new_delete,expl.memory_leak,REINFORCES_CONCEPT
concept.cpp.raii,expl.memory_leak,REINFORCES_CONCEPT
view.c_pointers,expl.memory_leak,VISIBLE_IN
view.cpp_modern,expl.memory_leak,VISIBLE_IN
fbp.locate_issue,expl.memory_leak,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.memory_leak,USES_FEEDBACK_PATTERN
fbp.modern_recommendation,expl.memory_leak,USES_FEEDBACK_PATTERN
fbp.remediation_path,expl.memory_leak,USES_FEEDBACK_PATTERN
ctx.line,expl.memory_leak,USES_CONTEXT_ANCHOR
ctx.trace,expl.memory_leak,USES_CONTEXT_ANCHOR
ctx.finding,expl.memory_leak,USES_CONTEXT_ANCHOR
plan.manual_memory,expl.memory_leak,RECOMMENDS_PLAN
expl.memory_leak.step1,expl.memory_leak,CONSISTS_OF_STEP
expl.memory_leak.step2,expl.memory_leak,CONSISTS_OF_STEP
expl.memory_leak.step3,expl.memory_leak,CONSISTS_OF_STEP
explcat.pointer,expl.use_after_free,BELONGS_TO_CATEGORY
bug.use_after_free,expl.use_after_free,EXPLAINS_BUG
bug.dangling_pointer,expl.use_after_free,EXPLAINS_BUG
rule.memory.use_after_free.flow,expl.use_after_free,TRIGGERED_BY_RULE
rule.memory.uaf.sanitizer,expl.use_after_free,TRIGGERED_BY_RULE
mis.pointer.free,expl.use_after_free,TARGETS_MISCONCEPTION
fix.no_use_after_release,expl.use_after_free,SUGGESTS_FIX
fix.smart_pointer,expl.use_after_free,SUGGESTS_FIX
concept.c.free,expl.use_after_free,REINFORCES_CONCEPT
concept.cpp.new_delete,expl.use_after_free,REINFORCES_CONCEPT
concept.c.pointer,expl.use_after_free,REINFORCES_CONCEPT
concept.cpp.pointer,expl.use_after_free,REINFORCES_CONCEPT
view.c_pointers,expl.use_after_free,VISIBLE_IN
fbp.locate_issue,expl.use_after_free,USES_FEEDBACK_PATTERN
fbp.trace_execution,expl.use_after_free,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.use_after_free,USES_FEEDBACK_PATTERN
ctx.trace,expl.use_after_free,USES_CONTEXT_ANCHOR
ctx.variable,expl.use_after_free,USES_CONTEXT_ANCHOR
ctx.finding,expl.use_after_free,USES_CONTEXT_ANCHOR
plan.pointer_lifetime,expl.use_after_free,RECOMMENDS_PLAN
expl.use_after_free.step1,expl.use_after_free,CONSISTS_OF_STEP
expl.use_after_free.step2,expl.use_after_free,CONSISTS_OF_STEP
expl.use_after_free.step3,expl.use_after_free,CONSISTS_OF_STEP
explcat.pointer,expl.double_free,BELONGS_TO_CATEGORY
bug.double_free,expl.double_free,EXPLAINS_BUG
rule.memory.double_free.flow,expl.double_free,TRIGGERED_BY_RULE
mis.pointer.free,expl.double_free,TARGETS_MISCONCEPTION
mis.ownership.shared,expl.double_free,TARGETS_MISCONCEPTION
fix.release.once,expl.double_free,SUGGESTS_FIX
fix.no_use_after_release,expl.double_free,SUGGESTS_FIX
concept.c.free,expl.double_free,REINFORCES_CONCEPT
concept.cpp.new_delete,expl.double_free,REINFORCES_CONCEPT
concept.cpp.smart_pointer,expl.double_free,REINFORCES_CONCEPT
view.c_pointers,expl.double_free,VISIBLE_IN
view.cpp_modern,expl.double_free,VISIBLE_IN
fbp.locate_issue,expl.double_free,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.double_free,USES_FEEDBACK_PATTERN
fbp.compare_fix,expl.double_free,USES_FEEDBACK_PATTERN
ctx.trace,expl.double_free,USES_CONTEXT_ANCHOR
ctx.variable,expl.double_free,USES_CONTEXT_ANCHOR
plan.manual_memory,expl.double_free,RECOMMENDS_PLAN
expl.double_free.step1,expl.double_free,CONSISTS_OF_STEP
expl.double_free.step2,expl.double_free,CONSISTS_OF_STEP
expl.double_free.step3,expl.double_free,CONSISTS_OF_STEP
explcat.function,expl.uninitialized_value,BELONGS_TO_CATEGORY
bug.uninitialized_value,expl.uninitialized_value,EXPLAINS_BUG
rule.loop.boundary.edge_case,expl.uninitialized_value,TRIGGERED_BY_RULE
mis.loop.init,expl.uninitialized_value,TARGETS_MISCONCEPTION
fix.loop.init,expl.uninitialized_value,SUGGESTS_FIX
concept.c.variable,expl.uninitialized_value,REINFORCES_CONCEPT
concept.cpp.default_init,expl.uninitialized_value,REINFORCES_CONCEPT
concept.cpp.value_init,expl.uninitialized_value,REINFORCES_CONCEPT
view.intro_c,expl.uninitialized_value,VISIBLE_IN
fbp.locate_issue,expl.uninitialized_value,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.uninitialized_value,USES_FEEDBACK_PATTERN
fbp.trace_execution,expl.uninitialized_value,USES_FEEDBACK_PATTERN
ctx.variable,expl.uninitialized_value,USES_CONTEXT_ANCHOR
ctx.line,expl.uninitialized_value,USES_CONTEXT_ANCHOR
plan.return_contract,expl.uninitialized_value,RECOMMENDS_PLAN
expl.uninitialized_value.step1,expl.uninitialized_value,CONSISTS_OF_STEP
expl.uninitialized_value.step2,expl.uninitialized_value,CONSISTS_OF_STEP
expl.uninitialized_value.step3,expl.uninitialized_value,CONSISTS_OF_STEP
explcat.function,expl.missing_return,BELONGS_TO_CATEGORY
bug.missing_return,expl.missing_return,EXPLAINS_BUG
rule.function.missing_return.compiler,expl.missing_return,TRIGGERED_BY_RULE
rule.function.missing_return.cfg,expl.missing_return,TRIGGERED_BY_RULE
mis.return.contract,expl.missing_return,TARGETS_MISCONCEPTION
fix.return,expl.missing_return,SUGGESTS_FIX
concept.c.function_def,expl.missing_return,REINFORCES_CONCEPT
concept.cpp.function_decl,expl.missing_return,REINFORCES_CONCEPT
concept.cpp.return,expl.missing_return,REINFORCES_CONCEPT
view.intro_c,expl.missing_return,VISIBLE_IN
fbp.locate_issue,expl.missing_return,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.missing_return,USES_FEEDBACK_PATTERN
fbp.compare_fix,expl.missing_return,USES_FEEDBACK_PATTERN
ctx.finding,expl.missing_return,USES_CONTEXT_ANCHOR
ctx.line,expl.missing_return,USES_CONTEXT_ANCHOR
ctx.expression,expl.missing_return,USES_CONTEXT_ANCHOR
plan.return_contract,expl.missing_return,RECOMMENDS_PLAN
expl.missing_return.step1,expl.missing_return,CONSISTS_OF_STEP
expl.missing_return.step2,expl.missing_return,CONSISTS_OF_STEP
expl.missing_return.step3,expl.missing_return,CONSISTS_OF_STEP
explcat.recursion,expl.wrong_base_case,BELONGS_TO_CATEGORY
bug.wrong_base_case,expl.wrong_base_case,EXPLAINS_BUG
rule.recursion.no_base_case,expl.wrong_base_case,TRIGGERED_BY_RULE
rule.recursion.unreachable_base,expl.wrong_base_case,TRIGGERED_BY_RULE
mis.recursion.base_case,expl.wrong_base_case,TARGETS_MISCONCEPTION
fix.recursion.base,expl.wrong_base_case,SUGGESTS_FIX
concept.c.function_def,expl.wrong_base_case,REINFORCES_CONCEPT
concept.cpp.function_decl,expl.wrong_base_case,REINFORCES_CONCEPT
view.algorithms,expl.wrong_base_case,VISIBLE_IN
fbp.locate_issue,expl.wrong_base_case,USES_FEEDBACK_PATTERN
fbp.counter_example,expl.wrong_base_case,USES_FEEDBACK_PATTERN
fbp.trace_execution,expl.wrong_base_case,USES_FEEDBACK_PATTERN
ctx.expression,expl.wrong_base_case,USES_CONTEXT_ANCHOR
ctx.trace,expl.wrong_base_case,USES_CONTEXT_ANCHOR
ctx.testcase,expl.wrong_base_case,USES_CONTEXT_ANCHOR
plan.recursion,expl.wrong_base_case,RECOMMENDS_PLAN
expl.wrong_base_case.step1,expl.wrong_base_case,CONSISTS_OF_STEP
expl.wrong_base_case.step2,expl.wrong_base_case,CONSISTS_OF_STEP
expl.wrong_base_case.step3,expl.wrong_base_case,CONSISTS_OF_STEP
explcat.recursion,expl.no_recursive_progress,BELONGS_TO_CATEGORY
bug.no_recursive_progress,expl.no_recursive_progress,EXPLAINS_BUG
rule.recursion.no_progress,expl.no_recursive_progress,TRIGGERED_BY_RULE
mis.recursion.progress,expl.no_recursive_progress,TARGETS_MISCONCEPTION
fix.recursion.progress,expl.no_recursive_progress,SUGGESTS_FIX
concept.c.function_def,expl.no_recursive_progress,REINFORCES_CONCEPT
concept.cpp.function_decl,expl.no_recursive_progress,REINFORCES_CONCEPT
view.algorithms,expl.no_recursive_progress,VISIBLE_IN
fbp.locate_issue,expl.no_recursive_progress,USES_FEEDBACK_PATTERN
fbp.trace_execution,expl.no_recursive_progress,USES_FEEDBACK_PATTERN
fbp.compare_fix,expl.no_recursive_progress,USES_FEEDBACK_PATTERN
ctx.trace,expl.no_recursive_progress,USES_CONTEXT_ANCHOR
ctx.expression,expl.no_recursive_progress,USES_CONTEXT_ANCHOR
plan.recursion,expl.no_recursive_progress,RECOMMENDS_PLAN
expl.no_recursive_progress.step1,expl.no_recursive_progress,CONSISTS_OF_STEP
expl.no_recursive_progress.step2,expl.no_recursive_progress,CONSISTS_OF_STEP
expl.no_recursive_progress.step3,expl.no_recursive_progress,CONSISTS_OF_STEP
explcat.iterator,expl.iterator_invalidation,BELONGS_TO_CATEGORY
bug.iterator_invalidation,expl.iterator_invalidation,EXPLAINS_BUG
bug.vector_out_of_range,expl.iterator_invalidation,EXPLAINS_BUG
rule.iterator.invalidation.modify_then_use,expl.iterator_invalidation,TRIGGERED_BY_RULE
rule.iterator.view_lifetime,expl.iterator_invalidation,TRIGGERED_BY_RULE
mis.iter.invalidate,expl.iterator_invalidation,TARGETS_MISCONCEPTION
fix.iterator.refresh,expl.iterator_invalidation,SUGGESTS_FIX
concept.cpp.iterator,expl.iterator_invalidation,REINFORCES_CONCEPT
concept.cpp.vector,expl.iterator_invalidation,REINFORCES_CONCEPT
concept.cpp.map,expl.iterator_invalidation,REINFORCES_CONCEPT
concept.cpp.unordered_map,expl.iterator_invalidation,REINFORCES_CONCEPT
concept.cpp.ranges,expl.iterator_invalidation,REINFORCES_CONCEPT
concept.cpp.views,expl.iterator_invalidation,REINFORCES_CONCEPT
view.cpp_stl,expl.iterator_invalidation,VISIBLE_IN
view.cpp_modern,expl.iterator_invalidation,VISIBLE_IN
fbp.locate_issue,expl.iterator_invalidation,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.iterator_invalidation,USES_FEEDBACK_PATTERN
fbp.compare_fix,expl.iterator_invalidation,USES_FEEDBACK_PATTERN
fbp.modern_recommendation,expl.iterator_invalidation,USES_FEEDBACK_PATTERN
ctx.trace,expl.iterator_invalidation,USES_CONTEXT_ANCHOR
ctx.variable,expl.iterator_invalidation,USES_CONTEXT_ANCHOR
ctx.line,expl.iterator_invalidation,USES_CONTEXT_ANCHOR
plan.iterator_range,expl.iterator_invalidation,RECOMMENDS_PLAN
expl.iterator_invalidation.step1,expl.iterator_invalidation,CONSISTS_OF_STEP
expl.iterator_invalidation.step2,expl.iterator_invalidation,CONSISTS_OF_STEP
expl.iterator_invalidation.step3,expl.iterator_invalidation,CONSISTS_OF_STEP
explcat.oop,expl.use_after_move,BELONGS_TO_CATEGORY
bug.use_after_move,expl.use_after_move,EXPLAINS_BUG
rule.move.use_after_move,expl.use_after_move,TRIGGERED_BY_RULE
mis.move.validity,expl.use_after_move,TARGETS_MISCONCEPTION
fix.move.use_state,expl.use_after_move,SUGGESTS_FIX
concept.cpp.move_semantics,expl.use_after_move,REINFORCES_CONCEPT
concept.cpp.unique_ptr,expl.use_after_move,REINFORCES_CONCEPT
concept.cpp.string,expl.use_after_move,REINFORCES_CONCEPT
concept.cpp.vector,expl.use_after_move,REINFORCES_CONCEPT
view.cpp_modern,expl.use_after_move,VISIBLE_IN
view.cpp_stl,expl.use_after_move,VISIBLE_IN
fbp.locate_issue,expl.use_after_move,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.use_after_move,USES_FEEDBACK_PATTERN
fbp.modern_recommendation,expl.use_after_move,USES_FEEDBACK_PATTERN
ctx.variable,expl.use_after_move,USES_CONTEXT_ANCHOR
ctx.trace,expl.use_after_move,USES_CONTEXT_ANCHOR
plan.modern_cpp_ownership,expl.use_after_move,RECOMMENDS_PLAN
expl.use_after_move.step1,expl.use_after_move,CONSISTS_OF_STEP
expl.use_after_move.step2,expl.use_after_move,CONSISTS_OF_STEP
expl.use_after_move.step3,expl.use_after_move,CONSISTS_OF_STEP
explcat.oop,expl.missing_virtual_destructor,BELONGS_TO_CATEGORY
bug.missing_virtual_destructor,expl.missing_virtual_destructor,EXPLAINS_BUG
rule.oop.delete_base_no_virtual,expl.missing_virtual_destructor,TRIGGERED_BY_RULE
mis.virtual.destructor,expl.missing_virtual_destructor,TARGETS_MISCONCEPTION
fix.virtual_destructor,expl.missing_virtual_destructor,SUGGESTS_FIX
concept.cpp.class,expl.missing_virtual_destructor,REINFORCES_CONCEPT
concept.cpp.inheritance,expl.missing_virtual_destructor,REINFORCES_CONCEPT
concept.cpp.virtual_function,expl.missing_virtual_destructor,REINFORCES_CONCEPT
concept.cpp.destructor,expl.missing_virtual_destructor,REINFORCES_CONCEPT
view.cpp_oop,expl.missing_virtual_destructor,VISIBLE_IN
fbp.locate_issue,expl.missing_virtual_destructor,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.missing_virtual_destructor,USES_FEEDBACK_PATTERN
fbp.compare_fix,expl.missing_virtual_destructor,USES_FEEDBACK_PATTERN
ctx.expression,expl.missing_virtual_destructor,USES_CONTEXT_ANCHOR
ctx.line,expl.missing_virtual_destructor,USES_CONTEXT_ANCHOR
plan.oop_destruction,expl.missing_virtual_destructor,RECOMMENDS_PLAN
expl.missing_virtual_destructor.step1,expl.missing_virtual_destructor,CONSISTS_OF_STEP
expl.missing_virtual_destructor.step2,expl.missing_virtual_destructor,CONSISTS_OF_STEP
expl.missing_virtual_destructor.step3,expl.missing_virtual_destructor,CONSISTS_OF_STEP
explcat.oop,expl.rule_of_five,BELONGS_TO_CATEGORY
bug.rule_of_five,expl.rule_of_five,EXPLAINS_BUG
rule.oop.rule_of_five,expl.rule_of_five,TRIGGERED_BY_RULE
mis.ownership.shared,expl.rule_of_five,TARGETS_MISCONCEPTION
fix.use_raii,expl.rule_of_five,SUGGESTS_FIX
fix.smart_pointer,expl.rule_of_five,SUGGESTS_FIX
concept.cpp.class,expl.rule_of_five,REINFORCES_CONCEPT
concept.cpp.copy_semantics,expl.rule_of_five,REINFORCES_CONCEPT
concept.cpp.move_semantics,expl.rule_of_five,REINFORCES_CONCEPT
concept.cpp.destructor,expl.rule_of_five,REINFORCES_CONCEPT
concept.cpp.raii,expl.rule_of_five,REINFORCES_CONCEPT
view.cpp_oop,expl.rule_of_five,VISIBLE_IN
view.cpp_modern,expl.rule_of_five,VISIBLE_IN
fbp.locate_issue,expl.rule_of_five,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.rule_of_five,USES_FEEDBACK_PATTERN
fbp.modern_recommendation,expl.rule_of_five,USES_FEEDBACK_PATTERN
fbp.remediation_path,expl.rule_of_five,USES_FEEDBACK_PATTERN
ctx.line,expl.rule_of_five,USES_CONTEXT_ANCHOR
ctx.variable,expl.rule_of_five,USES_CONTEXT_ANCHOR
plan.modern_cpp_ownership,expl.rule_of_five,RECOMMENDS_PLAN
expl.rule_of_five.step1,expl.rule_of_five,CONSISTS_OF_STEP
expl.rule_of_five.step2,expl.rule_of_five,CONSISTS_OF_STEP
expl.rule_of_five.step3,expl.rule_of_five,CONSISTS_OF_STEP
explcat.oop,expl.exception_safety,BELONGS_TO_CATEGORY
bug.exception_safety,expl.exception_safety,EXPLAINS_BUG
rule.oop.exception_safety,expl.exception_safety,TRIGGERED_BY_RULE
mis.exception.safety,expl.exception_safety,TARGETS_MISCONCEPTION
fix.use_raii,expl.exception_safety,SUGGESTS_FIX
concept.cpp.try_catch,expl.exception_safety,REINFORCES_CONCEPT
concept.cpp.noexcept,expl.exception_safety,REINFORCES_CONCEPT
concept.cpp.raii,expl.exception_safety,REINFORCES_CONCEPT
view.cpp_oop,expl.exception_safety,VISIBLE_IN
view.cpp_modern,expl.exception_safety,VISIBLE_IN
fbp.locate_issue,expl.exception_safety,USES_FEEDBACK_PATTERN
fbp.trace_execution,expl.exception_safety,USES_FEEDBACK_PATTERN
fbp.modern_recommendation,expl.exception_safety,USES_FEEDBACK_PATTERN
ctx.trace,expl.exception_safety,USES_CONTEXT_ANCHOR
ctx.line,expl.exception_safety,USES_CONTEXT_ANCHOR
plan.exception_safety,expl.exception_safety,RECOMMENDS_PLAN
expl.exception_safety.step1,expl.exception_safety,CONSISTS_OF_STEP
expl.exception_safety.step2,expl.exception_safety,CONSISTS_OF_STEP
expl.exception_safety.step3,expl.exception_safety,CONSISTS_OF_STEP
explcat.io,expl.format_specifier,BELONGS_TO_CATEGORY
bug.format_specifier_mismatch,expl.format_specifier,EXPLAINS_BUG
rule.format.specifier_mismatch,expl.format_specifier,TRIGGERED_BY_RULE
rule.format.modern_cpp_upgrade,expl.format_specifier,TRIGGERED_BY_RULE
mis.format.specifier,expl.format_specifier,TARGETS_MISCONCEPTION
fix.format.match,expl.format_specifier,SUGGESTS_FIX
concept.c.formatted_io,expl.format_specifier,REINFORCES_CONCEPT
concept.cpp.format,expl.format_specifier,REINFORCES_CONCEPT
concept.cpp.print_functions,expl.format_specifier,REINFORCES_CONCEPT
view.intro_c,expl.format_specifier,VISIBLE_IN
view.cpp_modern,expl.format_specifier,VISIBLE_IN
fbp.locate_issue,expl.format_specifier,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.format_specifier,USES_FEEDBACK_PATTERN
fbp.modern_recommendation,expl.format_specifier,USES_FEEDBACK_PATTERN
ctx.expression,expl.format_specifier,USES_CONTEXT_ANCHOR
ctx.finding,expl.format_specifier,USES_CONTEXT_ANCHOR
plan.formatting,expl.format_specifier,RECOMMENDS_PLAN
expl.format_specifier.step1,expl.format_specifier,CONSISTS_OF_STEP
expl.format_specifier.step2,expl.format_specifier,CONSISTS_OF_STEP
expl.format_specifier.step3,expl.format_specifier,CONSISTS_OF_STEP
explcat.concurrent,expl.condition_variable,BELONGS_TO_CATEGORY
bug.condition_variable_misuse,expl.condition_variable,EXPLAINS_BUG
rule.concurrent.wait_protocol,expl.condition_variable,TRIGGERED_BY_RULE
rule.concurrent.missing_sync,expl.condition_variable,TRIGGERED_BY_RULE
mis.wait.protocol,expl.condition_variable,TARGETS_MISCONCEPTION
fix.condition_wait,expl.condition_variable,SUGGESTS_FIX
concept.cpp.thread,expl.condition_variable,REINFORCES_CONCEPT
concept.cpp.mutex,expl.condition_variable,REINFORCES_CONCEPT
concept.cpp.condition_variable,expl.condition_variable,REINFORCES_CONCEPT
concept.cpp.atomic,expl.condition_variable,REINFORCES_CONCEPT
view.cpp_modern,expl.condition_variable,VISIBLE_IN
fbp.locate_issue,expl.condition_variable,USES_FEEDBACK_PATTERN
fbp.restate_rule,expl.condition_variable,USES_FEEDBACK_PATTERN
fbp.trace_execution,expl.condition_variable,USES_FEEDBACK_PATTERN
ctx.trace,expl.condition_variable,USES_CONTEXT_ANCHOR
ctx.line,expl.condition_variable,USES_CONTEXT_ANCHOR
ctx.variable,expl.condition_variable,USES_CONTEXT_ANCHOR
plan.concurrency_wait,expl.condition_variable,RECOMMENDS_PLAN
expl.condition_variable.step1,expl.condition_variable,CONSISTS_OF_STEP
expl.condition_variable.step2,expl.condition_variable,CONSISTS_OF_STEP
expl.condition_variable.step3,expl.condition_variable,CONSISTS_OF_STEP
concept.c.for,plan.loop_boundary,RECOMMENDS_CONCEPT
concept.c.while,plan.loop_boundary,RECOMMENDS_CONCEPT
concept.cpp.for,plan.loop_boundary,RECOMMENDS_CONCEPT
concept.cpp.range_for,plan.loop_boundary,RECOMMENDS_CONCEPT
concept.c.array,plan.array_indexing,RECOMMENDS_CONCEPT
concept.cpp.array,plan.array_indexing,RECOMMENDS_CONCEPT
concept.cpp.vector,plan.array_indexing,RECOMMENDS_CONCEPT
concept.c.pointer,plan.pointer_lifetime,RECOMMENDS_CONCEPT
concept.cpp.pointer,plan.pointer_lifetime,RECOMMENDS_CONCEPT
concept.cpp.smart_pointer,plan.pointer_lifetime,RECOMMENDS_CONCEPT
concept.c.malloc,plan.manual_memory,RECOMMENDS_CONCEPT
concept.c.free,plan.manual_memory,RECOMMENDS_CONCEPT
concept.cpp.new_delete,plan.manual_memory,RECOMMENDS_CONCEPT
concept.cpp.raii,plan.manual_memory,RECOMMENDS_CONCEPT
concept.c.function_def,plan.return_contract,RECOMMENDS_CONCEPT
concept.cpp.function_decl,plan.return_contract,RECOMMENDS_CONCEPT
concept.cpp.return,plan.return_contract,RECOMMENDS_CONCEPT
concept.c.function_def,plan.recursion,RECOMMENDS_CONCEPT
concept.cpp.function_decl,plan.recursion,RECOMMENDS_CONCEPT
concept.cpp.iterator,plan.iterator_range,RECOMMENDS_CONCEPT
concept.cpp.ranges,plan.iterator_range,RECOMMENDS_CONCEPT
concept.cpp.views,plan.iterator_range,RECOMMENDS_CONCEPT
concept.cpp.vector,plan.iterator_range,RECOMMENDS_CONCEPT
concept.cpp.raii,plan.modern_cpp_ownership,RECOMMENDS_CONCEPT
concept.cpp.move_semantics,plan.modern_cpp_ownership,RECOMMENDS_CONCEPT
concept.cpp.unique_ptr,plan.modern_cpp_ownership,RECOMMENDS_CONCEPT
concept.cpp.smart_pointer,plan.modern_cpp_ownership,RECOMMENDS_CONCEPT
concept.cpp.class,plan.oop_destruction,RECOMMENDS_CONCEPT
concept.cpp.inheritance,plan.oop_destruction,RECOMMENDS_CONCEPT
concept.cpp.destructor,plan.oop_destruction,RECOMMENDS_CONCEPT
concept.cpp.virtual_function,plan.oop_destruction,RECOMMENDS_CONCEPT
concept.cpp.try_catch,plan.exception_safety,RECOMMENDS_CONCEPT
concept.cpp.noexcept,plan.exception_safety,RECOMMENDS_CONCEPT
concept.cpp.raii,plan.exception_safety,RECOMMENDS_CONCEPT
concept.c.formatted_io,plan.formatting,RECOMMENDS_CONCEPT
concept.cpp.format,plan.formatting,RECOMMENDS_CONCEPT
concept.cpp.print_functions,plan.formatting,RECOMMENDS_CONCEPT
concept.cpp.thread,plan.concurrency_wait,RECOMMENDS_CONCEPT
concept.cpp.mutex,plan.concurrency_wait,RECOMMENDS_CONCEPT
concept.cpp.condition_variable,plan.concurrency_wait,RECOMMENDS_CONCEPT
concept.cpp.atomic,plan.concurrency_wait,RECOMMENDS_CONCEPT
view.intro_c,plan.loop_boundary,VISIBLE_IN
view.algorithms,plan.loop_boundary,VISIBLE_IN
view.intro_c,plan.array_indexing,VISIBLE_IN
view.algorithms,plan.array_indexing,VISIBLE_IN
view.cpp_stl,plan.array_indexing,VISIBLE_IN
view.c_pointers,plan.pointer_lifetime,VISIBLE_IN
view.c_pointers,plan.manual_memory,VISIBLE_IN
view.cpp_modern,plan.manual_memory,VISIBLE_IN
view.intro_c,plan.return_contract,VISIBLE_IN
view.algorithms,plan.recursion,VISIBLE_IN
view.cpp_stl,plan.iterator_range,VISIBLE_IN
view.cpp_modern,plan.iterator_range,VISIBLE_IN
view.cpp_modern,plan.modern_cpp_ownership,VISIBLE_IN
view.cpp_oop,plan.modern_cpp_ownership,VISIBLE_IN
view.cpp_oop,plan.oop_destruction,VISIBLE_IN
view.cpp_modern,plan.exception_safety,VISIBLE_IN
view.cpp_oop,plan.exception_safety,VISIBLE_IN
view.intro_c,plan.formatting,VISIBLE_IN
view.cpp_modern,plan.formatting,VISIBLE_IN
view.cpp_modern,plan.concurrency_wait,VISIBLE_IN
"""
SEED_CYPHER = r"""CREATE CONSTRAINT explanation_category_id_unique IF NOT EXISTS FOR (n:ExplanationCategory) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT explanation_template_id_unique IF NOT EXISTS FOR (n:ExplanationTemplate) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT explanation_step_id_unique IF NOT EXISTS FOR (n:ExplanationStep) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT feedback_pattern_id_unique IF NOT EXISTS FOR (n:FeedbackPattern) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT context_anchor_type_id_unique IF NOT EXISTS FOR (n:ContextAnchorType) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT remediation_plan_id_unique IF NOT EXISTS FOR (n:RemediationPlan) REQUIRE n.id IS UNIQUE;

// Explanation / Feedback ontology nodes
MERGE (n:ExplanationCategory {id: 'explcat.root'}) SET n += {id: 'explcat.root', name: 'ExplanationRoot', description: 'Root category for explanation and feedback templates', level: 'top', status: 'active'};
MERGE (n:ExplanationCategory {id: 'explcat.loop'}) SET n += {id: 'explcat.loop', name: 'LoopFeedback', description: 'Feedback templates for loop-related bugs', level: 'top', status: 'active'};
MERGE (n:ExplanationCategory {id: 'explcat.array'}) SET n += {id: 'explcat.array', name: 'ArrayAndBoundaryFeedback', description: 'Feedback templates for arrays, indexing, and boundaries', level: 'top', status: 'active'};
MERGE (n:ExplanationCategory {id: 'explcat.pointer'}) SET n += {id: 'explcat.pointer', name: 'PointerAndMemoryFeedback', description: 'Feedback templates for pointer and memory lifetime issues', level: 'top', status: 'active'};
MERGE (n:ExplanationCategory {id: 'explcat.function'}) SET n += {id: 'explcat.function', name: 'FunctionContractFeedback', description: 'Feedback templates for function return and contract violations', level: 'top', status: 'active'};
MERGE (n:ExplanationCategory {id: 'explcat.recursion'}) SET n += {id: 'explcat.recursion', name: 'RecursionFeedback', description: 'Feedback templates for base case and recursive progress issues', level: 'top', status: 'active'};
MERGE (n:ExplanationCategory {id: 'explcat.iterator'}) SET n += {id: 'explcat.iterator', name: 'IteratorAndRangeFeedback', description: 'Feedback templates for iterators, views, and invalidation', level: 'top', status: 'active'};
MERGE (n:ExplanationCategory {id: 'explcat.oop'}) SET n += {id: 'explcat.oop', name: 'OOPAndLifetimeFeedback', description: 'Feedback templates for OOP lifetime, move, and exception safety', level: 'top', status: 'active'};
MERGE (n:ExplanationCategory {id: 'explcat.io'}) SET n += {id: 'explcat.io', name: 'IOFormattingFeedback', description: 'Feedback templates for formatting and API misuse', level: 'top', status: 'active'};
MERGE (n:ExplanationCategory {id: 'explcat.concurrent'}) SET n += {id: 'explcat.concurrent', name: 'ConcurrencyFeedback', description: 'Feedback templates for synchronization and waiting protocols', level: 'top', status: 'active'};
MERGE (n:FeedbackPattern {id: 'fbp.locate_issue'}) SET n += {id: 'fbp.locate_issue', name: 'LocateIssueInStudentCode', patternType: 'diagnostic', description: 'Point to the likely code region and describe what is suspicious there.', status: 'active'};
MERGE (n:FeedbackPattern {id: 'fbp.restate_rule'}) SET n += {id: 'fbp.restate_rule', name: 'RestateCoreRule', patternType: 'conceptual', description: 'Restate the key programming rule in plain language.', status: 'active'};
MERGE (n:FeedbackPattern {id: 'fbp.counter_example'}) SET n += {id: 'fbp.counter_example', name: 'CounterExample', patternType: 'illustrative', description: 'Provide a minimal counterexample showing why the student logic fails.', status: 'active'};
MERGE (n:FeedbackPattern {id: 'fbp.trace_execution'}) SET n += {id: 'fbp.trace_execution', name: 'TraceExecutionNarration', patternType: 'dynamic', description: 'Walk through one concrete execution trace or edge case.', status: 'active'};
MERGE (n:FeedbackPattern {id: 'fbp.compare_fix'}) SET n += {id: 'fbp.compare_fix', name: 'CompareCurrentAndFixedLogic', patternType: 'repair', description: 'Contrast the current code behavior with the corrected version.', status: 'active'};
MERGE (n:FeedbackPattern {id: 'fbp.modern_recommendation'}) SET n += {id: 'fbp.modern_recommendation', name: 'ModernPracticeRecommendation', patternType: 'best-practice', description: 'Recommend a modern safer alternative such as RAII or std::format.', status: 'active'};
MERGE (n:FeedbackPattern {id: 'fbp.hint_escalation'}) SET n += {id: 'fbp.hint_escalation', name: 'HintEscalation', patternType: 'pedagogical', description: 'Start with mild hints and become increasingly explicit only if needed.', status: 'active'};
MERGE (n:FeedbackPattern {id: 'fbp.remediation_path'}) SET n += {id: 'fbp.remediation_path', name: 'RemediationPath', patternType: 'pedagogical', description: 'Suggest next concepts or exercises for strengthening the weak area.', status: 'active'};
MERGE (n:ContextAnchorType {id: 'ctx.line'}) SET n += {id: 'ctx.line', name: 'LineNumberAnchor', anchorType: 'source-location', description: 'Anchor explanation to a specific line or range of lines.', status: 'active'};
MERGE (n:ContextAnchorType {id: 'ctx.expression'}) SET n += {id: 'ctx.expression', name: 'ExpressionAnchor', anchorType: 'syntax', description: 'Anchor explanation to a concrete condition, expression, or statement.', status: 'active'};
MERGE (n:ContextAnchorType {id: 'ctx.variable'}) SET n += {id: 'ctx.variable', name: 'VariableAnchor', anchorType: 'state', description: 'Anchor explanation to a variable whose value or lifetime is central.', status: 'active'};
MERGE (n:ContextAnchorType {id: 'ctx.testcase'}) SET n += {id: 'ctx.testcase', name: 'TestCaseAnchor', anchorType: 'test', description: 'Anchor explanation to a failing boundary or counterexample test.', status: 'active'};
MERGE (n:ContextAnchorType {id: 'ctx.finding'}) SET n += {id: 'ctx.finding', name: 'AnalyzerFindingAnchor', anchorType: 'diagnostic', description: 'Anchor explanation to a compiler or analyzer finding.', status: 'active'};
MERGE (n:ContextAnchorType {id: 'ctx.trace'}) SET n += {id: 'ctx.trace', name: 'ExecutionTraceAnchor', anchorType: 'dynamic', description: 'Anchor explanation to a sequence of runtime states or steps.', status: 'active'};
MERGE (n:RemediationPlan {id: 'plan.loop_boundary'}) SET n += {id: 'plan.loop_boundary', name: 'ReviewLoopBoundaryReasoning', planType: 'concept-remediation', difficultyBand: 'basic-intermediate', description: 'Revisit strict versus non-strict inequalities and zero-based iteration.', status: 'active'};
MERGE (n:RemediationPlan {id: 'plan.array_indexing'}) SET n += {id: 'plan.array_indexing', name: 'ReviewArrayIndexingAndTraversal', planType: 'concept-remediation', difficultyBand: 'basic-intermediate', description: 'Practice indexing rules and traversal over fixed and dynamic sequences.', status: 'active'};
MERGE (n:RemediationPlan {id: 'plan.pointer_lifetime'}) SET n += {id: 'plan.pointer_lifetime', name: 'ReviewPointerValidityAndLifetime', planType: 'concept-remediation', difficultyBand: 'intermediate-advanced', description: 'Review pointer validity, ownership, free/delete semantics, and lifetime boundaries.', status: 'active'};
MERGE (n:RemediationPlan {id: 'plan.manual_memory'}) SET n += {id: 'plan.manual_memory', name: 'ReviewManualMemoryLifecycle', planType: 'concept-remediation', difficultyBand: 'intermediate-advanced', description: 'Practice allocate-use-release reasoning and matching ownership operations.', status: 'active'};
MERGE (n:RemediationPlan {id: 'plan.return_contract'}) SET n += {id: 'plan.return_contract', name: 'ReviewFunctionReturnContracts', planType: 'concept-remediation', difficultyBand: 'basic', description: 'Reinforce the idea that every non-void path must produce a value.', status: 'active'};
MERGE (n:RemediationPlan {id: 'plan.recursion'}) SET n += {id: 'plan.recursion', name: 'ReviewRecursiveBaseCaseAndProgress', planType: 'concept-remediation', difficultyBand: 'intermediate', description: 'Train on defining precise base cases and shrinking recursive state.', status: 'active'};
MERGE (n:RemediationPlan {id: 'plan.iterator_range'}) SET n += {id: 'plan.iterator_range', name: 'ReviewIteratorInvalidationAndRangeLifetimes', planType: 'concept-remediation', difficultyBand: 'advanced', description: 'Study invalidation rules, view lifetimes, and non-owning range semantics.', status: 'active'};
MERGE (n:RemediationPlan {id: 'plan.modern_cpp_ownership'}) SET n += {id: 'plan.modern_cpp_ownership', name: 'ReviewRAIIAndOwnershipModels', planType: 'concept-remediation', difficultyBand: 'advanced', description: 'Study single ownership, shared ownership, moved-from states, and RAII design.', status: 'active'};
MERGE (n:RemediationPlan {id: 'plan.oop_destruction'}) SET n += {id: 'plan.oop_destruction', name: 'ReviewPolymorphicDestruction', planType: 'concept-remediation', difficultyBand: 'advanced', description: 'Review virtual destructors, base pointers, and polymorphic object cleanup.', status: 'active'};
MERGE (n:RemediationPlan {id: 'plan.exception_safety'}) SET n += {id: 'plan.exception_safety', name: 'ReviewExceptionSafetyAndCleanup', planType: 'concept-remediation', difficultyBand: 'advanced', description: 'Study strong/basic/no-throw guarantees and exception-safe cleanup design.', status: 'active'};
MERGE (n:RemediationPlan {id: 'plan.formatting'}) SET n += {id: 'plan.formatting', name: 'ReviewFormattingAndTypeSafeOutput', planType: 'concept-remediation', difficultyBand: 'basic-intermediate', description: 'Practice matching types to format specifiers and prefer type-safe formatting APIs.', status: 'active'};
MERGE (n:RemediationPlan {id: 'plan.concurrency_wait'}) SET n += {id: 'plan.concurrency_wait', name: 'ReviewSynchronizationAndConditionProtocols', planType: 'concept-remediation', difficultyBand: 'advanced', description: 'Study locking discipline, predicate waits, and shared-state synchronization.', status: 'active'};
MERGE (n:ExplanationTemplate {id: 'expl.off_by_one'}) SET n += {id: 'expl.off_by_one', name: 'ExplainOffByOneBoundaryBug', toneLevel: 'novice', maxHintDepth: '3', explanationMode: 'step-by-step', description: 'Explain why a boundary that is one too small or too large breaks traversal logic.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.off_by_one.step1'}) SET n += {id: 'expl.off_by_one.step1', name: 'LocateBoundaryCondition', stepOrder: '1', stepKind: 'locate', text: 'Point to the loop condition or index access that determines the last iteration.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.off_by_one.step2'}) SET n += {id: 'expl.off_by_one.step2', name: 'RestateValidIndexRange', stepOrder: '2', stepKind: 'concept', text: 'Explain that a sequence of length n is normally indexed from 0 to n-1.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.off_by_one.step3'}) SET n += {id: 'expl.off_by_one.step3', name: 'WalkEdgeCaseAndPatch', stepOrder: '3', stepKind: 'repair', text: 'Walk through the boundary test case and show the corrected strict or non-strict condition.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.infinite_loop'}) SET n += {id: 'expl.infinite_loop', name: 'ExplainInfiniteLoop', toneLevel: 'novice', maxHintDepth: '3', explanationMode: 'step-by-step', description: 'Explain why the loop never reaches its exit condition and how to restore progress.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.infinite_loop.step1'}) SET n += {id: 'expl.infinite_loop.step1', name: 'FindProgressVariable', stepOrder: '1', stepKind: 'locate', text: 'Identify the variable or state that should move toward loop termination.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.infinite_loop.step2'}) SET n += {id: 'expl.infinite_loop.step2', name: 'ShowWhyExitIsNeverReached', stepOrder: '2', stepKind: 'concept', text: 'Show that the condition stays true forever or moves in the wrong direction.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.infinite_loop.step3'}) SET n += {id: 'expl.infinite_loop.step3', name: 'RepairUpdateOrCondition', stepOrder: '3', stepKind: 'repair', text: 'Adjust the update or condition so each iteration moves toward termination.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.array_out_of_bounds'}) SET n += {id: 'expl.array_out_of_bounds', name: 'ExplainArrayOutOfBounds', toneLevel: 'novice', maxHintDepth: '3', explanationMode: 'step-by-step', description: 'Explain why the current index can exceed valid sequence bounds.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.array_out_of_bounds.step1'}) SET n += {id: 'expl.array_out_of_bounds.step1', name: 'IdentifyUnsafeIndex', stepOrder: '1', stepKind: 'locate', text: 'Point to the index expression that can become equal to or larger than the container length.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.array_out_of_bounds.step2'}) SET n += {id: 'expl.array_out_of_bounds.step2', name: 'RunBoundaryCounterExample', stepOrder: '2', stepKind: 'concept', text: 'Use the smallest failing boundary case to show the invalid access.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.array_out_of_bounds.step3'}) SET n += {id: 'expl.array_out_of_bounds.step3', name: 'ConstrainIndexRange', stepOrder: '3', stepKind: 'repair', text: 'Rewrite the logic so every access stays within valid bounds.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.index_value_confusion'}) SET n += {id: 'expl.index_value_confusion', name: 'ExplainIndexValueConfusion', toneLevel: 'novice', maxHintDepth: '2', explanationMode: 'guided-hint', description: 'Explain the difference between index positions and the values stored at those positions.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.index_value_confusion.step1'}) SET n += {id: 'expl.index_value_confusion.step1', name: 'SeparateRoles', stepOrder: '1', stepKind: 'concept', text: 'Separate the variable representing the position from the value stored at that position.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.index_value_confusion.step2'}) SET n += {id: 'expl.index_value_confusion.step2', name: 'ShowCurrentMixUp', stepOrder: '2', stepKind: 'locate', text: 'Highlight where the code uses a value as if it were an index or vice versa.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.index_value_confusion.step3'}) SET n += {id: 'expl.index_value_confusion.step3', name: 'RefactorRoles', stepOrder: '3', stepKind: 'repair', text: 'Rename or restructure the variables so the two roles are not confused.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.null_dereference'}) SET n += {id: 'expl.null_dereference', name: 'ExplainNullDereference', toneLevel: 'intermediate', maxHintDepth: '3', explanationMode: 'step-by-step', description: 'Explain why a nullable or invalid pointer must not be dereferenced without proof of validity.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.null_dereference.step1'}) SET n += {id: 'expl.null_dereference.step1', name: 'ShowUnsafeDereference', stepOrder: '1', stepKind: 'locate', text: 'Point to the dereference site and the missing validity guarantee.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.null_dereference.step2'}) SET n += {id: 'expl.null_dereference.step2', name: 'ExplainValidityRequirement', stepOrder: '2', stepKind: 'concept', text: 'Explain that dereference is only safe when the pointer definitely refers to a live object.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.null_dereference.step3'}) SET n += {id: 'expl.null_dereference.step3', name: 'GuardOrRedesignOwnership', stepOrder: '3', stepKind: 'repair', text: 'Add a guard or redesign the ownership model to make invalid states impossible.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.memory_leak'}) SET n += {id: 'expl.memory_leak', name: 'ExplainMemoryLeak', toneLevel: 'intermediate', maxHintDepth: '3', explanationMode: 'step-by-step', description: 'Explain how allocation creates ownership obligations and why missing release causes leaks.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.memory_leak.step1'}) SET n += {id: 'expl.memory_leak.step1', name: 'LocateAllocationOwnership', stepOrder: '1', stepKind: 'locate', text: 'Point to the allocation site and ask who is responsible for releasing it.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.memory_leak.step2'}) SET n += {id: 'expl.memory_leak.step2', name: 'ShowMissingReleasePath', stepOrder: '2', stepKind: 'concept', text: 'Show the path where the resource is never released or returned safely.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.memory_leak.step3'}) SET n += {id: 'expl.memory_leak.step3', name: 'IntroduceLifecycleFix', stepOrder: '3', stepKind: 'repair', text: 'Add the missing release or replace manual ownership with RAII/smart pointers.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.use_after_free'}) SET n += {id: 'expl.use_after_free', name: 'ExplainUseAfterFree', toneLevel: 'intermediate', maxHintDepth: '3', explanationMode: 'step-by-step', description: 'Explain why a handle becomes invalid immediately after its resource is released.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.use_after_free.step1'}) SET n += {id: 'expl.use_after_free.step1', name: 'TraceReleaseThenUse', stepOrder: '1', stepKind: 'locate', text: 'Trace the point where the resource is released and the later point where it is still used.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.use_after_free.step2'}) SET n += {id: 'expl.use_after_free.step2', name: 'ExplainEndedLifetime', stepOrder: '2', stepKind: 'concept', text: 'Explain that releasing the underlying storage ends the object lifetime for that handle.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.use_after_free.step3'}) SET n += {id: 'expl.use_after_free.step3', name: 'InvalidateOrTransferOwnership', stepOrder: '3', stepKind: 'repair', text: 'Stop using the handle after release or replace manual lifetime management with safer ownership.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.double_free'}) SET n += {id: 'expl.double_free', name: 'ExplainDoubleFree', toneLevel: 'intermediate', maxHintDepth: '3', explanationMode: 'step-by-step', description: 'Explain why the same resource must be released exactly once.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.double_free.step1'}) SET n += {id: 'expl.double_free.step1', name: 'FindDuplicateReleasePath', stepOrder: '1', stepKind: 'locate', text: 'Locate the two paths that release the same resource.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.double_free.step2'}) SET n += {id: 'expl.double_free.step2', name: 'ExplainSingleOwnershipRule', stepOrder: '2', stepKind: 'concept', text: 'Explain that one owned resource must have one final release operation.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.double_free.step3'}) SET n += {id: 'expl.double_free.step3', name: 'RestructureOwnership', stepOrder: '3', stepKind: 'repair', text: 'Make ownership unique or centralize release so it happens only once.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.uninitialized_value'}) SET n += {id: 'expl.uninitialized_value', name: 'ExplainUninitializedValueUse', toneLevel: 'novice', maxHintDepth: '2', explanationMode: 'guided-hint', description: 'Explain why reading a variable before valid initialization leads to unstable behavior.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.uninitialized_value.step1'}) SET n += {id: 'expl.uninitialized_value.step1', name: 'FindFirstRead', stepOrder: '1', stepKind: 'locate', text: 'Find the first read of the variable before any guaranteed assignment.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.uninitialized_value.step2'}) SET n += {id: 'expl.uninitialized_value.step2', name: 'ExplainInitializationRequirement', stepOrder: '2', stepKind: 'concept', text: 'Explain that a variable must be initialized before its value is used.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.uninitialized_value.step3'}) SET n += {id: 'expl.uninitialized_value.step3', name: 'InitializeBeforeUse', stepOrder: '3', stepKind: 'repair', text: 'Introduce an explicit meaningful initialization before the first read.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.missing_return'}) SET n += {id: 'expl.missing_return', name: 'ExplainMissingReturnValue', toneLevel: 'novice', maxHintDepth: '2', explanationMode: 'guided-hint', description: 'Explain that every non-void function path must return a valid value.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.missing_return.step1'}) SET n += {id: 'expl.missing_return.step1', name: 'LocateMissingPath', stepOrder: '1', stepKind: 'locate', text: 'Locate the control-flow path that ends without returning a value.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.missing_return.step2'}) SET n += {id: 'expl.missing_return.step2', name: 'ExplainContract', stepOrder: '2', stepKind: 'concept', text: 'Explain the contract of a non-void function: every path must produce a result.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.missing_return.step3'}) SET n += {id: 'expl.missing_return.step3', name: 'AddReturnToAllPaths', stepOrder: '3', stepKind: 'repair', text: 'Make every branch return a valid value or redesign the function signature.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.wrong_base_case'}) SET n += {id: 'expl.wrong_base_case', name: 'ExplainWrongRecursiveBaseCase', toneLevel: 'intermediate', maxHintDepth: '3', explanationMode: 'step-by-step', description: 'Explain that recursion needs a reachable stopping condition that matches the smallest solvable case.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.wrong_base_case.step1'}) SET n += {id: 'expl.wrong_base_case.step1', name: 'LocateBaseCaseCondition', stepOrder: '1', stepKind: 'locate', text: 'Highlight the stopping condition and check whether it can actually be reached.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.wrong_base_case.step2'}) SET n += {id: 'expl.wrong_base_case.step2', name: 'ShowFailingInput', stepOrder: '2', stepKind: 'concept', text: 'Run a small input where the recursion should stop but does not stop correctly.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.wrong_base_case.step3'}) SET n += {id: 'expl.wrong_base_case.step3', name: 'DefineReachableBaseCase', stepOrder: '3', stepKind: 'repair', text: 'Rewrite the stopping condition so the smallest case terminates correctly.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.no_recursive_progress'}) SET n += {id: 'expl.no_recursive_progress', name: 'ExplainNoRecursiveProgress', toneLevel: 'intermediate', maxHintDepth: '3', explanationMode: 'step-by-step', description: 'Explain why recursive calls must reduce the problem size toward the base case.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.no_recursive_progress.step1'}) SET n += {id: 'expl.no_recursive_progress.step1', name: 'LocateRecursiveArgument', stepOrder: '1', stepKind: 'locate', text: 'Find the argument or state passed into the recursive call.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.no_recursive_progress.step2'}) SET n += {id: 'expl.no_recursive_progress.step2', name: 'ShowLackOfReduction', stepOrder: '2', stepKind: 'concept', text: 'Show that the recursive input does not become simpler or smaller.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.no_recursive_progress.step3'}) SET n += {id: 'expl.no_recursive_progress.step3', name: 'MakeProgressExplicit', stepOrder: '3', stepKind: 'repair', text: 'Change the recursive call so it moves toward the base case on every step.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.iterator_invalidation'}) SET n += {id: 'expl.iterator_invalidation', name: 'ExplainIteratorInvalidation', toneLevel: 'advanced', maxHintDepth: '3', explanationMode: 'step-by-step', description: 'Explain why some container operations invalidate iterators, references, or views.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.iterator_invalidation.step1'}) SET n += {id: 'expl.iterator_invalidation.step1', name: 'LocateModificationAndUse', stepOrder: '1', stepKind: 'locate', text: 'Locate the container modification and the later iterator or view use.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.iterator_invalidation.step2'}) SET n += {id: 'expl.iterator_invalidation.step2', name: 'ExplainInvalidationRule', stepOrder: '2', stepKind: 'concept', text: 'Explain that some operations reallocate or erase elements and invalidate observers.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.iterator_invalidation.step3'}) SET n += {id: 'expl.iterator_invalidation.step3', name: 'RefreshIteratorsOrChangePattern', stepOrder: '3', stepKind: 'repair', text: 'Reacquire iterators after modification or change to a safer traversal pattern.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.use_after_move'}) SET n += {id: 'expl.use_after_move', name: 'ExplainUseAfterMove', toneLevel: 'advanced', maxHintDepth: '3', explanationMode: 'step-by-step', description: 'Explain the valid but unspecified state of moved-from objects and how to use them safely.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.use_after_move.step1'}) SET n += {id: 'expl.use_after_move.step1', name: 'LocateMoveAndLaterRead', stepOrder: '1', stepKind: 'locate', text: 'Locate the move operation and the subsequent read that assumes the old value is still there.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.use_after_move.step2'}) SET n += {id: 'expl.use_after_move.step2', name: 'ExplainMovedFromState', stepOrder: '2', stepKind: 'concept', text: 'Explain that moved-from objects remain valid but their value is not the old owned resource.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.use_after_move.step3'}) SET n += {id: 'expl.use_after_move.step3', name: 'ReinitializeOrAvoidDependence', stepOrder: '3', stepKind: 'repair', text: 'Reinitialize the object or avoid reading semantic value after the move.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.missing_virtual_destructor'}) SET n += {id: 'expl.missing_virtual_destructor', name: 'ExplainMissingVirtualDestructor', toneLevel: 'advanced', maxHintDepth: '3', explanationMode: 'step-by-step', description: 'Explain why deleting a derived object through a base pointer requires a virtual base destructor.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.missing_virtual_destructor.step1'}) SET n += {id: 'expl.missing_virtual_destructor.step1', name: 'LocateDeleteThroughBase', stepOrder: '1', stepKind: 'locate', text: 'Locate the delete operation performed through a base-class pointer or reference-like owner.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.missing_virtual_destructor.step2'}) SET n += {id: 'expl.missing_virtual_destructor.step2', name: 'ExplainPolymorphicDestructionRule', stepOrder: '2', stepKind: 'concept', text: 'Explain that the base destructor must be virtual for derived cleanup to run correctly.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.missing_virtual_destructor.step3'}) SET n += {id: 'expl.missing_virtual_destructor.step3', name: 'AddVirtualDestructor', stepOrder: '3', stepKind: 'repair', text: 'Declare the base destructor virtual and verify derived cleanup now happens safely.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.rule_of_five'}) SET n += {id: 'expl.rule_of_five', name: 'ExplainRuleOfFiveViolation', toneLevel: 'advanced', maxHintDepth: '4', explanationMode: 'step-by-step', description: 'Explain why a resource-owning class must define consistent special member behavior or delegate ownership to RAII types.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.rule_of_five.step1'}) SET n += {id: 'expl.rule_of_five.step1', name: 'IdentifyOwnedResourceClass', stepOrder: '1', stepKind: 'locate', text: 'Identify the class that manually manages a resource such as dynamic memory or a handle.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.rule_of_five.step2'}) SET n += {id: 'expl.rule_of_five.step2', name: 'ExplainSpecialMemberConsistency', stepOrder: '2', stepKind: 'concept', text: 'Explain why copy, move, destruction, and assignment must agree on ownership semantics.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.rule_of_five.step3'}) SET n += {id: 'expl.rule_of_five.step3', name: 'PreferRAIIOrCompleteSpecialMembers', stepOrder: '3', stepKind: 'repair', text: 'Prefer composing RAII types or define the needed special members consistently.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.exception_safety'}) SET n += {id: 'expl.exception_safety', name: 'ExplainExceptionSafetyViolation', toneLevel: 'advanced', maxHintDepth: '4', explanationMode: 'step-by-step', description: 'Explain how exceptions can bypass manual cleanup and break invariants when ownership is not exception-safe.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.exception_safety.step1'}) SET n += {id: 'expl.exception_safety.step1', name: 'LocateExceptionalPath', stepOrder: '1', stepKind: 'locate', text: 'Locate the operation that can throw and the cleanup that may be skipped.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.exception_safety.step2'}) SET n += {id: 'expl.exception_safety.step2', name: 'ExplainInvariantAndCleanupRisk', stepOrder: '2', stepKind: 'concept', text: 'Explain what resource or invariant becomes inconsistent if an exception interrupts the path.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.exception_safety.step3'}) SET n += {id: 'expl.exception_safety.step3', name: 'AdoptRAIIBoundaries', stepOrder: '3', stepKind: 'repair', text: 'Move resource cleanup into RAII objects so normal and exceptional exits behave the same.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.format_specifier'}) SET n += {id: 'expl.format_specifier', name: 'ExplainFormatSpecifierMismatch', toneLevel: 'novice', maxHintDepth: '2', explanationMode: 'guided-hint', description: 'Explain that formatting placeholders and argument types must agree.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.format_specifier.step1'}) SET n += {id: 'expl.format_specifier.step1', name: 'LocateFormatMismatch', stepOrder: '1', stepKind: 'locate', text: 'Point to the formatting call where placeholder and argument type disagree.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.format_specifier.step2'}) SET n += {id: 'expl.format_specifier.step2', name: 'ExplainTypeAgreementRule', stepOrder: '2', stepKind: 'concept', text: 'Explain that formatting APIs interpret arguments according to the placeholder contract.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.format_specifier.step3'}) SET n += {id: 'expl.format_specifier.step3', name: 'CorrectSpecifierOrUpgradeAPI', stepOrder: '3', stepKind: 'repair', text: 'Choose the correct specifier or use a type-safe formatting API when available.', status: 'active', language: 'en'};
MERGE (n:ExplanationTemplate {id: 'expl.condition_variable'}) SET n += {id: 'expl.condition_variable', name: 'ExplainConditionVariableMisuse', toneLevel: 'advanced', maxHintDepth: '4', explanationMode: 'step-by-step', description: 'Explain the correct waiting protocol for condition variables and shared state synchronization.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.condition_variable.step1'}) SET n += {id: 'expl.condition_variable.step1', name: 'LocateWaitNotifyProtocol', stepOrder: '1', stepKind: 'locate', text: 'Locate the shared state, the lock, and the wait/notify operations.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.condition_variable.step2'}) SET n += {id: 'expl.condition_variable.step2', name: 'ExplainPredicateWaitRule', stepOrder: '2', stepKind: 'concept', text: 'Explain that waiting should re-check the predicate while holding the correct lock.', status: 'active', language: 'en'};
MERGE (n:ExplanationStep {id: 'expl.condition_variable.step3'}) SET n += {id: 'expl.condition_variable.step3', name: 'RepairSynchronizationProtocol', stepOrder: '3', stepKind: 'repair', text: 'Protect the shared state consistently and rewrite waiting as a predicate loop.', status: 'active', language: 'en'};

// Explanation / Feedback ontology relationships
MATCH (a {id: 'explcat.loop'}), (b {id: 'explcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'explcat.array'}), (b {id: 'explcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'explcat.pointer'}), (b {id: 'explcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'explcat.function'}), (b {id: 'explcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'explcat.recursion'}), (b {id: 'explcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'explcat.iterator'}), (b {id: 'explcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'explcat.oop'}), (b {id: 'explcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'explcat.io'}), (b {id: 'explcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'explcat.concurrent'}), (b {id: 'explcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'explcat.array'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'bug.off_by_one'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'rule.loop.off_by_one.leq_length'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'rule.loop.off_by_one.start_one'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'rule.meta.edge_case_boundary'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'mis.loop.bound'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'mis.array.last_index'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'fix.loop.bound'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'fix.array.bound'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'concept.c.array'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'concept.c.for'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'concept.cpp.range_for'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'view.cpp_stl'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'fbp.trace_execution'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'fbp.compare_fix'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'fbp.remediation_path'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'ctx.line'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'ctx.expression'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'ctx.testcase'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'plan.loop_boundary'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'expl.off_by_one.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'expl.off_by_one.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.off_by_one'}), (b {id: 'expl.off_by_one.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'explcat.loop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'bug.infinite_loop'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'bug.missing_loop_update'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'bug.wrong_loop_condition'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'rule.loop.infinite.missing_update'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'rule.loop.infinite.wrong_direction'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'mis.loop.progress'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'fix.loop.progress'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'fix.loop.bound'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'concept.c.for'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'concept.c.while'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'concept.cpp.for'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'concept.cpp.while'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'fbp.trace_execution'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'fbp.compare_fix'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'ctx.line'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'ctx.variable'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'ctx.trace'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'plan.loop_boundary'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'expl.infinite_loop.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'expl.infinite_loop.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.infinite_loop'}), (b {id: 'expl.infinite_loop.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'explcat.array'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'bug.array_out_of_bounds'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'bug.vector_out_of_range'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'rule.array.out_of_bounds.size_index'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'mis.array.last_index'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'fix.array.bound'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'concept.c.array'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'concept.cpp.array'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'view.cpp_stl'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'fbp.counter_example'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'fbp.trace_execution'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'fbp.compare_fix'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'ctx.expression'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'ctx.testcase'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'ctx.trace'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'plan.array_indexing'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'expl.array_out_of_bounds.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'expl.array_out_of_bounds.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.array_out_of_bounds'}), (b {id: 'expl.array_out_of_bounds.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'explcat.array'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'bug.index_value_confusion'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'rule.array.index_value_confusion'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'mis.array.index_value'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'fix.array.index_value'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'concept.c.array'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'concept.cpp.array'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'fbp.compare_fix'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'ctx.variable'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'ctx.expression'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'plan.array_indexing'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'expl.index_value_confusion.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'expl.index_value_confusion.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.index_value_confusion'}), (b {id: 'expl.index_value_confusion.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'explcat.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'bug.null_dereference'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'rule.pointer.null_deref.ast'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'rule.pointer.null_deref.clang'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'mis.pointer.null'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'fix.null.check'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'fix.smart_pointer'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'concept.c.pointer'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'concept.cpp.pointer'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'concept.cpp.smart_pointer'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'fbp.counter_example'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'fbp.modern_recommendation'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'ctx.finding'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'ctx.line'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'ctx.variable'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'plan.pointer_lifetime'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'expl.null_dereference.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'expl.null_dereference.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.null_dereference'}), (b {id: 'expl.null_dereference.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'explcat.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'bug.memory_leak'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'rule.memory.leak.alloc_no_release'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'rule.memory.leak.sanitizer'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'mis.memory.auto_cleanup'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'fix.release.once'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'fix.use_raii'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'fix.smart_pointer'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'concept.c.malloc'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'concept.c.realloc'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'concept.cpp.new_delete'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'concept.cpp.raii'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'fbp.modern_recommendation'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'fbp.remediation_path'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'ctx.line'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'ctx.trace'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'ctx.finding'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'plan.manual_memory'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'expl.memory_leak.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'expl.memory_leak.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.memory_leak'}), (b {id: 'expl.memory_leak.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'explcat.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'bug.use_after_free'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'bug.dangling_pointer'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'rule.memory.use_after_free.flow'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'rule.memory.uaf.sanitizer'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'mis.pointer.free'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'fix.no_use_after_release'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'fix.smart_pointer'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'concept.c.free'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'concept.cpp.new_delete'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'concept.c.pointer'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'concept.cpp.pointer'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'fbp.trace_execution'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'ctx.trace'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'ctx.variable'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'ctx.finding'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'plan.pointer_lifetime'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'expl.use_after_free.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'expl.use_after_free.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.use_after_free'}), (b {id: 'expl.use_after_free.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'explcat.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'bug.double_free'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'rule.memory.double_free.flow'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'mis.pointer.free'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'mis.ownership.shared'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'fix.release.once'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'fix.no_use_after_release'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'concept.c.free'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'concept.cpp.new_delete'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'concept.cpp.smart_pointer'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'fbp.compare_fix'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'ctx.trace'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'ctx.variable'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'plan.manual_memory'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'expl.double_free.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'expl.double_free.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.double_free'}), (b {id: 'expl.double_free.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'explcat.function'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'bug.uninitialized_value'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'rule.loop.boundary.edge_case'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'mis.loop.init'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'fix.loop.init'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'concept.c.variable'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'concept.cpp.default_init'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'concept.cpp.value_init'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'fbp.trace_execution'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'ctx.variable'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'ctx.line'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'plan.return_contract'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'expl.uninitialized_value.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'expl.uninitialized_value.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.uninitialized_value'}), (b {id: 'expl.uninitialized_value.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'explcat.function'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'bug.missing_return'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'rule.function.missing_return.compiler'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'rule.function.missing_return.cfg'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'mis.return.contract'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'fix.return'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'concept.c.function_def'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'concept.cpp.function_decl'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'concept.cpp.return'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'fbp.compare_fix'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'ctx.finding'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'ctx.line'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'ctx.expression'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'plan.return_contract'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'expl.missing_return.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'expl.missing_return.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.missing_return'}), (b {id: 'expl.missing_return.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'explcat.recursion'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'bug.wrong_base_case'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'rule.recursion.no_base_case'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'rule.recursion.unreachable_base'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'mis.recursion.base_case'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'fix.recursion.base'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'concept.c.function_def'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'concept.cpp.function_decl'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'fbp.counter_example'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'fbp.trace_execution'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'ctx.expression'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'ctx.trace'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'ctx.testcase'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'plan.recursion'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'expl.wrong_base_case.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'expl.wrong_base_case.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.wrong_base_case'}), (b {id: 'expl.wrong_base_case.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'explcat.recursion'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'bug.no_recursive_progress'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'rule.recursion.no_progress'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'mis.recursion.progress'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'fix.recursion.progress'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'concept.c.function_def'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'concept.cpp.function_decl'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'fbp.trace_execution'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'fbp.compare_fix'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'ctx.trace'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'ctx.expression'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'plan.recursion'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'expl.no_recursive_progress.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'expl.no_recursive_progress.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.no_recursive_progress'}), (b {id: 'expl.no_recursive_progress.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'explcat.iterator'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'bug.iterator_invalidation'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'bug.vector_out_of_range'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'rule.iterator.invalidation.modify_then_use'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'rule.iterator.view_lifetime'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'mis.iter.invalidate'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'fix.iterator.refresh'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'concept.cpp.iterator'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'concept.cpp.map'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'concept.cpp.unordered_map'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'concept.cpp.ranges'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'concept.cpp.views'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'view.cpp_stl'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'fbp.compare_fix'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'fbp.modern_recommendation'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'ctx.trace'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'ctx.variable'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'ctx.line'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'plan.iterator_range'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'expl.iterator_invalidation.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'expl.iterator_invalidation.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.iterator_invalidation'}), (b {id: 'expl.iterator_invalidation.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'explcat.oop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'bug.use_after_move'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'rule.move.use_after_move'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'mis.move.validity'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'fix.move.use_state'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'concept.cpp.move_semantics'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'concept.cpp.unique_ptr'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'concept.cpp.string'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'view.cpp_stl'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'fbp.modern_recommendation'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'ctx.variable'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'ctx.trace'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'plan.modern_cpp_ownership'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'expl.use_after_move.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'expl.use_after_move.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.use_after_move'}), (b {id: 'expl.use_after_move.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'explcat.oop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'bug.missing_virtual_destructor'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'rule.oop.delete_base_no_virtual'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'mis.virtual.destructor'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'fix.virtual_destructor'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'concept.cpp.class'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'concept.cpp.inheritance'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'concept.cpp.virtual_function'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'concept.cpp.destructor'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'view.cpp_oop'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'fbp.compare_fix'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'ctx.expression'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'ctx.line'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'plan.oop_destruction'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'expl.missing_virtual_destructor.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'expl.missing_virtual_destructor.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.missing_virtual_destructor'}), (b {id: 'expl.missing_virtual_destructor.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'explcat.oop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'bug.rule_of_five'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'rule.oop.rule_of_five'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'mis.ownership.shared'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'fix.use_raii'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'fix.smart_pointer'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'concept.cpp.class'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'concept.cpp.copy_semantics'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'concept.cpp.move_semantics'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'concept.cpp.destructor'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'concept.cpp.raii'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'view.cpp_oop'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'fbp.modern_recommendation'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'fbp.remediation_path'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'ctx.line'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'ctx.variable'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'plan.modern_cpp_ownership'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'expl.rule_of_five.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'expl.rule_of_five.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.rule_of_five'}), (b {id: 'expl.rule_of_five.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'explcat.oop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'bug.exception_safety'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'rule.oop.exception_safety'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'mis.exception.safety'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'fix.use_raii'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'concept.cpp.try_catch'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'concept.cpp.noexcept'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'concept.cpp.raii'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'view.cpp_oop'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'fbp.trace_execution'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'fbp.modern_recommendation'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'ctx.trace'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'ctx.line'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'plan.exception_safety'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'expl.exception_safety.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'expl.exception_safety.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.exception_safety'}), (b {id: 'expl.exception_safety.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'explcat.io'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'bug.format_specifier_mismatch'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'rule.format.specifier_mismatch'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'rule.format.modern_cpp_upgrade'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'mis.format.specifier'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'fix.format.match'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'concept.c.formatted_io'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'concept.cpp.format'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'concept.cpp.print_functions'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'fbp.modern_recommendation'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'ctx.expression'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'ctx.finding'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'plan.formatting'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'expl.format_specifier.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'expl.format_specifier.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.format_specifier'}), (b {id: 'expl.format_specifier.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'explcat.concurrent'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'bug.condition_variable_misuse'}) MERGE (a)-[r:EXPLAINS_BUG]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'rule.concurrent.wait_protocol'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'rule.concurrent.missing_sync'}) MERGE (a)-[r:TRIGGERED_BY_RULE]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'mis.wait.protocol'}) MERGE (a)-[r:TARGETS_MISCONCEPTION]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'fix.condition_wait'}) MERGE (a)-[r:SUGGESTS_FIX]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'concept.cpp.thread'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'concept.cpp.mutex'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'concept.cpp.condition_variable'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'concept.cpp.atomic'}) MERGE (a)-[r:REINFORCES_CONCEPT]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'fbp.locate_issue'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'fbp.restate_rule'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'fbp.trace_execution'}) MERGE (a)-[r:USES_FEEDBACK_PATTERN]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'ctx.trace'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'ctx.line'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'ctx.variable'}) MERGE (a)-[r:USES_CONTEXT_ANCHOR]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'plan.concurrency_wait'}) MERGE (a)-[r:RECOMMENDS_PLAN]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'expl.condition_variable.step1'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'expl.condition_variable.step2'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'expl.condition_variable'}), (b {id: 'expl.condition_variable.step3'}) MERGE (a)-[r:CONSISTS_OF_STEP]->(b);
MATCH (a {id: 'plan.loop_boundary'}), (b {id: 'concept.c.for'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.loop_boundary'}), (b {id: 'concept.c.while'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.loop_boundary'}), (b {id: 'concept.cpp.for'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.loop_boundary'}), (b {id: 'concept.cpp.range_for'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.array_indexing'}), (b {id: 'concept.c.array'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.array_indexing'}), (b {id: 'concept.cpp.array'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.array_indexing'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.pointer_lifetime'}), (b {id: 'concept.c.pointer'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.pointer_lifetime'}), (b {id: 'concept.cpp.pointer'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.pointer_lifetime'}), (b {id: 'concept.cpp.smart_pointer'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.manual_memory'}), (b {id: 'concept.c.malloc'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.manual_memory'}), (b {id: 'concept.c.free'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.manual_memory'}), (b {id: 'concept.cpp.new_delete'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.manual_memory'}), (b {id: 'concept.cpp.raii'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.return_contract'}), (b {id: 'concept.c.function_def'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.return_contract'}), (b {id: 'concept.cpp.function_decl'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.return_contract'}), (b {id: 'concept.cpp.return'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.recursion'}), (b {id: 'concept.c.function_def'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.recursion'}), (b {id: 'concept.cpp.function_decl'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.iterator_range'}), (b {id: 'concept.cpp.iterator'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.iterator_range'}), (b {id: 'concept.cpp.ranges'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.iterator_range'}), (b {id: 'concept.cpp.views'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.iterator_range'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.modern_cpp_ownership'}), (b {id: 'concept.cpp.raii'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.modern_cpp_ownership'}), (b {id: 'concept.cpp.move_semantics'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.modern_cpp_ownership'}), (b {id: 'concept.cpp.unique_ptr'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.modern_cpp_ownership'}), (b {id: 'concept.cpp.smart_pointer'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.oop_destruction'}), (b {id: 'concept.cpp.class'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.oop_destruction'}), (b {id: 'concept.cpp.inheritance'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.oop_destruction'}), (b {id: 'concept.cpp.destructor'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.oop_destruction'}), (b {id: 'concept.cpp.virtual_function'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.exception_safety'}), (b {id: 'concept.cpp.try_catch'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.exception_safety'}), (b {id: 'concept.cpp.noexcept'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.exception_safety'}), (b {id: 'concept.cpp.raii'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.formatting'}), (b {id: 'concept.c.formatted_io'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.formatting'}), (b {id: 'concept.cpp.format'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.formatting'}), (b {id: 'concept.cpp.print_functions'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.concurrency_wait'}), (b {id: 'concept.cpp.thread'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.concurrency_wait'}), (b {id: 'concept.cpp.mutex'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.concurrency_wait'}), (b {id: 'concept.cpp.condition_variable'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.concurrency_wait'}), (b {id: 'concept.cpp.atomic'}) MERGE (a)-[r:RECOMMENDS_CONCEPT]->(b);
MATCH (a {id: 'plan.loop_boundary'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.loop_boundary'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.array_indexing'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.array_indexing'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.array_indexing'}), (b {id: 'view.cpp_stl'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.pointer_lifetime'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.manual_memory'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.manual_memory'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.return_contract'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.recursion'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.iterator_range'}), (b {id: 'view.cpp_stl'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.iterator_range'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.modern_cpp_ownership'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.modern_cpp_ownership'}), (b {id: 'view.cpp_oop'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.oop_destruction'}), (b {id: 'view.cpp_oop'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.exception_safety'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.exception_safety'}), (b {id: 'view.cpp_oop'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.formatting'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.formatting'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'plan.concurrency_wait'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);"""
SUMMARY_JSON = r"""{
  "node_count": 112,
  "relationship_count": 480,
  "label_breakdown": {
    "ExplanationCategory": 10,
    "FeedbackPattern": 8,
    "ContextAnchorType": 6,
    "RemediationPlan": 12,
    "ExplanationTemplate": 19,
    "ExplanationStep": 57
  },
  "relationship_breakdown": {
    "SUBCATEGORY_OF": 9,
    "BELONGS_TO_CATEGORY": 19,
    "EXPLAINS_BUG": 24,
    "TRIGGERED_BY_RULE": 30,
    "TARGETS_MISCONCEPTION": 21,
    "SUGGESTS_FIX": 27,
    "REINFORCES_CONCEPT": 67,
    "VISIBLE_IN": 53,
    "USES_FEEDBACK_PATTERN": 65,
    "USES_CONTEXT_ANCHOR": 48,
    "RECOMMENDS_PLAN": 19,
    "CONSISTS_OF_STEP": 57,
    "RECOMMENDS_CONCEPT": 41
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
    "bug.uninitialized_value",
    "bug.use_after_free",
    "bug.use_after_move",
    "bug.vector_out_of_range",
    "bug.wrong_base_case",
    "bug.wrong_loop_condition",
    "concept.c.array",
    "concept.c.for",
    "concept.c.formatted_io",
    "concept.c.free",
    "concept.c.function_def",
    "concept.c.malloc",
    "concept.c.pointer",
    "concept.c.realloc",
    "concept.c.variable",
    "concept.c.while",
    "concept.cpp.array",
    "concept.cpp.atomic",
    "concept.cpp.class",
    "concept.cpp.condition_variable",
    "concept.cpp.copy_semantics",
    "concept.cpp.default_init",
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
    "concept.cpp.return",
    "concept.cpp.smart_pointer",
    "concept.cpp.string",
    "concept.cpp.thread",
    "concept.cpp.try_catch",
    "concept.cpp.unique_ptr",
    "concept.cpp.unordered_map",
    "concept.cpp.value_init",
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
    "fix.loop.init",
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
    "mis.array.index_value",
    "mis.array.last_index",
    "mis.exception.safety",
    "mis.format.specifier",
    "mis.iter.invalidate",
    "mis.loop.bound",
    "mis.loop.init",
    "mis.loop.progress",
    "mis.memory.auto_cleanup",
    "mis.move.validity",
    "mis.ownership.shared",
    "mis.pointer.free",
    "mis.pointer.null",
    "mis.recursion.base_case",
    "mis.recursion.progress",
    "mis.return.contract",
    "mis.virtual.destructor",
    "mis.wait.protocol",
    "rule.array.index_value_confusion",
    "rule.array.out_of_bounds.size_index",
    "rule.concurrent.missing_sync",
    "rule.concurrent.wait_protocol",
    "rule.format.modern_cpp_upgrade",
    "rule.format.specifier_mismatch",
    "rule.function.missing_return.cfg",
    "rule.function.missing_return.compiler",
    "rule.iterator.invalidation.modify_then_use",
    "rule.iterator.view_lifetime",
    "rule.loop.boundary.edge_case",
    "rule.loop.infinite.missing_update",
    "rule.loop.infinite.wrong_direction",
    "rule.loop.off_by_one.leq_length",
    "rule.loop.off_by_one.start_one",
    "rule.memory.double_free.flow",
    "rule.memory.leak.alloc_no_release",
    "rule.memory.leak.sanitizer",
    "rule.memory.uaf.sanitizer",
    "rule.memory.use_after_free.flow",
    "rule.meta.edge_case_boundary",
    "rule.move.use_after_move",
    "rule.oop.delete_base_no_virtual",
    "rule.oop.exception_safety",
    "rule.oop.rule_of_five",
    "rule.pointer.null_deref.ast",
    "rule.pointer.null_deref.clang",
    "rule.recursion.no_base_case",
    "rule.recursion.no_progress",
    "rule.recursion.unreachable_base",
    "view.algorithms",
    "view.c_pointers",
    "view.cpp_modern",
    "view.cpp_oop",
    "view.cpp_stl",
    "view.intro_c"
  ],
  "files": [
    "neo4j_explanation_feedback_nodes.csv",
    "neo4j_explanation_feedback_relationships.csv",
    "neo4j_explanation_feedback_seed.cypher",
    "build_neo4j_explanation_feedback_dataset.py"
  ]
}"""


def main() -> None:
    out_dir = Path('.')
    (out_dir / 'neo4j_explanation_feedback_nodes.csv').write_text(NODES_CSV, encoding='utf-8')
    (out_dir / 'neo4j_explanation_feedback_relationships.csv').write_text(RELATIONSHIPS_CSV, encoding='utf-8')
    (out_dir / 'neo4j_explanation_feedback_seed.cypher').write_text(SEED_CYPHER, encoding='utf-8')
    (out_dir / 'neo4j_explanation_feedback_summary.json').write_text(SUMMARY_JSON, encoding='utf-8')
    print('Explanation / Feedback dataset files created successfully.')


if __name__ == '__main__':
    main()
