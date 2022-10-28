from ipywidgets import FloatProgress, HTML, VBox
from IPython.display import display

class Bar():
    def __init__(self, **kwargs):
        self.progress = FloatProgress(min=0, max=1, value=0)
        self.label = HTML()
        self.vbox = VBox(children=[self.label, self.progress])
        display(self.vbox)
        
        super().__init__(**kwargs)