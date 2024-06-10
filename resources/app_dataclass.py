from typing import Tuple, List, Union
from dataclasses import dataclass


@dataclass
class Options:
    path_name: str
    show_coordinates: bool
    show_contours: bool
    show_info: bool
    show_path: bool
    show_realtime: bool
    save_as_video: str
    save_as_codec: str
    show_whole_path: str
    
    def __init__(
        self, path_name, show_coordinates, show_contours, show_info, show_path,
        show_realtime, save_as_video, save_as_codec, show_whole_path
        ):
        self.path_name = path_name
        self.show_coordinates = show_coordinates.lower() == 'true'
        self.show_contours = show_contours.lower() == 'true' 
        self.show_info = show_info.lower() == 'true'
        self.show_path = show_path.lower() == 'true'
        self.show_whole_path = show_whole_path.lower() == 'true'
        self.show_realtime = show_realtime.lower() == 'true'
        self.save_as_video = save_as_video
        self.save_as_codec = save_as_codec
        ...
        
@dataclass
class ObjectInfo:
    position: Tuple[int, int]
    color: Tuple[int, int, int]
    contour: List
    area: float
    steps: List[Union[Tuple[int, int]]]
    remove_step: bool
    
    @property
    def position_str(self):
        return f'{self.position[0]}, {self.position[1]}'
    