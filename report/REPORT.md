# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| | | |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`:
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker:
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): Dự đoán `subagents` đạt số check đánh giá bằng hoặc thấp hơn `baseline`, nhưng dùng nhiều token hơn. Trên tác vụ học, hai điều kiện cùng đạt 17/27 check trong khi `subagents` dùng 397316 so với 218064 token (+82,2%); các lỗi chủ yếu là 9 check quy ước (nhóm E) mà việc chia việc không tự bổ sung được. [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) cũng ghi nhận đa tác tử tốn token và thường kém phù hợp khi tác vụ lập trình có ít nhánh độc lập.
- H2 (skills-auto so với baseline): Dự đoán `skills-auto` đạt điểm **cao nhất trên tác vụ đánh giá**, hơn `baseline` khoảng 1–2 check, vì 9/10 lỗi baseline là quy ước và ba skill đã được đọc, giúp tăng điểm tác vụ học từ 17/27 lên 23/27. Đây là dự đoán thận trọng: [SkillsBench](https://arxiv.org/html/2602.12670v4) thấy skill tự sinh có thể kém hơn không dùng skill trong các cấu hình họ thử, nên mức tăng ở đây chưa chứng minh khả năng chuyển giao.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán tỉ lệ check đạt của `skills-auto` trên tác vụ đánh giá thấp hơn 23/27 (85,2%) ở tác vụ học và mức cải thiện so với `baseline` nhỏ hơn 6/27 (22,2 điểm phần trăm). Skill được curator rút từ phản hồi của đúng ba tác vụ học; quy ước mới có thể chưa được mô tả đủ, như `meta` và schema log còn bị bỏ sót. [SkillEvolBench](https://arxiv.org/abs/2605.24117) cũng ghi nhận lợi ích từ skill tự sinh ở giai đoạn học thường không ổn định khi triển khai trên tác vụ đã đóng băng.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có công cụ tập tin: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; shell: `execute`; và subagent: `task`. `execute` cho phép chạy lệnh shell.
2. `task` khởi chạy một subagent tạm thời để xử lý tác vụ phức tạp, nhiều bước; `general-purpose` dùng cho nghiên cứu, tìm kiếm tập tin/nội dung và thực hiện công việc nhiều bước. Mặc định subagent chỉ thấy prompt được giao (không kế thừa ngữ cảnh hội thoại), rồi trả về một báo cáo cuối.
3. System prompt mặc định rỗng (`''`). Từ `task`: “Launch multiple agents concurrently when their tasks are independent, using a single message with multiple tool calls.” Từ `execute`: “You MUST avoid using search commands like find and grep.”

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Chỉ xét ba lần chạy `baseline` của tác vụ học: `code-learn` đạt 6/10, `data-learn` 5/8, `logs-learn` 6/9. Mỗi dòng dưới đây là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng từ `detail` hoặc vết |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | G — lỗi môi trường/checker | `detail`: tệp test gốc không được sửa; vết không có lệnh sửa `tests/test_report.py`. Hash SHA-256 của bản checkout CRLF là `efb5e765…`, còn checker chờ `79e05f4c…`; chuẩn hóa CRLF thành LF cho đúng hash checker. Không quy lỗi này cho tác tử. |
| `code-learn` | `rule_type_hints` | E | `detail`: mọi hàm public phải chú thích kiểu cho tham số và giá trị trả về; vết sửa `inventory/*.py` nhưng không thêm type hints. |
| `code-learn` | `rule_regression_tests` | E | `detail`: cần `tests/test_regressions.py` với ít nhất 3 test; vết chỉ chạy 6 test có sẵn, không tạo tệp này. |
| `code-learn` | `rule_changelog` | E | `detail`: cần ít nhất 3 dòng `- fix(<function name>): ...` trong `CHANGELOG.md` dưới `## Unreleased`; vết không ghi changelog. |
| `data-learn` | `rule_money_in_cents` | E | `detail`: giá trị tiền trong `answer.json` phải là số nguyên cents; vết ghi `north_q1_revenue: 3130.24` dạng USD. |
| `data-learn` | `rule_meta_block` | E | `detail`: cần `meta` gồm `source`, `rows_in`, `rows_used`; vết ghi `answer.json` chỉ có 5 khóa kết quả, thiếu `meta`. |
| `data-learn` | `rule_clean_csv` | E | `detail`: cần `workspace/clean.csv` với dòng duy nhất theo đơn hàng, UTC, vùng chuẩn hóa, số cents; vết chỉ tạo `answer.json`. |
| `logs-learn` | `rule_service_names` | E | `detail`: tên service viết thường, thay `-` bằng `_`; vết vẫn dùng `inventory-service`, `auth-service`, `payment-service`. |
| `logs-learn` | `rule_sorted_errors` | E | `detail`: `errors` phải sắp theo service rồi `timestamp_utc` tăng dần; vết giữ thứ tự thời gian ban đầu (mục đầu là `inventory-service`, tiếp theo có `auth-service`). |
| `logs-learn` | `rule_schema_header` | E | `detail`: cần `schema_version: 2` và `generated_by: "log-triage"` ở cấp cao nhất; vết không thêm hai khóa này. |

Nhận xét: 9/10 check thất bại thuộc nhóm E (quy ước tổ chức không nêu trong đề); một check nhóm G do khác biệt xuống dòng của bản checkout Windows. Check kỹ thuật đạt 17/18, trong đó thất bại duy nhất là `tests_not_modified` nói trên; không có bằng chứng check thất bại thuộc A–D hoặc F. Skill mô tả các quy ước có thể giúp nhóm E nếu tác tử đọc và làm theo, nhưng cần kiểm chứng ở Phần 3–4.

## 5. Điều kiện `subagents` (Phần 2.3)

- Đã định nghĩa ba subagent trong `src/lab/subagents.py`: `explorer` đọc và báo cáo sự thật, `implementer` sửa và kiểm tra kết quả, `reviewer` rà độc lập trường hợp biên. Cách chia này nhằm tách khảo sát, thực hiện và kiểm tra.
- `subagent_calls`: `code-learn` gọi `implementer` rồi `reviewer` (2 lần); `data-learn` gọi `explorer` (1 lần); `logs-learn` gọi `implementer` (1 lần). Không có tác vụ nào bằng 0. `trace.md` chỉ cho thấy lời giao việc và báo cáo, không cho thấy thao tác bên trong subagent.
- Nội dung giao việc: `code-learn` nhắc docstring, không sửa test và chạy test, nhưng câu “make source changes only” hạn chế việc tạo test hồi quy/changelog; sau báo cáo của `reviewer`, tác tử chính đã sửa thêm `pricing.py`, `export.py` và chạy lại 6 test. `data-learn` giao tìm quy ước; `explorer` báo README không có schema `answer.json`; tác tử chính đọc lại README/CSV rồi vẫn thiếu `meta` và `clean.csv`. `logs-learn` giao các quy tắc hiện trong đề; tác tử chính đọc lại README và `errors.json`, kiểm tra JSON/counts, nhưng không bổ sung ba quy ước `rule_`.

| Tác vụ | Baseline: token / giây | Subagents: token / giây | Chênh token | Điểm hai điều kiện |
|---|---:|---:|---:|---:|
| `code-learn` | 109369 / 66,4 | 190086 / 207,8 | +80717 | 6/10 |
| `data-learn` | 33196 / 28,0 | 50720 / 62,1 | +17524 | 5/8 |
| `logs-learn` | 75499 / 45,2 | 156510 / 125,3 | +81011 | 6/9 |
| **Tổng** | **218064 / 139,6** | **397316 / 395,2** | **+179252 (+82,2%)** | **17/27 ở cả hai** |

Trong ba tác vụ này, `subagents` tăng token và thời gian nhưng không tăng số check đạt.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Lần chạy curator được cung cấp: 1; sinh 3 skill, không xóa skill nào và không chạy lại.

| Skill | Tổng quát và tính đúng | Độ dài, `description`, việc đọc và làm theo ở Phần 3.4 |
|---|---|---|
| `safe-python-maintenance` | Quy trình sửa gói Python, không lặp đáp án của `code-learn`. Khớp ba phản hồi `rule_type_hints`, `rule_regression_tests`, `rule_changelog`; không thấy chỉ dẫn sai. | 10 dòng (6 dòng thân); `description` nêu tình huống sửa gói Python. `skills_read = 1`; vết tạo type hints, 4 regression tests và 4 dòng changelog, sau đó chạy 10 test đạt. Điểm 6/10 → 9/10. `tests_not_modified` vẫn trượt do tệp test gốc ở checkout Windows có CRLF, không phải vì tác tử sửa test. |
| `reliable-tabular-data` | Checklist làm sạch bảng và tạo JSON, không lặp dữ liệu riêng của `data-learn`. Quy tắc cents, khử trùng lặp, UTC và metadata phù hợp phản hồi; cần đối chiếu đơn vị với yêu cầu của tác vụ mới. | 13 dòng (9 dòng thân); `description` nêu đúng tình huống bảng dữ liệu. `skills_read = 1`; vết dùng `Decimal`, xuất `north_q1_revenue` bằng 313024 cents nên `rule_money_in_cents` đạt. Tuy nhiên tác tử ghi khóa `metadata` thay vì `meta`, không tạo `clean.csv`; còn trượt `rule_meta_block`, `rule_clean_csv`. Điểm 5/8 → 6/8. |
| `normalized-log-triage` | Quy trình chuẩn hóa log, không lặp dữ liệu riêng của `logs-learn`. Đúng với quy tắc tên service và sắp thứ tự; chỉ dẫn schema còn thiếu khóa/giá trị chính xác của phản hồi. | 8 dòng (4 dòng thân); `description` nêu lúc tạo JSON từ service logs. `skills_read = 1`; vết dùng `auth_service`, `inventory_service`, `payment_service` và sắp xếp, nên hai check tương ứng đạt. Tác tử ghi `schema_version: "1.0"`, `generator: "acme-log-triage"` thay vì `schema_version: 2`, `generated_by: "log-triage"`; `rule_schema_header` trượt. Điểm 6/9 → 8/9. |


## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
