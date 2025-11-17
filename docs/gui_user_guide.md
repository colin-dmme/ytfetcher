# Hướng dẫn sử dụng YTFetcher GUI

Tài liệu này mô tả cách vận hành giao diện Tkinter của YTFetcher để lấy transcript YouTube và xuất dữ liệu hàng loạt. Mọi hướng dẫn đều áp dụng cho Python 3.12.10 và yêu cầu chạy lệnh thông qua `uv` theo chuẩn dự án.

## 1. Chuẩn bị môi trường

1. Cài đặt phụ thuộc (chỉ cần một lần):
   ```bash
   uv sync
   ```
2. Khởi động GUI:
   ```bash
   uv run python -m ytfetcher_gui
   ```
   Bạn cũng có thể dùng script đã khai báo sẵn: `uv run ytfetcher-gui`.
3. Cấu hình người dùng được lưu vào `~/.ytfetcher_gui_settings.json` và sẽ tự động nạp ở lần mở tiếp theo.

## 2. Tổng quan bố cục

Giao diện chia thành ba khối chính cùng một thanh điều khiển bên dưới:

| Khu vực | Chức năng chính |
| --- | --- |
| **Nguồn dữ liệu** | Chọn chế độ fetch (channel, playlist, video_ids), nhập tham số kèm ngôn ngữ & giới hạn. |
| **Kết nối** | Thiết lập HTTP/HTTPS proxy, Webshare, timeout và header JSON. |
| **Xuất dữ liệu** | Đặt tên file, thư mục, định dạng (txt/csv/json), metadata và tùy chọn chia file. |
| **Thanh trạng thái** | Chứa nút `Fetch dữ liệu`, `Export`, thanh tiến trình, thông báo số video đã xử lý. |

## 3. Cấu hình nguồn dữ liệu

- **Chế độ** (`video_ids`, `channel`, `playlist`): quyết định trường nào được nhập. GUI tự ẩn/hiện Channel handle, Playlist ID hoặc ô `Video IDs (mỗi dòng)` để tránh nhập sai.
- **Video IDs**: mỗi dòng một URL hoặc ID. Nhãn dưới hộp văn bản hiển thị tổng số ID hợp lệ.
- **Max results**: số video tối đa cần lấy. Nếu để trống hoặc giá trị ≤ 0, ứng dụng mặc định 25.
- **Ngôn ngữ**: danh sách mã ngôn ngữ (vd: `en, vi, fr`). Thứ tự thể hiện độ ưu tiên khi tìm transcript.
- **Kiểu dữ liệu** (`full`, `transcripts`, `metadata`): khớp với `DataScope` của core.
- **Chỉ transcript tạo thủ công**: chỉ bật nếu muốn lọc transcript có đánh dấu “manually created” từ API.

## 4. Thiết lập kết nối & proxy

- **HTTP/HTTPS proxy**: nhập URL đầy đủ dạng `http://user:pass@host:port`. Có thể để trống một trong hai nếu chỉ dùng một giao thức.
- **Webshare user/pass**: dành riêng cho dịch vụ Webshare (proxy residential). Nếu điền trường này, GUI sẽ tự ưu tiên cấu hình Webshare khi tạo `WebshareProxyConfig`.
- **Timeout (s)**: số giây tối đa cho mỗi request HTTP. Giá trị không hợp lệ sẽ quay về 4.0 giây.
- **HTTP headers (JSON)**: chuỗi JSON mô tả header tùy chỉnh. Ví dụ `{"User-Agent": "ytfetcher/1.0"}`. Dữ liệu sẽ được chuyển tới `HTTPConfig` giống CLI.

### Lưu ý

- Có thể kết hợp vừa Webshare vừa custom proxy, nhưng khi Webshare username/password hợp lệ thì controller sẽ ưu tiên chế độ Webshare.
- Thông tin proxy và header cũng được ghi vào file cấu hình ở thư mục home, vì vậy hãy xóa file này nếu không muốn tự động nạp.

## 5. Cấu hình xuất dữ liệu

