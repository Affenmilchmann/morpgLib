import time
from IPython.display import display, clear_output
from time import time, strftime, gmtime
from src.ParentBar import ParentBar

class TxtBar(ParentBar):
    def __init__(self, bar_len = 25, **kwargs):
        self.txt_bar_len = bar_len
        self.done_char = '#'
        self.left_char = '_'
        
        super().__init__(**kwargs)
        
    def set_text(self, text):
        pass
        
    def set_name(self, text):
        self.name = text
        
    def blank_progress(self, text):
        message = f'{text}'[:self.txt_bar_len - 1]
        side_bar = '_' * int((self.txt_bar_len - len(message)) / 2)
        display(f"[{self.name}] [{side_bar}{message}{side_bar}] (?/?) ?% | Estimated time:?")
        
    def next_cycle(self, index, size, float_presicion, show_time, begin_time):
        ratio=index/size
        bar_progress = int(self.txt_bar_len * ratio)
        if self.is_percent:
            sec_left = ""
            if show_time:
                sec_passed = int(round(time() - begin_time))
                sec_left = gmtime(int((sec_passed/index) * (size - index)))

            txt_label = u'[{name}] {txt_bar} ({index}/{size}) {perc}% {time}'.format(
                name=self.name,
                perc=round(100*ratio, float_presicion) if float_presicion else int(100*ratio),
                txt_bar = f"[{self.done_char * bar_progress}{self.left_char * (self.txt_bar_len - bar_progress)}]",
                index=index,
                size=int(size),
                time=strftime('| Estimated time: %Hh %Mm %Ss', sec_left) if show_time else ""
            )
        else:
            self.progress.value = index
            self.label.value = u'[{name}]  {txt_bar}  {index} / {size}'.format(
                name=self.name,
                txt_bar = f"[{self.done_char * bar_progress}{self.left_char * (self.txt_bar_len - bar_progress)}]",
                index=index,
                size=size,
                time=strftime('| Estimated time: %Hh %Mm %Ss', sec_left) if show_time else ""
            )
        clear_output(wait=True)
        display(txt_label)
        
    def danger(self):
        message = 'ERROR'[:self.txt_bar_len - 1]
        side_bar = '_' * int((self.txt_bar_len - len(message)) / 2)
        display(f"[{side_bar}{message}{side_bar}]")
    
    def done(self, index, size, show_time, begin_time):
        clear_output(wait=True)
        message = 'DONE'[:self.txt_bar_len - 1]
        side_bar = '_' * int((self.txt_bar_len - len(message)) / 2)
        end_time = f"{strftime('%Hh %Mm %Ss', gmtime(int(round(time() - begin_time))))}" if show_time else ""
        display(f"[{self.name}] [{side_bar}{message}{side_bar}] ({index}/{size}){end_time}")