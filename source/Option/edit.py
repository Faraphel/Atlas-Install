def edit(self, option, value, need_restart=False, gui=None):
    if type(value) in [str, int, bool]:
        setattr(self, option, value)
    else:
        setattr(self, option, value.get())
    self.save_to_file()
    if need_restart: gui.restart()