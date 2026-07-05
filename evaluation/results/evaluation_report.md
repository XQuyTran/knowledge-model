# Evaluation Report — Hybrid vs LLM-only

## Summary

| Metric | Hybrid (Rule + LLM) | LLM-only |
|--------|--------------------:|---------:|
| Detection Accuracy | 7/13 (54%) | 0/13 (0%) |
| Avg Time (s) | 2.84 | 0.00 |

## Per-Case Detail

| Case | Expected | Hybrid | LLM-only |
|------|----------|--------|----------|
| off_by_one_01 | bug.off_by_one | bug.array_out_of_bounds (✗) | None (✗) |
| off_by_one_02 | bug.off_by_one | bug.array_out_of_bounds (✗) | None (✗) |
| null_deref_01 | bug.null_dereference | bug.null_dereference (✓) | None (✗) |
| memory_leak_01 | bug.memory_leak | bug.memory_leak (✓) | None (✗) |
| missing_return_01 | bug.missing_return | bug.missing_return (✓) | None (✗) |
| array_oob_01 | bug.array_out_of_bounds | bug.array_out_of_bounds (✓) | None (✗) |
| infinite_loop_01 | bug.wrong_loop_condition | bug.wrong_loop_condition (✓) | None (✗) |
| use_after_free_01 | bug.use_after_free | bug.use_after_free (✓) | None (✗) |
| recursion_no_progress_01 | bug.no_recursive_progress | bug.null_dereference (✗) | None (✗) |
| correct_sum_01 | None | None (✓) | None (✗) |
| bubble_sort_oob_01 | bug.off_by_one | None (✗) | None (✗) |
| binary_search_wrong_01 | bug.wrong_loop_condition | None (✗) | None (✗) |
| factorial_rec_missing_return_01 | bug.missing_return | bug.array_out_of_bounds (✗) | None (✗) |

## Notes
- LLM-only requires valid LLM environment variables.
- Hybrid runs fully offline for static analysis.
