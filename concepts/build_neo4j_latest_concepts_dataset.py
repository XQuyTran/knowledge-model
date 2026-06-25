"""Build a latest-only Neo4j concept ontology dataset for C23 and C++23.

Outputs:
- neo4j_latest_concepts_nodes.csv
- neo4j_latest_concepts_relationships.csv
- neo4j_latest_concepts_seed.cypher
- neo4j_latest_concepts_summary.json

This script generates a concept ontology focused on the latest standards only:
- C23
- C++23

All comments and code are in English so the file can be used directly in a
technical project or academic prototype.
"""

from pathlib import Path
import csv
import json

out_dir = Path('.')

nodes = []
rels = []
node_index = {}


def add_node(node_id, label, **props):
    if node_id in node_index:
        raise ValueError(f"Duplicate node id: {node_id}")
    row = {'id': node_id, 'label': label}
    row.update(props)
    node_index[node_id] = row
    nodes.append(row)


def add_rel(start_id, rel_type, end_id, **props):
    if start_id not in node_index:
        raise ValueError(f"Unknown start node: {start_id}")
    if end_id not in node_index:
        raise ValueError(f"Unknown end node: {end_id}")
    row = {'start_id': start_id, 'type': rel_type, 'end_id': end_id}
    row.update(props)
    rels.append(row)


# Root nodes
add_node('lang.c', 'ProgrammingLanguage', name='C', family='C', standardVersion='C23', status='active', isModern='true', description='C language, latest baseline snapshot focused on C23')
add_node('lang.cpp', 'ProgrammingLanguage', name='C++', family='C++', standardVersion='C++23', status='active', isModern='true', description='C++ language, latest baseline snapshot focused on C++23')

# Pedagogical views
views = [
    ('view.intro_c', 'IntroC', 'Introductory C programming'),
    ('view.c_pointers', 'PointersAndMemoryInC', 'C pointers and memory management'),
    ('view.cpp_oop', 'OOPInCpp', 'Object-oriented programming in C++'),
    ('view.cpp_modern', 'ModernCpp', 'Modern C++ practices focused on C++23'),
    ('view.cpp_stl', 'TemplatesAndSTL', 'C++ templates, STL, ranges, and algorithms'),
    ('view.algorithms', 'AlgorithmsAndDSA', 'Algorithms and data structures across C/C++'),
]
for nid, name, desc in views:
    add_node(nid, 'PedagogicalView', name=name, status='active', isModern='true', description=desc)

# Categories
category_specs = [
    ('cat.c.core', 'C Core Language', 'C', 'top-level category for C core language concepts'),
    ('cat.c.basic', 'C Basic Concepts', 'C', 'Identifiers, scope, lifetime, objects, memory model, and undefined behavior'),
    ('cat.c.preprocessor', 'C Preprocessor', 'C', 'Directives and macro processing'),
    ('cat.c.statements', 'C Statements', 'C', 'Control-flow and jump statements'),
    ('cat.c.expressions', 'C Expressions', 'C', 'Operators, conversions, literals, and expression forms'),
    ('cat.c.declarations', 'C Declarations', 'C', 'Types, declarations, storage, qualifiers, and attributes'),
    ('cat.c.functions', 'C Functions', 'C', 'Function declarations, definitions, and variadic features'),
    ('cat.c.library', 'C Standard Library', 'C', 'Standard C library modules and selected concepts'),
    ('cat.cpp.core', 'C++ Core Language', 'C++', 'top-level category for C++ core language concepts'),
    ('cat.cpp.basic', 'C++ Basic Concepts', 'C++', 'Names, ODR, types, objects, scope, lifetime, modules, and memory model'),
    ('cat.cpp.preprocessor', 'C++ Preprocessor', 'C++', 'Directives and macro processing'),
    ('cat.cpp.expressions', 'C++ Expressions', 'C++', 'Value categories, casts, literals, and expression forms'),
    ('cat.cpp.declarations', 'C++ Declarations', 'C++', 'Namespaces, references, pointers, arrays, auto, decltype, constexpr, and attributes'),
    ('cat.cpp.initialization', 'C++ Initialization', 'C++', 'Initialization forms and copy elision'),
    ('cat.cpp.functions', 'C++ Functions', 'C++', 'Function declarations, overloads, lambdas, variadic arguments, and coroutines'),
    ('cat.cpp.statements', 'C++ Statements', 'C++', 'Control-flow statements including range-for'),
    ('cat.cpp.classes', 'C++ Classes', 'C++', 'Classes, constructors, destructors, inheritance, virtual dispatch, and polymorphism'),
    ('cat.cpp.templates', 'C++ Templates', 'C++', 'Templates, specialization, parameter packs, and concepts/constraints'),
    ('cat.cpp.exceptions', 'C++ Exceptions', 'C++', 'Exception handling and noexcept'),
    ('cat.cpp.library', 'C++ Standard Library', 'C++', 'Standard C++ library modules and selected concepts'),
]
for nid, name, language, desc in category_specs:
    add_node(nid, 'ConceptCategory', name=name, language=language, standardVersion='latest', status='active', isModern='true', description=desc)

for child in ['cat.c.basic', 'cat.c.preprocessor', 'cat.c.statements', 'cat.c.expressions', 'cat.c.declarations', 'cat.c.functions', 'cat.c.library']:
    add_rel(child, 'SUBCATEGORY_OF', 'cat.c.core')
for child in ['cat.cpp.basic', 'cat.cpp.preprocessor', 'cat.cpp.expressions', 'cat.cpp.declarations', 'cat.cpp.initialization', 'cat.cpp.functions', 'cat.cpp.statements', 'cat.cpp.classes', 'cat.cpp.templates', 'cat.cpp.exceptions', 'cat.cpp.library']:
    add_rel(child, 'SUBCATEGORY_OF', 'cat.cpp.core')

