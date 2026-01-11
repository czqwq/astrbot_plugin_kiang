from dataclasses import dataclass
from pathlib import Path
import os
from typing import List

from astrbot.api import logger


@dataclass
class VoiceCategory:
    dir: Path
    items: List[str]


class VoiceDataStore:
    def __init__(self, data_dir) -> None:
        self._data_dir = Path(data_dir)
        
        # 获取语音文件夹中的所有音频文件
        self.voice_items = self._get_voice_files()
        
        self.voice = VoiceCategory(
            dir=self._data_dir,
            items=self.voice_items,
        )

        logger.info(f"[voice:init] Loaded voice items: {self.voice_items}")

    def _get_voice_files(self) -> List[str]:
        """获取语音文件夹中的所有音频文件名（不含扩展名）"""
        voice_dir = self._data_dir
        if not voice_dir.exists():
            return []
        
        # 支持常见的音频文件格式
        audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg'}
        voice_files = []
        
        for file_path in voice_dir.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in audio_extensions:
                    voice_files.append(file_path.stem)  # 使用 stem 获取不带扩展名的文件名
        
        return voice_files

