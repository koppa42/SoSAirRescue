from typing import Optional, Unpack, Literal, Union
from math import isclose

from .aircraft import Aircraft
from .map import Map, Position
from .task import SubTask, Task, TaskType, SubTaskParams
from .examples import positions as epos


class AircraftAlreadyHasSubtask(Exception):
    def __init__(self, aircraft: Aircraft) -> None:
        super().__init__(f"航空器 {aircraft.name} 已经在执行子任务")
        self.aircraft = aircraft


class ParallelSubtaskException(Exception):
    def __init__(self, aircraft: Aircraft, subtask: SubTask) -> None:
        super().__init__(f"航空器 {aircraft.name} 无法进行子任务 {subtask}")
        self.aircraft = aircraft
        self.subtask = subtask


TimespanType = Literal["Move", "Subtask"]


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
        aircraft: Aircraft,
    ) -> bool:
        """设置航空器要执行的任务

        Args:
            aircraft (Aircraft): 要设置的航空器

        Raises:
            AircraftAlreadyHasSubtask: 当前航空已经在执行子任务

        Returns:
            bool: true 表示设置成功，false 任务队列为空
        """
        # # 设置子任务
        # if self.aircraft_to_subtask[aircraft] is not None:
        #     raise AircraftAlreadyHasSubtask(aircraft)
        # tmp_subtask = SubTask(self, s_type, aircraft, position, **addition)
        # if not self.check_parallel_subtask(aircraft, tmp_subtask):
        #     raise ParallelSubtaskException(aircraft, tmp_subtask)
        # self.aircraft_to_subtask[aircraft] = tmp_subtask
        if self.aircraft_to_subtask[aircraft] is not None:
            raise AircraftAlreadyHasSubtask(aircraft)
        tmp_subtask = (
            self.aircraft_subtask_queue[aircraft][0]
            if len(self.aircraft_subtask_queue[aircraft]) > 0
            else None
        )
        if tmp_subtask is None:
            return False
        if (not tmp_subtask.is_fueled) and isinstance(
            aircraft.now_position, epos.Airport
        ):
            tmp_subtask = SubTask(self, "加油保障", aircraft, aircraft.now_position)
        if not self.check_parallel_subtask(aircraft, tmp_subtask):
            raise ParallelSubtaskException(aircraft, tmp_subtask)
        return True

    def add_subtask(
        self,
        s_type: TaskType,
        aircraft: Aircraft,
        position: Position,
        **addition: Unpack[SubTaskParams],
    ) -> None:
        # 添加子任务
        if self.aircraft_to_subtask[aircraft] is not None:
            raise AircraftAlreadyHasSubtask(aircraft)
        tmp_subtask = SubTask(self, s_type, aircraft, position, **addition)
        self.aircraft_subtask_queue[aircraft].append(tmp_subtask)

    def find_minimum_subtask(self) -> Optional[SubTask]:
        minimum: Optional[tuple[SubTask, float]] = None

        for _, st in self.aircraft_to_subtask.items():
            if st is not None:
                if minimum is None:
                    minimum = (st, st.consume_time)
                else:
                    if st.consume_time < minimum[1]:
                        minimum = (st, st.consume_time)
        if minimum is None:
            return None
        else:
            return minimum[0]

    def find_minimum_timespan(self) -> Optional[tuple[TimespanType, SubTask]]:
        mimimum: Optional[tuple[TimespanType, SubTask, float]] = None
        for ac, st in self.aircraft_to_subtask.items():
            if st is not None:
                if mimimum is None:
                    # 已经到达
                    if st.is_arrived:
                        mimimum = ("Subtask", st, st.consume_time)
                    else:
                        mimimum = ("Move", st, st.move_time)
                else:
                    if st.is_arrived:
                        if st.consume_time < mimimum[2]:
                            mimimum = ("Subtask", st, st.consume_time)
                    else:
                        if st.move_time < mimimum[2]:
                            mimimum = ("Move", st, st.move_time)
        if mimimum is None:
            return None
        return mimimum[0], mimimum[1]

    def run(self) -> None:
        task = self.find_minimum_subtask()