# Library modules
lib_modules = [
    ('lib.c.type_support', 'LibraryModule', 'C Type Support', 'C', 'active', 'true', 'Type support and integer/size facilities'),
    ('lib.c.program_utilities', 'LibraryModule', 'C Program Utilities', 'C', 'active', 'true', 'General utilities including conversion and process control'),
    ('lib.c.diagnostics', 'LibraryModule', 'C Diagnostics Library', 'C', 'active', 'true', 'Assertions and error-reporting support'),
    ('lib.c.dynamic_memory', 'LibraryModule', 'C Dynamic Memory Management', 'C', 'active', 'true', 'Dynamic allocation and deallocation'),
    ('lib.c.strings', 'LibraryModule', 'C Strings Library', 'C', 'active', 'true', 'String and memory block operations'),
    ('lib.c.datetime', 'LibraryModule', 'C Date and Time Library', 'C', 'active', 'true', 'Time and date facilities'),
    ('lib.c.localization', 'LibraryModule', 'C Localization Library', 'C', 'active', 'true', 'Locale and localization support'),
    ('lib.c.io', 'LibraryModule', 'C Input/Output Library', 'C', 'active', 'true', 'Streams and formatted I/O'),
    ('lib.c.algorithms', 'LibraryModule', 'C Algorithms Library', 'C', 'active', 'true', 'qsort and bsearch style algorithms'),
    ('lib.c.numerics', 'LibraryModule', 'C Numerics Library', 'C', 'active', 'true', 'Math, floating-point, random, complex, bit tools, checked arithmetic'),
    ('lib.c.concurrency', 'LibraryModule', 'C Concurrency Support Library', 'C', 'active', 'true', 'Threads and atomic operations'),
    ('lib.cpp.language_support', 'LibraryModule', 'C++ Language Support Library', 'C++', 'active', 'true', 'Low-level language support and runtime support'),
    ('lib.cpp.concepts', 'LibraryModule', 'C++ Concepts Library', 'C++', 'active', 'true', 'Compile-time concepts and constraints support'),
    ('lib.cpp.diagnostics', 'LibraryModule', 'C++ Diagnostics Library', 'C++', 'active', 'true', 'Assertions, error codes, and stacktrace'),
    ('lib.cpp.memory', 'LibraryModule', 'C++ Memory Management Library', 'C++', 'active', 'true', 'Smart pointers, allocators, and memory resources'),
    ('lib.cpp.metaprogramming', 'LibraryModule', 'C++ Metaprogramming Library', 'C++', 'active', 'true', 'Type traits and compile-time utilities'),
    ('lib.cpp.utilities', 'LibraryModule', 'C++ General Utilities Library', 'C++', 'active', 'true', 'Pair, tuple, optional, variant, any, and function objects'),
    ('lib.cpp.containers', 'LibraryModule', 'C++ Containers Library', 'C++', 'active', 'true', 'Sequence, associative, unordered, and adaptor containers'),
    ('lib.cpp.iterators', 'LibraryModule', 'C++ Iterators Library', 'C++', 'active', 'true', 'Iterator abstractions and adapters'),
    ('lib.cpp.ranges', 'LibraryModule', 'C++ Ranges Library', 'C++', 'active', 'true', 'Views and range-based composition'),
    ('lib.cpp.algorithms', 'LibraryModule', 'C++ Algorithms Library', 'C++', 'active', 'true', 'Sorting, searching, numeric, and constrained algorithms'),
    ('lib.cpp.strings', 'LibraryModule', 'C++ Strings Library', 'C++', 'active', 'true', 'String and string_view support'),
    ('lib.cpp.text_processing', 'LibraryModule', 'C++ Text Processing Library', 'C++', 'active', 'true', 'Regex, formatting, and print functions'),
    ('lib.cpp.numerics', 'LibraryModule', 'C++ Numerics Library', 'C++', 'active', 'true', 'Random, numeric algorithms, and complex support'),
    ('lib.cpp.time', 'LibraryModule', 'C++ Time Library', 'C++', 'active', 'true', 'chrono, calendar, and timezone support'),
    ('lib.cpp.io', 'LibraryModule', 'C++ Input/Output Library', 'C++', 'active', 'true', 'Iostreams and printing facilities'),
    ('lib.cpp.filesystem', 'LibraryModule', 'C++ Filesystem Library', 'C++', 'active', 'true', 'Filesystem path and directory interaction'),
    ('lib.cpp.concurrency', 'LibraryModule', 'C++ Concurrency Support Library', 'C++', 'active', 'true', 'Threads, atomics, mutexes, and condition variables'),
]
for nid, label, name, language, status, is_modern, desc in lib_modules:
    add_node(nid, label, name=name, language=language, standardVersion='latest', status=status, isModern=is_modern, description=desc)

for lib_id in [x[0] for x in lib_modules if x[3] == 'C']:
    add_rel(lib_id, 'MODULE_OF', 'cat.c.library')
for lib_id in [x[0] for x in lib_modules if x[3] == 'C++']:
    add_rel(lib_id, 'MODULE_OF', 'cat.cpp.library')

# Headers
headers = [
    ('hdr.c.stdio', '<stdio.h>', 'C', 'active', 'true'),
    ('hdr.c.stdlib', '<stdlib.h>', 'C', 'active', 'true'),
    ('hdr.c.string', '<string.h>', 'C', 'active', 'true'),
    ('hdr.c.math', '<math.h>', 'C', 'active', 'true'),
    ('hdr.c.time', '<time.h>', 'C', 'active', 'true'),
    ('hdr.c.locale', '<locale.h>', 'C', 'active', 'true'),
    ('hdr.c.assert', '<assert.h>', 'C', 'active', 'true'),
    ('hdr.c.errno', '<errno.h>', 'C', 'active', 'true'),
    ('hdr.c.stdarg', '<stdarg.h>', 'C', 'active', 'true'),
    ('hdr.c.stddef', '<stddef.h>', 'C', 'active', 'true'),
    ('hdr.c.stdint', '<stdint.h>', 'C', 'active', 'true'),
    ('hdr.c.stdatomic', '<stdatomic.h>', 'C', 'active', 'true'),
    ('hdr.c.threads', '<threads.h>', 'C', 'active', 'true'),
    ('hdr.c.stdbit', '<stdbit.h>', 'C', 'active', 'true'),
    ('hdr.c.stdckdint', '<stdckdint.h>', 'C', 'active', 'true'),
    ('hdr.cpp.vector', '<vector>', 'C++', 'active', 'true'),
    ('hdr.cpp.array', '<array>', 'C++', 'active', 'true'),
    ('hdr.cpp.deque', '<deque>', 'C++', 'active', 'true'),
    ('hdr.cpp.list', '<list>', 'C++', 'active', 'true'),
    ('hdr.cpp.map', '<map>', 'C++', 'active', 'true'),
    ('hdr.cpp.unordered_map', '<unordered_map>', 'C++', 'active', 'true'),
    ('hdr.cpp.algorithm', '<algorithm>', 'C++', 'active', 'true'),
    ('hdr.cpp.ranges', '<ranges>', 'C++', 'active', 'true'),
    ('hdr.cpp.iterator', '<iterator>', 'C++', 'active', 'true'),
    ('hdr.cpp.memory', '<memory>', 'C++', 'active', 'true'),
    ('hdr.cpp.memory_resource', '<memory_resource>', 'C++', 'active', 'true'),
    ('hdr.cpp.string', '<string>', 'C++', 'active', 'true'),
    ('hdr.cpp.string_view', '<string_view>', 'C++', 'active', 'true'),
    ('hdr.cpp.format', '<format>', 'C++', 'active', 'true'),
    ('hdr.cpp.print', '<print>', 'C++', 'active', 'true'),
    ('hdr.cpp.regex', '<regex>', 'C++', 'active', 'true'),
    ('hdr.cpp.thread', '<thread>', 'C++', 'active', 'true'),
    ('hdr.cpp.mutex', '<mutex>', 'C++', 'active', 'true'),
    ('hdr.cpp.atomic', '<atomic>', 'C++', 'active', 'true'),
    ('hdr.cpp.filesystem', '<filesystem>', 'C++', 'active', 'true'),
    ('hdr.cpp.chrono', '<chrono>', 'C++', 'active', 'true'),
    ('hdr.cpp.concepts', '<concepts>', 'C++', 'active', 'true'),
    ('hdr.cpp.type_traits', '<type_traits>', 'C++', 'active', 'true'),
    ('hdr.cpp.any', '<any>', 'C++', 'active', 'true'),
    ('hdr.cpp.optional', '<optional>', 'C++', 'active', 'true'),
    ('hdr.cpp.variant', '<variant>', 'C++', 'active', 'true'),
    ('hdr.cpp.stacktrace', '<stacktrace>', 'C++', 'active', 'true'),
    ('hdr.cpp.iostream', '<iostream>', 'C++', 'active', 'true'),
]
for nid, name, language, status, is_modern in headers:
    add_node(nid, 'Header', name=name, language=language, standardVersion='latest', status=status, isModern=is_modern, description=f'{language} standard header {name}')

