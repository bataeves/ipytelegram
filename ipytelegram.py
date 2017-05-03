import warnings

import telepot
from IPython.core.magic import Magics, magics_class, line_magic, cell_magic


class TelegramSender(object):
    def __init__(self, token, user_id, prefix='', max_retries=2):
        self.user_id = user_id
        self.bot = telepot.Bot(token)
        self.prefix = prefix
        self.max_retries = int(max_retries)

    def send(self, message, output, error):
        retries = self.max_retries
        msg = message or "done"

        if self.prefix:
            msg = '[{}] {}'.format(self.prefix, msg)

        if output is not None:
            if output.__class__.__name__ == "DataFrame":
                output = output.head(20).to_string()

            if output:
                msg += '\n' + str(output)

        if error:
            msg += '\n' + 'Error: ' + str(error)

        while retries >= 0:
            try:
                self.bot.sendMessage(self.user_id, msg)
                return
            except Exception:
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
        run_result = self.shell.run_cell(cell)
        self.sender.send(line, output=run_result.result, error=run_result.error_in_exec)


def load_ipython_extension(ipython):
    magics = TelegramMagics(ipython)
    ipython.register_magics(magics)


def unload_ipython_extension(ipython):
    pass
