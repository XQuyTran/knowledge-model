from diagnostic_pipeline import DiagnosticPipeline, DiagnosticRequest, TestCase


SOURCE_CODE = """
#include <iostream>
int main() {
    int n = 5;
    int a[5] = {1, 2, 3, 4, 5};
    int sum = 0;
    for (int i = 0; i <= n; ++i) {
        sum += a[i];
    }
    std::cout << sum;
}
""".strip()


if __name__ == '__main__':
    request = DiagnosticRequest(
        problem_statement='Compute the sum of n array elements.',
        source_code=SOURCE_CODE,
        test_cases=[TestCase(name='sample', expected_output='15')],
    )

    pipeline = DiagnosticPipeline()
    report = pipeline.diagnose(request)
    print(report.natural_language_feedback)