header_module_map = {
    'hdr.c.stdio': 'lib.c.io', 'hdr.c.stdlib': 'lib.c.program_utilities', 'hdr.c.string': 'lib.c.strings',
    'hdr.c.math': 'lib.c.numerics', 'hdr.c.time': 'lib.c.datetime', 'hdr.c.locale': 'lib.c.localization',
    'hdr.c.assert': 'lib.c.diagnostics', 'hdr.c.errno': 'lib.c.diagnostics', 'hdr.c.stdarg': 'lib.c.program_utilities',
    'hdr.c.stddef': 'lib.c.type_support', 'hdr.c.stdint': 'lib.c.type_support', 'hdr.c.stdatomic': 'lib.c.concurrency',
    'hdr.c.threads': 'lib.c.concurrency', 'hdr.c.stdbit': 'lib.c.numerics', 'hdr.c.stdckdint': 'lib.c.numerics',
    'hdr.cpp.vector': 'lib.cpp.containers', 'hdr.cpp.array': 'lib.cpp.containers', 'hdr.cpp.deque': 'lib.cpp.containers',
    'hdr.cpp.list': 'lib.cpp.containers', 'hdr.cpp.map': 'lib.cpp.containers', 'hdr.cpp.unordered_map': 'lib.cpp.containers',
    'hdr.cpp.algorithm': 'lib.cpp.algorithms', 'hdr.cpp.ranges': 'lib.cpp.ranges', 'hdr.cpp.iterator': 'lib.cpp.iterators',
    'hdr.cpp.memory': 'lib.cpp.memory', 'hdr.cpp.memory_resource': 'lib.cpp.memory', 'hdr.cpp.string': 'lib.cpp.strings',
    'hdr.cpp.string_view': 'lib.cpp.strings', 'hdr.cpp.format': 'lib.cpp.text_processing', 'hdr.cpp.print': 'lib.cpp.io',
    'hdr.cpp.regex': 'lib.cpp.text_processing', 'hdr.cpp.thread': 'lib.cpp.concurrency', 'hdr.cpp.mutex': 'lib.cpp.concurrency',
    'hdr.cpp.atomic': 'lib.cpp.concurrency', 'hdr.cpp.filesystem': 'lib.cpp.filesystem', 'hdr.cpp.chrono': 'lib.cpp.time',
    'hdr.cpp.concepts': 'lib.cpp.concepts', 'hdr.cpp.type_traits': 'lib.cpp.metaprogramming', 'hdr.cpp.any': 'lib.cpp.utilities',
    'hdr.cpp.optional': 'lib.cpp.utilities', 'hdr.cpp.variant': 'lib.cpp.utilities', 'hdr.cpp.stacktrace': 'lib.cpp.diagnostics',
    'hdr.cpp.iostream': 'lib.cpp.io',
}
for hdr_id, mod_id in header_module_map.items():
    add_rel(hdr_id, 'HEADER_OF', mod_id)


def add_concept(node_id, name, language, category_id, kind, description, difficulty='intermediate', is_modern='true', status='active'):
    add_node(
        node_id, 'ProgrammingConcept', name=name, language=language, category=category_id, kind=kind,
        standardVersion='latest', status=status, isModern=is_modern, difficulty=difficulty, description=description,
    )
    add_rel(node_id, 'BELONGS_TO', category_id)
    add_rel(node_id, 'IMPLEMENTED_IN', 'lang.c' if language == 'C' else 'lang.cpp')

# C core concepts
c_concepts = [
    ('concept.c.identifier', 'Identifier', 'cat.c.basic', 'core-language', 'Named program entity in C', 'basic'),
    ('concept.c.scope', 'Scope', 'cat.c.basic', 'core-language', 'Visibility region of identifiers in C', 'basic'),
    ('concept.c.lifetime', 'Lifetime', 'cat.c.basic', 'core-language', 'Duration an object exists during execution', 'basic'),
    ('concept.c.type', 'Type', 'cat.c.basic', 'core-language', 'Classification of data and operations in C', 'basic'),
    ('concept.c.object', 'Object', 'cat.c.basic', 'core-language', 'Region of storage with a type and value', 'basic'),
    ('concept.c.memory_model', 'MemoryModel', 'cat.c.basic', 'core-language', 'Latest C memory model including data races and atomics', 'advanced'),
    ('concept.c.undefined_behavior', 'UndefinedBehavior', 'cat.c.basic', 'core-language', 'Behavior for which the C standard imposes no requirements', 'intermediate'),
    ('concept.c.macro_definition', 'MacroDefinition', 'cat.c.preprocessor', 'core-language', 'Definition of function-like and object-like macros', 'basic'),
    ('concept.c.file_inclusion', 'FileInclusion', 'cat.c.preprocessor', 'core-language', 'Including headers with preprocessing directives', 'basic'),
    ('concept.c.conditional_compilation', 'ConditionalCompilation', 'cat.c.preprocessor', 'core-language', 'Conditional preprocessing with #if and related directives', 'basic'),
    ('concept.c.pragmas', 'Pragmas', 'cat.c.preprocessor', 'core-language', 'Implementation-defined preprocessor control using pragma', 'advanced'),
    ('concept.c.if', 'IfStatement', 'cat.c.statements', 'statement', 'Conditional branching with if / else', 'basic'),
    ('concept.c.switch', 'SwitchStatement', 'cat.c.statements', 'statement', 'Multi-way branching with switch / case', 'basic'),
    ('concept.c.for', 'ForLoop', 'cat.c.statements', 'statement', 'Counter-controlled iteration with for', 'basic'),
    ('concept.c.while', 'WhileLoop', 'cat.c.statements', 'statement', 'Condition-controlled iteration with while', 'basic'),
    ('concept.c.do_while', 'DoWhileLoop', 'cat.c.statements', 'statement', 'Post-test loop with do-while', 'basic'),
    ('concept.c.break', 'BreakStatement', 'cat.c.statements', 'statement', 'Early exit from loops or switch', 'basic'),
    ('concept.c.continue', 'ContinueStatement', 'cat.c.statements', 'statement', 'Proceed to next iteration of loop', 'basic'),
    ('concept.c.goto', 'GotoStatement', 'cat.c.statements', 'statement', 'Unconditional jump to a labeled statement', 'advanced'),
    ('concept.c.return', 'ReturnStatement', 'cat.c.statements', 'statement', 'Return from function', 'basic'),
    ('concept.c.literal', 'Literal', 'cat.c.expressions', 'expression', 'A literal constant such as integer, floating, character, string, or nullptr', 'basic'),
    ('concept.c.implicit_conversion', 'ImplicitConversion', 'cat.c.expressions', 'expression', 'Standard implicit conversions in expressions', 'intermediate'),
    ('concept.c.assignment', 'AssignmentOperator', 'cat.c.expressions', 'operator', 'Assignment and compound assignment operators', 'basic'),
    ('concept.c.arithmetic', 'ArithmeticOperator', 'cat.c.expressions', 'operator', 'Arithmetic operators including +, -, *, /, and %', 'basic'),
    ('concept.c.comparison', 'ComparisonOperator', 'cat.c.expressions', 'operator', 'Comparison operators such as <, <=, ==, !=', 'basic'),
    ('concept.c.logical', 'LogicalOperator', 'cat.c.expressions', 'operator', 'Logical operators including &&, ||, and !', 'basic'),
    ('concept.c.incdec', 'IncrementDecrement', 'cat.c.expressions', 'operator', 'Prefix and postfix increment/decrement', 'basic'),
    ('concept.c.member_access', 'MemberAccess', 'cat.c.expressions', 'operator', 'Member access with . and ->', 'basic'),
    ('concept.c.indirection', 'Indirection', 'cat.c.expressions', 'operator', 'Pointer dereference and indirection', 'intermediate'),
    ('concept.c.ternary', 'TernaryOperator', 'cat.c.expressions', 'operator', 'Conditional operator ?: in C expressions', 'intermediate'),
    ('concept.c.sizeof', 'SizeofOperator', 'cat.c.expressions', 'operator', 'Compile-time size query of objects and types', 'basic'),
    ('concept.c.cast', 'CastOperator', 'cat.c.expressions', 'operator', 'Explicit cast in C expressions', 'intermediate'),
    ('concept.c.generic_selection', 'GenericSelection', 'cat.c.expressions', 'core-language', 'Type-generic selection expression', 'advanced'),
    ('concept.c.variable', 'Variable', 'cat.c.declarations', 'declaration', 'Named object declaration in C', 'basic'),
    ('concept.c.pointer', 'Pointer', 'cat.c.declarations', 'declaration', 'Typed memory address value in C', 'intermediate'),
    ('concept.c.array', 'Array', 'cat.c.declarations', 'declaration', 'Contiguous sequence of elements with fixed extent', 'basic'),
    ('concept.c.enumeration', 'Enumeration', 'cat.c.declarations', 'declaration', 'Enumeration types and constants in C', 'basic'),
    ('concept.c.structure', 'Structure', 'cat.c.declarations', 'declaration', 'Structured record type with named members', 'basic'),
    ('concept.c.union', 'Union', 'cat.c.declarations', 'declaration', 'Union type sharing storage across members', 'intermediate'),
    ('concept.c.bit_field', 'BitField', 'cat.c.declarations', 'declaration', 'Packed integral members in structures', 'advanced'),
    ('concept.c.storage_duration', 'StorageDurationAndLinkage', 'cat.c.declarations', 'declaration', 'Static, automatic, allocated duration and linkage', 'intermediate'),
    ('concept.c.type_qualifier', 'TypeQualifier', 'cat.c.declarations', 'declaration', 'const, volatile, restrict, and related qualifiers', 'intermediate'),
    ('concept.c.atomic_type', 'AtomicType', 'cat.c.declarations', 'declaration', 'Atomic object types for concurrent programming', 'advanced'),
    ('concept.c.typedef', 'Typedef', 'cat.c.declarations', 'declaration', 'Type aliasing in C declarations', 'basic'),
    ('concept.c.attributes', 'Attributes', 'cat.c.declarations', 'declaration', 'Standardized attribute syntax in latest C', 'advanced'),
    ('concept.c.alignment', 'AlignmentSpecifier', 'cat.c.declarations', 'declaration', 'Alignment control with alignas/related facilities', 'advanced'),
    ('concept.c.function_decl', 'FunctionDeclaration', 'cat.c.functions', 'function', 'Function type and declaration syntax in C', 'basic'),
    ('concept.c.function_def', 'FunctionDefinition', 'cat.c.functions', 'function', 'Function definition syntax and body', 'basic'),
    ('concept.c.inline', 'InlineFunction', 'cat.c.functions', 'function', 'Inline function specifier in C', 'intermediate'),
    ('concept.c.variadic_args', 'VariadicArguments', 'cat.c.functions', 'function', 'Variadic function arguments using stdarg', 'advanced'),
    ('concept.c.nullptr', 'nullptr', 'cat.c.basic', 'core-language', 'The nullptr keyword introduced in latest C', 'basic'),
]
for node_id, name, category_id, kind, desc, difficulty in c_concepts:
    add_concept(node_id, name, 'C', category_id, kind, desc, difficulty=difficulty)

