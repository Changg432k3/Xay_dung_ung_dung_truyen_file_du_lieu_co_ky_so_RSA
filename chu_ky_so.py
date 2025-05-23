from flask import Flask, request, render_template_string, send_from_directory
import os, hashlib, base64 # requests không còn cần thiết cho việc gửi file trực tiếp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
RECEIVED_FOLDER = "received"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RECEIVED_FOLDER, exist_ok=True)

# Khởi tạo RSA key pair (Chỉ tạo một lần khi ứng dụng khởi động)
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode()

# HTML Giao diện chính (đã được cải tiến đáng kể)
HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Truyền - Nhận File có Chữ Ký Số (RSA + SHA-512)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @keyframes fadeInScale {
      from { opacity: 0; transform: scale(0.95); }
      to { opacity: 1; transform: scale(1); }
    }
    .fade-in-scale {
      animation: fadeInScale 0.3s ease-out forwards;
    }
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-image: linear-gradient(to right top, #d1f4ff, #e7f7ff, #f3fbff, #f9fdff, #ffffff);
    }
    .message-box {
      padding: 0.75rem 1rem;
      border-radius: 0.5rem;
      font-size: 0.9rem;
      margin-top: 1rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      animation: fadeInScale 0.3s ease-out forwards;
    }
    .message-success {
      background-color: #d4edda;
      color: #155724;
      border: 1px solid #c3e6cb;
    }
    .message-error {
      background-color: #f8d7da;
      color: #721c24;
      border: 1px solid #f5c6cb;
    }
    .message-info {
      background-color: #d1ecf1;
      color: #0c5460;
      border: 1px solid #bee5eb;
    }
    .file-input-label {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0.75rem 1.25rem;
      background-color: #f0f4f8;
      border: 1px solid #cbd5e1;
      border-radius: 0.5rem;
      cursor: pointer;
      text-align: center;
      transition: background-color 0.2s ease, transform 0.1s ease;
      font-weight: 500;
      color: #4a5568;
    }
    .file-input-label:hover {
      background-color: #e2e8f0;
      transform: translateY(-1px);
    }
    .file-input-label:active {
      transform: translateY(0);
    }
    textarea {
        background-color: #f8fafc; /* Light gray for textareas */
    }
  </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
  <div class="max-w-4xl mx-auto p-8 bg-white rounded-3xl shadow-2xl space-y-10 w-full transform transition-all duration-300 ease-in-out hover:shadow-3xl">
    <h1 class="text-4xl font-extrabold text-center text-blue-800 tracking-tight flex flex-col items-center justify-center gap-2">
      <span class="text-6xl animate-pulse">🔒</span> Truyền - Nhận File có Chữ Ký Số
      <span class="text-lg font-medium text-gray-500">(RSA + SHA-512)</span>
    </h1>

    <div class="border border-green-300 rounded-2xl p-7 bg-gradient-to-br from-green-50 to-green-100 shadow-lg">
      <h2 class="text-2xl font-bold text-green-800 mb-5 flex items-center gap-3">
        <span class="text-3xl">📝</span> Ký file để gửi
      </h2>
      <p class="text-base text-gray-700 mb-5 leading-relaxed">
        Chọn tệp bạn muốn ký. Sau khi ký, ứng dụng sẽ tạo và hiển thị chữ ký số cùng public key của bạn.
        <br>
        **Quan trọng:** Bạn cần **tự chia sẻ tệp gốc này** qua một dịch vụ bên ngoài như:
        <ul class="list-disc list-inside mt-3 text-sm text-gray-600">
            <li>Dịch vụ lưu trữ đám mây: <a href="https://drive.google.com/" target="_blank" class="text-blue-600 hover:underline">Google Drive</a>, <a href="https://www.dropbox.com/" target="_blank" class="text-blue-600 hover:underline">Dropbox</a>, <a href="https://onedrive.live.com/" target="_blank" class="text-blue-600 hover:underline">OneDrive</a></li>
            <li>Dịch vụ chia sẻ file trực tiếp: <a href="https://snapdrop.net/" target="_blank" class="text-blue-600 hover:underline">Snapdrop.net</a>, <a href="https://sharedrop.io/" target="_blank" class="text-blue-600 hover:underline">Sharedrop.io</a>, <a href="https://send-anywhere.com/" target="_blank" class="text-blue-600 hover:underline">Send-Anywhere.com</a>, <a href="https://wormhole.app/" target="_blank" class="text-blue-600 hover:underline">Wormhole.app</a></li>
        </ul>
        Gửi **chữ ký số** và **public key của bạn** cho người nhận qua một kênh riêng biệt và an toàn (ví dụ: email, tin nhắn đã mã hóa).
      </p>
      <form method="POST" enctype="multipart/form-data" action="/sign_and_get_details" class="space-y-5">
        <div>
          <label for="file_to_sign" class="file-input-label">
            <span class="mr-2 text-xl">📁</span> Chọn tệp để ký
            <span id="file_to_sign_name" class="ml-2 text-gray-600 font-normal italic"></span>
          </label>
          <input type="file" name="file" id="file_to_sign" class="hidden" required onchange="document.getElementById('file_to_sign_name').innerText = this.files[0].name || 'Chưa có tệp nào được chọn'">
        </div>
        <button type="submit" class="w-full bg-green-700 text-white px-6 py-3 rounded-xl hover:bg-green-800 focus:outline-none focus:ring-4 focus:ring-green-300 focus:ring-offset-2 transition-all duration-300 text-lg font-semibold shadow-md hover:shadow-lg transform hover:scale-105">
          Ký file và nhận thông tin
          <span class="ml-2 text-xl">➡️</span>
        </button>
      </form>
      {% if signed_data %}
      <div class="mt-8 p-6 bg-gray-100 rounded-xl border border-gray-200 space-y-5 fade-in-scale">
          <p class="text-xl font-semibold text-gray-800 flex items-center gap-2">
            <span class="text-2xl">✨</span> Thông tin sau khi ký:
          </p>
          <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Chữ ký số (Base64):</label>
              <textarea readonly class="w-full border border-gray-300 p-3 rounded-lg bg-white text-gray-800 text-sm font-mono resize-y shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400" rows="5" onclick="this.select()">{{ signed_data.signature }}</textarea>
              <button onclick="navigator.clipboard.writeText(this.previousElementSibling.value)" class="mt-3 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 transition-colors duration-200 text-sm font-medium flex items-center gap-1">
                <span class="text-lg">📋</span> Sao chép Chữ ký
              </button>
          </div>
          <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Public Key (PEM):</label>
              <textarea readonly class="w-full border border-gray-300 p-3 rounded-lg bg-white text-gray-800 text-sm font-mono resize-y shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400" rows="9" onclick="this.select()">{{ signed_data.public_key }}</textarea>
              <button onclick="navigator.clipboard.writeText(this.previousElementSibling.value)" class="mt-3 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 transition-colors duration-200 text-sm font-medium flex items-center gap-1">
                <span class="text-lg">🔑</span> Sao chép Public Key
              </button>
          </div>
          <p class="text-sm text-red-700 font-semibold mt-4 bg-red-100 p-3 rounded-lg flex items-center gap-2">
              <span class="text-xl">⚠️</span> Quan trọng: Hãy tự chia sẻ tệp gốc đã ký qua dịch vụ bên ngoài và gửi Chữ ký số và Public Key trên cho người nhận.
          </p>
      </div>
      {% endif %}
      {% if sent_message %}
      <p class="message-box {% if 'Lỗi' in sent_message %}message-error{% else %}message-success{% endif %}">
        {% if 'Lỗi' in sent_message %}<span class="text-xl">❌</span>{% else %}<span class="text-xl">✅</span>{% endif %} {{ sent_message }}
      </p>
      {% endif %}
    </div>

    <div class="border border-purple-300 rounded-2xl p-7 bg-gradient-to-br from-purple-50 to-purple-100 shadow-lg">
      <h2 class="text-2xl font-bold text-purple-800 mb-5 flex items-center gap-3">
        <span class="text-3xl">📦</span> Nhận và xác minh file
      </h2>
      <p class="text-base text-gray-700 mb-5 leading-relaxed">
        Người nhận cần tải tệp gốc từ dịch vụ chia sẻ trực tiếp (hoặc đám mây) mà người gửi đã sử dụng.
        Sau đó, dán chữ ký số và public key được cung cấp bởi người gửi vào đây để xác minh tính toàn vẹn của tệp.
      </p>
      <form method="POST" enctype="multipart/form-data" action="/receive" class="space-y-5">
        <div>
          <label for="file_receive" class="file-input-label">
            <span class="mr-2 text-xl">📥</span> Chọn tệp đã nhận (từ dịch vụ chia sẻ)
            <span id="file_receive_name" class="ml-2 text-gray-600 font-normal italic"></span>
          </label>
          <input type="file" name="file" id="file_receive" class="hidden" required onchange="document.getElementById('file_receive_name').innerText = this.files[0].name || 'Chưa có tệp nào được chọn'">
        </div>
        <textarea name="signature" placeholder="Dán chữ ký (base64) từ người gửi vào đây..." class="w-full border border-gray-300 p-3 rounded-lg focus:ring-purple-500 focus:border-purple-500 bg-white text-gray-800 shadow-sm focus:outline-none focus:ring-2" rows="5" required></textarea>
        <textarea name="pubkey" placeholder="Dán public key (PEM) của người gửi vào đây..." class="w-full border border-gray-300 p-3 rounded-lg focus:ring-purple-500 focus:border-purple-500 bg-white text-gray-800 shadow-sm focus:outline-none focus:ring-2" rows="9" required></textarea>
        <button type="submit" class="w-full bg-purple-700 text-white px-6 py-3 rounded-xl hover:bg-purple-800 focus:outline-none focus:ring-4 focus:ring-purple-300 focus:ring-offset-2 transition-all duration-300 text-lg font-semibold shadow-md hover:shadow-lg transform hover:scale-105">
          Xác minh file
          <span class="ml-2 text-xl">✔️</span>
        </button>
      </form>
      {% if verify_message %}
      <p class="message-box {% if 'thất bại' in verify_message %}message-error{% else %}message-success{% endif %}">
        {% if 'thất bại' in verify_message %}<span class="text-xl">❌</span>{% else %}<span class="text-xl">✅</span>{% endif %} {{ verify_message }}
      </p>
      {% endif %}
    </div>

    <footer class="text-center text-gray-500 text-sm mt-10">
      Ứng dụng ký và xác minh chữ ký số RSA + SHA-512 (kết hợp với dịch vụ chia sẻ file trực tiếp)
      <div class="mt-2 text-xs">Phát triển bởi [Tên/Nhóm của bạn]</div>
    </footer>
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML)