- **Tên file**: tên cơ sở của file output (không gồm phần mở rộng). Nếu bỏ trống sẽ thành `ytfetcher_export`.
- **Thư mục xuất**: mặc định là thư mục hiện hành. Nhấn `Chọn...` để đổi.
- **Định dạng**: `txt`, `json`, hoặc `csv`. Ứng dụng sẽ sử dụng `Exporter` tương ứng.
- **Bao gồm thời gian transcript**: thêm `start`/`duration` vào dữ liệu transcript.
- **Mỗi video xuất 1 file riêng** (`per_video`): bật để tạo một file trên mỗi video (ví dụ `video_id.json`).
- **Metadata**: chọn các trường cần xuất (`title`, `description`, `url`, `duration`, `view_count`, `thumbnails`). Tối thiểu nên bật `title` hoặc `url` để dễ nhận biết video.

## 6. Quy trình thao tác chuẩn

1. **Điền nguồn dữ liệu** theo chế độ mong muốn.
2. **Nhập cấu hình kết nối** nếu cần proxy/timeout riêng.
3. **Điều chỉnh xuất dữ liệu**: định dạng, thư mục, metadata, thời gian transcript.
4. Nhấn **`Fetch dữ liệu`**:
   - Ứng dụng sẽ khóa các nút, chạy spinner và cập nhật trạng thái như “Fetching transcripts…”.
   - Khi hoàn tất, dialog “Hoàn tất” xuất hiện kèm số video. Nút `Export` tự động chuyển sang trạng thái khả dụng.
5. Nhấn **`Export`** để ghi dữ liệu đã fetch:
   - Có thể xuất nhiều lần với cấu hình khác nhau mà không cần fetch lại, miễn là chưa đóng app.
   - Dialog thành công hiển thị đường dẫn cuối cùng, hoặc số lượng file khi bật chế độ “per video”.
6. Khi đóng ứng dụng, cấu hình hiện tại được lưu tự động. Nếu muốn xóa, hãy xóa file `~/.ytfetcher_gui_settings.json` trước khi mở lại.

## 7. Mẹo & xử lý lỗi thường gặp

- **Thiếu dữ liệu bắt buộc**: nếu quên channel handle/video IDs, GUI sẽ báo lỗi “Thiếu dữ liệu” với thông tin cụ thể. Sửa và thử lại.
- **Proxy sai định dạng**: cần kèm protocol (`http://` hoặc `https://`). Nếu không, `youtube_transcript_api` sẽ báo lỗi kết nối.
- **Headers JSON không hợp lệ**: hãy dùng dấu nháy kép cho key/value như JSON chuẩn. Có thể kiểm tra nhanh bằng `python -m json.tool`.
- **Không thể export**: đảm bảo thư mục đích tồn tại và bạn có quyền ghi. Nếu `per_video` bật, hãy chọn thư mục trống để tránh nhầm lẫn.
- **Theo dõi tiến trình**: số video đã fetch hiển thị ở góc phải thanh điều khiển. Nếu dừng giữa chừng, kiểm tra log CLI nơi bạn khởi chạy để xem traceback.

## 8. Kịch bản mẫu (video IDs + proxy)

1. Chọn **Chế độ** → `video_ids` và dán mỗi URL vào một dòng.
2. Đặt **Ngôn ngữ** thành `vi, en` để ưu tiên transcript tiếng Việt.
3. Nhập **HTTP proxy**: `http://user:pass@proxy.example:8080` (để trống HTTPS nếu dùng cùng host).
4. Thay **Định dạng** → `txt`, bật `Bao gồm thời gian transcript`, chọn thêm metadata `url` và `view_count`.
5. Nhấn `Fetch dữ liệu` → đợi thông báo hoàn tất → nhấn `Export`. Thư mục sẽ chứa một file `ytfetcher_export.txt` với 1–n đoạn transcript tùy cấu hình.

GIờ đây bạn đã có thể vận hành toàn bộ quy trình bằng GUI mà không cần nhớ câu lệnh CLI, đồng thời vẫn giữ đầy đủ tính năng proxy, metadata và lưu cấu hình tự động.

