"""
精简版插件 - 只保留关键词触发语音发送功能
"""
import random
from pathlib import Path

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register
from astrbot.core.message.components import Plain, Record
from astrbot.core import AstrBotConfig
from astrbot.core.utils.astrbot_path import get_astrbot_data_path

from .datastore import VoiceDataStore


@register("kiang", "czqwq", "语音回复插件", "1.0.1")
class Kiang(Star):
    def __init__(self, *args, **kwargs):
        # 检查参数数量以适配框架的参数传递方式
        if len(args) == 1:
            # 只传递了 context 参数
            context = args[0]
            config = None
        elif len(args) == 2:
            # 传递了 context 和 config 参数
            context = args[0]
            config = args[1]
        else:
            # 参数数量不符合预期，尝试从 kwargs 获取
            context = kwargs.get('context')
            config = kwargs.get('config')
            
        super().__init__(context)
        self.config = config or {}

        # 使用插件数据目录规范路径
        base_path = get_astrbot_data_path()
        plugin_data_path = Path(str(base_path)) / "plugin_data" / "kiang"
        
        # 处理 config 为字典的情况
        if hasattr(self.config, 'get'):
            voice_path_config = self.config.get("voice_path", str(plugin_data_path / "voices/"))
            self.keywords = self.config.get("keywords", ["语音"])
        else:
            # 如果 config 不是字典形式，使用默认值
            voice_path_config = str(Path(str(base_path)) / "plugin_data" / "kiang" / "voices/")
            self.keywords = ["语音"]
            
        self.voice_path = Path(voice_path_config)
        self.data_store = VoiceDataStore(self.voice_path)
        self.voice = self.data_store.voice

        logger.info(f"voice_path: {self.voice_path}")
        logger.info(f"loaded voice items: {self.voice.items}")
        logger.info(f"keywords: {self.keywords}")

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_keyword_detect(self, event: AstrMessageEvent):
        message_text = event.message_str or ""
        if not message_text:
            return

        # 检查是否包含关键词
        if self._match_keywords(message_text, self.keywords):
            # 从语音数据存储中随机选择一个语音
            if self.voice.items:
                selected_voice = random.choice(self.voice.items)
                
                # 尝试不同的音频格式
                audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg']
                found_file = False
                voice_file_path = None
                
                for ext in audio_extensions:
                    voice_file_path = self.voice.dir / f"{selected_voice}{ext}"
                    if voice_file_path.exists():
                        found_file = True
                        break
                
                # 检查语音文件是否存在
                if found_file and voice_file_path:
                    # 创建包含语音文件的消息链，只发送语音，不发送文本
                    chain = [
                        Record.fromFileSystem(str(voice_file_path))
                    ]
                else:
                    # 如果语音文件不存在，则只发送文本
                    chain = [
                        Plain(f"找不到语音文件: {selected_voice}")
                    ]
                
                yield event.chain_result(chain)
                event.stop_event()

    @staticmethod
    def _match_keywords(text: str, keywords) -> bool:
        for keyword in keywords:
            if keyword in text:
                return True
        return False

    async def terminate(self):
        logger.info("[kiang] plugin terminated")