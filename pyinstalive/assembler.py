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
        ass_mp4_file = os.path.join(pil.dl_path, os.path.basename(pil.assemble_arg).replace("_downloads", "") + ".mp4")
        broadcast_info = {}
        if not os.listdir(pil.assemble_arg):
            logger.error('The segment directory does not exist or does not contain any files: %s' % pil.assemble_arg)
            logger.separator()
            return

        ass_stream_id = os.listdir(pil.assemble_arg)[0].split('-')[0]
        broadcast_info['id'] = ass_stream_id
        broadcast_info['broadcast_status'] = "active"
        broadcast_info['segments'] = {}

        stream_id = str(broadcast_info['id'])

        segment_meta = broadcast_info.get('segments', {})
        if segment_meta:
            all_segments = [
                os.path.join(pil.assemble_arg, k)
                for k in broadcast_info['segments'].keys()]
        else:
            all_segments = list(filter(
                os.path.isfile,
                glob.glob(os.path.join(pil.assemble_arg, '%s-*.m4v' % stream_id))))

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
                pil.assemble_arg, video_stream_format.format(stream_id, len(sources)))
            audio_stream = os.path.join(
                pil.assemble_arg, audio_stream_format.format(stream_id, len(sources)))


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
                ffmpeg_binary, '-loglevel', 'quiet', '-y',
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
                logger.separator()
                logger.info('Saved video: %s' % os.path.basename(ass_mp4_file))
                logger.separator()
                os.remove(source['audio'])
                os.remove(source['video'])
            if user_called:
                logger.separator()
    except Exception as e:
        logger.error("An error occurred: {:s}".format(str(e)))