# C library concepts
c_lib_concepts = [
    ('concept.c.malloc', 'malloc', 'lib.c.dynamic_memory', 'library-function', 'Allocate dynamic memory block', 'intermediate', 'hdr.c.stdlib'),
    ('concept.c.calloc', 'calloc', 'lib.c.dynamic_memory', 'library-function', 'Allocate zero-initialized dynamic memory block', 'intermediate', 'hdr.c.stdlib'),
    ('concept.c.realloc', 'realloc', 'lib.c.dynamic_memory', 'library-function', 'Resize dynamic allocation', 'intermediate', 'hdr.c.stdlib'),
    ('concept.c.free', 'free', 'lib.c.dynamic_memory', 'library-function', 'Release dynamic allocation', 'intermediate', 'hdr.c.stdlib'),
    ('concept.c.string_handling', 'StringHandling', 'lib.c.strings', 'library-concept', 'Functions for null-terminated byte strings', 'basic', 'hdr.c.string'),
    ('concept.c.memcpy', 'memcpy', 'lib.c.strings', 'library-function', 'Copy bytes between memory regions', 'intermediate', 'hdr.c.string'),
    ('concept.c.strlen', 'strlen', 'lib.c.strings', 'library-function', 'Measure string length excluding null terminator', 'basic', 'hdr.c.string'),
    ('concept.c.formatted_io', 'FormattedIO', 'lib.c.io', 'library-concept', 'Formatted input and output with printf/scanf families', 'basic', 'hdr.c.stdio'),
    ('concept.c.file_io', 'FileIO', 'lib.c.io', 'library-concept', 'Buffered stream file input and output', 'basic', 'hdr.c.stdio'),
    ('concept.c.qsort', 'qsort', 'lib.c.algorithms', 'library-function', 'Generic quicksort-like sorting function', 'intermediate', 'hdr.c.stdlib'),
    ('concept.c.bsearch', 'bsearch', 'lib.c.algorithms', 'library-function', 'Binary search over sorted arrays', 'intermediate', 'hdr.c.stdlib'),
    ('concept.c.math_functions', 'MathFunctions', 'lib.c.numerics', 'library-concept', 'Standard mathematical functions in C', 'intermediate', 'hdr.c.math'),
    ('concept.c.random_number', 'PseudoRandomNumberGeneration', 'lib.c.numerics', 'library-concept', 'Pseudo-random number generation facilities', 'intermediate', 'hdr.c.stdlib'),
    ('concept.c.bit_manipulation', 'BitManipulation', 'lib.c.numerics', 'library-concept', 'C23 bit manipulation facilities', 'advanced', 'hdr.c.stdbit'),
    ('concept.c.checked_integer_arithmetic', 'CheckedIntegerArithmetic', 'lib.c.numerics', 'library-concept', 'C23 checked integer arithmetic support', 'advanced', 'hdr.c.stdckdint'),
    ('concept.c.threads_api', 'ThreadsAPI', 'lib.c.concurrency', 'library-concept', 'Thread creation and management in C', 'advanced', 'hdr.c.threads'),
    ('concept.c.atomics_api', 'AtomicsAPI', 'lib.c.concurrency', 'library-concept', 'Atomic operations and synchronization primitives', 'advanced', 'hdr.c.stdatomic'),
]
for node_id, name, module_id, kind, desc, difficulty, hdr in c_lib_concepts:
    add_node(node_id, 'ProgrammingConcept', name=name, language='C', category=module_id, kind=kind, standardVersion='latest', status='active', isModern='true', difficulty=difficulty, description=desc)
    add_rel(node_id, 'BELONGS_TO_MODULE', module_id)
    add_rel(node_id, 'IMPLEMENTED_IN', 'lang.c')
    add_rel(node_id, 'DECLARED_IN', hdr)

add_rel('concept.c.nullptr', 'SPECIALIZES', 'concept.c.literal')

for a, b in [
    ('concept.c.identifier', 'concept.c.variable'), ('concept.c.type', 'concept.c.variable'),
    ('concept.c.variable', 'concept.c.assignment'), ('concept.c.assignment', 'concept.c.if'),
    ('concept.c.comparison', 'concept.c.if'), ('concept.c.variable', 'concept.c.for'),
    ('concept.c.comparison', 'concept.c.for'), ('concept.c.incdec', 'concept.c.for'),
    ('concept.c.variable', 'concept.c.array'), ('concept.c.type', 'concept.c.array'),
    ('concept.c.array', 'concept.c.qsort'), ('concept.c.pointer', 'concept.c.indirection'),
    ('concept.c.pointer', 'concept.c.malloc'), ('concept.c.pointer', 'concept.c.free'),
    ('concept.c.structure', 'concept.c.member_access'), ('concept.c.pointer', 'concept.c.member_access'),
    ('concept.c.function_decl', 'concept.c.function_def'), ('concept.c.variadic_args', 'concept.c.formatted_io'),
    ('concept.c.atomic_type', 'concept.c.atomics_api'),
]:
    add_rel(a, 'PREREQUISITE_OF', b)

for view_id, concept_ids in {
    'view.intro_c': ['concept.c.variable', 'concept.c.if', 'concept.c.for', 'concept.c.while', 'concept.c.array', 'concept.c.function_def', 'concept.c.formatted_io'],
    'view.c_pointers': ['concept.c.pointer', 'concept.c.indirection', 'concept.c.malloc', 'concept.c.realloc', 'concept.c.free', 'concept.c.structure', 'concept.c.member_access'],
    'view.algorithms': ['concept.c.array', 'concept.c.for', 'concept.c.qsort', 'concept.c.bsearch', 'concept.c.comparison'],
}.items():
    for concept_id in concept_ids:
        add_rel(concept_id, 'VISIBLE_IN', view_id)

