import bake
import tailer
import subprocess
import os

import logging
logger = logging.getLogger(__name__)


class RenderCommandError(Exception):
    pass


class RenderProgressError(Exception):
    pass


class RenderWorker():
    def __init__(self, ffmpeg='ffmpeg', progressfilename='progress.txt', codecname='libx264', codecflag='-crf 18 -preset slow'):
        ''' @ffmpeg: ffmpeg location
            @progressfilename: temp progress file name, will be deleted after rendering
            @codecname: default codec you want to use
            @codecflag: default codec flag you want to use
        '''
        self.ffmpeg = ffmpeg
        self.progressfilename = progressfilename
        self.codecname = codecname
        self.codecflag = codecflag

    def status(self):
        try:
            with open(self.progressfilename, 'r') as f:
                finaloutput = tailer.tail(f, lines=11)  # 11 is the output lines of worker.
                return str(finaloutput)
        except IOError:
            return 'File Doesn\'t Exist'

    def _render(self, render_command):
        ''' directly execute a ffmpeg command, ignore settings in global settings. '''
        if not render_command:
            logger.warning('Empty ffmpeg render command')
        else:
            # Step 2. Call subprocess to process this command.
            logger.info('Try to execute command: %s' % render_command)
            try:
                returncode = subprocess.call(render_command, shell=True)
                if returncode > 0:
                    raise RenderProgressError('Command %s failed. Exit code %d' % (render_command, returncode))
            except:
                logger.error('Command %s failed. Exit code %d' % (render_command, returncode))
                raise RenderProgressError('Command %s failed. Exit code %d' % (render_command, returncode))

    def render(self, cake, resultfilename=None):
        # Step 1. Generate a SH command.
        if not resultfilename:
            resultfilename = '%s.mp4' % cake['uid']

        render_command = ''
        try:
            render_command = bake.generate_cake_render_command(cake, resultfilename, self.codecname,
                                                               self.codecflag, self.ffmpeg, self.progressfilename)
        except:
            logger.error('Cake %s cannot be converted to a ffmpeg command' % cake['uid'])
            raise RenderCommandError('cake %s cannot be converted to a ffmpeg command' % cake['uid'])

        self._render(render_command)

    def clean_log(self):
        logger.info('Try to delete progress file name %s' % self.progressfilename)
        os.remove(self.progressfilename)
