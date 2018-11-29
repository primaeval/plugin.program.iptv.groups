from xbmcswift2 import Plugin
import re
import requests
import xbmc,xbmcaddon,xbmcvfs,xbmcgui
import xbmcplugin
import urllib,urlparse
import platform
import collections


plugin = Plugin()
big_list_view = False

def decode(x):
    try: return x.decode("utf8")
    except: return x

def addon_id():
    return xbmcaddon.Addon().getAddonInfo('id')

def log(v):
    xbmc.log(repr(v),xbmc.LOGERROR)

def get_icon_path(icon_name):
    return "special://home/addons/%s/resources/img/%s.png" % (addon_id(), icon_name)


@plugin.route('/update')
def update():
    url = plugin.get_setting('m3u.url')
    if not url:
        return
    groups = plugin.get_storage('groups')
    data = requests.get(url).content
    data = data.decode("utf8")

    channels = re.findall("#EXTINF.*?\r?\n.*?$",data,flags=re.MULTILINE)

    f = xbmcvfs.File("special://profile/addon_data/plugin.program.iptv.groups/iptv.m3u8","w")
    f.write("#EXTM3U\n")
    for g in groups:
        if g == "NONE":
            g = ""
        c = [x for x in channels if 'group-title="%s"' % g in x]
        data = '\n'.join(c)
        data = re.sub('[\n\r]+','\n',data,flags=(re.MULTILINE|re.DOTALL))
        f.write(data.encode("utf8"))
    f.close()

@plugin.route('/choose')
def choose():
    groups = plugin.get_storage('groups')
    data = requests.get(plugin.get_setting('m3u.url')).content
    data = data.decode("utf8")
    new_groups = sorted(list(set(re.findall('group-title="(.*?)"',data))))

    indicies = xbmcgui.Dialog().multiselect("Choose Groups",new_groups)
    #log(indicies)
    #log(new_groups)
    if indicies == None:
        return
    groups.clear()
    for i in indicies:
        group = new_groups[i]
        if not group:
            group = "NONE"
        groups[group] = group
    groups.sync()
    update()


@plugin.route('/')
def index():
    items = []
    items.append(
    {
        'label': "Choose Groups",
        'path': plugin.url_for('choose'),
        'thumbnail':get_icon_path('settings'),
    })
    return items


if __name__ == '__main__':
    plugin.run()
