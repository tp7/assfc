#!/usr/bin/env python3

from .font_loader import FontLoader
from .ass_parser import AssParser

from configparser import ConfigParser
from shutil import copy2 as copyfile
from time import ctime, time
from subprocess import call

import cProfile
import argparse
import logging
import sys
import os

default_config = {
    "font_dirs": "",
    "include_system_fonts": True,
    "verbose": False,
    "exclude_unused_fonts": False,
    "exclude_comments": False,
    "log_file": None,
}

def get_script_directory():
    return os.path.dirname(__file__)

def merge_configs(args, config):
    args = ((k, v) for k, v in args.__dict__.items() if v is not None)
    for arg, val in args:
        if type(val) == bool:
            config[arg] = 'yes' if val else 'no'
        else:
            config[arg] = str(val) if val != 'None' else None

    if config.get('additional_font_dirs', False):
        config['font_dirs'] = config['font_dirs'] + '\n' + '\n'.join(config['additional_font_dirs'])
    return config

def get_config(args):
    config = ConfigParser(default_config)
    config.read(os.path.join(get_script_directory(), "config.ini"))
    return merge_configs(args, config['assfc'])


def set_logging(log_file, verbose):
    level = logging.DEBUG if verbose else logging.INFO
    format = "LOG:%(levelname)s: %(message)s"
    logging.basicConfig(level = level, format=format)

    if log_file:
        log_file = log_file if os.path.isabs(log_file) else "%s/%s" %(get_script_directory(), log_file)
        console = logging.FileHandler(log_file)
        console.setFormatter(logging.Formatter(format))
        logging.getLogger('').addHandler(console)

def create_mmg_command(mmg_path, output_path, script_path, fonts):
    command_list = mmg_path
    command_list.extend(['-o', os.path.abspath(output_path)])
    command_list.extend(['--track-name', '0:[Shift]', '--language', '0:rus'])
    command_list.extend([os.path.abspath(script_path)])
    for font in fonts:
        command_list.extend(['--attachment-mime-type', 'application/x-truetype-font'])
        command_list.extend(['--attachment-name', os.path.basename(font.path)])
        command_list.extend(['--attach-file', font.path])
    return command_list

def create_mks_file(mmg_path, output_path, script_path, fonts):
    command = create_mmg_command(mmg_path, output_path, script_path, fonts)
    logging.debug('mks creation command: %s' % command)
    call(command)

def copy_fonts_to_folder(folder, fonts):
    folder = os.path.abspath(folder)
    logging.info('Copying fonts to %s' % folder)
    if not os.path.exists(folder):
        os.mkdir(folder)
    if not os.path.isdir(folder):
        logging.critical('File with the same name already exists at %s' % folder)
        sys.exit(1)
    for font in fonts:
        filename = os.path.basename(font.path)
        dest = os.path.join(folder, filename)
        copyfile(font.path, dest)

def process(args):
    config = get_config(args)
    set_logging(config.get('log_file', None), config.getboolean('verbose'))

    logging.debug(str(dict(config)))

    start_time = time()
    logging.info('-----Started new task at %s-----' % str(ctime()))

    fonts =  AssParser.get_fonts_statistics(os.path.abspath(config.get('script')), 
                                            config.getboolean('exclude_unused_fonts'), 
                                            config.getboolean('exclude_comments'))

    if config.getboolean('rebuild_cache'):
        FontLoader.discard_cache()

    font_dirs =  [v.strip() for v in config.get('font_dirs').split('\n') if len(v)]
    collector = FontLoader(font_dirs, config.getboolean('include_system_fonts'))
    
    found, not_found = collector.get_fonts_for_list(fonts)

    for font, usage in not_found.items():
        text = "Could not find font '%s'" % str(font)
        if usage.styles:
            text += '\nUsed in styles %s' % str(usage.styles)
        if usage.lines:
            if len(usage.lines) > 50:
                text += '\nUsed on more than 50 lines'
            else:
                text += '\nUsed on lines %s' % str(usage.lines)
        text += '\n\n'
        logging.warning(text)

    logging.info('Total found: %i', len(found))
    logging.info('Total not found: %i', len(not_found))

    if config.get('mmg') == 'guess':
        if sys.platform == 'linux' or sys.platfrom == 'darwin':
            mmg_path = ['/usr/bin/env', 'mkvmerge']
        if sys.platform == 'windows':
            raise NotImplementedError
    else:
        mmg_path = [os.path.abspath(config.get('mmg'))]


    if config.get('output_location') is not None:
        if config.get('output_location').endswith('.mks'):
            create_mks_file(mmg_path, config.get('output_location'), config.get('script'), found.values())
        else:
            copy_fonts_to_folder(config.get('output_location'), found.values())

    logging.debug('Job done in %fs' % round(time() - start_time, 5))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ASS font collector")

    parser.add_argument('--include', action='append', metavar='directory', dest='additional_font_dirs', help='Additional font directory to include')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--with-system', action='store_true', dest='include_system_fonts', help='Include system fonts')
    group.add_argument('--without-system', action='store_false', dest='include_system_fonts', help='Exclude system fonts')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--exclude-comments', action='store_true', dest='exclude_comments', help='Exclude comments')
    group.add_argument('--include-comments', action='store_false', dest='exclude_comments', help='Include comments')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--exclude-unused-fonts', action='store_true', dest='exclude_unused_fonts', help='Exclude fonts without any glyphs used')
    group.add_argument('--include-unused-fonts', action='store_false', dest='exclude_unused_fonts', help='Include fonts without any glyphs used')

    parser.add_argument('-v','--verbose', action='store_true', dest='verbose', help='print additional log info (debug level)')
    parser.add_argument('--log', dest='log_file', metavar='file', help='Output log to file')
    parser.add_argument('--rebuild-cache', action='store_true', dest='rebuild_cache', help='Rebuild font cache')

    parser.add_argument('-o', '--output', default=None, dest='output_location', metavar='folder/file', help='output folder or mks file')
    parser.add_argument('script', default=None, help='input script')
    parser.set_defaults(include_system_fonts = None, exclude_comments=None, exclude_unused_fonts = None,
                        verbose = None, log_file = None, rebuild_cache=False, output_location=None)
    args = parser.parse_args(sys.argv[1:])
    process(args)
#    cProfile.run('process(args)', sort='time', filename='profile.txt')

