import os
import shutil
import re
import glob
import subprocess
import json
import sys
try:
    import pil
    import logger
    import helpers
    from constants import Constants
except ImportError:
    from . import pil
    from . import logger
    from . import helpers
    from .constants import Constants

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


def assemble(user_called=True, retry_with_zero_m4v=False):
    try:
        ass_json_file = pil.assemble_arg if pil.assemble_arg.endswith(".json") else pil.assemble_arg + ".json"
        ass_mp4_file = os.path.join(pil.dl_path, os.path.basename(ass_json_file).replace("_downloads", "").replace(".json", ".mp4"))
        ass_segment_dir = pil.assemble_arg if not pil.assemble_arg.endswith(".json") else pil.assemble_arg.replace(".json", "")
        
        broadcast_info = {}
        if not os.path.isdir(ass_segment_dir) or not os.listdir(ass_segment_dir):
            logger.error('The segment directory does not exist or does not contain any files: %s' % ass_segment_dir)
            logger.separator()
            return
        if not os.path.isfile(ass_json_file):
            logger.warn("No matching json file found for the segment directory, trying to continue without it.")
            ass_stream_id = os.listdir(ass_segment_dir)[0].split('-')[0]
            broadcast_info['id'] = ass_stream_id
            broadcast_info['broadcast_status'] = "active"
            broadcast_info['segments'] = {}
        else:
            with open(ass_json_file) as info_file:
                try:
                    broadcast_info = json.load(info_file)
                except Exception as e:
                    logger.warn("Could not decode json file, trying to continue without it.")
                    ass_stream_id = os.listdir(ass_segment_dir)[0].split('-')[0]
                    broadcast_info['id'] = ass_stream_id
                    broadcast_info['broadcast_status'] = "active"
                    broadcast_info['segments'] = {}

        if broadcast_info.get('broadcast_status', '') == 'post_live':
            logger.error('Video segment files from replay downloads cannot be assembled.')
            return

        stream_id = str(broadcast_info['id'])

        segment_meta = broadcast_info.get('segments', {})
        if segment_meta:
            all_segments = [
                os.path.join(ass_segment_dir, k)
                for k in broadcast_info['segments'].keys()]
        else:
            all_segments = list(filter(
                os.path.isfile,
                glob.glob(os.path.join(ass_segment_dir, '%s-*.m4v' % stream_id))))

        all_segments = sorted(all_segments, key=lambda x: _get_file_index(x))
        sources = []
        audio_stream_format = 'assembled_source_{0}_{1}_mp4.tmp'
        video_stream_format = 'assembled_source_{0}_{1}_m4a.tmp'
        video_stream = ''
        audio_stream = ''
        has_skipped_zero_m4v = False

        if not all_segments:
            logger.error("No video segment files have been found in the specified folder.")
            logger.separator()
            return
        else:
            logger.info("Assembling video segment files from specified folder: {}".format(ass_segment_dir))

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
                ass_segment_dir, video_stream_format.format(stream_id, len(sources)))
            audio_stream = os.path.join(
                ass_segment_dir, audio_stream_format.format(stream_id, len(sources)))


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
                ffmpeg_binary, '-loglevel', 'warning', '-y',
                '-i', source['audio'],
                '-i', source['video'],
                '-c:v', 'copy', '-c:a', 'copy', ass_mp4_file]
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
                    logger.separator()
                    assemble(user_called, retry_with_zero_m4v=True)
                    return
            else:
                logger.info('The video file has been generated: %s' % os.path.basename(ass_mp4_file))
                os.remove(source['audio'])
                os.remove(source['video'])
            if user_called:
                logger.separator()
    except Exception as e:
        logger.error("An error occurred: {:s}".format(str(e)))
