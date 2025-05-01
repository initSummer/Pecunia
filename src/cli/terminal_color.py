class TerminalColor:
    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # 背景色
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    # 显示方式
    RESET = '\033[0m'  # 重置样式
    BOLD = '\033[1m'   # 加粗
    UNDERLINE = '\033[4m' # 下划线
    REVERSE = '\033[7m'  # 反色显示

    # 组合示例
    WARNING = BOLD + YELLOW
    ERROR = BOLD + RED + BG_WHITE
    HIGHLIGHT = REVERSE + CYAN