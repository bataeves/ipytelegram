import telepot
import warnings
from IPython.core.magic import Magics, magics_class, line_magic, cell_magic

class TelegramSender(object):
    
    def __init__(self, token, user_id, prefix='', max_retries=3):
        self.user_id = user_id
        self.bot = telepot.Bot(token)
        self.prefix = prefix
        self.max_retries = int(max_retries)
    
    def send(self, message):
        retries = self.max_retries
        msg = message
        if self.prefix:
            msg = '[{}] {}'.format(self.prefix, msg)

        while retries >= 0:
            try:
                self.bot.sendMessage(self.user_id, msg)
                return
            except Exception as e:
                if retries == 0:
                    warnings.warn('failed to send message {}'.format(message))
            retries -= 1


@magics_class
class TelegramMagics(Magics):

    def __init__(self, shell):
        super(TelegramMagics, self).__init__(shell)
        self.sender = None

    @line_magic
    def telegram_setup(self, line):
        r = line.strip().split()
        if len(r) < 2:
            raise ValueError()

        token = r[0]
        user_id = r[1]

        opts = {}
        for entry in r[2:]:
            k, v = entry.split(':', 1)
            opts[k] = v

        self.sender = TelegramSender(token, user_id, **opts)

    @cell_magic
    def telegram_send(self, line, cell):
        self.shell.run_cell(cell)
        self.sender.send(line)


def load_ipython_extension(ipython):
    magics = TelegramMagics(ipython)
    ipython.register_magics(magics)


def unload_ipython_extension(ipython):
    pass
