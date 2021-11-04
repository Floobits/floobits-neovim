from . import editor

from .common import msg, utils, shared as G
from collections import defaultdict

vim = None

# Foreground: background
COLORS = (
    ('white', 'red'),
    ('black', 'yellow'),
    ('black', 'green'),
    ('white', 'blue'),
)
HL_RULES = ['ctermfg=%s ctermbg=%s guifg=%s guibg=%s' % (fg, bg, fg, bg) for fg, bg in COLORS]


def user_id_to_region(user_id):
    return "floobitsuser%s" % user_id


def vim_buf_to_text(vim_buf):
    # Work around EOF new line handling in Vim. Vim always puts a newline at the end of a file,
    # but never exposes that newline in the view text.
    tail = '\n'
    if vim_buf[-1] == '':
        tail = ''
    text = '\n'.join(vim_buf[:]) + tail
    return text.decode('utf-8')


class View(object):
    """editors representation of the buffer"""

    current_highlights = defaultdict(list)
    pending_highlights = {}

    def __init__(self, vim_buf):
        self.vim_buf = vim_buf

    def __repr__(self):
        return '%s %s' % (self.native_id, self.vim_buf.name)

    def __str__(self):
        return repr(self)

    def _offset_to_vim(self, offset):
        current_offset = 0
        for line_num, line in enumerate(self.vim_buf):
            next_offset = len(line) + 1
            if current_offset + next_offset > offset:
                break
            current_offset += next_offset
        col = offset - current_offset
        msg.debug('offset %s is line %s column %s' % (offset, line_num + 1, col + 1))
        return line_num + 1, col + 1

    @property
    def native_id(self):
        return self.vim_buf.number

    def is_loading(self):
        return False

    def get_text(self):
        return vim_buf_to_text(self.vim_buf)

    def update(self, data, message=True):
        self.set_text(data["buf"])

    def set_text(self, text):
        msg.debug('About to patch %s %s' % (str(self), self.vim_buf.name))
        lines = text.encode('utf-8').split('\n')
        new_len = len(lines)
        end = start = -1
        i = 0

        def stomp_buffer():
            msg.debug('Stomping buffer.')
            G.AGENT.patching += 1
            self.vim_buf[:] = lines

        try:
            if new_len != len(self.vim_buf):
                stomp_buffer()
                return
            while i < new_len:
                if lines[i] != self.vim_buf[i]:
                    msg.debug('Lines are not the same. "%s" "%s"' % (self.vim_buf[i], lines[i]))
                    if start > -1:
                        if end > -1:
                            stomp_buffer()  # More than one contiguous change in patch.
                            return
                    else:
                        start = i
                else:
                    msg.debug('Lines are the same. "%s"' % lines[i])
                    if start > -1 and end == -1:
                        end = i
                i += 1
            if start == -1 and end == -1:
                msg.debug("Nothing to do here, buffers are the same.")
                return
            if start > -1 and end == -1:
                end = i
            msg.debug('Stomping lines %d to %d: "%s" -> "%s"' % (start, end, self.vim_buf[start:end],
                                                                 lines[start:end]))
            G.AGENT.patching += 1
            self.vim_buf[start:end] = lines[start:end]
        except Exception as e:
            msg.error('Couldn\'t apply patches because: %s!\nThe unencoded text was: "%s"' % (
                str(e), text))
            raise
        msg.debug('All done patching.')

    def set_read_only(self, read_only=True):
        pass

    def set_status(self, *args):
        pass

    def apply_patches(self, buf, patches, username):
        cursor_offset = self.get_cursor_offset()
        msg.debug('cursor offset is %s bytes' % cursor_offset)
        self.set_text(patches[0])

        for patch in patches[2]:
            offset = patch[0]
            length = patch[1]
            patch_text = patch[2]
            if cursor_offset > offset:
                new_offset = len(patch_text) - length
                cursor_offset += new_offset

        self.set_cursor_position(cursor_offset)

    def focus(self):
        editor.open_file(self.vim_buf.name)

    def set_cursor_position(self, offset):
        line_num, col = self._offset_to_vim(offset)
        command = ':silent! call setpos(".", [%s, %s, %s, %s])' % (self.native_id, line_num, col, 0)
        msg.debug('setting pos: %s' % command)
        vim.command(command)

    def get_cursor_offset(self):
        return int(vim.eval('line2byte(line("."))+col(".")')) - 2

    def get_selections(self):
        # Vim likes to return strings for numbers even if you use str2nr:
        return [[int(pos) for pos in range_] for range_ in vim.eval("g:FloobitsGetSelection()")]

    def clear_highlight(self, user_id):
        msg.debug('clearing selections for user %s in view %s' % (user_id, self.vim_buf.name))
        if user_id not in self.current_highlights:
            return
        for hl in self.current_highlights[user_id]:
            vim.command(":silent! :call matchdelete(%s)" % (hl,))
        del self.current_highlights[user_id]

    def clear_all_highlights(self):
        for user_id in list(self.current_highlights.keys()):
            self.clear_highlight(user_id)

    def highlight(self, ranges, user_id):
        msg.debug("got a highlight %s" % ranges)

        def doit():
            msg.debug("doing timed highlights")
            stored_ranges = self.pending_highlights[user_id]
            del self.pending_highlights[user_id]
            self._set_highlight(stored_ranges, user_id)

        if user_id not in self.pending_highlights:
            utils.set_timeout(doit, 150)
        self.pending_highlights[user_id] = ranges

    def _set_highlight(self, ranges, user_id):
        msg.debug('highlighting ranges %s' % (ranges))
        if vim.current.buffer.number != self.vim_buf.number:
            return
        region = user_id_to_region(user_id)

        hl_rule = HL_RULES[user_id % len(HL_RULES)]
        vim.command(":silent! highlight %s %s" % (region, hl_rule))

        self.clear_highlight(user_id)

        for _range in ranges:
            start_row, start_col = self._offset_to_vim(_range[0])
            end_row, end_col = self._offset_to_vim(_range[1])
            if start_row == end_row and start_col == end_col:
                if end_col >= len(self.vim_buf[end_row - 1]):
                    end_row += 1
                    end_col = 1
                else:
                    end_col += 1
            vim_region = "matchadd('{region}', '\%{start_row}l\%{start_col}v\_.*\%{end_row}l\%{end_col}v', 100)".\
                format(region=region, start_row=start_row, start_col=start_col, end_row=end_row, end_col=end_col)
            msg.debug("vim_region: %s" % (vim_region,))
            try:
                self.current_highlights[user_id].append(vim.eval(vim_region))
            except vim.api.NvimError:
                pass

    def rename(self, name):
        msg.debug('renaming %s to %s' % (self.vim_buf.name, name))
        current = vim.current.buffer
        text = self.get_text()
        old_name = self.vim_buf.name
        old_number = self.native_id
        with open(name, 'wb') as fd:
            fd.write(text.encode('utf-8'))
        vim.command('edit! %s' % name)
        self.vim_buf = vim.current.buffer
        vim.command('edit! %s' % current.name)
        try:
            vim.command('bdelete! %s' % old_number)
        except Exception as e:
            msg.debug("couldn't bdelete %s... maybe thats OK? err: %s" % (old_number, str(e)))
        try:
            utils.rm(old_name)
        except Exception as e:
            msg.debug("couldn't delete %s... maybe thats OK? err: %s" % (old_name, str(e)))

    def save(self):
        # TODO: switch to the correct buffer, then save, then switch back (or use writefile)
        if vim.current.buffer.name != self.vim_buf.name:
            return

        try:
            vim.command('silent w!')
        except Exception as e:
            msg.log('Error saving %s: %s' % (self.vim_buf.name, str(e)))

    def file_name(self):
        return self.vim_buf.name
