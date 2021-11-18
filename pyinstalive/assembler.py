import os
import shutil
import re
import glob
import subprocess
import json

from . import globals
from . import logger
from . import helpers
from .download import Download
"""
The content of this file was originally written by https://github.com/taengstagram
The code has been edited for use in PyInstaLive.
"""


def _get_file_index(filename):
    """ Extract the numbered index in filename for sorting """
    mobj = re.match(r'.+\-(?P<idx>[0-9]+)\.[a-z]+', filename)
    if mobj:
        return int(mobj.group('idx'))
    return -1


def assemble(retry_with_zero_m4v=False):
    try:
        logger.info('Assembling segments into video file.')
        livestream_info = {}
        if globals.args.generate_video_path:
            globals.download = Download()
            globals.download.segments_path = globals.args.generate_video_path if not globals.args.generate_video_path.endswith(".json") else globals.args.generate_video_path.replace(".json", "")
            globals.download.data_json_path = globals.args.generate_video_path if globals.args.generate_video_path.endswith(".json") else globals.args.generate_video_path + ".json"
            globals.download.video_path = globals.download.segments_path + ".mp4"

        if not os.path.isdir(globals.download.segments_path):
            logger.separator()
            logger.error("Could not assemble segments: The segment directory does not exist.")
            return
        elif not os.listdir(globals.download.segments_path):
            logger.separator()
            logger.error("Could not assemble segments: The segment directory does not contain any files.")
            return
        
        if not os.path.isfile(globals.download.data_json_path):
            logger.warn("No matching JSON file found for the segment directory, trying to continue without it.")
            ass_stream_id = os.listdir(globals.download.segments_path)[0].split('-')[0]
            livestream_info['id'] = ass_stream_id
            livestream_info['broadcast_status'] = "active"
            livestream_info['segments'] = {}
        else:
            with open(globals.download.data_json_path) as info_file:
                try:
                    livestream_info = json.load(info_file)
                except Exception as e:
                    logger.warn("Could not load JSON file, trying to continue without it.")
                    ass_stream_id = os.listdir(globals.download.segments_path)[0].split('-')[0]
                    livestream_info['id'] = ass_stream_id
                    livestream_info['broadcast_status'] = "active"
                    livestream_info['segments'] = {}

        stream_id = str(livestream_info['id'])

        segment_meta = livestream_info.get('segments', {})
        if segment_meta:
            all_segments = [
                os.path.join(globals.download.segments_path, k)
                for k in livestream_info['segments'].keys()]
        else:
            all_segments = list(filter(
                os.path.isfile,
                glob.glob(os.path.join(globals.download.segments_path, '%s-*.m4v' % stream_id))))

        all_segments = sorted(all_segments, key=lambda x: _get_file_index(x))
        sources = []
        audio_stream_format = 'assembled_source_{0}_{1}_mp4.tmp'
        video_stream_format = 'assembled_source_{0}_{1}_m4a.tmp'
        video_stream = ''
        audio_stream = ''
        has_skipped_zero_m4v = False

        if not all_segments:
            logger.error("Could not assemble segments: No files were loaded.")
            return

        for segment in all_segments:
            segment = re.sub('\?.*$', '', segment)
            if not os.path.isfile(segment.replace('.m4v', '.m4a')):
                logger.warn('Audio segment not found: {0!s}'.format(segment.replace('.m4v', '.m4a')))
                continue

            if segment.endswith('-init.m4v'):
                logger.info('Replacing %s' % segment)
                segment = os.path.join(
                    os.path.dirname(os.path.realpath(__file__)), 'repair', 'init.m4v')

            if segment.endswith('-0.m4v') and not retry_with_zero_m4v:
                has_skipped_zero_m4v = True
                continue

            video_stream = os.path.join(
                globals.download.segments_path, video_stream_format.format(stream_id, len(sources)))
            audio_stream = os.path.join(
                globals.download.segments_path, audio_stream_format.format(stream_id, len(sources)))


            file_mode = 'ab'

            with open(video_stream, file_mode) as outfile, open(segment, 'rb') as readfile:
                shutil.copyfileobj(readfile, outfile)

            with open(audio_stream, file_mode) as outfile, open(segment.replace('.m4v', '.m4a'), 'rb') as readfile:
                shutil.copyfileobj(readfile, outfile)

        if audio_stream and video_stream:
            sources.append({'video': video_stream, 'audio': audio_stream})

        for n, source in enumerate(sources):
            ffmpeg_binary = os.getenv('FFMPEG_BINARY', 'ffmpeg')
            cmd = [
                ffmpeg_binary, '-loglevel', 'error', '-y',
                '-i', source['audio'],
                '-i', source['video'],
                '-c:v', 'copy', '-c:a', 'copy', globals.download.video_path]
            #fnull = open(os.devnull, 'w')
            fnull = None
            exit_code = subprocess.call(cmd, stdout=fnull, stderr=subprocess.STDOUT)
            if exit_code != 0:
                logger.warn("FFmpeg exit code not '0' but '{:d}'.".format(exit_code))
                if has_skipped_zero_m4v and not retry_with_zero_m4v:
                    logger.binfo("*-0.m4v segment was detected but skipped, retrying to assemble video without "
                                 "skipping it.")
                    os.remove(source['audio'])
                    os.remove(source['video'])
                    assemble(retry_with_zero_m4v=True)
                    
            else:
                os.remove(source['audio'])
                os.remove(source['video'])
                logger.info('Successfully saved video file: %s' % os.path.basename(globals.download.video_path))
    except ValueError as e:
        logger.error('Could not assemble segment files: {:s}'.format(str(e)))
        if os.listdir(globals.download.segments_path):
            logger.binfo("Segment directory is not empty. Trying to assemble again.")
            assemble()
        else:
            logger.error("Segment directory is empty. There is nothing to assemble.")
    except Exception as e:
        logger.error('Could not assemble segment files: {:s}'.format(str(e)))