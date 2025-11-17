"""
Giao diện Tkinter cho YTFetcher

Gói này triển khai kiến trúc MVC nhỏ gọn để người dùng tương tác với
`ytfetcher` thông qua giao diện desktop. Các thành phần chính:

- `models`: nắm giữ cấu hình và trạng thái ứng dụng
- `controllers`: điều phối giữa GUI và lớp `YTFetcher`
- `views`: dựng layout Tkinter và widget chuyên biệt
- `services`: tiện ích hỗ trợ (ví dụ runner bất đồng bộ)
"""

from .main import run

__all__ = ["run"]

