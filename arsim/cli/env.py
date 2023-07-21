from .py import Module
from ..utils.logger import logger

def create_scene_from_pyfile(file_path: str):
    from ..scene import Scene

    module = Module.from_file(file_path)
    data_cls = module["SoSData"]
    if data_cls is None:
        logger.error(f"在文件 {file_path} 中无法找到 SoSData 类")
        raise RuntimeError(f"在文件 {file_path} 中无法找到 SoSData 类")
    data = data_cls()
    logger.info("实例化 SoSData 类")

    map = data.create_map()
    logger.info("成功创建地图")
    aircrafts = data.create_aircraft()
    logger.info("成功创建航空器")
    sc = Scene(
        aircrafts, map, [], on_subtask_finish=lambda _: data.on_subtask_finish()
    )
    logger.info("成功创建场景")
    data.api._scene = sc

    data.on_init()
    logger.info("执行 SoSData.on_init() 方法")

    return sc