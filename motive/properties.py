class Properties:
    AUTO = object()

    def __init__(self, update_context=False, force_sync=False, include_meta_arguments=False):
        self.update_context = update_context
        self.force_sync = force_sync
        self.include_meta_arguments = include_meta_arguments

