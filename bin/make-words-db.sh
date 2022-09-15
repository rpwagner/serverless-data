#!/bin/bash

sqlite3 words.db 'create table words (word text);'
sqlite3 words.db '.import /usr/share/dict/web2 words'
sqlite3 words.db 'select count(word) from words;'

