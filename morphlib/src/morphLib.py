from functools import total_ordering
from math import ceil
from time import time
from typing import List
from IPython.core.inputtransformer2 import tokenize
from pymorphy2 import MorphAnalyzer
from nltk.tokenize import word_tokenize
from nltk import sent_tokenize
from json import load, dump

from random import randint, choice
import matplotlib.pyplot as plt
from re import match, sub

from src.ParentBar import ParentBar
from src.PBar import PBar
from src.TxtBar import TxtBar

from pathlib import Path
Path("\morphlib\results").mkdir(parents=True, exist_ok=True)

morph = MorphAnalyzer()

pos_list = ["NOUN","ADJF","ADJS","COMP","VERB","INFN","PRTF","PRTS","GRND","NUMR","ADVB","NPRO","PRED","PREP","CONJ","PRCL","INTJ"]
bar_dict: dict[str, ParentBar] = {
    'text': TxtBar,
    'graphic': PBar
}

class MorphAn():
    def __init__(self, progress_bar=False):
        self.tokens = []
        self.norm_forms = []
        self.pos_norm_forms = None
        self.pos_amount = None
        self.pos_ratio = None
        self.dbg = True
        self.sentences = []
        self.norm_sentences = []
        self.p_bar: ParentBar|None = bar_dict[progress_bar]() if progress_bar in bar_dict else None
        
    def __str__(self):
        return f"[{self.tokens}, {self.pos_norm_forms}, {self.pos_ratio}]"
    
    def __iter__(self):
        yield 'token_amount', len(self.tokens) if self.tokens else None
        yield 'amount_of_words_per_POS', self.pos_amount
        yield 'ratio_of_POS_by_word_amount', self.pos_ratio
        yield 'norm_forms_by_POS', self.pos_norm_forms
        yield 'tokens', self.tokens
        yield 'norm_forms', self.norm_forms
        yield 'sentences', self.sentences
        yield 'norm_sentences', self.norm_sentences
        
    def __sort_dict_by_val(self, dict_, reverse=False, name=""):
        self.p_bar.set_name(f"Sorting {name}")
        dict_ = dict(sorted(dict_.items(), key=lambda item: item[1],reverse=reverse))
        self.p_bar.set_name(f"Sorting")
        return dict_

    def analyze(self, overwrite_tokens = True, enable_progress_bar=False, label_text = None, force=False, measure_time=False, float_presicion=0):
        if not force and self.pos_norm_forms and self.pos_ratio:
            self.__debug("Already analyzed")
            return
            
        label_text_add = label_text if label_text else ""
            
        self.pos_norm_forms = {k: {} for k in pos_list}
        self.pos_amount = {pos: 0 for pos in pos_list} 

        seq = self.norm_forms
        if self.p_bar:
            self.p_bar.set_name(f"Analyzing{label_text_add}")
            seq = self.p_bar.seq(self.norm_forms, show_time=measure_time, float_presicion=float_presicion)

        for t in seq:
            an_res = morph.parse(t)[0]
            pos_val = an_res.tag.POS
            n_form = an_res.normal_form
            
            # count normal forms by pos category
            if an_res.normal_form and pos_val:
                if an_res.normal_form in self.pos_norm_forms[pos_val]:
                    self.pos_norm_forms[pos_val][an_res.normal_form] += 1
                else:
                    self.pos_norm_forms[pos_val][an_res.normal_form] = 1

            # count general pos stats
            if pos_val in pos_list:
                self.pos_amount[pos_val] += 1
                
        #sorting pos amounts
        self.pos_amount = self.__sort_dict_by_val(self.pos_amount, reverse=True, name="amount_of_words_per_POS")
        self.pos_ratio = {k: round(v/len(self.tokens), 4) for k, v in self.pos_amount.items()}
        
        #sorting pos_norm_forms
        if self.p_bar:
            seq = self.p_bar.seq(self.pos_norm_forms.items(), show_time=measure_time) 
        else: 
            seq = self.pos_norm_forms.items()
            
        for k, v in seq:
            self.pos_norm_forms[k] = self.__sort_dict_by_val(self.pos_norm_forms[k], reverse=True, name=k)
        
    def normilize_tokens(self, enable_progress_bar=True):
        if not self.tokens:
            raise Exception('self.tokens is empty')
        seq = self.p_bar.seq(self.tokens) if enable_progress_bar else self.tokens
        self.norm_forms = []
        for t in seq:
            if match("^[A-Za-zа-яА-Я]", t):
                self.norm_forms.append(morph.parse(t)[0].normal_form)
        
    def tokenize(self, text: str, overwrite_tokens=True):
        if not type(text) is str:
            raise TypeError(f"text must be str. Got {type(text)}")

        if overwrite_tokens:
            self.tokens = []

        self.tokens += word_tokenize(text)       
          
    def sent_segmentation(self, text, get_tokens=False, overwrite_tokens=True):
        if overwrite_tokens:
            self.sentences.clear()
            
        self.sentences = sent_tokenize(text)
        
        if get_tokens:
            if overwrite_tokens:
                self.tokens.clear()
            for sent in self.sentences:
                self.tokens += sent.split(" ")
        
    def sent_normalization(self, get_norm_forms=False):
        self.norm_forms.clear()
        self.norm_sentences.clear()
        
        seq = range(len(self.sentences))
        if self.p_bar:
            seq = self.p_bar.seq(range(len(self.sentences)))
            self.p_bar.name = 'sent norm'
        
        norm_forms = []
        for i in seq:
            self.sentences[i] = sub('[^a-zA-Zа-яА-Я ]+', '', self.sentences[i]).lower()
            tokens = word_tokenize(self.sentences[i])
            for t in tokens:
                if match("^[A-Za-zа-яА-Я]", t):
                    norm_forms.append(morph.parse(t)[0].normal_form)
            self.norm_sentences.append(''.join([str(nf) + ' ' for nf in norm_forms]))
            
            if get_norm_forms:
                self.norm_forms += norm_forms
            
            norm_forms.clear()
            
    def word_positional_freq_count(self, words: list, normal_form_match=True, discretization=100, freq=0):
        """
        freq = 0(count of words per segment), 1(count_of_words/)
        """
        if not self.tokens:
            self.__debug("Tokens are not generated.")
            return None
        
        total_count = 0
        results_dict = {}
        total_count_dict = {}
        
        if self.p_bar:
            self.p_bar.name = 'Counting freq'

        # results_dict format {word1: [21, 0, 32 ...., 13], word2: [32, ...], ...}
        # where int arrays are word counts per segment (segment size - whole_text/discretization)
        # total_count_dict format {word1: 123, word2: 321, ....}
        # where int is total word count in all the segments (in the whole text)
        for w in words:
            w_ = w
            if normal_form_match:
                w_ = morph.parse(w)[0].normal_form
            results_dict[w_] = [0] * discretization
            total_count_dict[w_] = 0

        seg_size = ceil(len(self.tokens)/discretization)

        seq = self.__seq_or_progress_bar_seq(self.tokens)
        for token in seq:
            total_count += 1
            temp_token = token
            if normal_form_match:
                temp_token = morph.parse(temp_token)[0].normal_form
            else:
                continue
            
            if temp_token in results_dict:
                results_dict[temp_token][total_count//seg_size] += 1
                

        if freq:
            for k in list(results_dict.keys()):
                for i in range(len(results_dict[k])):
                    results_dict[k][i] /= total_count_dict[k]

        return results_dict

    def load(self, file_name, encoding='utf8'):
        with open(file_name, 'r', encoding=encoding) as f:
            data = load(f)
        
        self.pos_amount = data['amount_of_words_per_POS']
        self.pos_ratio = data['ratio_of_POS_by_word_amount']
        self.pos_norm_forms = data['norm_forms_by_POS']
        self.tokens = data['tokens']
        self.norm_forms = data['norm_forms']
        self.sentences = data['sentences']
        self.norm_sentences = data['norm_sentences']

    def save(self, file_name, encoding='utf8'):
        with open(file_name, "w", encoding=encoding) as f:
            dump(dict(self), f, ensure_ascii=False, indent=2)
            
    def save_norm_sent_list(self, file_name, encoding='utf8'):
        with open(file_name, "w", encoding=encoding) as f:
            for l in self.norm_sentences:
                f.write(l + '\n')
                                   
    def __debug(self, dbg_text):
        if self.dbg:
            print(dbg_text)

    def __seq_or_progress_bar_seq(self, input_seq):
        if not type(input_seq) is list:
            try:
                input_seq = list(input_seq)
            except TypeError as e:
                raise TypeError('input_seq must be convertable to list') from e

        if self.p_bar:
            return self.p_bar.seq(list(input_seq))
        else:
            return input_seq
        
def token_dispersion(tokens, target_tokens: list, do_token_normalize=True, progress_bar=False, alpha=1, squeeze=4, row_size=0.25):
    """
    Shows token dispersion plot.
        Parameters:
            tokens: list[str] - tokens or normalized words forms
            target_list: list[str | list[str]] - Str can be "word1" -> "normalized_word1"; "word1 word2 ... wordN" -> ["norm_word1", ... "norm_wordN"]
            list[str] -> list[normalized_str]
            do_token_normalize: bool - normalize 'tokens' or not. Set false if your 'tokens' are already normalized. It saves a lot of time
            progress_bar: bool - pring progress bar or not
            alpha: 0 <= float <= 1 - graph data transparency. Helps to see how dence dispersion is
            squeeze: int - the larger 'squeeze' is - the smaller gap between plot lines (y axes)
            row_size: 0 <= float <= 1 - row size (y axes)
    """
    def rnd_clr():
        l_clr = [0.0, 0.1, 0.2]
        m_clr = [0.2, 0.3, 0.4]
        u_clr = [0.3, 0.5, 0.6]
        color = [choice(l_clr), choice(m_clr), choice(u_clr)]
        for i in range(randint(0, 10)):
            i1 = randint(0, 2)
            i2 = (i1+1)%3
            color[i1], color[i2] = color[i2], color[i1]
        return color
    # reverse so its rendered in correct order (else its reversed)
    target_tokens = list(reversed(target_tokens))
    # making different colors for each subplot
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    # if there is a lack of colors, add random ones
    if len(target_tokens) > len(colors):
        for _ in range(len(target_tokens) - len(colors)):
            colors.append(rnd_clr())
    colors.reverse()
    nested_target_tokens_idx = []
                
    #normalizing input
    for i in range(len(target_tokens)):
        # if we get "делает", it will be "делать"
        # ["петю", "сидоров"] will be ["петя", "сидоров"]
        # "петю сидорова" will be ["петя", "сидоров"]
        # so we can count different words as one category
        if (type(target_tokens[i]) is str) and (" " in target_tokens[i]):
            target_tokens[i] = target_tokens[i].split(" ")
        if type(target_tokens[i]) is list:
            for j in range(len(target_tokens[i])):
                target_tokens[i][j] = morph.parse(target_tokens[i][j])[0].normal_form
            nested_target_tokens_idx.append(i)
        else:
            target_tokens[i] = morph.parse(target_tokens[i])[0].normal_form
            
    #arrays of entries for each token
    tokens_data = [[] for i in range(len(target_tokens))]
    
    seq = tokens
    if progress_bar:
        pb = TxtBar()
        pb.float_digits = 0
        seq = pb.seq(tokens)
    #index of an entry
    i = 0
    for t in seq:
        #normalizing if needed
        final_form = morph.parse(t)[0].normal_form if do_token_normalize else t
        if final_form in target_tokens:
            tokens_data[target_tokens.index(final_form)].append(i)
        for idx in nested_target_tokens_idx:
            if final_form in target_tokens[idx]:
                tokens_data[idx].append(i)
        i += 1
        
    for d in range(len(tokens_data)):
        if len(tokens_data[d]) == 0:
            tokens_data[d] = [0]
            target_tokens[d] += "(no entries)"
    
    fig, ax = plt.subplots()
    # plotting for each token
    #   we need handles array to reverse it in the end. So legend order matches plot order
    handles = []
    for i in range(len(tokens_data)):
        handles.append(ax.vlines(tokens_data[i], i-row_size/2, i+row_size/2, alpha=alpha, colors=[colors[i]]))
        
    ax.set_xlim([0, len(tokens)]) # set the lower and upper limits of graph
    ax.set_xlabel('narrative time')
    ax.set_xticks([]) # turn off
    ax.set_yticks([])
    fig.set_figheight(len(target_tokens)/squeeze) # figure height, see also fig.set_figwidth()
    
    # forming legend strings
    legend_strings = []
    for i in range(len(target_tokens)):
        legend_string = target_tokens[i]
        if type(target_tokens[i]) is list:
            legend_string = ''
            for t in target_tokens[i]:
                legend_string += t + ' '
            legend_string = legend_string[:-1]
        legend_strings.append(legend_string)
    # adding legend. Resetting alpha so legend lines arent transparent
    fig.set_label("Tokens")
    # handles are reversed relatively to the plot lines :) so we have to reverse it again as well as legend strings
    leg = ax.legend(reversed(handles), reversed(legend_strings), loc='center left', bbox_to_anchor=(1, 0.5))
    for lh in leg.legendHandles: 
        lh.set_alpha(1)

    return (target_tokens, tokens_data)