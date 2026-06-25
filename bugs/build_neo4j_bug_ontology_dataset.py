"""Recreate the Neo4j Bug Ontology dataset attached to the latest concept graph.

This script emits the following files in the current working directory:
- neo4j_bug_ontology_nodes.csv
- neo4j_bug_ontology_relationships.csv
- neo4j_bug_ontology_seed.cypher
- neo4j_bug_ontology_summary.json

The dataset is intended to attach to the existing latest-only concept graph
(C23 + C++23 snapshot) via shared concept IDs.
"""

from pathlib import Path

NODES_CSV = r"""description,detectionEase,fixType,id,impactLevel,label,level,misconceptionType,name,pedagogicalPriority,severity,standardVersion,status,symptomType
Root category for all programming bugs,,,bugcat.root,,BugCategory,top,,ProgrammingBugRoot,,,latest,active,
Bugs caused by incorrect program logic,,,bugcat.logic,,BugCategory,top,,LogicError,,,latest,active,
Bugs manifested during execution,,,bugcat.runtime,,BugCategory,top,,RuntimeError,,,latest,active,
"Bugs involving allocation, ownership, lifetime, or pointer/reference misuse",,,bugcat.memory,,BugCategory,top,,MemoryError,,,latest,active,
Bugs caused by wrong algorithm or incomplete strategy,,,bugcat.algorithm,,BugCategory,top,,AlgorithmicError,,,latest,active,
Bugs caused by incorrect use of standard library or language API,,,bugcat.api,,BugCategory,top,,APIAndLibraryMisuse,,,latest,active,
Bugs caused by synchronization or memory ordering mistakes,,,bugcat.concurrency,,BugCategory,top,,ConcurrencyError,,,latest,active,
"Logic bugs in loop initialization, condition, exit, or progress",,,bugcat.logic.loop,,BugCategory,sub,,LoopError,,,latest,active,
"Logic bugs around arrays, indexing, and traversal",,,bugcat.logic.array,,BugCategory,sub,,ArrayAndIndexError,,,latest,active,
Bugs around return values and basic contract behavior,,,bugcat.logic.function,,BugCategory,sub,,FunctionContractError,,,latest,active,
Base case or progress mistakes in recursive algorithms,,,bugcat.algorithm.recursion,,BugCategory,sub,,RecursionError,,,latest,active,
"Pointer lifetime, dereference, and ownership mistakes",,,bugcat.memory.pointer,,BugCategory,sub,,PointerLifetimeError,,,latest,active,
Modern C++ lifetime and move/ownership issues,,,bugcat.memory.cpp,,BugCategory,sub,,ModernCppLifetimeError,,,latest,active,
Iterator invalidation and range misuse,,,bugcat.api.iterator,,BugCategory,sub,,IteratorAndRangeError,,,latest,active,
Formatted I/O or output API misuse,,,bugcat.api.io,,BugCategory,sub,,IOAndFormattingError,,,latest,active,
"Waiting, locking, and thread coordination mistakes",,,bugcat.concurrency.sync,,BugCategory,sub,,SynchronizationError,,,latest,active,
Belief that loop boundaries include one more or one fewer valid iteration than they actually do.,,,mis.loop.bound,,Misconception,,conceptual,MisunderstandLoopBoundary,,,,active,
Belief that a loop progresses correctly even when state is not updated toward termination.,,,mis.loop.progress,,Misconception,,conceptual,MisunderstandLoopProgress,,,,active,
Incorrect mental model of initialization value or start state of a loop variable.,,,mis.loop.init,,Misconception,,conceptual,MisunderstandLoopInitialization,,,,active,
Belief that an array of size n has valid last index n instead of n-1.,,,mis.array.last_index,,Misconception,,conceptual,MisunderstandLastValidIndex,,,,active,
Confusion between element position and element contents during traversal or update.,,,mis.array.index_value,,Misconception,,conceptual,ConfuseIndexWithValue,,,,active,
Belief that a pointer can be dereferenced safely without checking validity or lifetime.,,,mis.pointer.null,,Misconception,,pointer,AssumePointerIsAlwaysValid,,,,active,
Belief that a pointer remains valid after free/delete.,,,mis.pointer.free,,Misconception,,pointer,AssumeFreedPointerStillUsable,,,,active,
Belief that manually allocated memory is automatically released when forgotten.,,,mis.memory.auto_cleanup,,Misconception,,memory,AssumeManualMemoryCleansItself,,,,active,
Belief that omitting a required return value has no observable consequence.,,,mis.return.contract,,Misconception,,function,AssumeMissingReturnIsBenign,,,,active,
Belief that recursion can terminate correctly without a precise base case.,,,mis.recursion.base_case,,Misconception,,algorithm,MisunderstandBaseCase,,,,active,
Belief that recursive calls need not reduce problem size toward the base case.,,,mis.recursion.progress,,Misconception,,algorithm,MisunderstandRecursiveProgress,,,,active,
Belief that iterators remain valid after container modifications that invalidate them.,,,mis.iter.invalidate,,Misconception,,stl,MisunderstandIteratorInvalidation,,,,active,
Belief that an object is fully reusable after its resources were moved away.,,,mis.move.validity,,Misconception,,modern-cpp,MisunderstandMovedFromState,,,,active,
"Confusion about single ownership, shared ownership, and non-owning references.",,,mis.ownership.shared,,Misconception,,modern-cpp,MisunderstandOwnershipModel,,,,active,
Belief that deleting through a base pointer is safe without a virtual destructor.,,,mis.virtual.destructor,,Misconception,,oop,MisunderstandPolymorphicDestruction,,,,active,
Belief that resource cleanup remains correct under exceptional control flow without RAII.,,,mis.exception.safety,,Misconception,,modern-cpp,MisunderstandExceptionSafety,,,,active,
Belief that any format specifier can print any type without mismatch problems.,,,mis.format.specifier,,Misconception,,io,MisunderstandFormatSpecifierTypeMatch,,,,active,
Belief that waiting on conditions does not require disciplined locking and predicate checks.,,,mis.wait.protocol,,Misconception,,concurrency,MisunderstandConditionWaitingProtocol,,,,active,
Program runs but produces wrong output for one or more cases.,,,sym.incorrect_output,,Symptom,,,IncorrectOutput,,,,active,observable
Program does not terminate in expected time or gets stuck.,,,sym.hangs,,Symptom,,,ProgramHangs,,,,active,runtime
Program exceeds time limit or performance budget.,,,sym.timeout,,Symptom,,,Timeout,,,,active,runtime
"Program aborts, segfaults, or terminates unexpectedly.",,,sym.crash,,Symptom,,,Crash,,,,active,runtime
Program accesses array or container outside valid range.,,,sym.out_of_bounds,,Symptom,,,OutOfBoundsAccess,,,,active,runtime
Program dereferences a null pointer or invalid nullable handle.,,,sym.null_deref,,Symptom,,,NullDereference,,,,active,runtime
Program accesses memory after it has been released.,,,sym.use_after_free,,Symptom,,,UseAfterFreeSymptom,,,,active,runtime
Memory usage grows because allocations are not released.,,,sym.memory_growth,,Symptom,,,UnboundedMemoryGrowth,,,,active,runtime
Iterator or view is used after invalidation.,,,sym.iterator_invalid,,Symptom,,,IteratorInvalidAccess,,,,active,runtime
A non-void function path finishes without returning a value.,,,sym.warn_return,,Symptom,,,ControlReachesEndOfNonVoid,,,,active,static
Same ownership resource is released multiple times.,,,sym.double_release,,Symptom,,,DoubleReleaseSymptom,,,,active,runtime
Output or state varies across runs due to synchronization mistakes.,,,sym.racey_behavior,,Symptom,,,NonDeterministicBehavior,,,,active,runtime
Program violates problem specification and returns incorrect results.,,,eff.wrong_answer,medium,Effect,,,WrongAnswer,,,,active,
Execution enters undefined behavior with unstable or unsafe outcomes.,,,eff.undefined_behavior,high,Effect,,,UndefinedBehavior,,,,active,
Program consumes memory or CPU excessively.,,,eff.resource_exhaustion,high,Effect,,,ResourceExhaustion,,,,active,
Bug may create memory corruption or exploitable behavior.,,,eff.security_risk,high,Effect,,,SecurityRisk,,,,active,
Program never reaches a terminating state for some inputs.,,,eff.nontermination,high,Effect,,,NonTermination,,,,active,
Program corrupts values or object state in memory.,,,eff.data_corruption,high,Effect,,,DataCorruption,,,,active,
Program leaves resources unreleased under some control paths.,,,eff.partial_cleanup,medium,Effect,,,PartialCleanup,,,,active,
Program violates expected library or language usage contract.,,,eff.api_contract_violation,medium,Effect,,,APIContractViolation,,,,active,
Replace incorrect boundary condition with the correct inclusive/exclusive condition.,,local-code-fix,fix.loop.bound,,FixStrategy,,,AdjustLoopBoundary,,,,active,
Update loop state so each iteration moves toward termination.,,local-code-fix,fix.loop.progress,,FixStrategy,,,EnsureLoopProgress,,,,active,
Initialize loop variable from the intended starting state.,,local-code-fix,fix.loop.init,,FixStrategy,,,CorrectLoopInitialization,,,,active,
Constrain index to valid range and use length-based reasoning.,,local-code-fix,fix.array.bound,,FixStrategy,,,ValidateArrayBoundary,,,,active,
Use distinct variables or logic for index and element value.,,local-code-fix,fix.array.index_value,,FixStrategy,,,SeparateIndexAndValueRoles,,,,active,
"Check for null or impossible state before dereferencing, or redesign ownership.",,defensive-fix,fix.null.check,,FixStrategy,,,CheckPointerBeforeDereference,,,,active,
Ensure each allocated resource has one matching release.,,ownership-fix,fix.release.once,,FixStrategy,,,ReleaseExactlyOnce,,,,active,
Clear or stop using handles after free/delete or hand over ownership safely.,,ownership-fix,fix.no_use_after_release,,FixStrategy,,,InvalidateAfterRelease,,,,active,
Tie resource lifetime to object lifetime using RAII wrappers and automatic cleanup.,,design-fix,fix.use_raii,,FixStrategy,,,AdoptRAII,,,,active,
Replace raw owning pointers with std::unique_ptr or std::shared_ptr as appropriate.,,modern-cpp-fix,fix.smart_pointer,,FixStrategy,,,UseSmartPointer,,,,active,
Add explicit valid return statements on every control path of a non-void function.,,local-code-fix,fix.return,,FixStrategy,,,ReturnOnAllPaths,,,,active,
Add a precise recursive base case that stops recursion.,,algorithm-fix,fix.recursion.base,,FixStrategy,,,DefineBaseCase,,,,active,
Ensure each recursive call reduces input toward the base case.,,algorithm-fix,fix.recursion.progress,,FixStrategy,,,ReduceProblemSize,,,,active,
Reacquire iterator/reference after container operations that may invalidate it.,,stl-fix,fix.iterator.refresh,,FixStrategy,,,RefreshIteratorAfterModification,,,,active,
Use moved-from objects only in documented valid ways or reinitialize them.,,modern-cpp-fix,fix.move.use_state,,FixStrategy,,,DoNotDependOnMovedFromValue,,,,active,
Make base destructor virtual when deleting derived objects via base pointers.,,oop-fix,fix.virtual_destructor,,FixStrategy,,,AddVirtualDestructor,,,,active,
Use the correct format specifier for the actual argument type.,,io-fix,fix.format.match,,FixStrategy,,,MatchFormatSpecifierToType,,,,active,
Protect shared state with locks and wait in a predicate-based loop.,,concurrency-fix,fix.condition_wait,,FixStrategy,,,UsePredicateWaitPattern,,,,active,
Loop or indexing logic uses a boundary that is one too small or one too large.,moderate,,bug.off_by_one,,ProgrammingBug,,,OffByOneError,critical,medium,latest,active,
Loop exit condition is unreachable or loop state never progresses to termination.,easy,,bug.infinite_loop,,ProgrammingBug,,,InfiniteLoopError,critical,high,latest,active,
Loop variable or progress state is not updated correctly inside or by the loop header.,easy,,bug.missing_loop_update,,ProgrammingBug,,,MissingLoopUpdateError,high,high,latest,active,
Loop starts from an incorrect initial state or index.,easy,,bug.wrong_loop_init,,ProgrammingBug,,,WrongLoopInitializationError,high,medium,latest,active,
Loop condition expresses the wrong continuation rule.,moderate,,bug.wrong_loop_condition,,ProgrammingBug,,,WrongLoopConditionError,high,medium,latest,active,
Built-in array is indexed outside its valid bounds.,moderate,,bug.array_out_of_bounds,,ProgrammingBug,,,ArrayOutOfBoundsError,critical,high,latest,active,
Logic confuses array index with array element value.,moderate,,bug.index_value_confusion,,ProgrammingBug,,,IndexValueConfusionError,high,medium,latest,active,
Null or otherwise invalid pointer/reference-like state is dereferenced.,easy,,bug.null_dereference,,ProgrammingBug,,,NullDereferenceError,critical,high,latest,active,
Dynamically allocated memory is not released when no longer needed.,moderate,,bug.memory_leak,,ProgrammingBug,,,MemoryLeakError,high,medium,latest,active,
Memory is accessed after the corresponding allocation was released.,hard,,bug.use_after_free,,ProgrammingBug,,,UseAfterFreeError,critical,high,latest,active,
The same allocation or ownership resource is released more than once.,moderate,,bug.double_free,,ProgrammingBug,,,DoubleFreeError,critical,high,latest,active,
Pointer continues to reference storage whose lifetime has ended.,moderate,,bug.dangling_pointer,,ProgrammingBug,,,DanglingPointerError,high,high,latest,active,
Variable or object state is read before receiving a valid initialization.,moderate,,bug.uninitialized_value,,ProgrammingBug,,,UninitializedValueUsageError,high,high,latest,active,
A non-void function can complete without returning a value.,easy,,bug.missing_return,,ProgrammingBug,,,MissingReturnValueError,high,medium,latest,active,
Recursive algorithm uses an incorrect or unreachable base case.,moderate,,bug.wrong_base_case,,ProgrammingBug,,,WrongRecursionBaseCaseError,high,high,latest,active,
Recursive calls do not reduce problem size toward the base case.,moderate,,bug.no_recursive_progress,,ProgrammingBug,,,NoRecursiveProgressError,high,high,latest,active,
"Code uses iterators, references, or views after container modification invalidates them.",hard,,bug.iterator_invalidation,,ProgrammingBug,,,IteratorInvalidationError,critical,high,latest,active,
Code relies on moved-from object state as if it were unchanged.,moderate,,bug.use_after_move,,ProgrammingBug,,,UseAfterMoveError,high,medium,latest,active,
Deleting a derived object through a base pointer without a virtual destructor.,easy,,bug.missing_virtual_destructor,,ProgrammingBug,,,MissingVirtualDestructorError,high,high,latest,active,
Custom resource-owning type defines inconsistent copy/move/destructor behavior.,hard,,bug.rule_of_five,,ProgrammingBug,,,RuleOfFiveViolation,medium,medium,latest,active,
Resource cleanup or object invariants break under exception paths.,hard,,bug.exception_safety,,ProgrammingBug,,,ExceptionSafetyViolation,medium,medium,latest,active,
std::vector access goes outside valid logical range.,moderate,,bug.vector_out_of_range,,ProgrammingBug,,,VectorOutOfRangeError,high,medium,latest,active,
Formatted I/O uses a specifier that does not match argument type.,easy,,bug.format_specifier_mismatch,,ProgrammingBug,,,FormatSpecifierMismatchError,high,medium,latest,active,
Wait/notify is used without proper locking or predicate-based rechecking.,hard,,bug.condition_variable_misuse,,ProgrammingBug,,,ConditionVariableMisuseError,medium,high,latest,active,
Memory usage grows due to leaks or incomplete destruction.,,,eff.memory_growth,medium,Effect,,,MemoryGrowth,,,,active,
"""
RELATIONSHIPS_CSV = r"""end_id,start_id,type
bugcat.root,bugcat.logic,SUBCATEGORY_OF
bugcat.root,bugcat.runtime,SUBCATEGORY_OF
bugcat.root,bugcat.memory,SUBCATEGORY_OF
bugcat.root,bugcat.algorithm,SUBCATEGORY_OF
bugcat.root,bugcat.api,SUBCATEGORY_OF
bugcat.root,bugcat.concurrency,SUBCATEGORY_OF
bugcat.logic,bugcat.logic.loop,SUBCATEGORY_OF
bugcat.logic,bugcat.logic.array,SUBCATEGORY_OF
bugcat.logic,bugcat.logic.function,SUBCATEGORY_OF
bugcat.algorithm,bugcat.algorithm.recursion,SUBCATEGORY_OF
bugcat.memory,bugcat.memory.pointer,SUBCATEGORY_OF
bugcat.memory,bugcat.memory.cpp,SUBCATEGORY_OF
bugcat.api,bugcat.api.iterator,SUBCATEGORY_OF
bugcat.api,bugcat.api.io,SUBCATEGORY_OF
bugcat.concurrency,bugcat.concurrency.sync,SUBCATEGORY_OF
bugcat.logic.array,bug.off_by_one,BELONGS_TO_CATEGORY
bugcat.logic.loop,bug.infinite_loop,BELONGS_TO_CATEGORY
bugcat.logic.loop,bug.missing_loop_update,BELONGS_TO_CATEGORY
bugcat.logic.loop,bug.wrong_loop_init,BELONGS_TO_CATEGORY
bugcat.logic.loop,bug.wrong_loop_condition,BELONGS_TO_CATEGORY
bugcat.logic.array,bug.array_out_of_bounds,BELONGS_TO_CATEGORY
bugcat.logic.array,bug.index_value_confusion,BELONGS_TO_CATEGORY
bugcat.memory.pointer,bug.null_dereference,BELONGS_TO_CATEGORY
bugcat.memory.pointer,bug.memory_leak,BELONGS_TO_CATEGORY
bugcat.memory.pointer,bug.use_after_free,BELONGS_TO_CATEGORY
bugcat.memory.pointer,bug.double_free,BELONGS_TO_CATEGORY
bugcat.memory.pointer,bug.dangling_pointer,BELONGS_TO_CATEGORY
bugcat.runtime,bug.uninitialized_value,BELONGS_TO_CATEGORY
bugcat.logic.function,bug.missing_return,BELONGS_TO_CATEGORY
bugcat.algorithm.recursion,bug.wrong_base_case,BELONGS_TO_CATEGORY
bugcat.algorithm.recursion,bug.no_recursive_progress,BELONGS_TO_CATEGORY
bugcat.api.iterator,bug.iterator_invalidation,BELONGS_TO_CATEGORY
bugcat.memory.cpp,bug.use_after_move,BELONGS_TO_CATEGORY
bugcat.memory.cpp,bug.missing_virtual_destructor,BELONGS_TO_CATEGORY
bugcat.memory.cpp,bug.rule_of_five,BELONGS_TO_CATEGORY
bugcat.memory.cpp,bug.exception_safety,BELONGS_TO_CATEGORY
bugcat.api.iterator,bug.vector_out_of_range,BELONGS_TO_CATEGORY
bugcat.api.io,bug.format_specifier_mismatch,BELONGS_TO_CATEGORY
bugcat.concurrency.sync,bug.condition_variable_misuse,BELONGS_TO_CATEGORY
concept.c.array,bug.off_by_one,OCCURS_IN_CONCEPT
concept.c.for,bug.off_by_one,OCCURS_IN_CONCEPT
concept.cpp.array,bug.off_by_one,OCCURS_IN_CONCEPT
concept.cpp.vector,bug.off_by_one,OCCURS_IN_CONCEPT
concept.cpp.range_for,bug.off_by_one,OCCURS_IN_CONCEPT
concept.c.for,bug.infinite_loop,OCCURS_IN_CONCEPT
concept.c.while,bug.infinite_loop,OCCURS_IN_CONCEPT
concept.cpp.for,bug.infinite_loop,OCCURS_IN_CONCEPT
concept.cpp.while,bug.infinite_loop,OCCURS_IN_CONCEPT
concept.cpp.range_for,bug.infinite_loop,OCCURS_IN_CONCEPT
concept.c.for,bug.missing_loop_update,OCCURS_IN_CONCEPT
concept.c.while,bug.missing_loop_update,OCCURS_IN_CONCEPT
concept.cpp.for,bug.missing_loop_update,OCCURS_IN_CONCEPT
concept.cpp.while,bug.missing_loop_update,OCCURS_IN_CONCEPT
concept.c.for,bug.wrong_loop_init,OCCURS_IN_CONCEPT
concept.cpp.for,bug.wrong_loop_init,OCCURS_IN_CONCEPT
concept.cpp.range_for,bug.wrong_loop_init,OCCURS_IN_CONCEPT
concept.c.for,bug.wrong_loop_condition,OCCURS_IN_CONCEPT
concept.c.while,bug.wrong_loop_condition,OCCURS_IN_CONCEPT
concept.cpp.for,bug.wrong_loop_condition,OCCURS_IN_CONCEPT
concept.cpp.while,bug.wrong_loop_condition,OCCURS_IN_CONCEPT
concept.cpp.if,bug.wrong_loop_condition,OCCURS_IN_CONCEPT
concept.c.array,bug.array_out_of_bounds,OCCURS_IN_CONCEPT
concept.cpp.array,bug.array_out_of_bounds,OCCURS_IN_CONCEPT
concept.cpp.vector,bug.array_out_of_bounds,OCCURS_IN_CONCEPT
concept.c.array,bug.index_value_confusion,OCCURS_IN_CONCEPT
concept.cpp.array,bug.index_value_confusion,OCCURS_IN_CONCEPT
concept.cpp.vector,bug.index_value_confusion,OCCURS_IN_CONCEPT
concept.c.pointer,bug.null_dereference,OCCURS_IN_CONCEPT
concept.cpp.pointer,bug.null_dereference,OCCURS_IN_CONCEPT
concept.cpp.smart_pointer,bug.null_dereference,OCCURS_IN_CONCEPT
concept.c.malloc,bug.memory_leak,OCCURS_IN_CONCEPT
concept.c.calloc,bug.memory_leak,OCCURS_IN_CONCEPT
concept.c.realloc,bug.memory_leak,OCCURS_IN_CONCEPT
concept.cpp.new_delete,bug.memory_leak,OCCURS_IN_CONCEPT
concept.cpp.smart_pointer,bug.memory_leak,OCCURS_IN_CONCEPT
concept.cpp.raii,bug.memory_leak,OCCURS_IN_CONCEPT
concept.c.free,bug.use_after_free,OCCURS_IN_CONCEPT
concept.cpp.new_delete,bug.use_after_free,OCCURS_IN_CONCEPT
concept.c.pointer,bug.use_after_free,OCCURS_IN_CONCEPT
concept.cpp.pointer,bug.use_after_free,OCCURS_IN_CONCEPT
concept.c.free,bug.double_free,OCCURS_IN_CONCEPT
concept.cpp.new_delete,bug.double_free,OCCURS_IN_CONCEPT
concept.cpp.smart_pointer,bug.double_free,OCCURS_IN_CONCEPT
concept.c.pointer,bug.dangling_pointer,OCCURS_IN_CONCEPT
concept.cpp.pointer,bug.dangling_pointer,OCCURS_IN_CONCEPT
concept.cpp.reference,bug.dangling_pointer,OCCURS_IN_CONCEPT
concept.c.variable,bug.uninitialized_value,OCCURS_IN_CONCEPT
concept.cpp.default_init,bug.uninitialized_value,OCCURS_IN_CONCEPT
concept.cpp.value_init,bug.uninitialized_value,OCCURS_IN_CONCEPT
concept.c.function_def,bug.missing_return,OCCURS_IN_CONCEPT
concept.cpp.function_decl,bug.missing_return,OCCURS_IN_CONCEPT
concept.cpp.return,bug.missing_return,OCCURS_IN_CONCEPT
concept.cpp.function_decl,bug.wrong_base_case,OCCURS_IN_CONCEPT
concept.cpp.lambda,bug.wrong_base_case,OCCURS_IN_CONCEPT
concept.c.function_def,bug.wrong_base_case,OCCURS_IN_CONCEPT
concept.cpp.function_decl,bug.no_recursive_progress,OCCURS_IN_CONCEPT
concept.c.function_def,bug.no_recursive_progress,OCCURS_IN_CONCEPT
concept.cpp.iterator,bug.iterator_invalidation,OCCURS_IN_CONCEPT
concept.cpp.vector,bug.iterator_invalidation,OCCURS_IN_CONCEPT
concept.cpp.map,bug.iterator_invalidation,OCCURS_IN_CONCEPT
concept.cpp.unordered_map,bug.iterator_invalidation,OCCURS_IN_CONCEPT
concept.cpp.ranges,bug.iterator_invalidation,OCCURS_IN_CONCEPT
concept.cpp.views,bug.iterator_invalidation,OCCURS_IN_CONCEPT
concept.cpp.move_semantics,bug.use_after_move,OCCURS_IN_CONCEPT
concept.cpp.unique_ptr,bug.use_after_move,OCCURS_IN_CONCEPT
concept.cpp.string,bug.use_after_move,OCCURS_IN_CONCEPT
concept.cpp.vector,bug.use_after_move,OCCURS_IN_CONCEPT
concept.cpp.class,bug.missing_virtual_destructor,OCCURS_IN_CONCEPT
concept.cpp.inheritance,bug.missing_virtual_destructor,OCCURS_IN_CONCEPT
concept.cpp.virtual_function,bug.missing_virtual_destructor,OCCURS_IN_CONCEPT
concept.cpp.destructor,bug.missing_virtual_destructor,OCCURS_IN_CONCEPT
concept.cpp.class,bug.rule_of_five,OCCURS_IN_CONCEPT
concept.cpp.destructor,bug.rule_of_five,OCCURS_IN_CONCEPT
concept.cpp.copy_semantics,bug.rule_of_five,OCCURS_IN_CONCEPT
concept.cpp.move_semantics,bug.rule_of_five,OCCURS_IN_CONCEPT
concept.cpp.raii,bug.rule_of_five,OCCURS_IN_CONCEPT
concept.cpp.try_catch,bug.exception_safety,OCCURS_IN_CONCEPT
concept.cpp.noexcept,bug.exception_safety,OCCURS_IN_CONCEPT
concept.cpp.raii,bug.exception_safety,OCCURS_IN_CONCEPT
concept.cpp.smart_pointer,bug.exception_safety,OCCURS_IN_CONCEPT
concept.cpp.vector,bug.vector_out_of_range,OCCURS_IN_CONCEPT
concept.cpp.range_for,bug.vector_out_of_range,OCCURS_IN_CONCEPT
concept.c.formatted_io,bug.format_specifier_mismatch,OCCURS_IN_CONCEPT
concept.cpp.format,bug.format_specifier_mismatch,OCCURS_IN_CONCEPT
concept.cpp.print_functions,bug.format_specifier_mismatch,OCCURS_IN_CONCEPT
concept.cpp.thread,bug.condition_variable_misuse,OCCURS_IN_CONCEPT
concept.cpp.mutex,bug.condition_variable_misuse,OCCURS_IN_CONCEPT
concept.cpp.condition_variable,bug.condition_variable_misuse,OCCURS_IN_CONCEPT
concept.cpp.atomic,bug.condition_variable_misuse,OCCURS_IN_CONCEPT
mis.loop.bound,bug.off_by_one,CAUSED_BY_MISCONCEPTION
mis.array.last_index,bug.off_by_one,CAUSED_BY_MISCONCEPTION
mis.loop.progress,bug.infinite_loop,CAUSED_BY_MISCONCEPTION
mis.loop.progress,bug.missing_loop_update,CAUSED_BY_MISCONCEPTION
mis.loop.init,bug.wrong_loop_init,CAUSED_BY_MISCONCEPTION
mis.loop.bound,bug.wrong_loop_condition,CAUSED_BY_MISCONCEPTION
mis.array.last_index,bug.array_out_of_bounds,CAUSED_BY_MISCONCEPTION
mis.array.index_value,bug.index_value_confusion,CAUSED_BY_MISCONCEPTION
mis.pointer.null,bug.null_dereference,CAUSED_BY_MISCONCEPTION
mis.memory.auto_cleanup,bug.memory_leak,CAUSED_BY_MISCONCEPTION
mis.pointer.free,bug.use_after_free,CAUSED_BY_MISCONCEPTION
mis.pointer.free,bug.double_free,CAUSED_BY_MISCONCEPTION
mis.ownership.shared,bug.double_free,CAUSED_BY_MISCONCEPTION
mis.pointer.free,bug.dangling_pointer,CAUSED_BY_MISCONCEPTION
mis.return.contract,bug.missing_return,CAUSED_BY_MISCONCEPTION
mis.recursion.base_case,bug.wrong_base_case,CAUSED_BY_MISCONCEPTION
mis.recursion.progress,bug.no_recursive_progress,CAUSED_BY_MISCONCEPTION
mis.iter.invalidate,bug.iterator_invalidation,CAUSED_BY_MISCONCEPTION
mis.move.validity,bug.use_after_move,CAUSED_BY_MISCONCEPTION
mis.virtual.destructor,bug.missing_virtual_destructor,CAUSED_BY_MISCONCEPTION
mis.ownership.shared,bug.rule_of_five,CAUSED_BY_MISCONCEPTION
mis.exception.safety,bug.exception_safety,CAUSED_BY_MISCONCEPTION
mis.format.specifier,bug.format_specifier_mismatch,CAUSED_BY_MISCONCEPTION
mis.wait.protocol,bug.condition_variable_misuse,CAUSED_BY_MISCONCEPTION
sym.incorrect_output,bug.off_by_one,HAS_SYMPTOM
sym.out_of_bounds,bug.off_by_one,HAS_SYMPTOM
sym.hangs,bug.infinite_loop,HAS_SYMPTOM
sym.timeout,bug.infinite_loop,HAS_SYMPTOM
sym.hangs,bug.missing_loop_update,HAS_SYMPTOM
sym.timeout,bug.missing_loop_update,HAS_SYMPTOM
sym.incorrect_output,bug.wrong_loop_init,HAS_SYMPTOM
sym.incorrect_output,bug.wrong_loop_condition,HAS_SYMPTOM
sym.out_of_bounds,bug.array_out_of_bounds,HAS_SYMPTOM
sym.crash,bug.array_out_of_bounds,HAS_SYMPTOM
sym.incorrect_output,bug.index_value_confusion,HAS_SYMPTOM
sym.null_deref,bug.null_dereference,HAS_SYMPTOM
sym.crash,bug.null_dereference,HAS_SYMPTOM
sym.memory_growth,bug.memory_leak,HAS_SYMPTOM
sym.use_after_free,bug.use_after_free,HAS_SYMPTOM
sym.crash,bug.use_after_free,HAS_SYMPTOM
sym.double_release,bug.double_free,HAS_SYMPTOM
sym.crash,bug.double_free,HAS_SYMPTOM
sym.crash,bug.dangling_pointer,HAS_SYMPTOM
sym.incorrect_output,bug.dangling_pointer,HAS_SYMPTOM
sym.incorrect_output,bug.uninitialized_value,HAS_SYMPTOM
sym.crash,bug.uninitialized_value,HAS_SYMPTOM
sym.warn_return,bug.missing_return,HAS_SYMPTOM
sym.incorrect_output,bug.missing_return,HAS_SYMPTOM
sym.hangs,bug.wrong_base_case,HAS_SYMPTOM
sym.incorrect_output,bug.wrong_base_case,HAS_SYMPTOM
sym.hangs,bug.no_recursive_progress,HAS_SYMPTOM
sym.timeout,bug.no_recursive_progress,HAS_SYMPTOM
sym.iterator_invalid,bug.iterator_invalidation,HAS_SYMPTOM
sym.crash,bug.iterator_invalidation,HAS_SYMPTOM
sym.incorrect_output,bug.use_after_move,HAS_SYMPTOM
sym.memory_growth,bug.missing_virtual_destructor,HAS_SYMPTOM
sym.crash,bug.rule_of_five,HAS_SYMPTOM
sym.incorrect_output,bug.rule_of_five,HAS_SYMPTOM
sym.crash,bug.exception_safety,HAS_SYMPTOM
sym.memory_growth,bug.exception_safety,HAS_SYMPTOM
sym.out_of_bounds,bug.vector_out_of_range,HAS_SYMPTOM
sym.crash,bug.vector_out_of_range,HAS_SYMPTOM
sym.incorrect_output,bug.format_specifier_mismatch,HAS_SYMPTOM
sym.crash,bug.format_specifier_mismatch,HAS_SYMPTOM
sym.hangs,bug.condition_variable_misuse,HAS_SYMPTOM
sym.racey_behavior,bug.condition_variable_misuse,HAS_SYMPTOM
eff.wrong_answer,bug.off_by_one,HAS_EFFECT
eff.undefined_behavior,bug.off_by_one,HAS_EFFECT
eff.nontermination,bug.infinite_loop,HAS_EFFECT
eff.resource_exhaustion,bug.infinite_loop,HAS_EFFECT
eff.nontermination,bug.missing_loop_update,HAS_EFFECT
eff.wrong_answer,bug.wrong_loop_init,HAS_EFFECT
eff.wrong_answer,bug.wrong_loop_condition,HAS_EFFECT
eff.undefined_behavior,bug.array_out_of_bounds,HAS_EFFECT
eff.security_risk,bug.array_out_of_bounds,HAS_EFFECT
eff.wrong_answer,bug.index_value_confusion,HAS_EFFECT
eff.undefined_behavior,bug.null_dereference,HAS_EFFECT
eff.security_risk,bug.null_dereference,HAS_EFFECT
eff.resource_exhaustion,bug.memory_leak,HAS_EFFECT
eff.partial_cleanup,bug.memory_leak,HAS_EFFECT
eff.undefined_behavior,bug.use_after_free,HAS_EFFECT
eff.security_risk,bug.use_after_free,HAS_EFFECT
eff.data_corruption,bug.use_after_free,HAS_EFFECT
eff.undefined_behavior,bug.double_free,HAS_EFFECT
eff.security_risk,bug.double_free,HAS_EFFECT
eff.undefined_behavior,bug.dangling_pointer,HAS_EFFECT
eff.data_corruption,bug.dangling_pointer,HAS_EFFECT
eff.undefined_behavior,bug.uninitialized_value,HAS_EFFECT
eff.wrong_answer,bug.uninitialized_value,HAS_EFFECT
eff.undefined_behavior,bug.missing_return,HAS_EFFECT
eff.wrong_answer,bug.missing_return,HAS_EFFECT
eff.nontermination,bug.wrong_base_case,HAS_EFFECT
eff.wrong_answer,bug.wrong_base_case,HAS_EFFECT
eff.nontermination,bug.no_recursive_progress,HAS_EFFECT
eff.undefined_behavior,bug.iterator_invalidation,HAS_EFFECT
eff.api_contract_violation,bug.iterator_invalidation,HAS_EFFECT
eff.wrong_answer,bug.use_after_move,HAS_EFFECT
eff.api_contract_violation,bug.use_after_move,HAS_EFFECT
eff.partial_cleanup,bug.missing_virtual_destructor,HAS_EFFECT
eff.data_corruption,bug.rule_of_five,HAS_EFFECT
eff.partial_cleanup,bug.rule_of_five,HAS_EFFECT
eff.partial_cleanup,bug.exception_safety,HAS_EFFECT
eff.data_corruption,bug.exception_safety,HAS_EFFECT
eff.api_contract_violation,bug.vector_out_of_range,HAS_EFFECT
eff.wrong_answer,bug.vector_out_of_range,HAS_EFFECT
eff.api_contract_violation,bug.format_specifier_mismatch,HAS_EFFECT
eff.wrong_answer,bug.format_specifier_mismatch,HAS_EFFECT
eff.nontermination,bug.condition_variable_misuse,HAS_EFFECT
eff.data_corruption,bug.condition_variable_misuse,HAS_EFFECT
fix.loop.bound,bug.off_by_one,FIXED_BY
fix.array.bound,bug.off_by_one,FIXED_BY
fix.loop.progress,bug.infinite_loop,FIXED_BY
fix.loop.bound,bug.infinite_loop,FIXED_BY
fix.loop.progress,bug.missing_loop_update,FIXED_BY
fix.loop.init,bug.wrong_loop_init,FIXED_BY
fix.loop.bound,bug.wrong_loop_condition,FIXED_BY
fix.array.bound,bug.array_out_of_bounds,FIXED_BY
fix.array.index_value,bug.index_value_confusion,FIXED_BY
fix.null.check,bug.null_dereference,FIXED_BY
fix.smart_pointer,bug.null_dereference,FIXED_BY
fix.release.once,bug.memory_leak,FIXED_BY
fix.use_raii,bug.memory_leak,FIXED_BY
fix.smart_pointer,bug.memory_leak,FIXED_BY
fix.no_use_after_release,bug.use_after_free,FIXED_BY
fix.use_raii,bug.use_after_free,FIXED_BY
fix.smart_pointer,bug.use_after_free,FIXED_BY
fix.release.once,bug.double_free,FIXED_BY
fix.no_use_after_release,bug.double_free,FIXED_BY
fix.no_use_after_release,bug.dangling_pointer,FIXED_BY
fix.smart_pointer,bug.dangling_pointer,FIXED_BY
fix.loop.init,bug.uninitialized_value,FIXED_BY
fix.return,bug.missing_return,FIXED_BY
fix.recursion.base,bug.wrong_base_case,FIXED_BY
fix.recursion.progress,bug.no_recursive_progress,FIXED_BY
fix.iterator.refresh,bug.iterator_invalidation,FIXED_BY
fix.move.use_state,bug.use_after_move,FIXED_BY
fix.virtual_destructor,bug.missing_virtual_destructor,FIXED_BY
fix.use_raii,bug.rule_of_five,FIXED_BY
fix.smart_pointer,bug.rule_of_five,FIXED_BY
fix.use_raii,bug.exception_safety,FIXED_BY
fix.array.bound,bug.vector_out_of_range,FIXED_BY
fix.format.match,bug.format_specifier_mismatch,FIXED_BY
fix.condition_wait,bug.condition_variable_misuse,FIXED_BY
view.intro_c,bug.off_by_one,VISIBLE_IN
view.intro_c,bug.infinite_loop,VISIBLE_IN
view.intro_c,bug.missing_loop_update,VISIBLE_IN
view.intro_c,bug.wrong_loop_init,VISIBLE_IN
view.intro_c,bug.array_out_of_bounds,VISIBLE_IN
view.intro_c,bug.missing_return,VISIBLE_IN
view.intro_c,bug.format_specifier_mismatch,VISIBLE_IN
view.c_pointers,bug.null_dereference,VISIBLE_IN
view.c_pointers,bug.memory_leak,VISIBLE_IN
view.c_pointers,bug.use_after_free,VISIBLE_IN
view.c_pointers,bug.double_free,VISIBLE_IN
view.c_pointers,bug.dangling_pointer,VISIBLE_IN
view.cpp_oop,bug.missing_virtual_destructor,VISIBLE_IN
view.cpp_oop,bug.rule_of_five,VISIBLE_IN
view.cpp_oop,bug.exception_safety,VISIBLE_IN
view.cpp_modern,bug.use_after_move,VISIBLE_IN
view.cpp_modern,bug.rule_of_five,VISIBLE_IN
view.cpp_modern,bug.exception_safety,VISIBLE_IN
view.cpp_modern,bug.iterator_invalidation,VISIBLE_IN
view.cpp_stl,bug.iterator_invalidation,VISIBLE_IN
view.cpp_stl,bug.vector_out_of_range,VISIBLE_IN
view.cpp_stl,bug.use_after_move,VISIBLE_IN
view.algorithms,bug.off_by_one,VISIBLE_IN
view.algorithms,bug.infinite_loop,VISIBLE_IN
view.algorithms,bug.wrong_base_case,VISIBLE_IN
view.algorithms,bug.no_recursive_progress,VISIBLE_IN
view.algorithms,bug.index_value_confusion,VISIBLE_IN
"""
SEED_CYPHER = r"""CREATE CONSTRAINT bug_category_id_unique IF NOT EXISTS FOR (n:BugCategory) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT bug_id_unique IF NOT EXISTS FOR (n:ProgrammingBug) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT mis_id_unique IF NOT EXISTS FOR (n:Misconception) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT symptom_id_unique IF NOT EXISTS FOR (n:Symptom) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT effect_id_unique IF NOT EXISTS FOR (n:Effect) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT fix_id_unique IF NOT EXISTS FOR (n:FixStrategy) REQUIRE n.id IS UNIQUE;

// Bug-side nodes
MERGE (n:BugCategory {id: 'bugcat.root'}) SET n += {id: 'bugcat.root', name: 'ProgrammingBugRoot', description: 'Root category for all programming bugs', level: 'top', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.logic'}) SET n += {id: 'bugcat.logic', name: 'LogicError', description: 'Bugs caused by incorrect program logic', level: 'top', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.runtime'}) SET n += {id: 'bugcat.runtime', name: 'RuntimeError', description: 'Bugs manifested during execution', level: 'top', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.memory'}) SET n += {id: 'bugcat.memory', name: 'MemoryError', description: 'Bugs involving allocation, ownership, lifetime, or pointer/reference misuse', level: 'top', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.algorithm'}) SET n += {id: 'bugcat.algorithm', name: 'AlgorithmicError', description: 'Bugs caused by wrong algorithm or incomplete strategy', level: 'top', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.api'}) SET n += {id: 'bugcat.api', name: 'APIAndLibraryMisuse', description: 'Bugs caused by incorrect use of standard library or language API', level: 'top', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.concurrency'}) SET n += {id: 'bugcat.concurrency', name: 'ConcurrencyError', description: 'Bugs caused by synchronization or memory ordering mistakes', level: 'top', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.logic.loop'}) SET n += {id: 'bugcat.logic.loop', name: 'LoopError', description: 'Logic bugs in loop initialization, condition, exit, or progress', level: 'sub', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.logic.array'}) SET n += {id: 'bugcat.logic.array', name: 'ArrayAndIndexError', description: 'Logic bugs around arrays, indexing, and traversal', level: 'sub', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.logic.function'}) SET n += {id: 'bugcat.logic.function', name: 'FunctionContractError', description: 'Bugs around return values and basic contract behavior', level: 'sub', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.algorithm.recursion'}) SET n += {id: 'bugcat.algorithm.recursion', name: 'RecursionError', description: 'Base case or progress mistakes in recursive algorithms', level: 'sub', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.memory.pointer'}) SET n += {id: 'bugcat.memory.pointer', name: 'PointerLifetimeError', description: 'Pointer lifetime, dereference, and ownership mistakes', level: 'sub', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.memory.cpp'}) SET n += {id: 'bugcat.memory.cpp', name: 'ModernCppLifetimeError', description: 'Modern C++ lifetime and move/ownership issues', level: 'sub', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.api.iterator'}) SET n += {id: 'bugcat.api.iterator', name: 'IteratorAndRangeError', description: 'Iterator invalidation and range misuse', level: 'sub', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.api.io'}) SET n += {id: 'bugcat.api.io', name: 'IOAndFormattingError', description: 'Formatted I/O or output API misuse', level: 'sub', status: 'active', standardVersion: 'latest'};
MERGE (n:BugCategory {id: 'bugcat.concurrency.sync'}) SET n += {id: 'bugcat.concurrency.sync', name: 'SynchronizationError', description: 'Waiting, locking, and thread coordination mistakes', level: 'sub', status: 'active', standardVersion: 'latest'};
MERGE (n:Misconception {id: 'mis.loop.bound'}) SET n += {id: 'mis.loop.bound', name: 'MisunderstandLoopBoundary', misconceptionType: 'conceptual', description: 'Belief that loop boundaries include one more or one fewer valid iteration than they actually do.', status: 'active'};
MERGE (n:Misconception {id: 'mis.loop.progress'}) SET n += {id: 'mis.loop.progress', name: 'MisunderstandLoopProgress', misconceptionType: 'conceptual', description: 'Belief that a loop progresses correctly even when state is not updated toward termination.', status: 'active'};
MERGE (n:Misconception {id: 'mis.loop.init'}) SET n += {id: 'mis.loop.init', name: 'MisunderstandLoopInitialization', misconceptionType: 'conceptual', description: 'Incorrect mental model of initialization value or start state of a loop variable.', status: 'active'};
MERGE (n:Misconception {id: 'mis.array.last_index'}) SET n += {id: 'mis.array.last_index', name: 'MisunderstandLastValidIndex', misconceptionType: 'conceptual', description: 'Belief that an array of size n has valid last index n instead of n-1.', status: 'active'};
MERGE (n:Misconception {id: 'mis.array.index_value'}) SET n += {id: 'mis.array.index_value', name: 'ConfuseIndexWithValue', misconceptionType: 'conceptual', description: 'Confusion between element position and element contents during traversal or update.', status: 'active'};
MERGE (n:Misconception {id: 'mis.pointer.null'}) SET n += {id: 'mis.pointer.null', name: 'AssumePointerIsAlwaysValid', misconceptionType: 'pointer', description: 'Belief that a pointer can be dereferenced safely without checking validity or lifetime.', status: 'active'};
MERGE (n:Misconception {id: 'mis.pointer.free'}) SET n += {id: 'mis.pointer.free', name: 'AssumeFreedPointerStillUsable', misconceptionType: 'pointer', description: 'Belief that a pointer remains valid after free/delete.', status: 'active'};
MERGE (n:Misconception {id: 'mis.memory.auto_cleanup'}) SET n += {id: 'mis.memory.auto_cleanup', name: 'AssumeManualMemoryCleansItself', misconceptionType: 'memory', description: 'Belief that manually allocated memory is automatically released when forgotten.', status: 'active'};
MERGE (n:Misconception {id: 'mis.return.contract'}) SET n += {id: 'mis.return.contract', name: 'AssumeMissingReturnIsBenign', misconceptionType: 'function', description: 'Belief that omitting a required return value has no observable consequence.', status: 'active'};
MERGE (n:Misconception {id: 'mis.recursion.base_case'}) SET n += {id: 'mis.recursion.base_case', name: 'MisunderstandBaseCase', misconceptionType: 'algorithm', description: 'Belief that recursion can terminate correctly without a precise base case.', status: 'active'};
MERGE (n:Misconception {id: 'mis.recursion.progress'}) SET n += {id: 'mis.recursion.progress', name: 'MisunderstandRecursiveProgress', misconceptionType: 'algorithm', description: 'Belief that recursive calls need not reduce problem size toward the base case.', status: 'active'};
MERGE (n:Misconception {id: 'mis.iter.invalidate'}) SET n += {id: 'mis.iter.invalidate', name: 'MisunderstandIteratorInvalidation', misconceptionType: 'stl', description: 'Belief that iterators remain valid after container modifications that invalidate them.', status: 'active'};
MERGE (n:Misconception {id: 'mis.move.validity'}) SET n += {id: 'mis.move.validity', name: 'MisunderstandMovedFromState', misconceptionType: 'modern-cpp', description: 'Belief that an object is fully reusable after its resources were moved away.', status: 'active'};
MERGE (n:Misconception {id: 'mis.ownership.shared'}) SET n += {id: 'mis.ownership.shared', name: 'MisunderstandOwnershipModel', misconceptionType: 'modern-cpp', description: 'Confusion about single ownership, shared ownership, and non-owning references.', status: 'active'};
MERGE (n:Misconception {id: 'mis.virtual.destructor'}) SET n += {id: 'mis.virtual.destructor', name: 'MisunderstandPolymorphicDestruction', misconceptionType: 'oop', description: 'Belief that deleting through a base pointer is safe without a virtual destructor.', status: 'active'};
MERGE (n:Misconception {id: 'mis.exception.safety'}) SET n += {id: 'mis.exception.safety', name: 'MisunderstandExceptionSafety', misconceptionType: 'modern-cpp', description: 'Belief that resource cleanup remains correct under exceptional control flow without RAII.', status: 'active'};
MERGE (n:Misconception {id: 'mis.format.specifier'}) SET n += {id: 'mis.format.specifier', name: 'MisunderstandFormatSpecifierTypeMatch', misconceptionType: 'io', description: 'Belief that any format specifier can print any type without mismatch problems.', status: 'active'};
MERGE (n:Misconception {id: 'mis.wait.protocol'}) SET n += {id: 'mis.wait.protocol', name: 'MisunderstandConditionWaitingProtocol', misconceptionType: 'concurrency', description: 'Belief that waiting on conditions does not require disciplined locking and predicate checks.', status: 'active'};
MERGE (n:Symptom {id: 'sym.incorrect_output'}) SET n += {id: 'sym.incorrect_output', name: 'IncorrectOutput', symptomType: 'observable', description: 'Program runs but produces wrong output for one or more cases.', status: 'active'};
MERGE (n:Symptom {id: 'sym.hangs'}) SET n += {id: 'sym.hangs', name: 'ProgramHangs', symptomType: 'runtime', description: 'Program does not terminate in expected time or gets stuck.', status: 'active'};
MERGE (n:Symptom {id: 'sym.timeout'}) SET n += {id: 'sym.timeout', name: 'Timeout', symptomType: 'runtime', description: 'Program exceeds time limit or performance budget.', status: 'active'};
MERGE (n:Symptom {id: 'sym.crash'}) SET n += {id: 'sym.crash', name: 'Crash', symptomType: 'runtime', description: 'Program aborts, segfaults, or terminates unexpectedly.', status: 'active'};
MERGE (n:Symptom {id: 'sym.out_of_bounds'}) SET n += {id: 'sym.out_of_bounds', name: 'OutOfBoundsAccess', symptomType: 'runtime', description: 'Program accesses array or container outside valid range.', status: 'active'};
MERGE (n:Symptom {id: 'sym.null_deref'}) SET n += {id: 'sym.null_deref', name: 'NullDereference', symptomType: 'runtime', description: 'Program dereferences a null pointer or invalid nullable handle.', status: 'active'};
MERGE (n:Symptom {id: 'sym.use_after_free'}) SET n += {id: 'sym.use_after_free', name: 'UseAfterFreeSymptom', symptomType: 'runtime', description: 'Program accesses memory after it has been released.', status: 'active'};
MERGE (n:Symptom {id: 'sym.memory_growth'}) SET n += {id: 'sym.memory_growth', name: 'UnboundedMemoryGrowth', symptomType: 'runtime', description: 'Memory usage grows because allocations are not released.', status: 'active'};
MERGE (n:Symptom {id: 'sym.iterator_invalid'}) SET n += {id: 'sym.iterator_invalid', name: 'IteratorInvalidAccess', symptomType: 'runtime', description: 'Iterator or view is used after invalidation.', status: 'active'};
MERGE (n:Symptom {id: 'sym.warn_return'}) SET n += {id: 'sym.warn_return', name: 'ControlReachesEndOfNonVoid', symptomType: 'static', description: 'A non-void function path finishes without returning a value.', status: 'active'};
MERGE (n:Symptom {id: 'sym.double_release'}) SET n += {id: 'sym.double_release', name: 'DoubleReleaseSymptom', symptomType: 'runtime', description: 'Same ownership resource is released multiple times.', status: 'active'};
MERGE (n:Symptom {id: 'sym.racey_behavior'}) SET n += {id: 'sym.racey_behavior', name: 'NonDeterministicBehavior', symptomType: 'runtime', description: 'Output or state varies across runs due to synchronization mistakes.', status: 'active'};
MERGE (n:Effect {id: 'eff.wrong_answer'}) SET n += {id: 'eff.wrong_answer', name: 'WrongAnswer', impactLevel: 'medium', description: 'Program violates problem specification and returns incorrect results.', status: 'active'};
MERGE (n:Effect {id: 'eff.undefined_behavior'}) SET n += {id: 'eff.undefined_behavior', name: 'UndefinedBehavior', impactLevel: 'high', description: 'Execution enters undefined behavior with unstable or unsafe outcomes.', status: 'active'};
MERGE (n:Effect {id: 'eff.resource_exhaustion'}) SET n += {id: 'eff.resource_exhaustion', name: 'ResourceExhaustion', impactLevel: 'high', description: 'Program consumes memory or CPU excessively.', status: 'active'};
MERGE (n:Effect {id: 'eff.security_risk'}) SET n += {id: 'eff.security_risk', name: 'SecurityRisk', impactLevel: 'high', description: 'Bug may create memory corruption or exploitable behavior.', status: 'active'};
MERGE (n:Effect {id: 'eff.nontermination'}) SET n += {id: 'eff.nontermination', name: 'NonTermination', impactLevel: 'high', description: 'Program never reaches a terminating state for some inputs.', status: 'active'};
MERGE (n:Effect {id: 'eff.data_corruption'}) SET n += {id: 'eff.data_corruption', name: 'DataCorruption', impactLevel: 'high', description: 'Program corrupts values or object state in memory.', status: 'active'};
MERGE (n:Effect {id: 'eff.partial_cleanup'}) SET n += {id: 'eff.partial_cleanup', name: 'PartialCleanup', impactLevel: 'medium', description: 'Program leaves resources unreleased under some control paths.', status: 'active'};
MERGE (n:Effect {id: 'eff.api_contract_violation'}) SET n += {id: 'eff.api_contract_violation', name: 'APIContractViolation', impactLevel: 'medium', description: 'Program violates expected library or language usage contract.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.loop.bound'}) SET n += {id: 'fix.loop.bound', name: 'AdjustLoopBoundary', fixType: 'local-code-fix', description: 'Replace incorrect boundary condition with the correct inclusive/exclusive condition.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.loop.progress'}) SET n += {id: 'fix.loop.progress', name: 'EnsureLoopProgress', fixType: 'local-code-fix', description: 'Update loop state so each iteration moves toward termination.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.loop.init'}) SET n += {id: 'fix.loop.init', name: 'CorrectLoopInitialization', fixType: 'local-code-fix', description: 'Initialize loop variable from the intended starting state.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.array.bound'}) SET n += {id: 'fix.array.bound', name: 'ValidateArrayBoundary', fixType: 'local-code-fix', description: 'Constrain index to valid range and use length-based reasoning.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.array.index_value'}) SET n += {id: 'fix.array.index_value', name: 'SeparateIndexAndValueRoles', fixType: 'local-code-fix', description: 'Use distinct variables or logic for index and element value.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.null.check'}) SET n += {id: 'fix.null.check', name: 'CheckPointerBeforeDereference', fixType: 'defensive-fix', description: 'Check for null or impossible state before dereferencing, or redesign ownership.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.release.once'}) SET n += {id: 'fix.release.once', name: 'ReleaseExactlyOnce', fixType: 'ownership-fix', description: 'Ensure each allocated resource has one matching release.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.no_use_after_release'}) SET n += {id: 'fix.no_use_after_release', name: 'InvalidateAfterRelease', fixType: 'ownership-fix', description: 'Clear or stop using handles after free/delete or hand over ownership safely.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.use_raii'}) SET n += {id: 'fix.use_raii', name: 'AdoptRAII', fixType: 'design-fix', description: 'Tie resource lifetime to object lifetime using RAII wrappers and automatic cleanup.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.smart_pointer'}) SET n += {id: 'fix.smart_pointer', name: 'UseSmartPointer', fixType: 'modern-cpp-fix', description: 'Replace raw owning pointers with std::unique_ptr or std::shared_ptr as appropriate.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.return'}) SET n += {id: 'fix.return', name: 'ReturnOnAllPaths', fixType: 'local-code-fix', description: 'Add explicit valid return statements on every control path of a non-void function.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.recursion.base'}) SET n += {id: 'fix.recursion.base', name: 'DefineBaseCase', fixType: 'algorithm-fix', description: 'Add a precise recursive base case that stops recursion.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.recursion.progress'}) SET n += {id: 'fix.recursion.progress', name: 'ReduceProblemSize', fixType: 'algorithm-fix', description: 'Ensure each recursive call reduces input toward the base case.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.iterator.refresh'}) SET n += {id: 'fix.iterator.refresh', name: 'RefreshIteratorAfterModification', fixType: 'stl-fix', description: 'Reacquire iterator/reference after container operations that may invalidate it.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.move.use_state'}) SET n += {id: 'fix.move.use_state', name: 'DoNotDependOnMovedFromValue', fixType: 'modern-cpp-fix', description: 'Use moved-from objects only in documented valid ways or reinitialize them.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.virtual_destructor'}) SET n += {id: 'fix.virtual_destructor', name: 'AddVirtualDestructor', fixType: 'oop-fix', description: 'Make base destructor virtual when deleting derived objects via base pointers.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.format.match'}) SET n += {id: 'fix.format.match', name: 'MatchFormatSpecifierToType', fixType: 'io-fix', description: 'Use the correct format specifier for the actual argument type.', status: 'active'};
MERGE (n:FixStrategy {id: 'fix.condition_wait'}) SET n += {id: 'fix.condition_wait', name: 'UsePredicateWaitPattern', fixType: 'concurrency-fix', description: 'Protect shared state with locks and wait in a predicate-based loop.', status: 'active'};
MERGE (n:ProgrammingBug {id: 'bug.off_by_one'}) SET n += {id: 'bug.off_by_one', name: 'OffByOneError', severity: 'medium', detectionEase: 'moderate', pedagogicalPriority: 'critical', description: 'Loop or indexing logic uses a boundary that is one too small or one too large.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.infinite_loop'}) SET n += {id: 'bug.infinite_loop', name: 'InfiniteLoopError', severity: 'high', detectionEase: 'easy', pedagogicalPriority: 'critical', description: 'Loop exit condition is unreachable or loop state never progresses to termination.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.missing_loop_update'}) SET n += {id: 'bug.missing_loop_update', name: 'MissingLoopUpdateError', severity: 'high', detectionEase: 'easy', pedagogicalPriority: 'high', description: 'Loop variable or progress state is not updated correctly inside or by the loop header.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.wrong_loop_init'}) SET n += {id: 'bug.wrong_loop_init', name: 'WrongLoopInitializationError', severity: 'medium', detectionEase: 'easy', pedagogicalPriority: 'high', description: 'Loop starts from an incorrect initial state or index.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.wrong_loop_condition'}) SET n += {id: 'bug.wrong_loop_condition', name: 'WrongLoopConditionError', severity: 'medium', detectionEase: 'moderate', pedagogicalPriority: 'high', description: 'Loop condition expresses the wrong continuation rule.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.array_out_of_bounds'}) SET n += {id: 'bug.array_out_of_bounds', name: 'ArrayOutOfBoundsError', severity: 'high', detectionEase: 'moderate', pedagogicalPriority: 'critical', description: 'Built-in array is indexed outside its valid bounds.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.index_value_confusion'}) SET n += {id: 'bug.index_value_confusion', name: 'IndexValueConfusionError', severity: 'medium', detectionEase: 'moderate', pedagogicalPriority: 'high', description: 'Logic confuses array index with array element value.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.null_dereference'}) SET n += {id: 'bug.null_dereference', name: 'NullDereferenceError', severity: 'high', detectionEase: 'easy', pedagogicalPriority: 'critical', description: 'Null or otherwise invalid pointer/reference-like state is dereferenced.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.memory_leak'}) SET n += {id: 'bug.memory_leak', name: 'MemoryLeakError', severity: 'medium', detectionEase: 'moderate', pedagogicalPriority: 'high', description: 'Dynamically allocated memory is not released when no longer needed.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.use_after_free'}) SET n += {id: 'bug.use_after_free', name: 'UseAfterFreeError', severity: 'high', detectionEase: 'hard', pedagogicalPriority: 'critical', description: 'Memory is accessed after the corresponding allocation was released.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.double_free'}) SET n += {id: 'bug.double_free', name: 'DoubleFreeError', severity: 'high', detectionEase: 'moderate', pedagogicalPriority: 'critical', description: 'The same allocation or ownership resource is released more than once.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.dangling_pointer'}) SET n += {id: 'bug.dangling_pointer', name: 'DanglingPointerError', severity: 'high', detectionEase: 'moderate', pedagogicalPriority: 'high', description: 'Pointer continues to reference storage whose lifetime has ended.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.uninitialized_value'}) SET n += {id: 'bug.uninitialized_value', name: 'UninitializedValueUsageError', severity: 'high', detectionEase: 'moderate', pedagogicalPriority: 'high', description: 'Variable or object state is read before receiving a valid initialization.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.missing_return'}) SET n += {id: 'bug.missing_return', name: 'MissingReturnValueError', severity: 'medium', detectionEase: 'easy', pedagogicalPriority: 'high', description: 'A non-void function can complete without returning a value.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.wrong_base_case'}) SET n += {id: 'bug.wrong_base_case', name: 'WrongRecursionBaseCaseError', severity: 'high', detectionEase: 'moderate', pedagogicalPriority: 'high', description: 'Recursive algorithm uses an incorrect or unreachable base case.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.no_recursive_progress'}) SET n += {id: 'bug.no_recursive_progress', name: 'NoRecursiveProgressError', severity: 'high', detectionEase: 'moderate', pedagogicalPriority: 'high', description: 'Recursive calls do not reduce problem size toward the base case.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.iterator_invalidation'}) SET n += {id: 'bug.iterator_invalidation', name: 'IteratorInvalidationError', severity: 'high', detectionEase: 'hard', pedagogicalPriority: 'critical', description: 'Code uses iterators, references, or views after container modification invalidates them.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.use_after_move'}) SET n += {id: 'bug.use_after_move', name: 'UseAfterMoveError', severity: 'medium', detectionEase: 'moderate', pedagogicalPriority: 'high', description: 'Code relies on moved-from object state as if it were unchanged.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.missing_virtual_destructor'}) SET n += {id: 'bug.missing_virtual_destructor', name: 'MissingVirtualDestructorError', severity: 'high', detectionEase: 'easy', pedagogicalPriority: 'high', description: 'Deleting a derived object through a base pointer without a virtual destructor.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.rule_of_five'}) SET n += {id: 'bug.rule_of_five', name: 'RuleOfFiveViolation', severity: 'medium', detectionEase: 'hard', pedagogicalPriority: 'medium', description: 'Custom resource-owning type defines inconsistent copy/move/destructor behavior.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.exception_safety'}) SET n += {id: 'bug.exception_safety', name: 'ExceptionSafetyViolation', severity: 'medium', detectionEase: 'hard', pedagogicalPriority: 'medium', description: 'Resource cleanup or object invariants break under exception paths.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.vector_out_of_range'}) SET n += {id: 'bug.vector_out_of_range', name: 'VectorOutOfRangeError', severity: 'medium', detectionEase: 'moderate', pedagogicalPriority: 'high', description: 'std::vector access goes outside valid logical range.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.format_specifier_mismatch'}) SET n += {id: 'bug.format_specifier_mismatch', name: 'FormatSpecifierMismatchError', severity: 'medium', detectionEase: 'easy', pedagogicalPriority: 'high', description: 'Formatted I/O uses a specifier that does not match argument type.', status: 'active', standardVersion: 'latest'};
MERGE (n:ProgrammingBug {id: 'bug.condition_variable_misuse'}) SET n += {id: 'bug.condition_variable_misuse', name: 'ConditionVariableMisuseError', severity: 'high', detectionEase: 'hard', pedagogicalPriority: 'medium', description: 'Wait/notify is used without proper locking or predicate-based rechecking.', status: 'active', standardVersion: 'latest'};
MERGE (n:Effect {id: 'eff.memory_growth'}) SET n += {id: 'eff.memory_growth', name: 'MemoryGrowth', impactLevel: 'medium', description: 'Memory usage grows due to leaks or incomplete destruction.', status: 'active'};

// Relationships, including links to existing concept graph nodes
MATCH (a {id: 'bugcat.logic'}), (b {id: 'bugcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bugcat.runtime'}), (b {id: 'bugcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bugcat.memory'}), (b {id: 'bugcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bugcat.algorithm'}), (b {id: 'bugcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bugcat.api'}), (b {id: 'bugcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bugcat.concurrency'}), (b {id: 'bugcat.root'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bugcat.logic.loop'}), (b {id: 'bugcat.logic'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bugcat.logic.array'}), (b {id: 'bugcat.logic'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bugcat.logic.function'}), (b {id: 'bugcat.logic'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bugcat.algorithm.recursion'}), (b {id: 'bugcat.algorithm'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bugcat.memory.pointer'}), (b {id: 'bugcat.memory'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bugcat.memory.cpp'}), (b {id: 'bugcat.memory'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bugcat.api.iterator'}), (b {id: 'bugcat.api'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bugcat.api.io'}), (b {id: 'bugcat.api'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bugcat.concurrency.sync'}), (b {id: 'bugcat.concurrency'}) MERGE (a)-[r:SUBCATEGORY_OF]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'bugcat.logic.array'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'bugcat.logic.loop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.missing_loop_update'}), (b {id: 'bugcat.logic.loop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.wrong_loop_init'}), (b {id: 'bugcat.logic.loop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.wrong_loop_condition'}), (b {id: 'bugcat.logic.loop'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.array_out_of_bounds'}), (b {id: 'bugcat.logic.array'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.index_value_confusion'}), (b {id: 'bugcat.logic.array'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.null_dereference'}), (b {id: 'bugcat.memory.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'bugcat.memory.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'bugcat.memory.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.double_free'}), (b {id: 'bugcat.memory.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.dangling_pointer'}), (b {id: 'bugcat.memory.pointer'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.uninitialized_value'}), (b {id: 'bugcat.runtime'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.missing_return'}), (b {id: 'bugcat.logic.function'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.wrong_base_case'}), (b {id: 'bugcat.algorithm.recursion'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.no_recursive_progress'}), (b {id: 'bugcat.algorithm.recursion'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'bugcat.api.iterator'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.use_after_move'}), (b {id: 'bugcat.memory.cpp'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.missing_virtual_destructor'}), (b {id: 'bugcat.memory.cpp'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'bugcat.memory.cpp'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.exception_safety'}), (b {id: 'bugcat.memory.cpp'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.vector_out_of_range'}), (b {id: 'bugcat.api.iterator'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.format_specifier_mismatch'}), (b {id: 'bugcat.api.io'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.condition_variable_misuse'}), (b {id: 'bugcat.concurrency.sync'}) MERGE (a)-[r:BELONGS_TO_CATEGORY]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'concept.c.array'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'concept.c.for'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'concept.cpp.array'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'concept.cpp.range_for'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'concept.c.for'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'concept.c.while'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'concept.cpp.for'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'concept.cpp.while'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'concept.cpp.range_for'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.missing_loop_update'}), (b {id: 'concept.c.for'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.missing_loop_update'}), (b {id: 'concept.c.while'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.missing_loop_update'}), (b {id: 'concept.cpp.for'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.missing_loop_update'}), (b {id: 'concept.cpp.while'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.wrong_loop_init'}), (b {id: 'concept.c.for'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.wrong_loop_init'}), (b {id: 'concept.cpp.for'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.wrong_loop_init'}), (b {id: 'concept.cpp.range_for'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.wrong_loop_condition'}), (b {id: 'concept.c.for'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.wrong_loop_condition'}), (b {id: 'concept.c.while'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.wrong_loop_condition'}), (b {id: 'concept.cpp.for'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.wrong_loop_condition'}), (b {id: 'concept.cpp.while'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.wrong_loop_condition'}), (b {id: 'concept.cpp.if'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.array_out_of_bounds'}), (b {id: 'concept.c.array'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.array_out_of_bounds'}), (b {id: 'concept.cpp.array'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.array_out_of_bounds'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.index_value_confusion'}), (b {id: 'concept.c.array'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.index_value_confusion'}), (b {id: 'concept.cpp.array'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.index_value_confusion'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.null_dereference'}), (b {id: 'concept.c.pointer'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.null_dereference'}), (b {id: 'concept.cpp.pointer'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.null_dereference'}), (b {id: 'concept.cpp.smart_pointer'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'concept.c.malloc'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'concept.c.calloc'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'concept.c.realloc'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'concept.cpp.new_delete'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'concept.cpp.smart_pointer'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'concept.cpp.raii'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'concept.c.free'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'concept.cpp.new_delete'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'concept.c.pointer'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'concept.cpp.pointer'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.double_free'}), (b {id: 'concept.c.free'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.double_free'}), (b {id: 'concept.cpp.new_delete'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.double_free'}), (b {id: 'concept.cpp.smart_pointer'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.dangling_pointer'}), (b {id: 'concept.c.pointer'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.dangling_pointer'}), (b {id: 'concept.cpp.pointer'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.dangling_pointer'}), (b {id: 'concept.cpp.reference'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.uninitialized_value'}), (b {id: 'concept.c.variable'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.uninitialized_value'}), (b {id: 'concept.cpp.default_init'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.uninitialized_value'}), (b {id: 'concept.cpp.value_init'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.missing_return'}), (b {id: 'concept.c.function_def'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.missing_return'}), (b {id: 'concept.cpp.function_decl'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.missing_return'}), (b {id: 'concept.cpp.return'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.wrong_base_case'}), (b {id: 'concept.cpp.function_decl'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.wrong_base_case'}), (b {id: 'concept.cpp.lambda'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.wrong_base_case'}), (b {id: 'concept.c.function_def'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.no_recursive_progress'}), (b {id: 'concept.cpp.function_decl'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.no_recursive_progress'}), (b {id: 'concept.c.function_def'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'concept.cpp.iterator'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'concept.cpp.map'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'concept.cpp.unordered_map'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'concept.cpp.ranges'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'concept.cpp.views'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.use_after_move'}), (b {id: 'concept.cpp.move_semantics'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.use_after_move'}), (b {id: 'concept.cpp.unique_ptr'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.use_after_move'}), (b {id: 'concept.cpp.string'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.use_after_move'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.missing_virtual_destructor'}), (b {id: 'concept.cpp.class'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.missing_virtual_destructor'}), (b {id: 'concept.cpp.inheritance'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.missing_virtual_destructor'}), (b {id: 'concept.cpp.virtual_function'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.missing_virtual_destructor'}), (b {id: 'concept.cpp.destructor'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'concept.cpp.class'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'concept.cpp.destructor'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'concept.cpp.copy_semantics'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'concept.cpp.move_semantics'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'concept.cpp.raii'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.exception_safety'}), (b {id: 'concept.cpp.try_catch'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.exception_safety'}), (b {id: 'concept.cpp.noexcept'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.exception_safety'}), (b {id: 'concept.cpp.raii'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.exception_safety'}), (b {id: 'concept.cpp.smart_pointer'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.vector_out_of_range'}), (b {id: 'concept.cpp.vector'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.vector_out_of_range'}), (b {id: 'concept.cpp.range_for'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.format_specifier_mismatch'}), (b {id: 'concept.c.formatted_io'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.format_specifier_mismatch'}), (b {id: 'concept.cpp.format'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.format_specifier_mismatch'}), (b {id: 'concept.cpp.print_functions'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.condition_variable_misuse'}), (b {id: 'concept.cpp.thread'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.condition_variable_misuse'}), (b {id: 'concept.cpp.mutex'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.condition_variable_misuse'}), (b {id: 'concept.cpp.condition_variable'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.condition_variable_misuse'}), (b {id: 'concept.cpp.atomic'}) MERGE (a)-[r:OCCURS_IN_CONCEPT]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'mis.loop.bound'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'mis.array.last_index'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'mis.loop.progress'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.missing_loop_update'}), (b {id: 'mis.loop.progress'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.wrong_loop_init'}), (b {id: 'mis.loop.init'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.wrong_loop_condition'}), (b {id: 'mis.loop.bound'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.array_out_of_bounds'}), (b {id: 'mis.array.last_index'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.index_value_confusion'}), (b {id: 'mis.array.index_value'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.null_dereference'}), (b {id: 'mis.pointer.null'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'mis.memory.auto_cleanup'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'mis.pointer.free'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.double_free'}), (b {id: 'mis.pointer.free'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.double_free'}), (b {id: 'mis.ownership.shared'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.dangling_pointer'}), (b {id: 'mis.pointer.free'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.missing_return'}), (b {id: 'mis.return.contract'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.wrong_base_case'}), (b {id: 'mis.recursion.base_case'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.no_recursive_progress'}), (b {id: 'mis.recursion.progress'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'mis.iter.invalidate'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.use_after_move'}), (b {id: 'mis.move.validity'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.missing_virtual_destructor'}), (b {id: 'mis.virtual.destructor'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'mis.ownership.shared'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.exception_safety'}), (b {id: 'mis.exception.safety'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.format_specifier_mismatch'}), (b {id: 'mis.format.specifier'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.condition_variable_misuse'}), (b {id: 'mis.wait.protocol'}) MERGE (a)-[r:CAUSED_BY_MISCONCEPTION]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'sym.incorrect_output'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'sym.out_of_bounds'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'sym.hangs'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'sym.timeout'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.missing_loop_update'}), (b {id: 'sym.hangs'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.missing_loop_update'}), (b {id: 'sym.timeout'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.wrong_loop_init'}), (b {id: 'sym.incorrect_output'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.wrong_loop_condition'}), (b {id: 'sym.incorrect_output'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.array_out_of_bounds'}), (b {id: 'sym.out_of_bounds'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.array_out_of_bounds'}), (b {id: 'sym.crash'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.index_value_confusion'}), (b {id: 'sym.incorrect_output'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.null_dereference'}), (b {id: 'sym.null_deref'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.null_dereference'}), (b {id: 'sym.crash'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'sym.memory_growth'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'sym.use_after_free'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'sym.crash'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.double_free'}), (b {id: 'sym.double_release'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.double_free'}), (b {id: 'sym.crash'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.dangling_pointer'}), (b {id: 'sym.crash'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.dangling_pointer'}), (b {id: 'sym.incorrect_output'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.uninitialized_value'}), (b {id: 'sym.incorrect_output'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.uninitialized_value'}), (b {id: 'sym.crash'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.missing_return'}), (b {id: 'sym.warn_return'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.missing_return'}), (b {id: 'sym.incorrect_output'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.wrong_base_case'}), (b {id: 'sym.hangs'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.wrong_base_case'}), (b {id: 'sym.incorrect_output'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.no_recursive_progress'}), (b {id: 'sym.hangs'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.no_recursive_progress'}), (b {id: 'sym.timeout'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'sym.iterator_invalid'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'sym.crash'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.use_after_move'}), (b {id: 'sym.incorrect_output'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.missing_virtual_destructor'}), (b {id: 'sym.memory_growth'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'sym.crash'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'sym.incorrect_output'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.exception_safety'}), (b {id: 'sym.crash'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.exception_safety'}), (b {id: 'sym.memory_growth'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.vector_out_of_range'}), (b {id: 'sym.out_of_bounds'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.vector_out_of_range'}), (b {id: 'sym.crash'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.format_specifier_mismatch'}), (b {id: 'sym.incorrect_output'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.format_specifier_mismatch'}), (b {id: 'sym.crash'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.condition_variable_misuse'}), (b {id: 'sym.hangs'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.condition_variable_misuse'}), (b {id: 'sym.racey_behavior'}) MERGE (a)-[r:HAS_SYMPTOM]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'eff.wrong_answer'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'eff.undefined_behavior'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'eff.nontermination'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'eff.resource_exhaustion'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.missing_loop_update'}), (b {id: 'eff.nontermination'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.wrong_loop_init'}), (b {id: 'eff.wrong_answer'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.wrong_loop_condition'}), (b {id: 'eff.wrong_answer'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.array_out_of_bounds'}), (b {id: 'eff.undefined_behavior'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.array_out_of_bounds'}), (b {id: 'eff.security_risk'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.index_value_confusion'}), (b {id: 'eff.wrong_answer'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.null_dereference'}), (b {id: 'eff.undefined_behavior'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.null_dereference'}), (b {id: 'eff.security_risk'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'eff.resource_exhaustion'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'eff.partial_cleanup'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'eff.undefined_behavior'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'eff.security_risk'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'eff.data_corruption'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.double_free'}), (b {id: 'eff.undefined_behavior'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.double_free'}), (b {id: 'eff.security_risk'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.dangling_pointer'}), (b {id: 'eff.undefined_behavior'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.dangling_pointer'}), (b {id: 'eff.data_corruption'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.uninitialized_value'}), (b {id: 'eff.undefined_behavior'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.uninitialized_value'}), (b {id: 'eff.wrong_answer'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.missing_return'}), (b {id: 'eff.undefined_behavior'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.missing_return'}), (b {id: 'eff.wrong_answer'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.wrong_base_case'}), (b {id: 'eff.nontermination'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.wrong_base_case'}), (b {id: 'eff.wrong_answer'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.no_recursive_progress'}), (b {id: 'eff.nontermination'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'eff.undefined_behavior'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'eff.api_contract_violation'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.use_after_move'}), (b {id: 'eff.wrong_answer'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.use_after_move'}), (b {id: 'eff.api_contract_violation'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.missing_virtual_destructor'}), (b {id: 'eff.partial_cleanup'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'eff.data_corruption'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'eff.partial_cleanup'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.exception_safety'}), (b {id: 'eff.partial_cleanup'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.exception_safety'}), (b {id: 'eff.data_corruption'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.vector_out_of_range'}), (b {id: 'eff.api_contract_violation'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.vector_out_of_range'}), (b {id: 'eff.wrong_answer'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.format_specifier_mismatch'}), (b {id: 'eff.api_contract_violation'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.format_specifier_mismatch'}), (b {id: 'eff.wrong_answer'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.condition_variable_misuse'}), (b {id: 'eff.nontermination'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.condition_variable_misuse'}), (b {id: 'eff.data_corruption'}) MERGE (a)-[r:HAS_EFFECT]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'fix.loop.bound'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'fix.array.bound'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'fix.loop.progress'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'fix.loop.bound'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.missing_loop_update'}), (b {id: 'fix.loop.progress'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.wrong_loop_init'}), (b {id: 'fix.loop.init'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.wrong_loop_condition'}), (b {id: 'fix.loop.bound'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.array_out_of_bounds'}), (b {id: 'fix.array.bound'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.index_value_confusion'}), (b {id: 'fix.array.index_value'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.null_dereference'}), (b {id: 'fix.null.check'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.null_dereference'}), (b {id: 'fix.smart_pointer'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'fix.release.once'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'fix.use_raii'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'fix.smart_pointer'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'fix.no_use_after_release'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'fix.use_raii'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'fix.smart_pointer'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.double_free'}), (b {id: 'fix.release.once'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.double_free'}), (b {id: 'fix.no_use_after_release'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.dangling_pointer'}), (b {id: 'fix.no_use_after_release'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.dangling_pointer'}), (b {id: 'fix.smart_pointer'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.uninitialized_value'}), (b {id: 'fix.loop.init'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.missing_return'}), (b {id: 'fix.return'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.wrong_base_case'}), (b {id: 'fix.recursion.base'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.no_recursive_progress'}), (b {id: 'fix.recursion.progress'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'fix.iterator.refresh'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.use_after_move'}), (b {id: 'fix.move.use_state'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.missing_virtual_destructor'}), (b {id: 'fix.virtual_destructor'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'fix.use_raii'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'fix.smart_pointer'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.exception_safety'}), (b {id: 'fix.use_raii'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.vector_out_of_range'}), (b {id: 'fix.array.bound'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.format_specifier_mismatch'}), (b {id: 'fix.format.match'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.condition_variable_misuse'}), (b {id: 'fix.condition_wait'}) MERGE (a)-[r:FIXED_BY]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.missing_loop_update'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.wrong_loop_init'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.array_out_of_bounds'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.missing_return'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.format_specifier_mismatch'}), (b {id: 'view.intro_c'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.null_dereference'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.memory_leak'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.use_after_free'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.double_free'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.dangling_pointer'}), (b {id: 'view.c_pointers'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.missing_virtual_destructor'}), (b {id: 'view.cpp_oop'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'view.cpp_oop'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.exception_safety'}), (b {id: 'view.cpp_oop'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.use_after_move'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.rule_of_five'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.exception_safety'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'view.cpp_modern'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.iterator_invalidation'}), (b {id: 'view.cpp_stl'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.vector_out_of_range'}), (b {id: 'view.cpp_stl'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.use_after_move'}), (b {id: 'view.cpp_stl'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.off_by_one'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.infinite_loop'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.wrong_base_case'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.no_recursive_progress'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);
MATCH (a {id: 'bug.index_value_confusion'}), (b {id: 'view.algorithms'}) MERGE (a)-[r:VISIBLE_IN]->(b);"""
SUMMARY_JSON = r"""{
  "node_count": 97,
  "relationship_count": 299,
  "labels": {
    "BugCategory": 16,
    "Misconception": 18,
    "Symptom": 12,
    "Effect": 9,
    "FixStrategy": 18,
    "ProgrammingBug": 24
  },
  "relationship_types": {
    "SUBCATEGORY_OF": 15,
    "BELONGS_TO_CATEGORY": 24,
    "OCCURS_IN_CONCEPT": 90,
    "CAUSED_BY_MISCONCEPTION": 24,
    "HAS_SYMPTOM": 42,
    "HAS_EFFECT": 43,
    "FIXED_BY": 34,
    "VISIBLE_IN": 27
  },
  "linked_concept_ids": [
    "concept.c.array",
    "concept.c.calloc",
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
    "concept.cpp.if",
    "concept.cpp.inheritance",
    "concept.cpp.iterator",
    "concept.cpp.lambda",
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
    "concept.cpp.reference",
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
    "view.algorithms",
    "view.c_pointers",
    "view.cpp_modern",
    "view.cpp_oop",
    "view.cpp_stl",
    "view.intro_c"
  ],
  "files": [
    "neo4j_bug_ontology_nodes.csv",
    "neo4j_bug_ontology_relationships.csv",
    "neo4j_bug_ontology_seed.cypher",
    "build_neo4j_bug_ontology_dataset.py"
  ]
}"""


def main() -> None:
    out_dir = Path('.')
    (out_dir / 'neo4j_bug_ontology_nodes.csv').write_text(NODES_CSV, encoding='utf-8')
    (out_dir / 'neo4j_bug_ontology_relationships.csv').write_text(RELATIONSHIPS_CSV, encoding='utf-8')
    (out_dir / 'neo4j_bug_ontology_seed.cypher').write_text(SEED_CYPHER, encoding='utf-8')
    (out_dir / 'neo4j_bug_ontology_summary.json').write_text(SUMMARY_JSON, encoding='utf-8')
    print('Bug ontology dataset files created successfully.')


if __name__ == '__main__':
    main()
