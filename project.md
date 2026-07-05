1 – HỆ THỐNG HỖ TRỢ HỌC TẬP
Project 1 (1 nhóm). Hệ thống hỗ trợ giải bài tập lập trình có hướng dẫn từng bước
+ Mục tiêu: Phát triển hệ thống chẩn đoán lỗi logic và thuật toán trong mã nguồn sinh viên, sau
đó tạo ra lời giải từng bước có giải thích ngữ cảnh (Context-Aware Explanations) dựa trên mô hình
tri thức lỗi.
+ Thu thập tri thức:
• Các sách về bài tập lập trình cơ bản (C/C++).
• Phân loại bài tập theo chủ đề: mảng, vòng lặp, đệ quy, cấu trúc dữ liệu, thuật toán sắp
xếp...
• Tập luật chẩn đoán lỗi (Diagnostic Rules) và mô hình hóa lỗi thường gặp (e.g., lỗi vòng
lặp vô hạn, điều kiện biên sai, quản lý bộ nhớ).
+ Mô hình biểu diễn tri thức:
• Mô hình hóa mối quan hệ giữa:
Bài toán  Thuật toán  Cấu trúc Dữ liệu  Lỗi thường gặp  Hướng khắc phục.
• Cấu trúc tri thức: Code → Pattern Matching → Rule_Triggered → Step_Explanation.
+ Bài toán và các Thuật giải tương ứng:
• Đề xuất các vấn đề cần vấn đề trong hệ thống và phương pháp giải tương ứng.
• Kỹ thuật chính: Kết hợp LLMs (ví dụ: Code Llama/GPT-4) để phân tích ngữ nghĩa mã
nguồn và mô tả sai sót bằng ngôn ngữ tự nhiên.
• Suy luận: Triển khai hệ thống suy luận dựa trên luật (Rule-Based Reasoning) để chẩn
đoán lỗi chính xác và xác định bước hướng dẫn kế tiếp
Yêu cầu sản phẩm
• Giao diện nhập bài và hiển thị lời giải từng bước.
• CSDL tri thức bài tập.
• Mô hình biểu diễn lỗi và cách sửa.
• So sánh hiệu quả giữa hệ thống xây dựng và giải pháp chỉ sử dụng LLM
