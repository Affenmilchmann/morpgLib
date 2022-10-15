from ipywidgets import FloatProgress, HTML, VBox
from IPython.display import display
from time import time, strftime, gmtime

from src.ParentBar import ParentBar

class PBar(ParentBar):
    def __init__(self, **kwargs):
        self.progress = FloatProgress(min=0, max=1, value=0)
        self.label = HTML()
        self.vbox = VBox(children=[self.label, self.progress])
        display(self.vbox)
        
        super().__init__(**kwargs)
        
    def set_text(self, text):
        self.label.value = text
        
    def set_name(self, text):
        self.name = text
        
    def blank_progress(self, text):
        self.progress.max = 1
        self.progress.value = 1
        self.set_text(text)
        
    def next_cycle(self, index, size, float_presicion, show_time, begin_time):
        self.progress.value = index
        self.progress.max = size
        if self.is_percent:
            sec_left = ""
            if show_time:
                sec_passed = int(round(time() - begin_time))
                sec_left = gmtime(int((sec_passed/index) * (size - index)))

            self.label.value = u'[{name}] {perc}%  ({index}/{size}) {time}'.format(
                name=self.name,
                perc=round(100*index/size, float_presicion) if float_presicion else int(100*index/size),
                index=index,
                size=int(size),
                time=strftime('| Estimated time: %Hh %Mm %Ss', sec_left) if show_time else ""
            )
        else:
            self.label.value = u'[{name}] {index} / {size}'.format(
                name=self.name,
                index=index,
                size=size
            )
        
    def danger(self):
        self.progress.bar_style = 'danger'
    
    def done(self, index, size, show_time, begin_time):
        self.progress.bar_style = 'success'
        self.progress.value = index
        self.label.value = f"[{self.name} done] {index}/{size}"
        if self.is_percent:
            end_time = f"{strftime('%Hh %Mm %Ss', gmtime(int(round(time() - begin_time))))}" if show_time else ""
            self.label.value = f"[{self.name} done] 100% \t#\t ({index}/{size}) \t#\t {end_time}"
        