for nid, name, desc in [
    ('kp.c.array_bounds', 'ArrayBoundsInC', 'Correct indexing boundaries for arrays in C'),
    ('kp.c.pointer_arithmetic', 'PointerArithmeticBasics', 'How pointer arithmetic maps to element sizes'),
    ('kp.c.memory_lifecycle', 'DynamicMemoryLifecycle', 'Allocate, use, resize, and free heap memory correctly'),
    ('kp.c.struct_layout', 'StructMemberAccess', 'Access members correctly with . and -> operators'),
]:
    add_node(nid, 'KnowledgePoint', name=name, language='C', standardVersion='latest', status='active', isModern='true', description=desc)

add_rel('concept.c.array', 'HAS_KNOWLEDGE_POINT', 'kp.c.array_bounds')
add_rel('concept.c.pointer', 'HAS_KNOWLEDGE_POINT', 'kp.c.pointer_arithmetic')
add_rel('concept.c.malloc', 'HAS_KNOWLEDGE_POINT', 'kp.c.memory_lifecycle')
add_rel('concept.c.free', 'HAS_KNOWLEDGE_POINT', 'kp.c.memory_lifecycle')
add_rel('concept.c.structure', 'HAS_KNOWLEDGE_POINT', 'kp.c.struct_layout')

# C++ core concepts
cpp_concepts = [
    ('concept.cpp.name_lookup', 'NameLookup', 'cat.cpp.basic', 'core-language', 'Association of names with declarations in C++', 'basic'),
    ('concept.cpp.odr', 'OneDefinitionRule', 'cat.cpp.basic', 'core-language', 'ODR and definition consistency across translation units', 'advanced'),
    ('concept.cpp.type_system', 'TypeSystem', 'cat.cpp.basic', 'core-language', 'Fundamental, compound, and user-defined types in C++', 'basic'),
    ('concept.cpp.object_lifetime', 'ObjectLifetime', 'cat.cpp.basic', 'core-language', 'Construction, lifetime, and destruction of objects', 'intermediate'),
    ('concept.cpp.memory_model', 'MemoryModel', 'cat.cpp.basic', 'core-language', 'Concurrency-aware memory model in latest C++', 'advanced'),
    ('concept.cpp.modules', 'Modules', 'cat.cpp.basic', 'core-language', 'Modular code organization and import semantics', 'advanced'),
    ('concept.cpp.macro_definition', 'MacroDefinition', 'cat.cpp.preprocessor', 'core-language', 'Definition of function-like and object-like macros', 'basic'),
    ('concept.cpp.file_inclusion', 'FileInclusion', 'cat.cpp.preprocessor', 'core-language', 'Including headers with preprocessing directives', 'basic'),
    ('concept.cpp.conditional_compilation', 'ConditionalCompilation', 'cat.cpp.preprocessor', 'core-language', 'Conditional preprocessing in C++', 'basic'),
    ('concept.cpp.value_category', 'ValueCategory', 'cat.cpp.expressions', 'expression', 'lvalue, xvalue, prvalue model in C++', 'advanced'),
    ('concept.cpp.evaluation_order', 'EvaluationOrder', 'cat.cpp.expressions', 'expression', 'Sequencing and evaluation order rules', 'advanced'),
    ('concept.cpp.literal', 'Literal', 'cat.cpp.expressions', 'expression', 'Literal syntax including nullptr and user-defined literals', 'basic'),
    ('concept.cpp.new_delete', 'NewDeleteExpression', 'cat.cpp.expressions', 'expression', 'Dynamic object allocation and deallocation in C++', 'intermediate', 'false'),
    ('concept.cpp.casts', 'Casts', 'cat.cpp.expressions', 'expression', 'static_cast, dynamic_cast, const_cast, reinterpret_cast', 'intermediate'),
    ('concept.cpp.operator_overloading', 'OperatorOverloading', 'cat.cpp.functions', 'function', 'Custom operator implementations in user-defined types', 'advanced'),
    ('concept.cpp.namespace', 'Namespace', 'cat.cpp.declarations', 'declaration', 'Namespace declarations and organization', 'basic'),
    ('concept.cpp.reference', 'Reference', 'cat.cpp.declarations', 'declaration', 'Reference binding semantics in C++', 'basic'),
    ('concept.cpp.pointer', 'Pointer', 'cat.cpp.declarations', 'declaration', 'Raw pointers in C++', 'intermediate', 'false'),
    ('concept.cpp.array', 'Array', 'cat.cpp.declarations', 'declaration', 'Built-in arrays in C++', 'basic', 'false'),
    ('concept.cpp.structured_binding', 'StructuredBinding', 'cat.cpp.declarations', 'declaration', 'Decomposition declarations', 'intermediate'),
    ('concept.cpp.enum', 'Enumeration', 'cat.cpp.declarations', 'declaration', 'Scoped and unscoped enumerations', 'basic'),
    ('concept.cpp.auto', 'AutoTypeDeduction', 'cat.cpp.declarations', 'declaration', 'Type deduction with auto', 'basic'),
    ('concept.cpp.decltype', 'Decltype', 'cat.cpp.declarations', 'declaration', 'Type inference from expression form', 'advanced'),
    ('concept.cpp.constexpr', 'Constexpr', 'cat.cpp.declarations', 'declaration', 'Compile-time evaluation opt-in facility', 'advanced'),
    ('concept.cpp.constinit', 'Constinit', 'cat.cpp.declarations', 'declaration', 'Constant initialization requirement', 'advanced'),
    ('concept.cpp.attributes', 'Attributes', 'cat.cpp.declarations', 'declaration', 'Standard attribute syntax', 'intermediate'),
    ('concept.cpp.default_init', 'DefaultInitialization', 'cat.cpp.initialization', 'initialization', 'Initialization without explicit initializer', 'basic'),
    ('concept.cpp.value_init', 'ValueInitialization', 'cat.cpp.initialization', 'initialization', 'Value initialization rules in C++', 'basic'),
    ('concept.cpp.copy_init', 'CopyInitialization', 'cat.cpp.initialization', 'initialization', 'Copy-initialization semantics', 'basic'),
    ('concept.cpp.direct_init', 'DirectInitialization', 'cat.cpp.initialization', 'initialization', 'Direct-initialization semantics', 'basic'),
    ('concept.cpp.list_init', 'ListInitialization', 'cat.cpp.initialization', 'initialization', 'Brace initialization in C++', 'basic'),
    ('concept.cpp.aggregate_init', 'AggregateInitialization', 'cat.cpp.initialization', 'initialization', 'Aggregate initialization for aggregate types', 'intermediate'),
    ('concept.cpp.reference_init', 'ReferenceInitialization', 'cat.cpp.initialization', 'initialization', 'Reference binding during initialization', 'intermediate'),
    ('concept.cpp.copy_elision', 'CopyElision', 'cat.cpp.initialization', 'initialization', 'Elision of copies and moves', 'advanced'),
    ('concept.cpp.function_decl', 'FunctionDeclaration', 'cat.cpp.functions', 'function', 'Declaration of free and member functions in C++', 'basic'),
    ('concept.cpp.overload_resolution', 'OverloadResolution', 'cat.cpp.functions', 'function', 'Selection among overloaded functions', 'advanced'),
    ('concept.cpp.default_args', 'DefaultArguments', 'cat.cpp.functions', 'function', 'Default function arguments', 'basic'),
    ('concept.cpp.variadic_args', 'VariadicArguments', 'cat.cpp.functions', 'function', 'Variadic arguments in C++', 'advanced'),
    ('concept.cpp.lambda', 'LambdaExpression', 'cat.cpp.functions', 'function', 'Anonymous function objects in C++', 'intermediate'),
    ('concept.cpp.coroutines', 'Coroutines', 'cat.cpp.functions', 'function', 'Coroutine support in modern C++', 'advanced'),
    ('concept.cpp.if', 'IfStatement', 'cat.cpp.statements', 'statement', 'Conditional branching with if / else', 'basic'),
    ('concept.cpp.switch', 'SwitchStatement', 'cat.cpp.statements', 'statement', 'Multi-way branching with switch / case', 'basic'),
    ('concept.cpp.for', 'ForLoop', 'cat.cpp.statements', 'statement', 'Counter-controlled iteration with for', 'basic'),
    ('concept.cpp.range_for', 'RangeForLoop', 'cat.cpp.statements', 'statement', 'Range-based for loop in modern C++', 'basic'),
    ('concept.cpp.while', 'WhileLoop', 'cat.cpp.statements', 'statement', 'Condition-controlled iteration with while', 'basic'),
    ('concept.cpp.do_while', 'DoWhileLoop', 'cat.cpp.statements', 'statement', 'Post-test loop with do-while', 'basic'),
    ('concept.cpp.break', 'BreakStatement', 'cat.cpp.statements', 'statement', 'Early exit from loops or switch', 'basic'),
    ('concept.cpp.continue', 'ContinueStatement', 'cat.cpp.statements', 'statement', 'Proceed to next iteration of loop', 'basic'),
    ('concept.cpp.return', 'ReturnStatement', 'cat.cpp.statements', 'statement', 'Return from function', 'basic'),
    ('concept.cpp.class', 'Class', 'cat.cpp.classes', 'class', 'User-defined class type in C++', 'basic'),
    ('concept.cpp.struct', 'Struct', 'cat.cpp.classes', 'class', 'Struct type in C++ with default public access', 'basic'),
    ('concept.cpp.union', 'Union', 'cat.cpp.classes', 'class', 'Union type in C++', 'intermediate'),
    ('concept.cpp.access_specifier', 'AccessSpecifier', 'cat.cpp.classes', 'class', 'public, protected, and private access control', 'basic'),
    ('concept.cpp.constructor', 'Constructor', 'cat.cpp.classes', 'class', 'Object construction routines', 'basic'),
    ('concept.cpp.destructor', 'Destructor', 'cat.cpp.classes', 'class', 'Object destruction routine', 'basic'),
    ('concept.cpp.copy_semantics', 'CopySemantics', 'cat.cpp.classes', 'class', 'Copy constructor and copy assignment semantics', 'intermediate'),
    ('concept.cpp.move_semantics', 'MoveSemantics', 'cat.cpp.classes', 'class', 'Move constructor and move assignment semantics', 'advanced'),
    ('concept.cpp.inheritance', 'Inheritance', 'cat.cpp.classes', 'class', 'Deriving one class from another', 'intermediate'),
    ('concept.cpp.virtual_function', 'VirtualFunction', 'cat.cpp.classes', 'class', 'Runtime polymorphic virtual dispatch', 'advanced'),
    ('concept.cpp.abstract_class', 'AbstractClass', 'cat.cpp.classes', 'class', 'Class with pure virtual functions', 'advanced'),
    ('concept.cpp.polymorphism', 'Polymorphism', 'cat.cpp.classes', 'class', 'Dynamic polymorphism and runtime type behavior', 'advanced'),
    ('concept.cpp.friend', 'FriendDeclaration', 'cat.cpp.classes', 'class', 'Friend relationships between entities', 'advanced'),
    ('concept.cpp.static_member', 'StaticMember', 'cat.cpp.classes', 'class', 'Static data and functions in classes', 'intermediate'),
    ('concept.cpp.class_template', 'ClassTemplate', 'cat.cpp.templates', 'template', 'Family of class definitions parameterized by template parameters', 'advanced'),
    ('concept.cpp.function_template', 'FunctionTemplate', 'cat.cpp.templates', 'template', 'Family of functions parameterized by template parameters', 'advanced'),
    ('concept.cpp.variable_template', 'VariableTemplate', 'cat.cpp.templates', 'template', 'Variable templates in C++', 'advanced'),
    ('concept.cpp.template_specialization', 'TemplateSpecialization', 'cat.cpp.templates', 'template', 'Explicit specialization of templates', 'advanced'),
    ('concept.cpp.partial_specialization', 'PartialSpecialization', 'cat.cpp.templates', 'template', 'Partial specialization of class or variable templates', 'advanced'),
    ('concept.cpp.concepts_constraints', 'ConceptsAndConstraints', 'cat.cpp.templates', 'template', 'Template constraints and concepts', 'advanced'),
    ('concept.cpp.parameter_pack', 'ParameterPack', 'cat.cpp.templates', 'template', 'Variadic template pack parameters', 'advanced'),
    ('concept.cpp.template_instantiation', 'TemplateInstantiation', 'cat.cpp.templates', 'template', 'Instantiation of template definitions into concrete entities', 'advanced'),
    ('concept.cpp.throw', 'ThrowExpression', 'cat.cpp.exceptions', 'exception', 'Throwing exceptions in C++', 'intermediate'),
    ('concept.cpp.try_catch', 'TryCatch', 'cat.cpp.exceptions', 'exception', 'Handling exceptions with try and catch', 'intermediate'),
    ('concept.cpp.noexcept', 'Noexcept', 'cat.cpp.exceptions', 'exception', 'noexcept for exception specification and optimization', 'advanced'),
    ('concept.cpp.standard_exception', 'StandardException', 'cat.cpp.exceptions', 'exception', 'Standard library exception hierarchy', 'intermediate'),
]
for item in cpp_concepts:
    if len(item) == 6:
        node_id, name, category_id, kind, desc, difficulty = item
        is_modern = 'true'
    else:
        node_id, name, category_id, kind, desc, difficulty, is_modern = item
    add_concept(node_id, name, 'C++', category_id, kind, desc, difficulty=difficulty, is_modern=is_modern)

