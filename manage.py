import multiprocessing as mp
from config import proc_lists
from general import main


def start():
    """
    Creating processes for each group of tickers
    """
    procs = []
    print('Starting processes')
    for i in range(len(proc_lists)):
        proc = mp.Process(target=main, args=(i, ))
        proc.start()
        procs.append(proc)
    for p in procs:
        p.join()


if __name__ == '__main__':
    start()
