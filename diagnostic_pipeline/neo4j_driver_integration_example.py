from neo4j import GraphDatabase

from diagnostic_pipeline import DiagnosticPipeline, DiagnosticRequest, TestCase
from diagnostic_pipeline.graph_repository import Neo4jGraphRepository
from diagnostic_pipeline.llm_client import OpenAICompatibleLLMClient


def main() -> None:
    driver = GraphDatabase.driver(
        'neo4j://localhost:7687',
        auth=('neo4j', 'password'),
    )
    try:
        graph_repository = Neo4jGraphRepository(driver=driver, database='neo4j')
        llm_client = OpenAICompatibleLLMClient(
            api_base_url='https://api.openai.com/v1',
            api_key='YOUR_API_KEY',
            model='gpt-4.1-mini',
        )
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
