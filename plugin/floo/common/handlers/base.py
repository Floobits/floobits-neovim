try:
    from ... import editor
except ValueError:
    from floo import editor
from .. import msg, event_emitter, shared as G, utils


class BaseHandler(event_emitter.EventEmitter):
    PROTOCOL = None

    def __init__(self):
        super(BaseHandler, self).__init__()
        self.joined_workspace = False
        G.AGENT = self
        # TODO: removeme?
        utils.reload_settings()

    def build_protocol(self, *args):
        self.proto = self.PROTOCOL(*args)
        self.proto.on('data', self.on_data)
        self.proto.on('connect', self.on_connect)
        return self.proto

    def send(self, *args, **kwargs):
        self.proto.put(*args, **kwargs)

    def on_data(self, name, data):
        handler = getattr(self, '_on_%s' % name, None)
        if handler:
            return handler(data)
        msg.debug('unknown name!', name, 'data:', data)

    @property
    def client(self):
        return editor.name()

    @property
    def codename(self):
        return editor.codename()

    def _on_error(self, data):
        message = 'Error from Floobits server: %s' % str(data.get('msg'))
        msg.error(message)
        if data.get('flash'):
            editor.error_message(message)

    def _on_disconnect(self, data):
        message = 'Disconnected from server! Reason: %s' % str(data.get('reason'))
        msg.error(message)
        editor.error_message(message)
        self.stop()

    def stop(self):
        from .. import reactor
        reactor.reactor.stop_handler(self)
        if G.AGENT is self:
            G.AGENT = None

    def is_ready(self):
        return self.joined_workspace

    def tick(self):
        pass
