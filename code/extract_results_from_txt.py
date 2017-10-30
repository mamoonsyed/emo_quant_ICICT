# -*- coding: utf-8 -*-
'''
this code takes the text data that has been extracted from the 
excel sheet before and processes it and assigns to different PoS pools 
save the result to excel files in RESULT_PATH folder. also saves the plot.
'''
#import seaborn
import nltk
import re
import csv
import os.path
import operator
#import mpld3
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.patches as mpatches
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

#seaborn.set()
feature_pool={}
noun_pool={}
verb_pool={}
adverb_pool={}
adjective_pool={}

EVENT_NUM = 114    #   NUMBER OF EVENTS IN THE CSV FILE
TXT_PATH = 'E:/Google Drive/research/emo_quant_ICICT/txt_data'
RESULT_PATH = 'E:/Google Drive/research/emo_quant_ICICT/results'

def make_file_name (event_num, news_num ,title_body_rating):
    file_name = os.path.join(TXT_PATH,
                         str(event_num)+
                         '_'+str(news_num)+
                         '_'+title_body_rating+
                         '.txt')
    return file_name

def read_file(file_name):
    with open(file_name, 'r') as f:
        content = f.read()
    f.closed
    return content

def clean_current(current_string):
#    print "inside clean_current function"
    rx = re.compile('\[a-zA-Z]')
    clean_string = rx.sub(' ', current_string).strip()
    return clean_string

def process_current(current_string):
    #   nltk.pos_tag() CONVERTS OUR STRING INTO A LIST OF TUPLES
    tagged_tuples = nltk.pos_tag(nltk.word_tokenize(current_string))
    #   CONVERTING LIST OF TUPLES INTO 2D LIST
    pos_tagged = map(list, tagged_tuples)
    stop=stopwords.words('english')
    #   IN PLACE LIST COMPREHENSION TO REMOVE STOP WORDS
    pos_tagged[:] = [w for w in pos_tagged
                     if w[0] not in stop]
#    pos_tagged[:] = [w for w in pos_tagged] # include stopwords
    #   LOOPING OVER NON-STOP WORDS FOR STEMMING.
    for item in pos_tagged:
        item[0]=stem_current(item[0])
    return pos_tagged
    
def stem_current(current_member):
    stemmer=SnowballStemmer('english')
    return stemmer.stem(current_member)

def populate_pool(current_list, current_sent):
    #LOOPING THE CLEAN CURRENT STRING TO POPULATE SEPERATE POOLS
    for item in current_list: 
        key=item[0]
        current_pos=item[1]
        if (current_pos=='NNP' or current_pos=='NNPS' or current_pos=='DT'
            or current_pos=='PRP' or current_pos=='PRP$' or current_pos=='IN'
            or current_pos=='TO'): # ELIMINATE UNWANTED POS REFER UPENN POS LIST
            continue
        elif (current_pos.startswith('N')): #CHECKING FOR COMMON NOUNS
            if noun_pool.has_key(key):
                noun_pool[key][0]+=current_sent
            else:
                noun_pool[key]=[current_sent, current_pos]
        elif (current_pos.startswith('V')):#   CHECKING FOR VERBS
            if verb_pool.has_key(key):
                verb_pool[key][0]+=current_sent
            else:
                verb_pool[key]=[current_sent, current_pos]
        elif (current_pos.startswith('R')):#   CHECKING FOR ADVERBS
            if adverb_pool.has_key(key):
                adverb_pool[key][0]+=current_sent
            else:
                adverb_pool[key]=[current_sent, current_pos]
        elif (current_pos.startswith('J')):#   CHECKING FOR ADJECTIVES
            if adjective_pool.has_key(key):
                adjective_pool[key][0]+=current_sent
            else:
                adjective_pool[key]=[current_sent, current_pos]
        else:   #   ADD TO FEATURE POOL IF DOESN'T FIT ANYWHERE ELSE
            if feature_pool.has_key(key):
                feature_pool[key][0]+=current_sent
            else:
                feature_pool[key]=[current_sent, current_pos]
            
def merge_pools(): #   MERGE ALL POOLS INTO THE FEATURE_POOL AS A SHALLOW COPY
    feature_pool.update(noun_pool)
    feature_pool.update(verb_pool)
    feature_pool.update(adverb_pool)
    feature_pool.update(adjective_pool)

def sort_pool(to_be_sorted,a):
    return sorted(to_be_sorted.items(),
                  key=operator.itemgetter(1),
                  reverse=a)

def write_file(to_write, pool): #WRITE RESULTS TO CSV
    file_name = os.path.join(RESULT_PATH,
                             pool+
                             '.csv')
    
    with open(file_name, 'wb') as f:
        wtr = csv.writer(f, delimiter= ',')
#        wtr.writerow([file_desc])
        wtr.writerows(to_write)

def line_plot(sorted_n, sorted_v, sorted_r, sorted_j, pool): 
    #SAVE FIGURE TO RESULTS
    
    fig = plt.figure() ; ax = plt.axes()
    
    score_pos_n = zip(*sorted_n)[1] ; score_pos_v = zip(*sorted_v)[1] 
    score_pos_r = zip(*sorted_r)[1] ; score_pos_j = zip(*sorted_j)[1] 
    
    #   x_n MEANS X-AXIS OF NOUN DATA
    x_n = np.arange(len(score_pos_n)) ; x_v = np.arange(len(score_pos_v))
    x_r = np.arange(len(score_pos_r)) ; x_j = np.arange(len(score_pos_j))
    
    y_n = zip(*score_pos_n)[0] ; y_v = zip(*score_pos_v)[0] 
    y_r = zip(*score_pos_r)[0] ; y_j = zip(*score_pos_j)[0]

    ax.plot(x_n, y_n, '-g', label='Noun')
    ax.plot(x_v, y_v, ':b', label='Verb')
    ax.plot(x_r, y_r, '--r', label='Adv')
    ax.plot(x_j, y_j, '-.c', label='Adj')
    
    ax.set(xlabel='Words',
           ylabel='Frequency')
    
    ax.legend()
    fig_name = pool + '.pdf'
    fig.savefig (os.path.join(RESULT_PATH, fig_name), bbox_inches='tight')
    fig.show ()

