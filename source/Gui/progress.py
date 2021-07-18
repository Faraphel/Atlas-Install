def progress(self, show=None, indeter=None, step=None, statut=None, max=None, add=None):
    if indeter is True:
        self.progressbar.config(mode="indeterminate")
        self.progressbar.start(50)
    elif indeter is False:
        self.progressbar.config(mode="determinate")
        self.progressbar.stop()
    if show is True:
        self.state_button(enable=False)
        self.progressbar.grid(row=100, column=1, sticky="NEWS")
        self.progresslabel.grid(row=101, column=1, sticky="NEWS")
    elif show is False:
        self.state_button(enable=True)
        self.progressbar.grid_forget()
        self.progresslabel.grid_forget()

    if statut: self.progresslabel.config(text=statut)
    if step: self.progressbar["value"] = step
    if max:
        self.progressbar["maximum"] = max
        self.progressbar["value"] = 0
    if add: self.progressbar.step(add)