cpp_lib_concepts = [
    ('concept.cpp.smart_pointer', 'SmartPointer', 'lib.cpp.memory', 'library-concept', 'Smart pointer ownership abstraction in modern C++', 'advanced', 'hdr.cpp.memory'),
    ('concept.cpp.unique_ptr', 'std::unique_ptr', 'lib.cpp.memory', 'library-class', 'Exclusive ownership smart pointer', 'intermediate', 'hdr.cpp.memory'),
    ('concept.cpp.shared_ptr', 'std::shared_ptr', 'lib.cpp.memory', 'library-class', 'Reference-counted shared ownership smart pointer', 'advanced', 'hdr.cpp.memory'),
    ('concept.cpp.weak_ptr', 'std::weak_ptr', 'lib.cpp.memory', 'library-class', 'Non-owning weak reference to shared object', 'advanced', 'hdr.cpp.memory'),
    ('concept.cpp.memory_resource', 'MemoryResource', 'lib.cpp.memory', 'library-concept', 'Polymorphic memory resources and allocators', 'advanced', 'hdr.cpp.memory_resource'),
    ('concept.cpp.type_traits', 'TypeTraits', 'lib.cpp.metaprogramming', 'library-concept', 'Compile-time type inspection and transformation', 'advanced', 'hdr.cpp.type_traits'),
    ('concept.cpp.any', 'std::any', 'lib.cpp.utilities', 'library-class', 'Type-erased single value holder', 'intermediate', 'hdr.cpp.any'),
    ('concept.cpp.optional', 'std::optional', 'lib.cpp.utilities', 'library-class', 'Optional contained value or empty state', 'intermediate', 'hdr.cpp.optional'),
    ('concept.cpp.variant', 'std::variant', 'lib.cpp.utilities', 'library-class', 'Type-safe tagged union', 'advanced', 'hdr.cpp.variant'),
    ('concept.cpp.pair_tuple', 'PairAndTuple', 'lib.cpp.utilities', 'library-concept', 'Fixed-size heterogeneous value groups', 'basic', 'hdr.cpp.any'),
    ('concept.cpp.vector', 'std::vector', 'lib.cpp.containers', 'library-class', 'Contiguous dynamic array container', 'basic', 'hdr.cpp.vector'),
    ('concept.cpp.array_container', 'std::array', 'lib.cpp.containers', 'library-class', 'Fixed-size array wrapper with STL interface', 'basic', 'hdr.cpp.array'),
    ('concept.cpp.deque', 'std::deque', 'lib.cpp.containers', 'library-class', 'Double-ended queue container', 'intermediate', 'hdr.cpp.deque'),
    ('concept.cpp.list', 'std::list', 'lib.cpp.containers', 'library-class', 'Bidirectional linked list container', 'intermediate', 'hdr.cpp.list'),
    ('concept.cpp.map', 'std::map', 'lib.cpp.containers', 'library-class', 'Ordered key-value associative container', 'intermediate', 'hdr.cpp.map'),
    ('concept.cpp.unordered_map', 'std::unordered_map', 'lib.cpp.containers', 'library-class', 'Hash-based key-value associative container', 'intermediate', 'hdr.cpp.unordered_map'),
    ('concept.cpp.stack_queue', 'ContainerAdaptors', 'lib.cpp.containers', 'library-concept', 'Adaptors such as stack, queue, and priority_queue', 'intermediate', 'hdr.cpp.vector'),
    ('concept.cpp.span', 'std::span', 'lib.cpp.containers', 'library-class', 'Non-owning view over contiguous sequence', 'advanced', 'hdr.cpp.array'),
    ('concept.cpp.iterator', 'Iterator', 'lib.cpp.iterators', 'library-concept', 'Iterator abstraction over sequences and containers', 'intermediate', 'hdr.cpp.iterator'),
    ('concept.cpp.ranges', 'RangesLibrary', 'lib.cpp.ranges', 'library-concept', 'Composable range and view abstraction', 'advanced', 'hdr.cpp.ranges'),
    ('concept.cpp.views', 'Views', 'lib.cpp.ranges', 'library-concept', 'Lazy composable range adaptors', 'advanced', 'hdr.cpp.ranges'),
    ('concept.cpp.sort', 'std::sort', 'lib.cpp.algorithms', 'library-function', 'General-purpose sorting algorithm', 'basic', 'hdr.cpp.algorithm'),
    ('concept.cpp.find', 'std::find', 'lib.cpp.algorithms', 'library-function', 'Linear search algorithm', 'basic', 'hdr.cpp.algorithm'),
    ('concept.cpp.binary_search', 'std::binary_search', 'lib.cpp.algorithms', 'library-function', 'Binary search over sorted range', 'intermediate', 'hdr.cpp.algorithm'),
    ('concept.cpp.accumulate', 'std::accumulate', 'lib.cpp.algorithms', 'library-function', 'Numeric accumulation algorithm', 'intermediate', 'hdr.cpp.algorithm'),
    ('concept.cpp.string', 'std::string', 'lib.cpp.strings', 'library-class', 'Dynamic owning string type', 'basic', 'hdr.cpp.string'),
    ('concept.cpp.string_view', 'std::string_view', 'lib.cpp.strings', 'library-class', 'Non-owning string view type', 'intermediate', 'hdr.cpp.string_view'),
    ('concept.cpp.regex', 'std::regex', 'lib.cpp.text_processing', 'library-class', 'Regular expression engine and matcher', 'advanced', 'hdr.cpp.regex'),
    ('concept.cpp.format', 'std::format', 'lib.cpp.text_processing', 'library-function', 'Type-safe formatting facility', 'intermediate', 'hdr.cpp.format'),
    ('concept.cpp.print_functions', 'PrintFunctions', 'lib.cpp.io', 'library-concept', 'High-level print functions standardized in C++23', 'basic', 'hdr.cpp.print'),
    ('concept.cpp.random', 'RandomNumberGeneration', 'lib.cpp.numerics', 'library-concept', 'Pseudo-random engines and distributions', 'advanced', 'hdr.cpp.algorithm'),
    ('concept.cpp.chrono', 'std::chrono', 'lib.cpp.time', 'library-concept', 'Time durations, clocks, and calendar facilities', 'intermediate', 'hdr.cpp.chrono'),
    ('concept.cpp.iostream', 'Iostreams', 'lib.cpp.io', 'library-concept', 'Standard stream-based input and output', 'basic', 'hdr.cpp.iostream'),
    ('concept.cpp.filesystem', 'std::filesystem', 'lib.cpp.filesystem', 'library-concept', 'Filesystem path and directory operations', 'intermediate', 'hdr.cpp.filesystem'),
    ('concept.cpp.thread', 'std::thread', 'lib.cpp.concurrency', 'library-class', 'Thread object for concurrent execution', 'advanced', 'hdr.cpp.thread'),
    ('concept.cpp.jthread', 'std::jthread', 'lib.cpp.concurrency', 'library-class', 'Joining thread wrapper with stop token support', 'advanced', 'hdr.cpp.thread'),
    ('concept.cpp.mutex', 'std::mutex', 'lib.cpp.concurrency', 'library-class', 'Mutual exclusion primitive', 'advanced', 'hdr.cpp.mutex'),
    ('concept.cpp.atomic', 'std::atomic', 'lib.cpp.concurrency', 'library-class', 'Atomic object wrapper for lock-free and lock-based concurrency', 'advanced', 'hdr.cpp.atomic'),
    ('concept.cpp.condition_variable', 'std::condition_variable', 'lib.cpp.concurrency', 'library-class', 'Blocking synchronization primitive for waiting threads', 'advanced', 'hdr.cpp.mutex'),
    ('concept.cpp.stacktrace', 'std::stacktrace', 'lib.cpp.diagnostics', 'library-class', 'Stacktrace support added in modern C++', 'advanced', 'hdr.cpp.stacktrace'),
    ('concept.cpp.library_concepts', 'ConceptsLibrary', 'lib.cpp.concepts', 'library-concept', 'Standard library concepts used for template constraints', 'advanced', 'hdr.cpp.concepts'),
]
for node_id, name, module_id, kind, desc, difficulty, hdr in cpp_lib_concepts:
    add_node(node_id, 'ProgrammingConcept', name=name, language='C++', category=module_id, kind=kind, standardVersion='latest', status='active', isModern='true', difficulty=difficulty, description=desc)
    add_rel(node_id, 'BELONGS_TO_MODULE', module_id)
    add_rel(node_id, 'IMPLEMENTED_IN', 'lang.cpp')
    add_rel(node_id, 'DECLARED_IN', hdr)

