import sys
from math import dist
from typing import Tuple, List, Dict, Union
from pathlib import Path

import cv2 as cv

from resources.app_dataclass import Options, ObjectInfo
from resources.app_logger import logger
from resources.app_utils import get_center_coordinates_and_area


class Simulation:
    def __init__(self, options: Options) -> None:
        self.options: Options = options
        self.video_path_input: str = str(Path(options.path_name).resolve())
        self.video_path_output: str = str(Path(options.path_name).with_name(options.save_as_video).resolve()) 
        self.video_codec_output = cv.VideoWriter_fourcc(*options.save_as_codec)
        self.video_width: int = -1
        self.video_height: int = -1
        self.video_fps: int = -1
        self.video_frames: int = -1
        self.history_objects: Dict = {} 
        self.current_objects_count: int = -1
        return
    
    @property
    def get_resolution(self) -> Tuple[int, int]:
        return self.video_width, self.video_height
    
    def get_objects(self, frame) -> List:
        """This function will return all founded shape.
        Process:
            * The frame is turned into gray scale color
            * The frame is "cleaned" by Morphological Transformations
            * Each object has a different color there for we need to ideally retrive frames 
            with each of them individually. But because almost each object has a different
            color at the border and at the center, even after "cleaning part", we need to take that into a consideration. 
            What is being done here is retriving only color objects in a specific range of color. 
            That way we can extract the most of the individual objects.
              * That is important because in some moments objects collide together which resolves in a creation of one big object.
            * Each specific range is being turned into binary image (white, black)
            * Each binary image is put through function which retrieves contours (detected objects in a frame).
            
        Args:
            frame: Matrice of points

        Returns:
            List: All founded contours
        """
        
        contours_all: List = []
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        
        morph_kernel = cv.getStructuringElement(cv.MORPH_RECT, (3,3))
        morph_open = cv.morphologyEx(frame_gray, cv.MORPH_OPEN, morph_kernel)
        morph_closed = cv.morphologyEx(morph_open, cv.MORPH_CLOSE, morph_kernel)
        
        color_overlay = 15  # observed value which works nicely
        for min_shade in range(3, 300, step := 50):  # step by 50 of shade results in great detection
            mask_lower = (calc_min  if (calc_min := min_shade - color_overlay) >= 0 else min_shade)
            mask_upper = (min_shade * step + step + color_overlay)
            mask = cv.inRange(morph_closed, mask_lower, mask_upper)
            
            ret, thresh = cv.threshold(mask, min_shade, 255, cv.THRESH_BINARY)
            contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            contours_all += contours
            ...
        
        return contours_all
    
    def validate_contours(self, contours: List) -> List:
        """Now when we have all our contours in a frame, it is needed to deduplicate them.
            * First all contours with smaller area than specified area will be dropped. 
            It is duo a collision when one object is splitted into 3 peaces and it would have been wrong detection.
            Also some noice is still present in those frames resulting small contours, which are nothing but a mess.            

        Args:
            contours (List): detected contours

        Returns:
            List: Validated contours
        """
        contours_center: List[Union[Tuple[int, int, float]]] = []
        contours_validated: List = []
        
        for contour in contours:
            
            contour_x, contour_y, contour_area = get_center_coordinates_and_area(contour)
            contour_center: Tuple[int, int, float] = (contour_x, contour_y, contour_area)
            
            if contour_area < 150:
                continue
            
            already_in: bool = False
            for center_object in contours_center:
                # Compare only about the same size contour's area
                if not(center_object[2] * .9 < contour_center[2] < center_object[2] * 1.1):
                    continue
                # If the area is almost same and center point aswell mark as duplication
                if center_object[0] * .99 < contour_center[0] < center_object[0] * 1.01:
                    already_in = True
                if center_object[1] * .99 < contour_center[1] < center_object[1] * 1.01:
                    already_in = True
                ...
            
            # Duplications are dropped out
            if already_in:
                continue
            
            contours_center.append(contour_center)
            contours_validated.append(contour)
            
            ...
            
        return contours_validated
    
    def resolve_collision_contours(self, frame, contours: List) -> List:
        """Since we have our contours validated, we still need to check and resolve
        if some contour is not just a concatenation of two small contours.
        * It is done by checking if a max distance between contour center and contour points is smaller
        than a distance between two others contour's center distances, which mean these two countours are in reach.
        * Once we have two contours in reach we add up their areas and compare it with original contour, if it
        fits than the original contour is a concatenation of these two contours.  

        Args:
            frame (_type_): Original frame
            contours (List): Validated contours

        Returns:
            List: Resolved contours
        """
        
        resolved_contours: List = []
        
        for orig_idx, contour in enumerate(contours):
            
            contour_x, contour_y, contour_area = get_center_coordinates_and_area(contour)
            contour_coords: Tuple[int, int] = (contour_x, contour_y)
            
            max_inner_distance: float = max([dist(point[0], contour_coords) for point in contour])

            skip_centour: bool = False
            
            for first_idx, tmp_contour in enumerate(contours):
                # Do not compare original contour with itself
                if orig_idx == first_idx:
                    continue
                
                tmp_contour_x, tmp_contour_y, tmp_contour_area = get_center_coordinates_and_area(tmp_contour)                
                tmp_dist = dist((tmp_contour_x, tmp_contour_y), contour_coords)
                
                if tmp_dist > max_inner_distance:
                    continue
                
                for second_idx, tmp_contour_2 in enumerate(contours):
                    # Do not compare original contour with itself and the first other contour
                    if orig_idx == second_idx or first_idx == second_idx:
                        continue
                    
                    tmp_contour_x_2, tmp_contour_y_2, tmp_contour_area_2 = get_center_coordinates_and_area(tmp_contour_2)   
                    tmp_dist_2 = dist((tmp_contour_x_2, tmp_contour_y_2), contour_coords)
                                 
                    if tmp_dist_2 > max_inner_distance:
                        continue

                    skip_centour = (tmp_contour_area_2 + tmp_contour_area) * .9 < contour_area
                    
                    break
                    ...
                    
                if skip_centour:
                    break
                ...
            
            if skip_centour:
                continue
            
            resolved_contours.append(contour)
            ...
        
        return resolved_contours
    
    def get_contour_information(self, frame, contours: List) -> List[Union[ObjectInfo]]:
        """Obtain information about objects from contours.

        Args:
            frame (_type_): Original frame
            contours (List): Objects contours

        Returns:
            List: Objects information
        """
        
        current_objects: List[Union[ObjectInfo]] = []
        
        for _, contour in enumerate(contours):
            contour_x, contour_y, contor_area = get_center_coordinates_and_area(contour)

            object_info = ObjectInfo(
                position=(contour_x, contour_y),
                color=[int(color_channel) for color_channel in frame[contour_y, contour_x]],
                contour=contour,
                area=contor_area,
                steps=[],
                remove_step=False
            )
            
            current_objects.append(object_info)
            ...
            
        return current_objects
    
    def track(self, contours_info: List[Union[ObjectInfo]]) -> None:
        """Save founded object into a history

        Args:
            contours_info (List[Union[ObjectInfo]]): List of founded objects
        """
        
        self.current_objects_count: int = len(contours_info)
        
        for current_object in contours_info:
            in_history = None
            for key, history_object in self.history_objects.items():
                if (current_object.position[0] - self.video_width * .1 < history_object.position[0] < current_object.position[0] + self.video_width * .1) \
                    and (current_object.position[1] - self.video_height * .1 < history_object.position[1] < current_object.position[1] + self.video_height * .1) \
                    and (current_object.area * .1 < history_object.area < current_object.area * 10) \
                    and (current_object.color[0] - 50 < history_object.color[0] < current_object.color[0] + 50) \
                    and (current_object.color[1] - 50 < history_object.color[1] < current_object.color[1] + 50) \
                    and (current_object.color[2] - 50 < history_object.color[2] < current_object.color[2] + 50):                    
                    
                    in_history = key
                    break
                    ...
                ...
                
            if in_history is not None:
                self.history_objects[in_history].position = current_object.position
                self.history_objects[in_history].area = current_object.area
                self.history_objects[in_history].color = current_object.color
                self.history_objects[in_history].contour = current_object.contour
                self.history_objects[in_history].steps.append(self.history_objects[in_history].position)
                self.history_objects[in_history].remove_step = False
            else:
                self.history_objects[f'obj_{len(self.history_objects)}'] = current_object
            ...
        
        return
        
    
    def visualise(self, frame) -> None:
        """Visualise information

        Args:
            frame (_type_): Original frame
        """

        for _, history_object in enumerate(self.history_objects.values()):
            
            prev_point = None
            for point in history_object.steps:
                if prev_point is None:
                    prev_point = point
                    continue
                
                if self.options.show_path or self.options.show_whole_path:
                    cv.line(frame, point, prev_point, color=history_object.color, thickness=3)
                
                prev_point = point
                ...
                
            if self.options.show_contours and not history_object.remove_step:
                cv.drawContours(frame, [history_object.contour], -1, (17, 237, 74), 3)    
            if self.options.show_coordinates and not history_object.remove_step:
                cv.putText(frame, history_object.position_str, history_object.position, cv.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 2)
            if self.options.show_info:
                cv.circle(frame, (15 * (_ + 1), 65), 5, color=history_object.color, thickness=-1)
            
            
            line_color: Tuple[int, int, int] = (
                0 if history_object.remove_step else 255,
                0,
                255 if history_object.remove_step else 0
            )
            
            if not self.options.show_whole_path:
                history_object.steps = history_object.steps[-50:]
                
                if history_object.remove_step:
                    history_object.steps = history_object.steps[1:]
                ...
                
            if self.options.show_info:
                cv.line(frame, (15 * (_ + 1) - 5, 75), (15 * (_ + 1) + 5, 80), color=line_color, thickness=2)
                ...

            history_object.remove_step = True
            ...

        if self.options.show_info:
            cv.putText(frame, f'Num of current objects: {self.current_objects_count}', (10, 25), cv.FONT_HERSHEY_SIMPLEX, .5, (17, 237, 74), 2)
            cv.putText(frame, f'Num of history objects: {len(self.history_objects)}', (10, 50), cv.FONT_HERSHEY_SIMPLEX, .5, (17, 237, 74), 2)
            ...

        if self.options.show_realtime:
            cv.imshow('frame', frame)

        return
    
    def run(self) -> None:
        """Run the whole simulation
        * Detect objects
        * Filter them
        * Save/track them
        * Visualise them
        """
        
        cap = cv.VideoCapture(self.video_path_input)
        
        if not cap.isOpened():
            logger.exception('Cannot read the source video!')
            sys.exit(1)
        
        self.video_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        self.video_fps = int(cap.get(cv.CAP_PROP_FPS))
        self.video_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        out = cv.VideoWriter(self.video_path_output, self.video_codec_output, self.video_fps, self.get_resolution)
        
        if not out.isOpened():
            logger.exception('Cannot write into output video!')
            sys.exit(1)
        
        current_frame: int = -1
        while cap.isOpened() and out.isOpened():
            current_frame += 1
            
            logger.info(f'[Frame: {current_frame}/{self.video_frames}]')
            ret, frame = cap.read()
            
            if not ret:
                logger.info('No frame has been recieved. Exiting simulation!')
                break
            
            contours_raw: List = self.get_objects(frame)
            contours_validated: List = self.validate_contours(contours_raw)
            contours_resolved: List = self.resolve_collision_contours(frame, contours_validated)
            contours_info: List = self.get_contour_information(frame, contours_resolved)
            
            self.track(contours_info)
            self.visualise(frame)
        
            out.write(frame)
            if cv.waitKey(25 if self.options.show_realtime else 1) == ord('q'):
                break
            ...
        
        out.release()
        logger.info(f'Output video has been saved into: {self.video_path_output}')
        
        cap.release()
        cv.destroyAllWindows()
        
        return
    
    ...
