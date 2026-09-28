# Phiếu Phản Ánh — K4 Level 3A, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng mẫu trả lời còn trống bằng câu trả lời của chính bạn.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Bùi Hoàng Anh  Mã học viên: 2A202602697

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Nếu để mặc định 'changeme', app vẫn bật lên và phục vụ /ask mà mình không hề biết là quên set secret; kẻ tấn công chỉ cần đoán đúng khóa mặc định là gọi API bằng hóa đơn LLM của mình. Không có giá trị mặc định thì Settings() ném lỗi ngay lúc khởi động, pipeline đỏ trước khi service được public, buộc mình phải set khóa trước khi nhận traffic thật.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> JSON thật: {"event":"ask_completed","level":"info","timestamp":"2026-09-28T08:12:59.449229+00:00","user_id":"sv01","tokens_in":3,"tokens_out":34,"cost_usd":2.085e-05}. Với nó mình (1) lọc/đếm theo field event bằng công cụ gom log, và (2) SUM(cost_usd) nhóm theo user_id để tìm user tiêu tiền nhiều nhất. print chuỗi tự do không có cấu trúc nên không lọc/đếm/cảnh báo theo field được.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | 1700 MB |
| Multi-stage | 271 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

> Khác biệt chủ yếu ở tầng build: bản 1-stage dùng base python:3.11 đầy đủ, giữ lại compiler/toolchain, bộ đệm pip và cả tầng cài đặt ngay trong image cuối; bản multi-stage chỉ COPY --from=builder /install /usr/local sang stage runtime slim nên loại bỏ compiler và bộ đệm pip. Đo thật trên máy mình: 1-stage là 1,7 GB, còn multi-stage slim là 271 MB - chênh lệch 1,4 GB gần như toàn bộ là các thứ chỉ cần lúc build, không cần lúc chạy.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> Với Dockerfile đã sửa, thứ tự là COPY requirements.txt -> RUN pip install -> COPY app/utils, nên khi sửa app/main.py thì hai layer cài dependency lấy lại từ cache, chỉ từ layer COPY app trở đi build lại. Nếu đặt COPY . . trước RUN pip install, hash layer COPY đổi mỗi lần sửa code làm hỏng cache và Docker phải cài lại toàn bộ thư viện.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> Một lỗ hổng RCE trong code Python cho phép kẻ tấn công có shell trong container. Nếu container chạy root, uid 0 ấy kết hợp với Docker cấu hình lỏng (mount docker.sock, privileged...) có thể vọt quyền ra host và chiếm toàn bộ máy. USER appuser giới hạn process ở uid 10001, nên dù code bị phá cũng chỉ có quyền user thường, thu hẹp phạm vi phá hoại.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> Đếm theo phút đồng hồ, user gửi 10 request lúc 10:00:59 và 10 request lúc 10:01:01 là 20 request trong khoảng 2 giây vẫn hợp lệ. Sliding window 60 giây luôn đếm số request trong 60 giây trượt gần nhất nên không có kẽ hở reset cố định để lách.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> Rate limit giới hạn tần suất (số request/phút), cost guard giới hạn tiền (USD/user/tháng). Rate limit cho qua nhưng cost guard phải chặn: user đúng 10 request/phút nhưng mỗi câu dài hàng chục nghìn token. Ngược lại, cost guard cho qua nhưng rate limit chặn: user chỉ gửi câu ngắn rất rẻ nhưng spam hàng trăm lần/phút.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> Nếu gộp /health và /ready rồi bắt ping Redis, khi Redis mất kết nối 30 giây cả 3 container cùng 503 ở health check. Orchestrator/load balancer thấy cả cụm không khỏe sẽ restart/ngừng điều hướng toàn bộ, biến sự cố nhỏ của Redis thành ngừng dịch vụ. /health chỉ nên trả lời process có sống không, /ready mới kiểm tra dependency.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> Nếu lịch sử nằm trong dict của từng process, mỗi câu có thể rơi vào container khác nhau sau load balancer, nên history_length nhảy lung tung thay vì tăng đều. Khi lưu vào Redis, cả 3 container cùng nhìn một state nên con số ổn định, phản ánh đúng hội thoại.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> Lỗi thật mình gặp: mở link gốc https://day12-agent-y9v3.onrender.com/ trong trình duyệt thì thấy "Not Found" (404), tưởng deploy hỏng. Mình kiểm tra bằng curl thì thấy chỉ link gốc trả 404 còn /health và /ready đều 200. Nguyên nhân là app không khai báo route cho đường dẫn "/", nên trình duyệt mở đúng link nền render.com thì không có gì để hiển thị. Cách sửa/kiểm tra đúng: gọi trực tiếp https://day12-agent-y9v3.onrender.com/health; đây là lỗi do hiểu nhầm "service không có trang chủ" thành "deploy không thành công", không cần sửa code service.
