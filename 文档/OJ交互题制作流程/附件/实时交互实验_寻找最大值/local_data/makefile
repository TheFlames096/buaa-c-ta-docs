CC = cc
CFLAGS = -O2 -std=c11 -Wall -Wextra -pedantic

.PHONY: all
all: compare interactor

compare: compare.c judge.h
	$(CC) $(CFLAGS) compare.c -o compare

interactor: interactor.c judge.h
	$(CC) $(CFLAGS) interactor.c -o interactor
