
stopwords_path = './agregator/parcer/globalpars/stopwords/'

class Ya:
    """Search-engine class."""
    name = 'Yandex News'
    query_start = 'https://newssearch.yandex.ru/news/search?text='
    article_class = 'mg-snippet__url'

    query_end = (
        f'+date%3A{0}..{0}'
        '&flat=1&sortby=date&filter_date='
        f'{1}%2C{1}'
    )

    @staticmethod
    def get_article(el):
        """Load link and title, using Yandex News configuration."""
        link = el['href']
        tail = link[link.find('utm') - 1:]
        link = link.replace(tail, '')
        title = el.div.span.text
        return link, title
