from .scene import Scene
from .examples import positions as epos
from .examples import aircrafts as eac
from .map import Map
from .task import Task, SubTask


# type: ignore
class SoSAPI:
    def __init__(self) -> None:
        self.scene = Scene
        self.position = epos
        self.aircraft = eac
        self.map = Map
        # self.task = Task
        # self.subtask = SubTask

    def add_task(self, t_type, position, /, on_finished=None) -> None:
        self._scene.tasks.append(Task(self._scene, t_type, position, on_finished))  # type: ignore

    def add_subtask(self, task_type, aircraft, position, **kwargs):
        self._scene.add_subtask(SubTask(self._scene, task_type, aircraft, position, **kwargs))  # type: ignore
