import threading


class DifferencesReferenceNotGivenError(Exception):
    pass


class KanjiComparisonThread(threading.Thread):
    '''
    A thread to compare kanji large amounts of kanji at once.

    differences -- a reference to the primary `dict` containing all differences
    '''
    differences = None

    def __init__(self, main_kanji, kanji_list, function):
        '''
        main_kanji -- the primary kanji being compared to those in `kanji_list`
        kanji_list -- a list of kanji to compare `main_kanji` to
        function -- a function that can called with `main_kanji, kanji_list, differences`
        '''
        super().__init__()
        if __class__.differences is None:
            raise DifferencesReferenceNotGivenError

        self.main_kanji = main_kanji
        self.kanji_list = kanji_list
        self.function = function

    def run(self):
        self.function(self.main_kanji, self.kanji_list, __class__.differences)
