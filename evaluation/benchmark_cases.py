BENCHMARK_CASES = [
    {
        "id": "off_by_one_01",
        "title": "Off-by-one trong vòng lặp tính tổng",
        "problem": "Tính tổng n phần tử mảng",
        "expected_bug": "bug.off_by_one",
        # Loop bound `i <= n` is an off-by-one that manifests as an out-of-bounds read;
        # both labels describe the same defect (same diagnostic rule emits both).
        "acceptable_bugs": ["bug.off_by_one", "bug.array_out_of_bounds"],
        "problem_id": "ex_array_sum",
        "source_code": """#include <iostream>
int main() {
    int n = 5;
    int a[5] = {1, 2, 3, 4, 5};
    int sum = 0;
    for (int i = 0; i <= n; ++i) {
        sum += a[i];
    }
    std::cout << sum;
}""",
        "test_cases": [{"name": "sample", "input_data": "", "expected_output": "15"}],
    },
    {
        "id": "off_by_one_02",
        "title": "Off-by-one khi duyệt mảng từ 1",
        "problem": "In các phần tử mảng",
        "expected_bug": "bug.off_by_one",
        "acceptable_bugs": ["bug.off_by_one", "bug.array_out_of_bounds"],
        "problem_id": "ex_array_sum",
        "source_code": """#include <iostream>
int main() {
    int arr[] = {10, 20, 30, 40};
    int n = 4;
    for (int i = 1; i <= n; ++i) {
        std::cout << arr[i] << " ";
    }
}""",
        "test_cases": [{"name": "sample", "input_data": "", "expected_output": "10 20 30 40"}],
    },
    {
        "id": "null_deref_01",
        "title": "Null pointer dereference",
        "problem": "Gán giá trị cho con trỏ",
        "expected_bug": "bug.null_dereference",
        "problem_id": "ex_ds_linked_list",
        "source_code": """#include <iostream>
int main() {
    int* p = nullptr;
    *p = 42;
    std::cout << *p;
}""",
        "test_cases": [],
    },
    {
        "id": "memory_leak_01",
        "title": "Memory leak không giải phóng",
        "problem": "Cấp phát mảng động, tính tổng",
        "expected_bug": "bug.memory_leak",
        "problem_id": None,
        "source_code": """#include <iostream>
int main() {
    int* a = new int[10];
    for (int i = 0; i < 10; ++i) a[i] = i;
    int sum = 0;
    for (int i = 0; i < 10; ++i) sum += a[i];
    std::cout << sum;
}""",
        "test_cases": [{"name": "sample", "input_data": "", "expected_output": "45"}],
    },
    {
        "id": "missing_return_01",
        "title": "Thiếu return trong hàm",
        "problem": "Viết hàm trả về tổng hai số",
        "expected_bug": "bug.missing_return",
        "problem_id": None,
        "source_code": """#include <iostream>
int add(int a, int b) {
    int c = a + b;
}
int main() {
    std::cout << add(3, 4);
}""",
        "test_cases": [{"name": "sample", "input_data": "", "expected_output": "7"}],
    },
    {
        "id": "array_oob_01",
        "title": "Truy cập mảng vượt biên",
        "problem": "In mảng 5 phần tử",
        "expected_bug": "bug.array_out_of_bounds",
        "problem_id": "ex_array_sum",
        "source_code": """#include <iostream>
int main() {
    int a[5] = {1, 2, 3, 4, 5};
    for (int i = 0; i <= 5; ++i) {
        std::cout << a[i] << " ";
    }
}""",
        "test_cases": [{"name": "sample", "input_data": "", "expected_output": "1 2 3 4 5"}],
    },
    {
        "id": "infinite_loop_01",
        "title": "Vòng lặp vô hạn do quên tăng biến",
        "problem": "In số từ 0 đến 4",
        "expected_bug": "bug.wrong_loop_condition",
        "problem_id": "ex_loop_prime",
        "source_code": """#include <iostream>
int main() {
    int i = 0;
    while (i < 5) {
        std::cout << i << " ";
    }
}""",
        "test_cases": [{"name": "sample", "input_data": "", "expected_output": "0 1 2 3 4"}],
    },
    {
        "id": "use_after_free_01",
        "title": "Use-after-free",
        "problem": "Cấp phát, giải phóng, và dùng lại",
        "expected_bug": "bug.use_after_free",
        "problem_id": "ex_ds_linked_list",
        "source_code": """#include <iostream>
int main() {
    int* p = new int(42);
    delete p;
    std::cout << *p;
}""",
        "test_cases": [],
    },
    {
        "id": "recursion_no_progress_01",
        "title": "Đệ quy không tiến về base case",
        "problem": "Tính giai thừa",
        "expected_bug": "bug.no_recursive_progress",
        "problem_id": "ex_rec_factorial",
        "source_code": """#include <iostream>
int factorial(int n) {
    return n * factorial(n - 1);
}
int main() {
    std::cout << factorial(5);
}""",
        "test_cases": [{"name": "sample", "input_data": "", "expected_output": "120"}],
    },
    {
        "id": "correct_sum_01",
        "title": "Bài đúng tính tổng",
        "problem": "Tính tổng n phần tử mảng",
        "expected_bug": None,
        "problem_id": "ex_array_sum",
        "source_code": """#include <iostream>
int main() {
    int n = 5;
    int a[5] = {1, 2, 3, 4, 5};
    int sum = 0;
    for (int i = 0; i < n; ++i) {
        sum += a[i];
    }
    std::cout << sum;
}""",
        "test_cases": [{"name": "sample", "input_data": "", "expected_output": "15"}],
    },
    {
        "id": "bubble_sort_oob_01",
        "title": "Bubble Sort sai biên",
        "problem": "Sắp xếp mảng tăng dần bằng bubble sort",
        "expected_bug": "bug.off_by_one",
        "acceptable_bugs": ["bug.off_by_one", "bug.array_out_of_bounds"],
        "problem_id": "ex_sort_bubble",
        # BUG: inner bound `j <= n - 1` makes a[j + 1] read/write a[n] (off-by-one -> OOB).
        "source_code": """#include <iostream>
int main() {
    int a[] = {5, 3, 1, 4, 2};
    int n = 5;
    for (int i = 0; i < n; ++i)
        for (int j = 0; j <= n - 1; ++j)
            if (a[j] > a[j + 1]) {
                int t = a[j];
                a[j] = a[j + 1];
                a[j + 1] = t;
            }
    for (int i = 0; i < n; ++i)
        std::cout << a[i] << " ";
}""",
        "test_cases": [{"name": "sample", "input_data": "", "expected_output": "1 2 3 4 5"}],
    },
    {
        "id": "binary_search_wrong_01",
        "title": "Tìm kiếm nhị phân sai điều kiện",
        "problem": "Tìm phần tử trong mảng đã sắp xếp",
        "expected_bug": "bug.wrong_loop_condition",
        "acceptable_bugs": ["bug.wrong_loop_condition", "bug.infinite_loop"],
        "problem_id": "ex_search_binary",
        # BUG: `right = mid` (should be mid - 1) with `left <= right` never shrinks the
        # interval when the target is absent -> infinite loop. Search x=6 (not present).
        "source_code": """#include <iostream>
int main() {
    int a[] = {1, 3, 5, 7, 9};
    int n = 5, x = 6, pos = -1;
    int left = 0, right = n;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (a[mid] == x) { pos = mid; break; }
        if (a[mid] < x) left = mid + 1;
        else right = mid;
    }
    std::cout << pos;
}""",
        "test_cases": [{"name": "sample", "input_data": "", "expected_output": "-1"}],
    },
    {
        "id": "factorial_rec_missing_return_01",
        "title": "Giai thừa đệ quy thiếu return",
        "problem": "Tính giai thừa bằng đệ quy",
        "expected_bug": "bug.missing_return",
        "problem_id": "ex_rec_factorial",
        "source_code": """#include <iostream>
int factorial(int n) {
    if (n <= 1) return 1;
    int result = n * factorial(n - 1);
}
int main() {
    std::cout << factorial(5);
}""",
        "test_cases": [{"name": "sample", "input_data": "", "expected_output": "120"}],
    },
]
