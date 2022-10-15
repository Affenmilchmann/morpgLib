from time import time, strftime, gmtime

class ParentBar(object):
    def __init__(self, is_percent=True):
        self.is_percent = is_percent
        self.float_digits = 0
        self.name = "Items"
        
    def set_text(self, text):
        raise Exception('Smelly socks')
        
    def set_name(self, text):
        self.name = text
        
    def blank_progress(self, text):
        raise Exception("blank_progress() isn't overrided")
        
    def seq(self, sequence, name="Wait...", percent_type=True, show_time=True, float_presicion=0):
        size = len(sequence)
        if size <= 100:
            every = 1
        else:
            every = max(int(size / (100*(10**self.float_digits))), 1)
            
        index = 0
        begin_time = None
        if show_time:
            begin_time = time()
        try:
            for index, record in enumerate(sequence, 1):
                if index == 1 or index % every == 0:
                    self.set_name(self.name)
                    self.next_cycle(index, size, self.float_digits, show_time, begin_time)
                yield record
        except Exception as e:
            self.danger()
            raise e
        else:
            self.done(index, size, show_time, begin_time)