from typing import Optional, Unpack

from .aircraft import Aircraft
from .map import Map, Position
from .task import SubTask, Task, TaskType, SubTaskParams
from .examples import positions as epos


class AircraftAlreadyHasSubTask(Exception):
    def __init__(self, aircraft: Aircraft) -> None:
        super().__init__(f"Aircraft {aircraft.name} already has a subtask")
        self.aircraft = aircraft


class Scene:
    def __init__(self, aircrafts: list[Aircraft], map: Map, tasks: list[Task]) -> None:
        self.aircrafts: list[Aircraft] = aircrafts
        self.map: Map = map
        self.tasks: list[Task] = tasks
        self.now: int = 0

        self.aircraft_to_subtask: dict[Aircraft, Optional[SubTask]] = {}
        self.aircraft_subtask_queue: dict[Aircraft, list[SubTask]] = {}

        self.setup_env()

    def setup_env(self) -> None:
        # 建立任务执行环境
        for ac in self.aircrafts:
            self.aircraft_to_subtask[ac] = None

        # 航空器子任务队列
        for ac in self.aircrafts:
            self.aircraft_subtask_queue[ac] = []

    def check_parallel_subtask(self, aircraft: Aircraft, subtask: SubTask) -> bool:
        # 获取在同一地点执行任务的航空器
        # 检查作业空间
        tmp = [
            ac
            for ac, sub in self.aircraft_to_subtask.items()
            if sub is not None
            and sub.position == subtask.position
            and ac.type == aircraft.type
        ]

        if subtask.type in SubTask._LAND_SUBTASK:
            sum_area = sum([ac.rotor_area for ac in tmp]) + aircraft.rotor_area
            if aircraft.type == "FixedWing":
                if sum_area > subtask.position.fixed_area:
                    return False
            elif aircraft.type == "Helicopter":
                if sum_area > subtask.position.helicopter_area:
                    return False
        elif subtask.type in SubTask._AIR_SUBTASK:
            sum_area = sum([ac.air_area for ac in tmp]) + aircraft.air_area
            if sum_area > subtask.position.air_work_area:
                return False

        return True

    def set_subtask(
        self,
        s_type: TaskType,
        aircraft: Aircraft,
        position: Position,
        **addition: Unpack[SubTaskParams],
    ) -> None:
        # 设置子任务
        if self.aircraft_to_subtask[aircraft] is not None:
            raise AircraftAlreadyHasSubTask(aircraft)
        tmp_subtask = SubTask(self, s_type, aircraft, position, **addition)
        if not self.check_parallel_subtask(aircraft, tmp_subtask):
            raise
        self.aircraft_to_subtask[aircraft] = tmp_subtask

    def find_minuim_subtask(self) -> tuple[Aircraft, SubTask]:
        ...

    def run(self) -> None:
        task = self.find_minuim_subtask()
