from pathlib import Path

import astrbot.api.message_components as Comp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, StarTools
from astrbot.api.star import register
import os
from astrbot.core.config import AstrBotConfig
from astrbot.core.utils.astrbot_path import get_astrbot_plugin_path

@register("Kiang", "czqwq", "Kiang!", "1.0.0")
class Kiang(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.name = "astrbot_plugin_kiang"
        self.config = config
        self.commands = self.config.get("commands", "kiang")
        self.base_dir: Path = StarTools.get_data_dir("astrbot_kiang")
        self.audio = self.config.get("audio","Kiang.wav")

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    @filter.command("kiang")
    async def kiang(self, event: AstrMessageEvent):
        if "kiang" not in self.commands:
          return

        chain = [
        Comp.Record(file=str(self.audio))
        ]
        yield event.chain_result(chain)


    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""