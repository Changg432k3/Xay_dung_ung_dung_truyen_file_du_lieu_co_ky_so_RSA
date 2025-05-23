# Xay_dung_ung_dung_truyen_file_du_lieu_co_ky_so_RSA
Đây là một ứng dụng web Flask đơn giản cho phép người dùng ký số các tệp tin bằng thuật toán RSA với hàm băm SHA-512 và xác minh tính toàn vẹn cũng như nguồn gốc của tệp tin đã ký. Để giải quyết vấn đề truyền file giữa các mạng khác nhau (ví dụ: lỗi "Connection timed out"), ứng dụng này kết hợp với các dịch vụ lưu trữ đám mây hoặc chia sẻ file trực tiếp qua web để phân phối tệp gốc.
# 💡 Giới thiệu
Trong môi trường mạng hiện đại, việc truyền tải dữ liệu an toàn là vô cùng quan trọng. Ứng dụng này cung cấp một giải pháp cơ bản nhưng hiệu quả để đảm bảo:
- Tính toàn vẹn của dữ liệu: Xác nhận rằng tệp tin không bị thay đổi trong quá trình truyền.
- Xác thực nguồn gốc: Xác minh rằng tệp tin thực sự được gửi bởi người mà bạn mong đợi.
# Ứng dụng sử dụng:
- RSA (Rivest–Shamir–Adleman): Một thuật toán mã hóa khóa công khai phổ biến để tạo và xác minh chữ ký số.
- SHA-512 (Secure Hash Algorithm 512): Một hàm băm mật mã dùng để tạo ra một "dấu vân tay" duy nhất cho tệp tin, đảm bảo tính toàn vẹn của dữ liệu.
- Để khắc phục các hạn chế về mạng (như firewall, NAT, IP nội bộ) khi truyền file trực tiếp, ứng dụng này được thiết kế để hoạt động song song với các dịch vụ lưu trữ đám mây (Google Drive, Dropbox, v.v.) hoặc các dịch vụ chia sẻ file trực tiếp (Snapdrop, Sharedrop, v.v.) để truyền tải tệp gốc, trong khi vẫn giữ chức năng cốt lõi là ký và xác minh chữ ký số.
# ✨ Tính năng
- Tạo chữ ký số: Người gửi có thể chọn một tệp và tạo chữ ký số cho tệp đó.
- Hiển thị thông tin ký: Sau khi ký, ứng dụng sẽ hiển thị chữ ký số (Base64) và Public Key (PEM) tương ứng để người gửi có thể chia sẻ thủ công.
- Xác minh chữ ký số: Người nhận có thể tải tệp gốc, sau đó nhập chữ ký số và Public Key từ người gửi để xác minh tính hợp lệ của tệp.
- Giao diện người dùng thân thiện: Sử dụng Flask và Tailwind CSS để tạo giao diện web đơn giản và dễ sử dụng.
- Lưu trữ tệp cục bộ: Tệp được ký và tệp đã nhận sẽ được lưu trữ tạm thời trong các thư mục uploads và received trên máy cục bộ.
# ⚙️ Cách hoạt động
- Người gửi:
+ Chọn tệp muốn ký trong ứng dụng.
+ Ứng dụng sử dụng khóa riêng (Private Key) của người gửi để tạo chữ ký số cho tệp.
+ Ứng dụng hiển thị chữ ký số (Base64) và khóa công khai (Public Key) tương ứng.
+ Thủ công: Người gửi tải tệp gốc lên một dịch vụ lưu trữ đám mây (ví dụ: Google Drive) HOẶC sử dụng dịch vụ chia sẻ file trực tiếp (ví dụ: Snapdrop.net).
+ Thủ công: Người gửi gửi chữ ký số và khóa công khai cho người nhận thông qua một kênh riêng biệt (ví dụ: email, tin nhắn).
- Người nhận:
+Thủ công: Tải tệp gốc về máy tính từ dịch vụ lưu trữ đám mây HOẶC nhận từ dịch vụ chia sẻ file trực tiếp.
+ Trong ứng dụng, người nhận chọn tệp vừa tải về.
+ Người nhận dán chữ ký số và khóa công khai mà người gửi đã cung cấp vào các trường tương ứng.
+ Ứng dụng sử dụng Public Key để xác minh chữ ký số của tệp.
+ Ứng dụng thông báo kết quả xác minh (thành công/thất bại).
# 🚀 Yêu cầu
- Python 3.x
- Các thư viện Python: Flask, cryptography
