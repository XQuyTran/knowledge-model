# Hệ thống hỗ trợ giải bài tập lập trình có hướng dẫn

## Tổng quan

Hệ thống chẩn đoán lỗi logic và thuật toán trong mã nguồn C/C++ sinh viên, sau đó tạo ra lời giải từng bước có giải thích ngữ cảnh (Context-Aware Explanations) dựa trên mô hình tri thức lỗi.

Hệ thống bao gồm bốn lớp ontology tích hợp:

1. Concept Ontology
2. Bug Ontology
3. Diagnostic Rules Ontology
4. Explanation and Feedback Ontology

Các lớp này được liên kết thông qua các định danh thống nhất như:

- concept.*
- bug.*
- rule.*
- fix.*
- mis.*
- view.*

Kiến trúc cho phép phát hiện bug tự động, suy luận và sinh phản hồi hướng dẫn học.

---

## 1. Concept Ontology

Tập tin:
- neo4j_latest_concepts_nodes.csv
- neo4j_latest_concepts_relationships.csv
- neo4j_latest_concepts_seed.cypher

Mục đích:
- Biểu diễn kiến thức lập trình C (C23) và C++ (C++23)

Các loại node chính:
- ProgrammingConcept
- ConceptCategory
- LibraryModule
- PedagogicalView
- KnowledgePoint

Các quan hệ chính:
- BELONGS_TO
- PREREQUISITE_OF
- IMPLEMENTED_IN
- MODULE_OF
- VISIBLE_IN

Vai trò:
- Lớp nền tảng cho toàn bộ hệ thống

---

## 2. Bug Ontology

Tập tin:
- neo4j_bug_ontology_nodes.csv
- neo4j_bug_ontology_relationships.csv
- neo4j_bug_ontology_seed.cypher

Mục đích:
- Mô tả lỗi lập trình dưới dạng có cấu trúc

Các loại node chính:
- ProgrammingBug
- BugCategory
- Symptom
- Effect
- Misconception
- FixStrategy

Các quan hệ chính:
- BELONGS_TO_CATEGORY
- HAS_SYMPTOM
- HAS_EFFECT
- CAUSED_BY_MISCONCEPTION
- FIXED_BY
- OCCURS_IN_CONCEPT
- VISIBLE_IN

Vai trò:
- Liên kết giữa code lỗi và tri thức

---

## 3. Diagnostic Rules Ontology

Tập tin:
- neo4j_diagnostic_rules_nodes.csv
- neo4j_diagnostic_rules_relationships.csv
- neo4j_diagnostic_rules_seed.cypher
- build_neo4j_diagnostic_rules_dataset.py

Mục đích:
- Xây dựng các luật phát hiện lỗi

Các loại node chính:
- DiagnosticRule
- RuleCategory
- EvidencePattern
- ToolSignature

Các quan hệ chính:
- DETECTS_BUG
- APPLIES_TO_CONCEPT
- USES_EVIDENCE
- SUPPORTED_BY_TOOL
- RECOMMENDS_FIX
- VISIBLE_IN

Vai trò:
- Lớp suy luận phát hiện lỗi

---

## 4. Explanation and Feedback Ontology

Tập tin:
- neo4j_explanation_feedback_nodes.csv
- neo4j_explanation_feedback_relationships.csv
- neo4j_explanation_feedback_seed.cypher
- build_neo4j_explanation_feedback_dataset.py

Mục đích:
- Sinh lời giải thích và phản hồi học tập có cấu trúc

Các loại node chính:
- ExplanationTemplate
- ExplanationStep
- ExplanationCategory
- FeedbackPattern
- ContextAnchorType
- RemediationPlan

Các quan hệ chính:
- EXPLAINS_BUG
- TRIGGERED_BY_RULE
- TARGETS_MISCONCEPTION
- SUGGESTS_FIX
- REINFORCES_CONCEPT
- USES_FEEDBACK_PATTERN
- USES_CONTEXT_ANCHOR
- CONSISTS_OF_STEP
- RECOMMENDS_PLAN
- RECOMMENDS_CONCEPT

Vai trò:
- Lớp sinh phản hồi
---

## Liên kết giữa các lớp

Pipeline suy luận tổng thể:

Concept -> Bug -> Diagnostic Rule -> Explanation -> Feedback -> Remediation Plan
---

## Thứ tự import vào Neo4j

Thực hiện theo thứ tự:

1. Concept Ontology
2. Bug Ontology
3. Diagnostic Rules Ontology
4. Explanation and Feedback Ontology

Lý do:
- Các lớp sau phụ thuộc vào id của lớp trước
---

## Tái tạo tập dữ liệu

Chạy các lệnh:

python build_neo4j_diagnostic_rules_dataset.py
python build_neo4j_explanation_feedback_dataset.py

---

## Khả năng của hệ thống

Hệ tri thức hỗ trợ:

- Phát hiện lỗi tự động
- Sinh phản hồi có cấu trúc
- Giải thích theo ngữ cảnh khái niệm
- Liên kết misconception với hướng sửa
- Gợi ý lộ trình học tập
