from typing import Optional

from .aircraft import Aircraft
from .map import Map
from .task import SubTask, Task

class Scene:
    def __init__(self, aircrafts: list[Aircraft], map: Map, tasks: list[Task]) -> None:
        self.aircrafts: list[Aircraft] = aircrafts
        self.map: Map = map
        self.tasks: list[Task] = tasks

        self.setup_env()

    def setup_env(self) -> None:
        # 建立任务执行环境
        self.aircraft_to_subtask: dict[Aircraft, Optional[SubTask]] = {}
        for ac in self.aircrafts:
            self.aircraft_to_subtask[ac] = None
