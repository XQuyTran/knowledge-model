# Hệ thống hỗ trợ giải bài tập lập trình có hướng dẫn từng bước

**Môn học:** Biểu diễn Tri Thức (BDTT)  
**Đề tài:** Project 1 — Hệ thống chẩn đoán lỗi logic và thuật toán trong mã nguồn sinh viên

---

## Kiến trúc tổng quan

```
                     ┌─────────────────────┐
                     │   Frontend (HTML/JS) │
                     │  /static/index.html  │
                     └──────────┬──────────┘
                                │ POST /diagnose
                     ┌──────────▼──────────┐
                     │    FastAPI Backend   │
                     │   api/main.py        │
                     └──────────┬──────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                  ▼
     ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
     │  Static     │   │  Semantic    │   │  Graph DB    │
     │  Analyzers  │   │  LLM Analysis│   │  (Neo4j)     │
     │  (Clang...) │   │  (GPT-4...)  │   │  Ontology    │
     └─────────────┘   └──────────────┘   └──────────────┘
```

### 4 tầng Ontology (Neo4j)

| Tầng | Mô tả | Thư mục |
|------|-------|---------|
| Concept Ontology | Kiến thức C/C++ (biến, mảng, vòng lặp...) | `concepts/` |
| Bug Ontology | Lỗi thường gặp, symptom, misconception | `bugs/` |
| Diagnostic Rules Ontology | Luật phát hiện lỗi từ evidence | `diagnostic/` |
| Explanation & Feedback Ontology | Sinh giải thích từng bước + hướng sửa | `explanation/` |

---

## Cách chạy

### Yêu cầu
- Docker & Docker Compose v2+
- Git

### 1. Clone & setup

```bash
git clone <repo-url> project
cd project

# Copy environment configs
cp .env.example .env
cp .env.llm.example .env.llm
# Sửa .env.llm với API key của bạn (nếu dùng LLM)
```

### 2. Chạy full stack (recommended)

```bash
# Khởi động Neo4j + App
docker compose up -d neo4j app

# Seed dữ liệu ontology vào Neo4j (chạy 1 lần)
docker compose --profile seed run neo4j-seed

# Kiểm tra
curl http://localhost:8000/health
```

### 3. Hoặc chạy local (không Docker, không LLM)

```bash
# Cài Python >= 3.11 + clang/clang-tidy
pip install -r requirements.txt

# Chạy backend
export USE_NEO4J=false
uvicorn diagnostic_pipeline.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Truy cập

Mở trình duyệt: [http://localhost:8000](http://localhost:8000)

---

## Cấu trúc thư mục

```
project/
├── concepts/           # Concept Ontology (C/C++ knowledge)
│   ├── neo4j_*_nodes.csv
│   ├── neo4j_*_relationships.csv
│   └── neo4j_*_seed.cypher
├── bugs/               # Bug Ontology
├── diagnostic/         # Diagnostic Rules Ontology
├── explanation/        # Explanation & Feedback Ontology
├── repairs/            # Repair Ontology
├── diagnostic_pipeline/ # Core engine
│   ├── api/            # FastAPI backend
│   │   └── main.py
│   ├── static/         # Frontend (HTML/CSS/JS)
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── app.js
│   ├── pipeline.py     # DiagnosticPipeline orchestrator
│   ├── clang_analyzers.py
│   ├── evidence_builder.py
│   ├── graph_repository.py
│   ├── ranking.py
│   ├── llm_client.py
│   └── llm_semantic.py
├── evaluation/         # So sánh Hybrid vs LLM-only
│   ├── benchmark_cases.py
│   ├── run_evaluation.py
│   └── results/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── .env.example
└── .env.llm.example
```

---

## Pipeline chẩn đoán

```
Student Code
    │
    ▼
┌─────────────────────────────────────┐
│  Static Analyzers                   │
│  ├─ ClangASTAnalyzer (AST dump)     │
│  ├─ ClangStaticAnalyzer (--analyze) │
│  ├─ ClangTidyAnalyzer               │
│  ├─ LocalSandboxRunner (chạy thử)   │
│  └─ SanitizerRunner (ASan/UBSan)    │
└──────────────┬──────────────────────┘
               │ EvidenceInstance[]
               ▼
┌─────────────────────────────────────┐
│  Evidence Builder                   │
│  ├─ Merge & dedup evidence          │
│  └─ Infer concepts from evidence    │
└──────────────┬──────────────────────┘
               │ evidence_ids + concept_ids
               ▼
┌─────────────────────────────────────┐
│  Graph Repository (Neo4j / Memory)  │
│  ├─ match_rules(evidence, concepts) │
│  ├─ select_explanation(bug_id)      │
│  └─ select_repair_plan(bug_id)      │
└──────────────┬──────────────────────┘
               │ RuleHit[]
               ▼
┌─────────────────────────────────────┐
│  Bug Ranking Engine                 │
│  (score = 0.5*rule + 0.42*evidence)│
└──────────────┬──────────────────────┘
               │ top BugCandidate
               ▼
┌─────────────────────────────────────┐
│  LLM Semantic Analysis (optional)   │
│  + Feedback Generation              │
└──────────────┬──────────────────────┘
               │ DiagnosticReport
               ▼
         Step-by-step Explanation + Repair Plan
```

---

## Chạy đánh giá (so sánh Hybrid vs LLM-only)

Yêu cầu đồ án: so sánh hiệu quả giữa hệ thống và giải pháp chỉ dùng LLM.

```bash
cd evaluation
python run_evaluation.py
```

Kết quả được ghi tại `evaluation/results/` gồm:
- `evaluation_report.md` — báo cáo Markdown
- `evaluation_results.json` — dữ liệu JSON chi tiết

---

## Cách đóng góp

Xem `project.md` để biết yêu cầu đầy đủ. Các việc cần làm:

- [x] Sửa lỗi import package name
- [x] Tạo pyproject.toml cho Docker build
- [x] Tạo .env.example và .env.llm.example
- [x] Xóa duplicate SanitizerRunner
- [x] Cải thiện Frontend UI
- [x] Tạo module đánh giá (Hybrid vs LLM-only)
- [ ] Mở rộng Bug Ontology với nhiều loại lỗi hơn
- [ ] Thêm bài tập mẫu cho testing
- [ ] Viết unit tests
- [ ] Cải thiện pipeline chẩn đoán