for s, rt, e in [
    ('concept.cpp.unique_ptr', 'SPECIALIZES', 'concept.cpp.smart_pointer'),
    ('concept.cpp.shared_ptr', 'SPECIALIZES', 'concept.cpp.smart_pointer'),
    ('concept.cpp.weak_ptr', 'SPECIALIZES', 'concept.cpp.smart_pointer'),
    ('concept.cpp.vector', 'SPECIALIZES', 'concept.cpp.array_container'),
    ('concept.cpp.range_for', 'SPECIALIZES', 'concept.cpp.for'),
    ('concept.cpp.views', 'SPECIALIZES', 'concept.cpp.ranges'),
]:
    add_rel(s, rt, e)

for a, b in [
    ('concept.cpp.type_system', 'concept.cpp.class'), ('concept.cpp.class', 'concept.cpp.constructor'),
    ('concept.cpp.class', 'concept.cpp.destructor'), ('concept.cpp.class', 'concept.cpp.inheritance'),
    ('concept.cpp.inheritance', 'concept.cpp.virtual_function'), ('concept.cpp.virtual_function', 'concept.cpp.polymorphism'),
    ('concept.cpp.class', 'concept.cpp.copy_semantics'), ('concept.cpp.copy_semantics', 'concept.cpp.move_semantics'),
    ('concept.cpp.reference', 'concept.cpp.move_semantics'), ('concept.cpp.value_category', 'concept.cpp.move_semantics'),
    ('concept.cpp.class_template', 'concept.cpp.vector'), ('concept.cpp.function_template', 'concept.cpp.sort'),
    ('concept.cpp.class_template', 'concept.cpp.optional'), ('concept.cpp.reference', 'concept.cpp.range_for'),
    ('concept.cpp.iterator', 'concept.cpp.ranges'), ('concept.cpp.vector', 'concept.cpp.iterator'),
    ('concept.cpp.vector', 'concept.cpp.range_for'), ('concept.cpp.lambda', 'concept.cpp.views'),
    ('concept.cpp.smart_pointer', 'concept.cpp.filesystem'), ('concept.cpp.noexcept', 'concept.cpp.smart_pointer'),
    ('concept.cpp.namespace', 'concept.cpp.iostream'), ('concept.cpp.thread', 'concept.cpp.mutex'),
    ('concept.cpp.mutex', 'concept.cpp.condition_variable'), ('concept.cpp.memory_model', 'concept.cpp.atomic'),
]:
    add_rel(a, 'PREREQUISITE_OF', b)

