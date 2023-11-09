import logging
import os
import json
import sys

# Strong colors are in the 90s. What am I gonna do about it? Strong red = 31+60=91 TODO
FG_COLORS = dict(zip(
    ['BLACK', 'RED', 'GREEN', 'ORANGE', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE', 'GRAY', 'YELLOW', 'CYAN_LIGHT'],
    ([30, 31, 32, 33, 34, 35, 36, 37, 38, 93, 96])))

BG_COLORS = dict(zip(
    ['GRAY', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE', 'BLACK'],
    list(range(40, 49))))

def add_styling(logger_method, _fg_color, _bg_color=None, _bold=False, _no_header=False, _inline=False):
    def wrapper(message, *args, **kwargs):
        underline   = kwargs.pop('underline', False)
        blink       = kwargs.pop('blink', False)
        fg_color    = kwargs.pop('fg', _fg_color)
        bg_color    = kwargs.pop('bg', _bg_color)
        bold        = kwargs.pop('bold', _bold)
        inline      = kwargs.pop('inline', _inline)
        no_header   = kwargs.pop('nh', _no_header)
        if not no_header: 
            no_header = kwargs.pop('no_header', _no_header)
        
        if isinstance(fg_color, int):
            set_fg_color = '\33[%dm' % fg_color
        elif isinstance(fg_color, str) and fg_color.upper() in FG_COLORS:
            set_fg_color = '\33[%dm' % FG_COLORS[fg_color.upper()]
        else:
            set_fg_color = ''

        if isinstance(bg_color, int):
            set_bg_color = '\33[%dm' % bg_color
        elif isinstance(bg_color, str) and bg_color.upper() in BG_COLORS:
            set_bg_color = '\33[%dm' % BG_COLORS[bg_color.upper()]
        else:
            set_bg_color = ''

        set_bold = '\33[1m' if isinstance(bold, bool) and bold is True else ''
        set_underline = '\33[1m' if isinstance(underline, bool) and underline is True else ''
        set_blink = '\33[5m' if isinstance(blink, bool) and blink is True else ''
        set_no_header = '\x1b[80D\x1b[K' if isinstance(no_header, bool) and no_header is True else ''
        
        if isinstance(inline, bool) and inline is True:
            print('\x1b[80D\x1b[1A\x1b[K', end='', flush=True)

        if isinstance(message, dict):
            message = json.dumps(message)

        if not isinstance(message, str):
            message = str(message)

        return logger_method(
                set_no_header + set_underline + set_blink + \
                        set_bold + set_bg_color + set_fg_color + message + '\33[m',
                *args, **kwargs
                )
    return wrapper

def get_default_log_level():
    return os.environ.get('MFG_LOG_LEVEL', os.environ.get('LOG_LEVEL', 'INFO'))

def create_root_logger():
    logging.addLevelName(15, "DETAIL")
    def detail(self, message, *args, **kws):
        if self.isEnabledFor(15):
            # Yes, logger takes its '*args' as 'args'.
            self._log(15, message, args, **kws)
    logging.Logger.detail = detail

    _logger = logging.getLogger()
    _logger.setLevel(get_default_log_level())
    
    if _logger.getEffectiveLevel() <= 10:
        DEFAULT_LOG_FORMAT = '%(name)s[%(levelname).3s]: %(message)s'
        #DEFAULT_LOG_FORMAT = '%(asctime)s %(name)s[%(levelname)s]: %(message)s'
    else:
        DEFAULT_LOG_FORMAT = '%(message)s'

    _formatter = logging.Formatter(DEFAULT_LOG_FORMAT, '%H:%M:%S')
    _handler = logging.StreamHandler()
    _handler.setFormatter(_formatter)
    _logger.addHandler(_handler)
    return _logger

def create_logger(name, level=None):
    # NOTE: this is admittedly a little silly, but python logging is weird..
    # By enforcing that the name starts with `mfg.` we are allowing the logger
    # that is created to defer to the root logger `mfg`, which will define
    # the formatting and stream handling.
    # see: https://docs.python.org/3.6/library/logging.html#logger-objects
    #if not name.startswith('mfg'):
    #    name = 'mfg.' + name

    _logger = logging.getLogger(name)
    
    if level is None:
        level = get_default_log_level()
    
    _logger.setLevel(level)

    for level, boldness, fg_color, bg_color in zip(
            ("detail", "info", "warning", "error", "debug", "critical", "exception"), 
            (False, False, True, False, False, True, True), 
            (FG_COLORS["ORANGE"], FG_COLORS["ORANGE"], FG_COLORS["GRAY"], FG_COLORS["RED"], FG_COLORS["CYAN"], FG_COLORS["RED"], FG_COLORS["RED"]),
            (None, None, None, None, None, None, None),
            ):
        setattr(_logger, 
                level, 
                add_styling(getattr(_logger, level), _fg_color=fg_color, _bg_color=bg_color, _bold=boldness)
                )

    return _logger

# Create root logger singleton
# NOTE: modules should create their own logger using `create_logger`
# This singleton can be used by itself in a pinch.. but just don't
logger = create_root_logger()