# ---------------------------- MAIN ROUTINE -----------------------------------

for event_num in range(0,EVENT_NUM):    # ITERATE THROUGH THE EVENTS
    news_num = 0
    rating_file = make_file_name(event_num, news_num, 'rating')
    stock_sent = float(read_file(rating_file))
    body_sent = stock_sent
    title_sent = stock_sent * 3
    print "-------------------"
    while True:   #ITERATE THROUGH NEWS
        
        title_file = make_file_name(event_num,news_num,'title')
        if os.path.isfile(title_file):
            body_file = make_file_name(event_num,news_num,'body')
            event_news = 'event: ' + str(event_num) + " | news: " + str(news_num)
            print event_news
            
            title_string=read_file(title_file)
            clean_title = clean_current(title_string)
            
            body_string=read_file(body_file)
            clean_body = clean_current(body_string)
            
            processed_title = process_current(clean_title)
            populate_pool(processed_title, title_sent)
            processed_body = process_current(clean_body)
            populate_pool(processed_body, body_sent)
            
        else:
            break
        news_num +=1


merge_pools()
sorted_n = sort_pool(noun_pool,True)
sorted_v = sort_pool(verb_pool,True)
sorted_r = sort_pool(adverb_pool,True)
sorted_j = sort_pool(adjective_pool,True)
sorted_f = sort_pool(feature_pool,True)

write_file (sorted_f, 'feature')
write_file (sorted_n, 'noun')
write_file (sorted_v, 'verb')
write_file (sorted_r, 'adverb')
write_file (sorted_j, 'adjective')
line_plot (sorted_n, sorted_v, sorted_r, sorted_j, 'all_PoS')

''' COMMANDS CALLED FOR EACH INSTANCE OF EXPERIMENT #2'''

#data_tail=sorted_adj[-100:]
#data_head=sorted_adj[:100]
#data_tail.reverse()
#
#xlabel='Adjectives'
#ylabel='Sentiment Score'
#file_desc='normalized sentiment score each adjective'
##write_file(sorted_feature,3.2,'features','head-tail-30', file_desc)
#plot_data(data_head,data_tail,3.2,'adjective','100', file_desc, xlabel, ylabel)

''' BELOW PLOTTING FUNC USED FOR ALL EXP@ 1 AND 2. '''

#def plot_data(to_plot_a,to_plot_b, exp_num, pool, position, graph_title, a, b): #SAVE FIGURE TO RESULTS
#    words_a = zip(*to_plot_a)[0]
#    score_pos_a = zip(*to_plot_a)[1]
#    score_a = zip(*score_pos_a)[0]
#    x_pos_a = np.arange(len(words_a))
#    
#    words_b = zip(*to_plot_b)[0]
#    score_pos_b = zip(*to_plot_b)[1]
#    score_b= zip(*score_pos_b)[0]
#    x_pos_b= np.arange(len(words_b))
#    barlist_a=plt.bar(x_pos_a, score_a,align='center')
#    barlist_b=plt.bar(x_pos_b, score_b,align='center')
#    #   this loop sets different color for different PoS
#    for index, item in enumerate(score_pos_a):
#        if item[1].startswith('N'):
#            barlist_a[index].set_color('darkolivegreen')
#        elif item[1].startswith('V'):
#            barlist_a[index].set_color('yellow')
#        elif item[1].startswith('R'):
#            barlist_a[index].set_color('orange')
#        elif item[1].startswith('J'):
#            barlist_a[index].set_color('crimson')
#        else:
#            barlist_a[index].set_color('deepskyblue')
#    for index, item in enumerate(score_pos_b):
#        if item[1].startswith('N'):
#            barlist_b[index].set_color('yellowgreen')
#        elif item[1].startswith('V'):
#            barlist_b[index].set_color('gold')
#        elif item[1].startswith('R'):
#            barlist_b[index].set_color('tomato')
#        elif item[1].startswith('J'):
#            barlist_b[index].set_color('coral')
#        else:
#            barlist_b[index].set_color('skyblue')
##    plt.xticks(x_pos, words) 
#    plt.xlabel(a)
#    plt.ylabel(b)
##    feature = mpatches.Patch(color='deepskyblue', label='other feature')
##    noun = mpatches.Patch(color='darkolivegreen', label='noun')
##    verb = mpatches.Patch(color='yellow', label='verb')
##    adverb = mpatches.Patch(color='orange', label='adverb')
##    adjective = mpatches.Patch(color='crimson', label='adjective')
##    plt.legend(handles=[feature,noun,verb,adverb,adjective])
#    plt.suptitle(graph_title, fontsize=14, fontweight='bold')
#    fig_name=str(exp_num)+'-'+pool+'-'+position+'.pdf'
#    plt.savefig(os.path.join(RESULT_PATH, fig_name), bbox_inches='tight')
#    plt.show()