for view_id, concept_ids in {
    'view.cpp_oop': ['concept.cpp.class', 'concept.cpp.constructor', 'concept.cpp.destructor', 'concept.cpp.inheritance', 'concept.cpp.virtual_function', 'concept.cpp.abstract_class', 'concept.cpp.polymorphism'],
    'view.cpp_modern': ['concept.cpp.auto', 'concept.cpp.list_init', 'concept.cpp.range_for', 'concept.cpp.lambda', 'concept.cpp.move_semantics', 'concept.cpp.smart_pointer', 'concept.cpp.unique_ptr', 'concept.cpp.string_view', 'concept.cpp.print_functions'],
    'view.cpp_stl': ['concept.cpp.class_template', 'concept.cpp.function_template', 'concept.cpp.vector', 'concept.cpp.map', 'concept.cpp.unordered_map', 'concept.cpp.iterator', 'concept.cpp.ranges', 'concept.cpp.views', 'concept.cpp.sort', 'concept.cpp.find', 'concept.cpp.binary_search'],
    'view.algorithms': ['concept.cpp.vector', 'concept.cpp.sort', 'concept.cpp.find', 'concept.cpp.binary_search', 'concept.cpp.accumulate', 'concept.cpp.range_for'],
}.items():
    for concept_id in concept_ids:
        add_rel(concept_id, 'VISIBLE_IN', view_id)

for nid, name, desc in [
    ('kp.cpp.raii', 'RAIIOwnership', 'Tie resource lifetime to object lifetime using constructors and destructors'),
    ('kp.cpp.move_ownership', 'MoveOwnershipTransfer', 'Transfer ownership safely using move semantics'),
    ('kp.cpp.iterator_invalidation', 'IteratorInvalidation', 'Understand when container operations invalidate iterators and references'),
    ('kp.cpp.template_deduction', 'TemplateArgumentDeduction', 'How template arguments are deduced from call-site context'),
    ('kp.cpp.range_pipeline', 'RangePipelineBasics', 'Compose filters, transforms, and views over ranges'),
]:
    add_node(nid, 'KnowledgePoint', name=name, language='C++', standardVersion='latest', status='active', isModern='true', description=desc)

add_concept('concept.cpp.raii', 'RAII', 'C++', 'cat.cpp.classes', 'design-principle', 'Resource Acquisition Is Initialization for deterministic cleanup', difficulty='advanced')
add_rel('concept.cpp.raii', 'VISIBLE_IN', 'view.cpp_modern')
add_rel('concept.cpp.destructor', 'PREREQUISITE_OF', 'concept.cpp.raii')
add_rel('concept.cpp.raii', 'PREREQUISITE_OF', 'concept.cpp.smart_pointer')
add_rel('concept.cpp.raii', 'HAS_KNOWLEDGE_POINT', 'kp.cpp.raii')
add_rel('concept.cpp.move_semantics', 'HAS_KNOWLEDGE_POINT', 'kp.cpp.move_ownership')
add_rel('concept.cpp.iterator', 'HAS_KNOWLEDGE_POINT', 'kp.cpp.iterator_invalidation')
add_rel('concept.cpp.function_template', 'HAS_KNOWLEDGE_POINT', 'kp.cpp.template_deduction')
add_rel('concept.cpp.ranges', 'HAS_KNOWLEDGE_POINT', 'kp.cpp.range_pipeline')

constraints = [
    "CREATE CONSTRAINT language_id_unique IF NOT EXISTS FOR (n:ProgrammingLanguage) REQUIRE n.id IS UNIQUE;",
    "CREATE CONSTRAINT category_id_unique IF NOT EXISTS FOR (n:ConceptCategory) REQUIRE n.id IS UNIQUE;",
    "CREATE CONSTRAINT module_id_unique IF NOT EXISTS FOR (n:LibraryModule) REQUIRE n.id IS UNIQUE;",
    "CREATE CONSTRAINT header_id_unique IF NOT EXISTS FOR (n:Header) REQUIRE n.id IS UNIQUE;",
    "CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (n:ProgrammingConcept) REQUIRE n.id IS UNIQUE;",
    "CREATE CONSTRAINT kp_id_unique IF NOT EXISTS FOR (n:KnowledgePoint) REQUIRE n.id IS UNIQUE;",
    "CREATE CONSTRAINT view_id_unique IF NOT EXISTS FOR (n:PedagogicalView) REQUIRE n.id IS UNIQUE;",
]


def quote(v):
    if v is None:
        return 'null'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    s = str(v)
    if s.lower() in {'true', 'false'}:
        return s.lower()
    escaped = s.replace('\\', '\\\\').replace("'", "\\'")
    return f"'{escaped}'"

cypher_lines = []
cypher_lines.extend(constraints)
cypher_lines.append('')
cypher_lines.append('// Nodes')
for row in nodes:
    props = ', '.join([f"{k}: {quote(v)}" for k, v in row.items() if k != 'label'])
    cypher_lines.append(f"MERGE (n:{row['label']} {{id: {quote(row['id'])}}}) SET n += {{{props}}};")

cypher_lines.append('')
cypher_lines.append('// Relationships')
for row in rels:
    prop_items = {k: v for k, v in row.items() if k not in {'start_id', 'type', 'end_id'}}
    prop_text = ''
    if prop_items:
        prop_text = ' {' + ', '.join(f"{k}: {quote(v)}" for k, v in prop_items.items()) + '}'
    cypher_lines.append(
        f"MATCH (a {{id: {quote(row['start_id'])}}}), (b {{id: {quote(row['end_id'])}}}) MERGE (a)-[r:{row['type']}{prop_text}]->(b);"
    )

node_fields = sorted({k for row in nodes for k in row.keys()})
with (out_dir / 'neo4j_latest_concepts_nodes.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=node_fields)
    writer.writeheader()
    for row in nodes:
        writer.writerow(row)

rel_fields = sorted({k for row in rels for k in row.keys()})
with (out_dir / 'neo4j_latest_concepts_relationships.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rel_fields)
    writer.writeheader()
    for row in rels:
        writer.writerow(row)

(out_dir / 'neo4j_latest_concepts_seed.cypher').write_text('\n'.join(cypher_lines), encoding='utf-8')

summary = {
    'node_count': len(nodes),
    'relationship_count': len(rels),
    'label_breakdown': {},
    'relationship_breakdown': {},
    'files': [
        'neo4j_latest_concepts_nodes.csv',
        'neo4j_latest_concepts_relationships.csv',
        'neo4j_latest_concepts_seed.cypher',
        'build_neo4j_latest_concepts_dataset.py',
    ],
}
for row in nodes:
    summary['label_breakdown'][row['label']] = summary['label_breakdown'].get(row['label'], 0) + 1
for row in rels:
    summary['relationship_breakdown'][row['type']] = summary['relationship_breakdown'].get(row['type'], 0) + 1
(out_dir / 'neo4j_latest_concepts_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')

print(json.dumps(summary, indent=2, ensure_ascii=False))
