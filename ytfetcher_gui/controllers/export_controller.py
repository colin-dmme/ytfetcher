from __future__ import annotations

from pathlib import Path
from typing import Callable, Sequence

from ytfetcher.models.channel import ChannelData
from ytfetcher.services.exports import METEDATA_LIST, Exporter

from ytfetcher_gui.models import ExportConfig
from ytfetcher_gui.services import AsyncTaskRunner
from ytfetcher_gui.utils import extract_primary_language, slugify_title


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
        language_codes: Sequence[str] | None,
        on_success: Callable[[Sequence[Path]], None],
        on_error: Callable[[Exception], None],
    ):
        if not data:
            on_error(ValueError("Chưa có dữ liệu để export."))
            return

        def _task():
            if export_config.per_video:
                written_paths: list[Path] = []
                for channel_data in data:
                    video_id = channel_data.video_id
                    title = channel_data.metadata.title if channel_data.metadata else "video"
                    lang = extract_primary_language(language_codes or [])
                    slug = (slugify_title(title) or "video")[:25]
                    base_name = f"{slug}-{video_id}-{lang}"
                    exporter = Exporter(
                        channel_data=[channel_data],
                        allowed_metadata_list=list(metadata_fields) or list(METEDATA_LIST.__args__),
                        timing=include_timing,
                        filename=base_name,
                        output_dir=str(export_config.output_dir),
                    )
                    method_name = f"export_as_{export_config.format.value}"
                    export_method = getattr(exporter, method_name)
                    export_method()
                    written_paths.append(export_config.output_dir / f"{base_name}.{export_config.format.value}")
                return written_paths
            else:
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
                return [export_config.output_dir / f"{export_config.filename}.{export_config.format.value}"]

        self._runner.submit(_task, on_success, on_error)

