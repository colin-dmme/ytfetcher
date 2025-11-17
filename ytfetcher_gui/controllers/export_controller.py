from __future__ import annotations

from pathlib import Path
from typing import Callable, Sequence

from ytfetcher.models.channel import ChannelData
from ytfetcher.services.exports import METEDATA_LIST, Exporter

from ytfetcher_gui.models import ExportConfig
from ytfetcher_gui.services import AsyncTaskRunner


class ExportController:
    """
    Thực thi Exporter trong thread riêng để không khóa giao diện.
    """

    def __init__(self, runner: AsyncTaskRunner):
        self._runner = runner

    def start_export(
        self,
        export_config: ExportConfig,
        data: Sequence[ChannelData],
        metadata_fields: Sequence[str],
        include_timing: bool,
        on_success: Callable[[Path], None],
        on_error: Callable[[Exception], None],
    ):
        if not data:
            on_error(ValueError("Chưa có dữ liệu để export."))
            return

        def _task():
            exporter = Exporter(
                channel_data=list(data),
                allowed_metadata_list=list(metadata_fields) or list(METEDATA_LIST.__args__),
                timing=include_timing,
                filename=export_config.filename,
                output_dir=str(export_config.output_dir),
            )
            method_name = f"export_as_{export_config.format.value}"
            export_method = getattr(exporter, method_name)
            export_method()
            return export_config.output_dir / f"{export_config.filename}.{export_config.format.value}"

        self._runner.submit(_task, on_success, on_error)

