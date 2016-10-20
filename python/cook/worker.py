from __future__ import division
import bake
import tailer
import subprocess
import os
import datetime

import logging
logger = logging.getLogger(__name__)


class RenderCommandError(Exception):
    pass


class RenderProgressError(Exception):
    pass


class ReportHandler():
    def __init__(self, name):
        self.name = name

    def report(self, messageobj):
        ''' To be implemented by the child class.'''
        pass


class RenderWorker():
    def __init__(self, ffmpeg='ffmpeg', codecname='libx264', codecflag='-crf 18 -preset slow'):
        ''' @ffmpeg: ffmpeg location
            @progressfilename: temp progress file name, will be deleted after rendering
            @codecname: default codec you want to use
            @codecflag: default codec flag you want to use
        '''
        self.ffmpeg = ffmpeg
        self.codecname = codecname
        self.codecflag = codecflag
        self.progressfilename = None
        self.is_render = False  # Flag of during rendering or not.
        self.failed = False  # Flag of the current job has failed or not.
        self.cake = None  # Hold the cake we want to render
        self.report_handlers = []  # Hold the handlers of type ReportHandler

    def worker_settings(self):
        return {'ffmpeg': self.ffmpeg, 'codecname': self.codecname, 'codecflag': self.codecflag}

    def is_rendering(self):
        return self.is_render

    def has_failed(self):
        return self.failed

    def get_cake(self):
        return self.cake  # Get the current cake that mounted on the worker.

    def add_handler(self, handler):
        ''' @handler : ReportHandler '''
        self.report_handlers.append(handler)

    def _report_progress(self, messageobj):
        for each_handler in self.report_handlers:
            each_handler.report(messageobj)

    def report_progress(self):
        ''' Show progress of ffmpeg rendering progress file. '''
        if self.progressfilename is None:
            self._report_progress({'error': 'Progress File Not Exist'})

        try:
            with open(self.progressfilename, 'r') as f:
                status_dict = {
                    'frame': None,
                    'fps': None,
                    'stream_0_0_q': None,
                    'bitrate': None,
                    'total_size': None,
                    'out_time_ms': None,
                    'out_time': None,
                    'dup_frames': None,
                    'drop_frames': None,
                    'speed': None,
                    'progress': None,
                }  # The dict object hold the ffmpeg status

                flush_count = 11
                for each_status_line in tailer.follow(f):
                    pure = each_status_line.strip().split('=')
                    key, value = pure  # unpack the key value pair.
                    # if key not in status_dict or status_dict[key] is None:
                    #    status_dict[key] = value
                    self._report_progress(status_dict)
                else:
                    self._report_progress({'error': 'Progress File Is Empty'})

        except IOError:
            return {'error': 'Cannot Read File. IOError.'}

    def status(self):
        ''' Show progress of ffmpeg rendering progress file. '''
        if self.progressfilename is None:
            return {'error': 'File Not Exist'}

        try:
            with open(self.progressfilename, 'r') as f:
                finaloutput = tailer.tail(f, lines=22)  # magic number.
                status_dict = {}
                for each in finaloutput[::-1]:  # from behind to front.
                    pure = each.strip().split('=')
                    key, value = pure  # unpack the key value pair.
                    if key not in status_dict:
                        status_dict[key] = value

                if status_dict:
                    return status_dict
                else:
                    return {'error': 'File Is Empty'}

        except IOError:
            return {'error': 'Cannot Read File. IOError.'}

    def render_progress(self):
        ''' Show rendering progress of current worker, including status from ffmpeg '''
        ffmpeg_status = self.status()
        ffmpeg_status['is_render'] = self.is_rendering()
        ffmpeg_status['has_failed'] = self.has_failed()

        if self.cake and self.is_rendering() and 'error' not in self.status():
            percent = int(ffmpeg_status['frame']) / \
                (int(self.cake['range_end']) - int(self.cake['range_start']))
            percent *= 100
            percent = int(percent)
            ffmpeg_status['percent'] = percent

        return ffmpeg_status

    def _render(self, render_command):
        ''' Directly execute a ffmpeg command, ignore settings in global settings.
            raise RenderProgressError if ffmpeg calling has something wrong.
        '''
        if not render_command:
            logger.error('Empty ffmpeg render command')
        else:
            # Step 2. Call subprocess to process this command.
            logger.info('Try to execute command: %s' % render_command)
            try:
                self.is_render = True  # Now we entering rendering.
                returncode = subprocess.call(render_command, shell=True)
                if returncode > 0:
                    raise RenderProgressError('Command [%s] failed. Exit code %d' % (render_command, returncode))
            except:
                logger.exception('Command [%s] failed. Exit code %d' % (render_command, returncode))
                raise RenderProgressError('Command [%s] failed. Exit code %d' % (render_command, returncode))

            finally:
                self.is_render = False

    def render(self, cake, resultfilename=None):
        # Step 1. Mount the cake onto worker
        self.cake = cake
        # Step 2. Determine the result file name
        if not resultfilename:
            resultfilename = '%s.mp4' % cake['uid']

        # Step 3. Determine the progress temp file name.
        self.progressfilename = self._make_time_now_str() + '.progress'

        # Step 4. Render progress
        render_command = ''
        try:
            self.failed = False  # We haven't failed, yet.
            render_command = bake.generate_cake_render_command(self.cake, resultfilename, self.codecname,
                                                               self.codecflag, self.ffmpeg, self.progressfilename)
            self._render(render_command)
        except RenderProgressError as ex:
            self.failed = True
            raise ex
        except:
            self.failed = True
            logger.error('Cake %s cannot be converted to a ffmpeg command' % cake['uid'])
            raise RenderCommandError('cake %s cannot be converted to a ffmpeg command' % cake['uid'])
        finally:
            self.cake = None  # unmount the cake

    def clean_log(self):
        logger.info('Try to delete progress file name %s' % self.progressfilename)
        try:
            os.remove(self.progressfilename)
        except Exception:
            logger.error('Remove File %s Failed.' % self.progressfilename)

    def _make_time_now_str(self):
        ''' Automatically return a name as current time '''
        now = datetime.datetime.now()
        str_now = datetime.datetime.strftime(now, '%Y%m%d-%H%M%S')
        return str_now
