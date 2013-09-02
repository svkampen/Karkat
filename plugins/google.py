import json
import requests
import re
import urllib.parse as urllib

from irc import Callback
from text import unescape

cb = Callback()

@cb.threadsafe
@cb.command("google", "(.+)", help="12Google05⎟ Usage: !google <query>")
def google(message, query):
    request = requests.get("http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s" % urllib.quote(query))
    page = json.loads(request.text)
    # TODO: Error handling

    first = True
    for i, result in enumerate(page["responseData"]["results"]): 
        colour = [12, 5, 8, 3][i % 4]
        yield "%.2d⎟ 02%s" % (colour, unescape(result["title"].replace("<b>", "").replace("</b>", "")))
        yield "%.2d⎟ 03▸ %s" % (colour, result["unescapedUrl"])
        yield "%.2d⎟ %s" % (colour, 
                                   re.sub(r"\s+", 
                                          " ", 
                                          unescape(result["content"].replace("<b>", "").replace("</b>", ""))))
        if first: 
        	first = False
        if message.text[0] == "@":
        	return
    if first:
        yield "12Google⎟ No results found."


__initialise__ = cb.initialise
__callbacks__  = {"privmsg": [google]}