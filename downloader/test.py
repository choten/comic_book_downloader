import timeit

def test():
    """
    測試程式碼
    """
    t = timeit.timeit(stmt="app_start('http://www.dm5.com/manhua-dangxinelingqishi/')", setup="from downloader import app_start", number=1)
    print(t)

test()