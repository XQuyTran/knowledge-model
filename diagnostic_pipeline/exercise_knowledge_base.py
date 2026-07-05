from typing import Dict, List, Optional

from .models import ProblemKnowledge

EXERCISES: List[ProblemKnowledge] = [
    # ─── MẢNG (Arrays) ───
    ProblemKnowledge(
        problem_id="ex_array_sum",
        title="Tính tổng các phần tử mảng",
        description="Cho mảng số nguyên a gồm n phần tử. Hãy tính tổng tất cả các phần tử trong mảng.",
        category="Mảng",
        algorithm="Duyệt mảng tuần tự",
        data_structures=["Mảng một chiều"],
        difficulty="Dễ",
        common_bugs=["bug.off_by_one", "bug.array_out_of_bounds"],
        correct_code="""#include <iostream>
int main() {
    int n = 5;
    int a[5] = {1, 2, 3, 4, 5};
    int sum = 0;
    for (int i = 0; i < n; ++i)
        sum += a[i];
    std::cout << sum;
}""",
        expected_output="15",
        source="Sách Bài tập Lập trình C cơ bản - Chương 4: Mảng một chiều",
    ),
    ProblemKnowledge(
        problem_id="ex_array_max",
        title="Tìm phần tử lớn nhất trong mảng",
        description="Cho mảng số nguyên a gồm n phần tử. Hãy tìm giá trị lớn nhất.",
        category="Mảng",
        algorithm="Duyệt mảng tìm max",
        data_structures=["Mảng một chiều"],
        difficulty="Dễ",
        common_bugs=["bug.off_by_one", "bug.uninitialized_value"],
        correct_code="""#include <iostream>
int main() {
    int n = 5;
    int a[5] = {3, 1, 7, 2, 9};
    int max = a[0];
    for (int i = 1; i < n; ++i)
        if (a[i] > max) max = a[i];
    std::cout << max;
}""",
        expected_output="9",
        source="Sách Bài tập Lập trình C cơ bản - Chương 4: Mảng một chiều",
    ),
    ProblemKnowledge(
        problem_id="ex_array_reverse",
        title="Đảo ngược mảng",
        description="Cho mảng số nguyên a gồm n phần tử. Hãy đảo ngược thứ tự các phần tử.",
        category="Mảng",
        algorithm="Đảo ngược tại chỗ (two-pointer)",
        data_structures=["Mảng một chiều"],
        difficulty="Trung bình",
        common_bugs=["bug.off_by_one", "bug.array_out_of_bounds"],
        correct_code="""#include <iostream>
int main() {
    int a[] = {1, 2, 3, 4, 5};
    int n = 5;
    for (int i = 0; i < n / 2; ++i) {
        int t = a[i];
        a[i] = a[n - 1 - i];
        a[n - 1 - i] = t;
    }
    for (int i = 0; i < n; ++i)
        std::cout << a[i] << " ";
}""",
        expected_output="5 4 3 2 1",
        source="Sách Bài tập Lập trình C cơ bản - Chương 4: Mảng một chiều",
    ),

    # ─── VÒNG LẶP (Loops) ───
    ProblemKnowledge(
        problem_id="ex_loop_factorial",
        title="Tính giai thừa bằng vòng lặp",
        description="Nhập số nguyên n (n >= 0). Tính n! = 1 * 2 * ... * n. Quy ước 0! = 1.",
        category="Vòng lặp",
        algorithm="Vòng lặp tích lũy",
        data_structures=["Biến cơ bản"],
        difficulty="Dễ",
        common_bugs=["bug.off_by_one", "bug.wrong_loop_condition"],
        correct_code="""#include <iostream>
int main() {
    int n = 5;
    unsigned long long fact = 1;
    for (int i = 2; i <= n; ++i)
        fact *= i;
    std::cout << fact;
}""",
        expected_output="120",
        source="Sách Bài tập Lập trình C cơ bản - Chương 3: Cấu trúc lặp",
    ),
    ProblemKnowledge(
        problem_id="ex_loop_prime",
        title="Kiểm tra số nguyên tố",
        description="Nhập số nguyên dương n. Kiểm tra xem n có phải số nguyên tố không.",
        category="Vòng lặp",
        algorithm="Vòng lặp kiểm tra ước số",
        data_structures=["Biến cơ bản"],
        difficulty="Trung bình",
        common_bugs=["bug.wrong_loop_condition", "bug.off_by_one"],
        correct_code="""#include <iostream>
int main() {
    int n = 7;
    if (n < 2) { std::cout << "No"; return 0; }
    for (int i = 2; i * i <= n; ++i)
        if (n % i == 0) { std::cout << "No"; return 0; }
    std::cout << "Yes";
}""",
        expected_output="Yes",
        source="Sách Bài tập Lập trình C cơ bản - Chương 3: Cấu trúc lặp",
    ),
    ProblemKnowledge(
        problem_id="ex_loop_fibonacci",
        title="Dãy Fibonacci",
        description="In n số đầu tiên của dãy Fibonacci: F0 = 0, F1 = 1, Fn = Fn-1 + Fn-2.",
        category="Vòng lặp",
        algorithm="Vòng lặp với bộ nhớ đệm hai biến",
        data_structures=["Biến cơ bản"],
        difficulty="Trung bình",
        common_bugs=["bug.off_by_one", "bug.uninitialized_value"],
        correct_code="""#include <iostream>
int main() {
    int n = 7;
    unsigned long long f0 = 0, f1 = 1;
    for (int i = 0; i < n; ++i) {
        std::cout << f0 << " ";
        unsigned long long f2 = f0 + f1;
        f0 = f1; f1 = f2;
    }
}""",
        expected_output="0 1 1 2 3 5 8",
        source="Sách Bài tập Lập trình C cơ bản - Chương 3: Cấu trúc lặp",
    ),

    # ─── ĐỆ QUY (Recursion) ───
    ProblemKnowledge(
        problem_id="ex_rec_factorial",
        title="Tính giai thừa bằng đệ quy",
        description="Viết hàm đệ quy tính n!. n! = n * (n-1)!, với 0! = 1.",
        category="Đệ quy",
        algorithm="Đệ quy tuyến tính",
        data_structures=["Stack (ngầm định)"],
        difficulty="Trung bình",
        common_bugs=["bug.no_recursive_progress", "bug.missing_return"],
        correct_code="""#include <iostream>
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
int main() {
    std::cout << factorial(5);
}""",
        expected_output="120",
        source="Sách Bài tập Lập trình C cơ bản - Chương 6: Hàm và đệ quy",
    ),
    ProblemKnowledge(
        problem_id="ex_rec_fibonacci",
        title="Fibonacci bằng đệ quy",
        description="Viết hàm đệ quy tính số Fibonacci thứ n: F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2).",
        category="Đệ quy",
        algorithm="Đệ quy nhị phân",
        data_structures=["Stack (ngầm định)"],
        difficulty="Trung bình",
        common_bugs=["bug.no_recursive_progress", "bug.missing_return", "bug.off_by_one"],
        correct_code="""#include <iostream>
int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}
int main() {
    std::cout << fib(7);
}""",
        expected_output="13",
        source="Sách Bài tập Lập trình C cơ bản - Chương 6: Hàm và đệ quy",
    ),
    ProblemKnowledge(
        problem_id="ex_rec_hanoi",
        title="Tháp Hà Nội",
        description="In các bước di chuyển n đĩa từ cột A sang cột C dùng cột B làm trung gian.",
        category="Đệ quy",
        algorithm="Đệ quy chia để trị",
        data_structures=["Stack (ngầm định)"],
        difficulty="Khó",
        common_bugs=["bug.no_recursive_progress", "bug.wrong_loop_condition"],
        correct_code="""#include <iostream>
void hanoi(int n, char from, char to, char aux) {
    if (n == 1) {
        std::cout << from << "->" << to << "\\n";
        return;
    }
    hanoi(n - 1, from, aux, to);
    std::cout << from << "->" << to << "\\n";
    hanoi(n - 1, aux, to, from);
}
int main() {
    hanoi(3, 'A', 'C', 'B');
}""",
        expected_output="A->C\nA->B\nC->B\nA->C\nB->A\nB->C\nA->C",
        source="Sách Bài tập Lập trình C cơ bản - Chương 6: Hàm và đệ quy",
    ),

    # ─── CẤU TRÚC DỮ LIỆU (Data Structures) ───
    ProblemKnowledge(
        problem_id="ex_ds_linked_list",
        title="Danh sách liên kết đơn",
        description="Cài đặt danh sách liên kết đơn với các thao tác: thêm đầu, xóa đầu, duyệt danh sách.",
        category="Cấu trúc dữ liệu",
        algorithm="Thao tác danh sách liên kết",
        data_structures=["Danh sách liên kết đơn", "Con trỏ"],
        difficulty="Khó",
        common_bugs=["bug.null_dereference", "bug.memory_leak", "bug.dangling_pointer"],
        correct_code="""#include <iostream>
struct Node { int data; Node* next; };
void push(Node*& head, int val) {
    Node* n = new Node{val, head};
    head = n;
}
void print(Node* head) {
    while (head) {
        std::cout << head->data << " ";
        head = head->next;
    }
}
int main() {
    Node* head = nullptr;
    push(head, 3); push(head, 2); push(head, 1);
    print(head);
}""",
        expected_output="1 2 3",
        source="Sách Bài tập Lập trình C cơ bản - Chương 8: Cấu trúc dữ liệu động",
    ),
    ProblemKnowledge(
        problem_id="ex_ds_stack_array",
        title="Ngăn xếp dùng mảng",
        description="Cài đặt ngăn xếp (stack) sử dụng mảng với các thao tác push, pop, isEmpty.",
        category="Cấu trúc dữ liệu",
        algorithm="Ngăn xếp (LIFO)",
        data_structures=["Mảng một chiều"],
        difficulty="Trung bình",
        common_bugs=["bug.array_out_of_bounds", "bug.off_by_one"],
        correct_code="""#include <iostream>
struct Stack {
    int data[100];
    int top = -1;
    void push(int v) { if (top < 99) data[++top] = v; }
    int pop() { return data[top--]; }
    bool empty() { return top == -1; }
};
int main() {
    Stack s;
    s.push(1); s.push(2); s.push(3);
    while (!s.empty()) std::cout << s.pop() << " ";
}""",
        expected_output="3 2 1",
        source="Sách Bài tập Lập trình C cơ bản - Chương 8: Cấu trúc dữ liệu động",
    ),

    # ─── SẮP XẾP (Sorting) ───
    ProblemKnowledge(
        problem_id="ex_sort_bubble",
        title="Sắp xếp nổi bọt (Bubble Sort)",
        description="Cho mảng số nguyên a gồm n phần tử. Sắp xếp mảng tăng dần bằng thuật toán nổi bọt.",
        category="Sắp xếp",
        algorithm="Bubble Sort",
        data_structures=["Mảng một chiều"],
        difficulty="Dễ",
        common_bugs=["bug.off_by_one", "bug.array_out_of_bounds", "bug.wrong_loop_condition"],
        correct_code="""#include <iostream>
int main() {
    int a[] = {5, 3, 1, 4, 2};
    int n = 5;
    for (int i = 0; i < n - 1; ++i)
        for (int j = 0; j < n - 1 - i; ++j)
            if (a[j] > a[j + 1]) {
                int t = a[j];
                a[j] = a[j + 1];
                a[j + 1] = t;
            }
    for (int i = 0; i < n; ++i)
        std::cout << a[i] << " ";
}""",
        expected_output="1 2 3 4 5",
        source="Sách Bài tập Lập trình C cơ bản - Chương 7: Sắp xếp và tìm kiếm",
    ),
    ProblemKnowledge(
        problem_id="ex_sort_selection",
        title="Sắp xếp chọn (Selection Sort)",
        description="Cho mảng số nguyên a gồm n phần tử. Sắp xếp tăng dần bằng thuật toán chọn trực tiếp.",
        category="Sắp xếp",
        algorithm="Selection Sort",
        data_structures=["Mảng một chiều"],
        difficulty="Dễ",
        common_bugs=["bug.off_by_one", "bug.array_out_of_bounds"],
        correct_code="""#include <iostream>
int main() {
    int a[] = {5, 3, 1, 4, 2};
    int n = 5;
    for (int i = 0; i < n - 1; ++i) {
        int min = i;
        for (int j = i + 1; j < n; ++j)
            if (a[j] < a[min]) min = j;
        int t = a[i]; a[i] = a[min]; a[min] = t;
    }
    for (int i = 0; i < n; ++i)
        std::cout << a[i] << " ";
}""",
        expected_output="1 2 3 4 5",
        source="Sách Bài tập Lập trình C cơ bản - Chương 7: Sắp xếp và tìm kiếm",
    ),
    ProblemKnowledge(
        problem_id="ex_sort_insertion",
        title="Sắp xếp chèn (Insertion Sort)",
        description="Cho mảng số nguyên a gồm n phần tử. Sắp xếp tăng dần bằng thuật toán chèn trực tiếp.",
        category="Sắp xếp",
        algorithm="Insertion Sort",
        data_structures=["Mảng một chiều"],
        difficulty="Trung bình",
        common_bugs=["bug.array_out_of_bounds", "bug.off_by_one"],
        correct_code="""#include <iostream>
int main() {
    int a[] = {5, 3, 1, 4, 2};
    int n = 5;
    for (int i = 1; i < n; ++i) {
        int key = a[i];
        int j = i - 1;
        while (j >= 0 && a[j] > key) {
            a[j + 1] = a[j];
            --j;
        }
        a[j + 1] = key;
    }
    for (int i = 0; i < n; ++i)
        std::cout << a[i] << " ";
}""",
        expected_output="1 2 3 4 5",
        source="Sách Bài tập Lập trình C cơ bản - Chương 7: Sắp xếp và tìm kiếm",
    ),

    # ─── TÌM KIẾM (Searching) ───
    ProblemKnowledge(
        problem_id="ex_search_linear",
        title="Tìm kiếm tuyến tính",
        description="Cho mảng số nguyên a gồm n phần tử và số x. Tìm vị trí đầu tiên của x trong mảng.",
        category="Tìm kiếm",
        algorithm="Tìm kiếm tuyến tính",
        data_structures=["Mảng một chiều"],
        difficulty="Dễ",
        common_bugs=["bug.off_by_one", "bug.wrong_loop_condition"],
        correct_code="""#include <iostream>
int main() {
    int a[] = {4, 2, 7, 1, 9};
    int n = 5, x = 7;
    int pos = -1;
    for (int i = 0; i < n; ++i)
        if (a[i] == x) { pos = i; break; }
    std::cout << pos;
}""",
        expected_output="2",
        source="Sách Bài tập Lập trình C cơ bản - Chương 7: Sắp xếp và tìm kiếm",
    ),
    ProblemKnowledge(
        problem_id="ex_search_binary",
        title="Tìm kiếm nhị phân",
        description="Cho mảng số nguyên a đã sắp xếp tăng dần gồm n phần tử và số x. Tìm vị trí của x bằng tìm kiếm nhị phân.",
        category="Tìm kiếm",
        algorithm="Tìm kiếm nhị phân",
        data_structures=["Mảng một chiều"],
        difficulty="Trung bình",
        common_bugs=["bug.off_by_one", "bug.wrong_loop_condition", "bug.infinite_loop"],
        correct_code="""#include <iostream>
int main() {
    int a[] = {1, 3, 5, 7, 9};
    int n = 5, x = 7;
    int left = 0, right = n - 1, pos = -1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (a[mid] == x) { pos = mid; break; }
        if (a[mid] < x) left = mid + 1;
        else right = mid - 1;
    }
    std::cout << pos;
}""",
        expected_output="3",
        source="Sách Bài tập Lập trình C cơ bản - Chương 7: Sắp xếp và tìm kiếm",
    ),
]

PROBLEM_ALGORITHM_MAP: Dict[str, str] = {}
PROBLEM_DATASTRUCTURE_MAP: Dict[str, List[str]] = {}
PROBLEM_BUG_MAP: Dict[str, List[str]] = {}
PROBLEM_BY_ID: Dict[str, ProblemKnowledge] = {}

for ex in EXERCISES:
    PROBLEM_BY_ID[ex.problem_id] = ex
    PROBLEM_ALGORITHM_MAP[ex.problem_id] = ex.algorithm_key
    PROBLEM_DATASTRUCTURE_MAP[ex.problem_id] = ex.data_structures[:]
    PROBLEM_BUG_MAP[ex.problem_id] = ex.common_bugs[:]


def find_matching_problems(statement: str, top_n: int = 3) -> List[ProblemKnowledge]:
    scored = [(ex, ex.matches_statement(statement)) for ex in EXERCISES]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [ex for ex, s in scored if s > 0][:top_n]


def get_problem_by_id(problem_id: str) -> Optional[ProblemKnowledge]:
    return PROBLEM_BY_ID.get(problem_id)
