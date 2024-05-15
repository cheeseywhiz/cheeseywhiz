#!/usr/bin/env bash
set -ex
sqlite3 dream_journal.sql "select datetime(time, 'auto') as time, text from posts order by time desc"
