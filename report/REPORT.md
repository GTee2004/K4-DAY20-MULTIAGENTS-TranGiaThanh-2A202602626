# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Trần Gia Thành | 2A202602626 | Tất cả |

- Mô hình: `LAB_MODEL=openai:gpt-6-luna`; `LAB_TEMPERATURE=0`; `recursion_limit=60` (mặc định của runner).
- Deep Agents `0.7.21`; Windows, chạy trực tiếp trong môi trường ảo Python/PowerShell, không dùng Docker.
- Số lần chạy tác vụ đã dùng / ngân sách: 21 / $0,16.
- Commit của tag `freeze`: `8bfe7cee8181ecd5cee1b2c5c94ad7b4665d472b`.

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

Bảng từ `report/table.md` (điểm trung bình là trung bình tỉ lệ đạt của từng tác vụ):

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 6/10 | 9/10 |
| data-learn | 5/8 | 5/8 | 6/8 |
| logs-learn | 6/9 | 6/9 | 8/9 |
| code-eval | 6/11 | 6/11 | 9/11 |
| data-eval | 5/9 | 5/9 | 5/9 |
| logs-eval | 6/10 | 3/10 | 8/10 |
| **Mean score - learning tasks** | 0.63 | 0.63 | 0.85 |
| **Mean score - evaluation tasks** | 0.57 | 0.47 | 0.72 |
| **Mean tokens per run** | 67,571 | 116,022 | 95,357 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |

Kết quả `python scripts/check_breakdown.py`:

| Điều kiện | Vai trò | Check kỹ thuật | Check quy ước | Token trung bình | Có đọc skill |
|---|---|---:|---:|---:|---:|
| baseline | eval | 17/18 | 0/12 | 62,454 | 0/3 |
| baseline | learn | 17/18 | 0/9 | 72,688 | 0/3 |
| subagents | eval | 14/18 | 0/12 | 99,606 | 0/3 |
| subagents | learn | 17/18 | 0/9 | 132,438 | 0/3 |
| skills-auto | eval | 17/18 | 5/12 | 92,473 | 3/3 |
| skills-auto | learn | 17/18 | 6/9 | 98,241 | 3/3 |

Cả 18 lần chạy chính thức đều có `error = null` và `skills_modified = false`; không có lần nào phải chạy lại vì hai trường này. `python -X utf8 scripts/verify_freeze.py` cho kết quả `OK` (PowerShell/Windows cần UTF-8 để đọc báo cáo qua Git). Check `tests_not_modified` của cả hai tác vụ code thất bại ở mọi điều kiện do tệp test gốc trong checkout Windows dùng CRLF, còn checker băm nội dung LF; đây là giới hạn môi trường khi diễn giải điểm kỹ thuật.

## 8. Phân tích

1. Trên tác vụ học, chỉ `skills-auto` cải thiện so với `baseline`: 23/27 so với 17/27 check (+6), điểm trung bình 0,85 so với 0,63. Trên tác vụ đánh giá, `skills-auto` cũng đứng đầu: 22/30 so với 17/30 (+5), điểm trung bình 0,72 so với 0,57; dự đoán H2 đúng về thứ hạng nhưng thấp hơn mức tăng thực tế (dự đoán +1–2 check). `subagents` không cải thiện tác vụ học (17/27 ở cả hai) và giảm điểm đánh giá xuống 14/30, chủ yếu do `logs-eval` chỉ đạt 3/10 thay vì 6/10. Không có điều kiện nào cải thiện tác vụ học mà không cải thiện tác vụ đánh giá. H3 đúng về hướng: điểm `skills-auto` giảm từ 23/27 (85,2%) ở học xuống 22/30 (73,3%) ở đánh giá; lợi ích so với baseline giảm từ 22,2 xuống 16,7 điểm phần trăm.
2. Check kỹ thuật: `skills-auto` và `baseline` cùng 17/18 ở cả học lẫn đánh giá; `subagents` còn 14/18 ở đánh giá. Skill giúp check quy ước: 6/9 ở học và 5/12 ở đánh giá, trong khi `baseline` và `subagents` đều 0 ở cả hai vai trò. Ba check quy ước chỉ có ở đánh giá (`rule_version_bump`, `rule_sorted_keys_format`, `rule_source_line`) đều không đạt với skill; 5/9 check quy ước còn lại ở đánh giá đạt. Skill rút từ phản hồi học chỉ mô tả quy trình đã gặp, không nêu ba quy ước mới.
3. Cả ba vết `skills-auto` đánh giá đều đọc một skill (`skills_read = 1`). Ví dụ skill `safe-python-maintenance` giúp `rule_regression_tests` ở `code-eval`: vết tạo `workspace/tests/test_regressions.py` với 4 test, khác `baseline` không đạt check này. Trái lại, `normalized-log-triage` được đọc ở `logs-eval` nhưng chỉ yêu cầu chung về schema; tác tử tự ghi `schema_version: "1.0"` và `generator: "acme-log-triage"` thay vì `schema_version: 2`, `generated_by: "log-triage"`, nên `rule_schema_header` vẫn trượt. Ở `data-eval`, vết ghi `metadata` thay vì `meta`, không tạo `clean.csv` và giữ giá trị tiền dạng USD, nên cả ba quy ước tương ứng vẫn trượt.
4. Token trung bình mỗi lần chạy: `baseline` 67.571, `subagents` 116.022 (+71,7%), `skills-auto` 95.357 (+41,1%). Tính trên toàn bộ 6 tác vụ, số check đạt trên 100.000 token lần lượt là 8,39 (`baseline`: 34/405426), 4,45 (`subagents`: 31/696136), 7,87 (`skills-auto`: 45/572145). Vì vậy `baseline` hiệu quả nhất theo điểm/token, còn `skills-auto` đạt điểm tuyệt đối cao nhất. Trong thí nghiệm này `subagents` không đáng chi phí thêm: tốn token hơn và ít check đạt hơn, dù kết luận bị giới hạn bởi ba tác vụ mỗi vai trò.
5. Không thấy tên tệp dữ liệu, định danh hay đáp án riêng của tác vụ đánh giá trong ba skill; curator chỉ nhận run có `role = learn`, `validate_skill` loại định danh eval, và bộ skill được đóng băng trước khi chạy eval (`verify_freeze.py: OK`, `skills_modified = false`). Có dấu hiệu lợi ích gắn với quy ước đã học hơn là khái quát hoàn toàn: `skills-auto` tăng 6/9 check quy ước ở học nhưng chỉ 5/12 ở đánh giá, trong đó cả ba check mới đều trượt. Đây là dấu hiệu chuyển giao hạn chế, chưa đủ chứng minh rò rỉ hay quá khớp do số lần chạy ít.
6. Cùng bộ skill, bản Phần 3.4 trong `results/skills-auto-dev/` và lần sau đóng băng đều đạt `code-learn` 9/10, `data-learn` 6/8, `logs-learn` 8/9: chênh **0/27 check**. Tuy nhiên tổng token tăng từ 274191 lên 294724 (+20533, +7,5%), chứng tỏ đường chạy không giống hệt nhau. Một lần lặp có điểm ổn định không loại trừ nhiễu; chênh lệch nhỏ trong bảng cần được xác nhận bằng nhiều lần chạy, còn mức tăng 6 check ở học và 5 check ở đánh giá là kết quả quan sát được của các lần chạy này.

