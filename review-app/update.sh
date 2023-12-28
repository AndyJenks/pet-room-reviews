#!/bin/sh

ROOM_REVIEW_FDR="/home/adj35/public_html/room-reviews/"

# first update the room pages, which are more likely to be needed
python3 ./room-pages.py $ROOM_REVIEW_FDR/rooms

# Then check whether we need to update the homepage
# This will only notify that it needs to be done
python3 ./homepage.py $ROOM_REVIEW_FDR/index.html
