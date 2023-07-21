from typing import Optional, Unpack, Literal, Union
from math import isclose

from .aircraft import Aircraft
from .map import Map, Position
from .task import SubTask, Task, TaskType, SubTaskParams
from .examples import positions as epos
from .utils.logger import logger


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
    MAX_RESCUE_TIME: float = 3600 * 24 * 3

    def __init__(self, aircrafts: list[Aircraft], map: Map, tasks: list[Task]) -> None:
        self.aircrafts: list[Aircraft] = aircrafts
        self.map: Map = map
        self.tasks: list[Task] = tasks
        self.now_time: float = 0

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

        logger.info("成功建立任务执行环境")

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

    def is_subtask_queue_empty(self) -> bool:
        """子任务队列是否为空

        Returns:
            bool: 是否为空
        """
        for _, v in self.aircraft_subtask_queue.items():
            if len(v) != 0:
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
            logger.error(f"航空器 {aircraft.name} 已经在执行子任务")
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
            logger.error(f"航空器 {aircraft.name} 无法进行子任务 {tmp_subtask}")
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
            logger.error(f"航空器 {aircraft.name} 已经在执行子任务")
            raise AircraftAlreadyHasSubtask(aircraft)
        tmp_subtask = SubTask(self, s_type, aircraft, position, **addition)
        self.aircraft_subtask_queue[aircraft].append(tmp_subtask)

        logger.info(f"航空器 {aircraft.name} 添加子任务 {tmp_subtask.type}")

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
        for _, st in self.aircraft_to_subtask.items():
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

        logger.info(f"找到 {mimimum[0]} 最小时间片 {mimimum[1].type}, 用时 {mimimum[2]}")
        return mimimum[0], mimimum[1]

    def update_subtask_time(self, time: float, ex: SubTask) -> None:
        if not ex.is_arrived:
            ex.move_process += time * ex.aircraft.cruising_speed / ex.distance
            if ex.is_arrived:
                ex.aircraft.now_position = ex.position
                logger.info(f'[{self.now_time}] 航空器 {ex.aircraft.name} 到达地点 {ex.position.name}')
        else:
            ex.task_process += time / ex.consume_time_raw
            if ex.is_finished:
                ex.on_finish()
                logger.info(f'[{self.now_time}] 航空器 {ex.aircraft.name} 完成 {ex.type} 任务')

    def run(self) -> None:
        while (
            self.now_time <= Scene.MAX_RESCUE_TIME and not self.is_subtask_queue_empty()
        ):
            # 得到最小时间片
            minimum = self.find_minimum_timespan()
            if minimum is None:
                logger.error("无法找到最小时间片")
                raise RuntimeError("无法找到最小时间片")

            # 获取时间片需要时间，并完成该最小时间片
            minimum_consume_time: float = 0
            if minimum[0] == "Move":
                minimum_consume_time = minimum[1].move_time
                minimum[1].move_process = 1
                minimum[1].aircraft.now_position = minimum[1].position
            elif minimum[0] == "Subtask":
                minimum_consume_time = minimum[1].consume_time
                minimum[1].task_process = 1
                minimum[1].on_finish()
                logger.info(f'[{self.now_time}] 航空器 {minimum[1].aircraft.name} 完成 {minimum[1].type} 任务')

            # 更新时间，
            self.now_time += minimum_consume_time
            # 完成其他子任务
            for st in self.aircraft_to_subtask.values():
                if st is not None and st is not minimum[1]:
                    self.update_subtask_time(minimum_consume_time, st)

            # 去除完成的子任务，设置新的子任务
            for ac in self.aircraft_to_subtask:
                now_st = self.aircraft_to_subtask[ac]
                if now_st is None:
                    continue
                if now_st.is_finished:
                    # 判断下一个进行的子任务是否需要加油
                    next_st = (
                        self.aircraft_subtask_queue[ac][0]
                        if len(self.aircraft_subtask_queue[ac]) > 0
                        else None
                    )
                    if next_st is None:
                        self.aircraft_to_subtask[ac] = None
                        continue
                    if isinstance(ac.now_position, epos.Airport) and (
                        not next_st.is_fueled
                    ):
                        # 需要加油
                        tmp_st = SubTask(self, "加油保障", ac, ac.now_position)
                        tmp_st.setup()
                        self.aircraft_to_subtask[ac] = tmp_st
                        next_st.is_fueled = True
                    else:
                        tmp_st = self.aircraft_subtask_queue[ac].pop(0)
                        tmp_st.setup()
                        self.aircraft_to_subtask[ac] = tmp_st
                        logger.info(f'[{self.now_time}] 航空器 {ac.name} 开始执行 {tmp_st.type} 任务')
