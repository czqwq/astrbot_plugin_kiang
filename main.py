import random
from pathlib import Path

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register
from astrbot.core import AstrBotConfig
from astrbot.core.message.components import Plain, Record

from .datastore import VoiceDataStore


@register("kiang", "czqwq", "语音回复插件", "1.0.1")
class Kiang(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

        # 初始化语音数据存储
        self.voice_path = Path(self.config.get("voice_path", "data/voices/"))
        self.data_store = VoiceDataStore(self.voice_path)
        self.voice = self.data_store.voice

        logger.info(f"voice_path: {self.voice_path}")
        logger.info(f"loaded voice items: {self.voice.items}")

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        message_text = event.message_str or ""
        if not message_text:
            return

        # 简单的关键词检测，如果有"语音"关键词就播放随机语音
        if "语音" in message_text:
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
                    # 创建包含语音文件的消息链
                    chain = [
                        Record.fromFileSystem(str(voice_file_path)),
                        Plain(f"播放语音: {selected_voice}")
                    ]
                else:
                    # 如果语音文件不存在，则只发送文本
                    chain = [
                        Plain(f"找不到语音文件: {selected_voice}")
                    ]
                
                yield event.chain_result(chain)
                event.stop_event()

    async def terminate(self):
        logger.info("[kiang] plugin terminated")