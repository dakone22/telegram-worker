#!/usr/bin/python3

from multiprocessing import Process

from consumer import main as consumer_main
from producer import main as producer_main


def main():
    for f in (producer_main, consumer_main,):
        p = Process(target=f)
        p.start()


if __name__ == '__main__':
    main()