## 9. Hạn chế và tính hợp lệ

1. Chỉ có 3 tác vụ học và 3 tác vụ đánh giá, với 27 và 30 check; một check có thể đổi tỉ lệ học 3,7 điểm phần trăm hoặc tỉ lệ đánh giá 3,3 điểm. Vì vậy không suy rộng thứ hạng ba điều kiện sang nhiều loại tác vụ khác.
2. Mỗi cấu hình/tác vụ chính thức chạy một lần. Lần lặp cùng skill ở tác vụ học cho cùng 23/27 điểm nhưng tổng token khác 7,5%; chưa thể ước lượng độ biến thiên điểm hay kiểm định ý nghĩa của chênh lệch giữa điều kiện.
3. Các tác vụ và `rule_` do giảng viên thiết kế; curator được phản hồi trực tiếp về quy ước của tập học. Mức tăng check quy ước có thể phản ánh độ giống giữa hai tập, nên ba quy ước mới trượt là bằng chứng quan trọng về giới hạn chuyển giao.
4. Chỉ dùng một cấu hình mô hình và môi trường Windows. Tệp test gốc CRLF làm `tests_not_modified` trượt ở cả hai tác vụ code dù không có bằng chứng tác tử sửa test; tỷ lệ check kỹ thuật vì thế không phản ánh hoàn toàn năng lực tác tử và có thể khác trên Linux/WSL.

## 10. Kết luận

Trên ba tác vụ đánh giá, `skills-auto` đạt 22/30 check, cao hơn `baseline` 17/30 và `subagents` 14/30. Lợi ích quan sát được nằm ở check quy ước (5/12 so với 0/12 của baseline), còn ba quy ước mới đều trượt. `subagents` tốn token trung bình cao nhất nhưng không tăng điểm học và giảm điểm đánh giá trong các lần chạy này. Bước tiếp theo nên kiểm tra bộ skill đóng băng trên nhiều tác vụ mới và lặp lại mỗi điều kiện nhiều lần để đo độ ổn định và khả năng chuyển giao.

## Phụ lục

- Lệnh chính đã chạy (theo thứ tự có thể xác nhận từ hội thoại, commit và timestamp trong `run.json`; không phải toàn bộ lịch sử terminal):

```powershell
python scripts/tour.py
pytest tests/test_02_agent.py
python -m lab.runner --condition baseline --tasks data-learn
python -m lab.runner --condition baseline --tasks code-learn logs-learn
python -m lab.runner --condition subagents --tasks learn
pytest tests/test_04_curator.py
python -m lab.curator
python -m lab.runner --condition skills-auto --tasks learn
git add -A
git commit -m "hypotheses"
git commit --allow-empty -m "freeze skills"
Move-Item -LiteralPath results/skills-auto -Destination results/skills-auto-dev
git add -A
git commit -m "hypotheses"
git commit --allow-empty -m "freeze skills"
git tag -f freeze
python -m lab.runner --condition baseline --tasks eval
python -m lab.runner --condition subagents --tasks eval
python -m lab.runner --condition skills-auto --tasks all
python -X utf8 scripts/verify_freeze.py
python -m lab.compare > report/table.md
python scripts/check_breakdown.py
```

- Ghi chú: commit `hypotheses` đầu tiên chưa có H1–H3; nhóm đã tạo commit `hypotheses` mới có đủ ba dòng rồi chuyển tag `freeze` tới commit đóng băng sau nó (`8bfe7ce`).
- Thử thách mở rộng (Phần 6): chưa thực hiện.
