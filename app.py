import click

from resources.app_dataclass import Options
from resources.app_simulation import Simulation
from resources.app_logger import logger


@click.command()
@click.option('--path-name', required=True, help='A path to your video source on which objects will be detected')
@click.option('--show-coordinates', default='False', help='The app will write into each frame coordinates of detected objects.')
@click.option('--show-contours', default='False', help='The app will write into each frame contours outline of detected objects.')
@click.option('--show-info', default='False', help='The app will write into each frame information about tracked and detected objects.')
@click.option('--show-path', default='False', help='The app will write into each frame followed path of each object.')
@click.option('--show-whole-path', default='False', help='The app will write into each frame followed path of each object across the whole time when they have been detected.')
@click.option('--show-realtime', default='False', help='The app will prompt frames to a visible window.')
@click.option('--save-as-video', default='output.mp4', help='The app will save the output video into a source video path under this name.')
@click.option('--save-as-codec', default='mp4v', help='The app will save the output video with created by this codec.')
def main(
    path_name, show_coordinates, show_contours, show_info,
    show_path, show_realtime, save_as_video, save_as_codec,
    show_whole_path
    ) -> None:
    """Retrieving main informations."""
    logger.info('App is starting...')
    
    options = Options(
        path_name, show_coordinates, show_contours, show_info,
        show_path, show_realtime, save_as_video, save_as_codec,
        show_whole_path
    )
    
    simulation = Simulation(options)
    simulation.run()

    logger.info('App is closing now...')

    return


if __name__ == '__main__':
    main()  
    ...