@app.route("/sign_and_get_details", methods=["POST"])
def sign_and_get_details():
    file = request.files.get("file")

    if not file:
        return render_template_string(HTML, sent_message="❌ Lỗi: Vui lòng chọn tệp để ký.")

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(filepath)
    except Exception as e:
        return render_template_string(HTML, sent_message=f"❌ Lỗi khi lưu tệp: {e}")

    with open(filepath, "rb") as f:
        data = f.read()

    # Tạo chữ ký
    digest = hashlib.sha512(data).digest()
    try:
        signature = private_key.sign(
            digest,
            padding.PKCS1v15(),
            hashes.SHA512()
        )
        signature_b64 = base64.b64encode(signature).decode()
        
        # Trả về chữ ký và public key để người dùng sao chép
        signed_data = {
            "signature": signature_b64,
            "public_key": public_pem
        }
        return render_template_string(HTML, signed_data=signed_data)

    except Exception as e:
        return render_template_string(HTML, sent_message=f"❌ Lỗi khi tạo chữ ký: {e}")

@app.route("/receive", methods=["POST"])
def receive():
    file = request.files.get("file")
    signature_b64 = request.form.get("signature")
    pubkey_pem = request.form.get("pubkey")

    if not file or not signature_b64 or not pubkey_pem:
        return render_template_string(HTML, verify_message="❌ Lỗi: Vui lòng cung cấp đầy đủ tệp, chữ ký và public key.")

    filepath = os.path.join(RECEIVED_FOLDER, file.filename)
    try:
        file.save(filepath)
    except Exception as e:
        return render_template_string(HTML, verify_message=f"❌ Lỗi khi lưu tệp đã nhận: {e}")

    with open(filepath, "rb") as f:
        data = f.read()
    digest = hashlib.sha512(data).digest()
    
    try:
        signature = base64.b64decode(signature_b64)
    except Exception as e:
        return render_template_string(HTML, verify_message=f"❌ Xác minh thất bại: Chữ ký không hợp lệ (không phải Base64): {e}")

    try:
        public_key = serialization.load_pem_public_key(pubkey_pem.encode())
        # Cố gắng xác minh chữ ký
        public_key.verify(signature, digest, padding.PKCS1v15(), hashes.SHA512())
        verify_msg = f"✅ Xác minh thành công! File '{file.filename}' hợp lệ và đã được lưu tại thư mục '{RECEIVED_FOLDER}'."
    except InvalidSignature:
        verify_msg = "❌ Xác minh thất bại: Chữ ký không khớp với dữ liệu hoặc public key. File có thể đã bị thay đổi hoặc chữ ký/public key không đúng."
    except ValueError as e:
        verify_msg = f"❌ Xác minh thất bại: Public key không hợp lệ (không phải định dạng PEM hoặc lỗi khác): {e}"
    except Exception as e:
        verify_msg = f"❌ Xác minh thất bại: Xảy ra lỗi không xác định trong quá trình xác minh: {e}"

    return render_template_string(HTML, verify_message=verify_msg)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    