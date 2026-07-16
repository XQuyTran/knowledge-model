from neo4j import GraphDatabase

from diagnostic_pipeline import DiagnosticPipeline, DiagnosticRequest, TestCase
from diagnostic_pipeline.graph_repository import Neo4jGraphRepository
from diagnostic_pipeline.llm_client import build_llm_client_from_env


def main() -> None:
    driver = GraphDatabase.driver(
        'neo4j://localhost:7687',
        auth=('neo4j', 'password'),
    )
    try:
        graph_repository = Neo4jGraphRepository(driver=driver, database='neo4j')
        # Configure via env: OPENAI_API_KEY/OPENAI_BASE_URL (or LLM_API_KEY/LLM_API_BASE_URL)
        # plus OPENAI_MODEL/LLM_MODEL, or the AZURE_OPENAI_* variables.
        llm_client = build_llm_client_from_env()
        pipeline = DiagnosticPipeline(graph_repository=graph_repository, llm_client=llm_client)

        source_code = """
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

        request = DiagnosticRequest(
            problem_statement='Compute the sum of n array elements.',
            source_code=source_code,
            test_cases=[TestCase(name='sample', expected_output='15')],
        )

        report = pipeline.diagnose(request)
        print(report.natural_language_feedback)
    finally:
        driver.close()


if __name__ == '__main__':
    main()
