from wordcloud import *
from io import BytesIO

__author__ = 'TimeWz667'
__all__ = ['make_word_cloud']

EscapeWords = ['background','methods','results','conclusions','included',
               'used','used','using','use','compared','may','associated',
               'will','conducted','however','identified','will','different',
               'difference','can','provide','based','approach','across','factors',
               'two','potential', 'many', 'much', 'more', 'could', 'would']


def make_word_cloud(txt):
    stopwords = set(STOPWORDS)

    for word in EscapeWords:
        stopwords.add(word)

    wc = WordCloud(max_font_size=50, max_words=100, stopwords=stopwords).generate(txt)

    file = BytesIO()
    wc.to_image().save(file, 'png')

    file.seek(0)
    return file
