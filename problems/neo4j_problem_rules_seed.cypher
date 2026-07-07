// Seed file for problem-level priors used by Neo4jGraphRepository.match_problem_rules
// Generated from InMemoryGraphRepository.PROBLEM_RULES in graph_repository.py

// Optional uniqueness constraints (safe on Neo4j 5+)
CREATE CONSTRAINT problem_id_unique IF NOT EXISTS FOR (p:Problem) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT algorithm_id_unique IF NOT EXISTS FOR (a:Algorithm) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT programming_bug_id_unique IF NOT EXISTS FOR (b:ProgrammingBug) REQUIRE b.id IS UNIQUE;

// ex_array_sum
MERGE (p:Problem {id: "ex_array_sum"})
SET p.name = "Array Sum";
MERGE (algo:Algorithm {id: "algorithm.duyet_mang_tuan_tu"})
SET algo.name = "Sequential Array Traversal";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.off_by_one"});

MATCH (p:Problem {id: "ex_array_sum"}), (bug:ProgrammingBug {id: "bug.off_by_one"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.array_out_of_bounds"});

MATCH (p:Problem {id: "ex_array_sum"}), (bug:ProgrammingBug {id: "bug.array_out_of_bounds"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_array_max
MERGE (p:Problem {id: "ex_array_max"})
SET p.name = "Array Maximum";
MERGE (algo:Algorithm {id: "algorithm.duyet_mang_tim_max"})
SET algo.name = "Array Traversal for Maximum";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.off_by_one"});

MATCH (p:Problem {id: "ex_array_max"}), (bug:ProgrammingBug {id: "bug.off_by_one"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.uninitialized_value"});

MATCH (p:Problem {id: "ex_array_max"}), (bug:ProgrammingBug {id: "bug.uninitialized_value"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_array_reverse
MERGE (p:Problem {id: "ex_array_reverse"})
SET p.name = "Array Reverse";
MERGE (algo:Algorithm {id: "algorithm.dao_nguoc_tai_cho"})
SET algo.name = "In-place Array Reversal";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.off_by_one"});

MATCH (p:Problem {id: "ex_array_reverse"}), (bug:ProgrammingBug {id: "bug.off_by_one"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.array_out_of_bounds"});

MATCH (p:Problem {id: "ex_array_reverse"}), (bug:ProgrammingBug {id: "bug.array_out_of_bounds"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_loop_factorial
MERGE (p:Problem {id: "ex_loop_factorial"})
SET p.name = "Loop Factorial";
MERGE (algo:Algorithm {id: "algorithm.vong_lap_tich_luy"})
SET algo.name = "Iterative Accumulation";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.off_by_one"});

MATCH (p:Problem {id: "ex_loop_factorial"}), (bug:ProgrammingBug {id: "bug.off_by_one"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.wrong_loop_condition"});

MATCH (p:Problem {id: "ex_loop_factorial"}), (bug:ProgrammingBug {id: "bug.wrong_loop_condition"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_loop_prime
MERGE (p:Problem {id: "ex_loop_prime"})
SET p.name = "Prime Check";
MERGE (algo:Algorithm {id: "algorithm.kiem_tra_uoc_so"})
SET algo.name = "Divisor Checking";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.wrong_loop_condition"});

MATCH (p:Problem {id: "ex_loop_prime"}), (bug:ProgrammingBug {id: "bug.wrong_loop_condition"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.off_by_one"});

MATCH (p:Problem {id: "ex_loop_prime"}), (bug:ProgrammingBug {id: "bug.off_by_one"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_loop_fibonacci
MERGE (p:Problem {id: "ex_loop_fibonacci"})
SET p.name = "Loop Fibonacci";
MERGE (algo:Algorithm {id: "algorithm.vong_lap_bo_nho_dem"})
SET algo.name = "Iterative Fibonacci with State Variables";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.off_by_one"});

MATCH (p:Problem {id: "ex_loop_fibonacci"}), (bug:ProgrammingBug {id: "bug.off_by_one"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.uninitialized_value"});

MATCH (p:Problem {id: "ex_loop_fibonacci"}), (bug:ProgrammingBug {id: "bug.uninitialized_value"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_rec_factorial
MERGE (p:Problem {id: "ex_rec_factorial"})
SET p.name = "Recursive Factorial";
MERGE (algo:Algorithm {id: "algorithm.de_quy_tuyen_tinh"})
SET algo.name = "Linear Recursion";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.no_recursive_progress"});

MATCH (p:Problem {id: "ex_rec_factorial"}), (bug:ProgrammingBug {id: "bug.no_recursive_progress"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.missing_return"});

MATCH (p:Problem {id: "ex_rec_factorial"}), (bug:ProgrammingBug {id: "bug.missing_return"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_rec_fibonacci
MERGE (p:Problem {id: "ex_rec_fibonacci"})
SET p.name = "Recursive Fibonacci";
MERGE (algo:Algorithm {id: "algorithm.de_quy_nhi_phan"})
SET algo.name = "Binary Recursion";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.no_recursive_progress"});

MATCH (p:Problem {id: "ex_rec_fibonacci"}), (bug:ProgrammingBug {id: "bug.no_recursive_progress"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.missing_return"});

MATCH (p:Problem {id: "ex_rec_fibonacci"}), (bug:ProgrammingBug {id: "bug.missing_return"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.off_by_one"});

MATCH (p:Problem {id: "ex_rec_fibonacci"}), (bug:ProgrammingBug {id: "bug.off_by_one"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_rec_hanoi
MERGE (p:Problem {id: "ex_rec_hanoi"})
SET p.name = "Tower of Hanoi";
MERGE (algo:Algorithm {id: "algorithm.de_quy_chia_de_tri"})
SET algo.name = "Divide and Conquer Recursion";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.no_recursive_progress"});

MATCH (p:Problem {id: "ex_rec_hanoi"}), (bug:ProgrammingBug {id: "bug.no_recursive_progress"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.wrong_loop_condition"});

MATCH (p:Problem {id: "ex_rec_hanoi"}), (bug:ProgrammingBug {id: "bug.wrong_loop_condition"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_ds_linked_list
MERGE (p:Problem {id: "ex_ds_linked_list"})
SET p.name = "Linked List Operations";
MERGE (algo:Algorithm {id: "algorithm.thao_tac_danh_sach_lien_ket"})
SET algo.name = "Linked List Manipulation";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.null_dereference"});

MATCH (p:Problem {id: "ex_ds_linked_list"}), (bug:ProgrammingBug {id: "bug.null_dereference"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.memory_leak"});

MATCH (p:Problem {id: "ex_ds_linked_list"}), (bug:ProgrammingBug {id: "bug.memory_leak"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.dangling_pointer"});

MATCH (p:Problem {id: "ex_ds_linked_list"}), (bug:ProgrammingBug {id: "bug.dangling_pointer"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_ds_stack_array
MERGE (p:Problem {id: "ex_ds_stack_array"})
SET p.name = "Array-based Stack";
MERGE (algo:Algorithm {id: "algorithm.ngan_xep_lifo"})
SET algo.name = "LIFO Stack";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.array_out_of_bounds"});

MATCH (p:Problem {id: "ex_ds_stack_array"}), (bug:ProgrammingBug {id: "bug.array_out_of_bounds"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.off_by_one"});

MATCH (p:Problem {id: "ex_ds_stack_array"}), (bug:ProgrammingBug {id: "bug.off_by_one"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_sort_bubble
MERGE (p:Problem {id: "ex_sort_bubble"})
SET p.name = "Bubble Sort";
MERGE (algo:Algorithm {id: "algorithm.bubble_sort"})
SET algo.name = "Bubble Sort";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.off_by_one"});

MATCH (p:Problem {id: "ex_sort_bubble"}), (bug:ProgrammingBug {id: "bug.off_by_one"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.array_out_of_bounds"});

MATCH (p:Problem {id: "ex_sort_bubble"}), (bug:ProgrammingBug {id: "bug.array_out_of_bounds"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.wrong_loop_condition"});

MATCH (p:Problem {id: "ex_sort_bubble"}), (bug:ProgrammingBug {id: "bug.wrong_loop_condition"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_sort_selection
MERGE (p:Problem {id: "ex_sort_selection"})
SET p.name = "Selection Sort";
MERGE (algo:Algorithm {id: "algorithm.selection_sort"})
SET algo.name = "Selection Sort";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.off_by_one"});

MATCH (p:Problem {id: "ex_sort_selection"}), (bug:ProgrammingBug {id: "bug.off_by_one"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.array_out_of_bounds"});

MATCH (p:Problem {id: "ex_sort_selection"}), (bug:ProgrammingBug {id: "bug.array_out_of_bounds"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_sort_insertion
MERGE (p:Problem {id: "ex_sort_insertion"})
SET p.name = "Insertion Sort";
MERGE (algo:Algorithm {id: "algorithm.insertion_sort"})
SET algo.name = "Insertion Sort";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.array_out_of_bounds"});

MATCH (p:Problem {id: "ex_sort_insertion"}), (bug:ProgrammingBug {id: "bug.array_out_of_bounds"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.off_by_one"});

MATCH (p:Problem {id: "ex_sort_insertion"}), (bug:ProgrammingBug {id: "bug.off_by_one"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_search_linear
MERGE (p:Problem {id: "ex_search_linear"})
SET p.name = "Linear Search";
MERGE (algo:Algorithm {id: "algorithm.tim_kiem_tuyen_tinh"})
SET algo.name = "Linear Search";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.off_by_one"});

MATCH (p:Problem {id: "ex_search_linear"}), (bug:ProgrammingBug {id: "bug.off_by_one"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.wrong_loop_condition"});

MATCH (p:Problem {id: "ex_search_linear"}), (bug:ProgrammingBug {id: "bug.wrong_loop_condition"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);

// ex_search_binary
MERGE (p:Problem {id: "ex_search_binary"})
SET p.name = "Binary Search";
MERGE (algo:Algorithm {id: "algorithm.tim_kiem_nhi_phan"})
SET algo.name = "Binary Search";
MERGE (p)-[:HAS_ALGORITHM]->(algo);
MERGE (bug:ProgrammingBug {id: "bug.off_by_one"});

MATCH (p:Problem {id: "ex_search_binary"}), (bug:ProgrammingBug {id: "bug.off_by_one"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.wrong_loop_condition"});

MATCH (p:Problem {id: "ex_search_binary"}), (bug:ProgrammingBug {id: "bug.wrong_loop_condition"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
MERGE (bug:ProgrammingBug {id: "bug.infinite_loop"});

MATCH (p:Problem {id: "ex_search_binary"}), (bug:ProgrammingBug {id: "bug.infinite_loop"})
MERGE (p)-[:HAS_COMMON_BUG]->(bug);
