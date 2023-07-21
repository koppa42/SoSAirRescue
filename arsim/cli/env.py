from .py import Module

def create_scene_from_pyfile(file_path: str):
    from ..scene import Scene

    module = Module.from_file(file_path)
    data_cls = module["SoSData"]
    if data_cls is None:
        raise RuntimeError(f"在文件 {file_path} 中无法找到 SoSData 类")
    data = data_cls()

    map = data.create_map()
    aircrafts = data.create_aircraft()
    sc = Scene(
        aircrafts, map, [], on_subtask_finish=lambda _: data.on_subtask_finish()
    )
    data.api._scene = sc

    data.on_init()

    return sc