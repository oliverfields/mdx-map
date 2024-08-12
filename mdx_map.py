"""
Markup for annotating an openstreetmap with markers, routes etc
"""

import re
import markdown
import json


class InlineMapExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        """ Add InlineMapPreprocessor to the Markdown instance. """
        md.registerExtension(self)
        md.preprocessors.add('map', InlineMapCompiler(md), "_begin")


class InlineMapCompiler(markdown.preprocessors.Preprocessor):

    def __init__(self, md):
        super(InlineMapCompiler, self).__init__(md)

    def run(self, lines):
        """ Match and generate map html """

        CONVO_RE_QUESTION = re.compile(
            r'^<map>\n(?P<map_config>.*?)</map>$',
            re.MULTILINE | re.DOTALL
        )

        text = "\n".join(lines)
        map_id_counter = 1

        # Use these vars to ensure leaflet js and css are only included once (i.e. in first iteration). Can be overriden using include_leaflet_[css|js] map settings
        inc_leaflet_css = True
        inc_leaflet_js = True
        inc_leaflet_gpx = True

        while 1:
            m = CONVO_RE_QUESTION.search(text)
            if m:
                map_html_id = 'mdx_map_' + str(map_id_counter)

                map_html = generate_map_html(m.group('map_config'), map_html_id, include_leaflet_js=inc_leaflet_js, include_leaflet_css=inc_leaflet_css, include_leaflet_gpx=inc_leaflet_gpx)

                text = '%s\n%s\n%s' % (text[:m.start()], map_html, text[m.end():])

                map_id_counter += 1
                inc_leaflet_css = False
                inc_leaflet_js = False
                inc_leaflet_gpx = False
            else:
                break

        return text.split("\n")


def makeExtension(*args, **kwargs):
    return InlineMapExtension(*args, **kwargs)


def generate_map_html(map_config, map_html_id, include_leaflet_css=True, include_leaflet_js=True, include_leaflet_gpx=True):
    """ Parse map json config and create javascript/html to create leaflet code to view openstreetmap map """

    if not map_config.startswith('{'):
        map_config = '{' + map_config

    if not map_config.rstrip().endswith('}'):
        map_config = map_config + '}'

    data = json.loads(map_config)

    try:
        initial_lat = data['settings']['initial-lat']
    except:
        initial_lat = "62.3479"

    try:
        initial_lng = data['settings']['initial-lng']
    except:
        initial_lng = "12.3970"

    try:
        initial_zoom = data['settings']['initial-zoom']
    except:
        initial_zoom = "9"

    try:
        width = data['settings']['width']
    except:
        width = "600px"

    try:
        height = data['settings']['height']
    except:
        height = "400px"

    try:
        include_leaflet_js = data['settings']['include_leaflet_js']
    except:
        pass

    try:
        include_leaflet_css = data['settings']['include_leaflet_css']
    except:
        pass

    try:
        include_leaflet_gpx = data['settings']['include_leaflet_gpx']
    except:
        pass

    html = ''

    if include_leaflet_css:
        html += '<link rel=stylesheet href=https://unpkg.com/leaflet@1.9.4/dist/leaflet.css integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin>'

    # Leaflet js goes after css
    if include_leaflet_js:
        html += '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>'

    if include_leaflet_gpx:
        html += '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-gpx/2.1.0/gpx.min.js"></script>'

    # Map html container
    html += '<div class="mdx-map" id="' + map_html_id + '" style="width: ' + width + '; height: ' + height + '"></div>'

    # Map leaflet script
    html += '<script>'

    html += "var map = L.map('" + str(map_html_id) + "').setView([" + initial_lat + ", " + initial_lng + "], " + initial_zoom + ");"

    html += "L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; <a href=\"http://www.openstreetmap.org/copyright\">OpenStreetMap</a>'}).addTo(map);"

    html += "map.zoomControl.setPosition('topright');"

    # Add any markers
    mcount = 0
    try:
        for m in data['markers']:
            mcount += 1

            try:
                marker_name = m['name']
            except:
                marker_name = 'Marker ' + str(mcount)

            try:
                marker_html = m['html']
            except KeyError:
                marker_html = "<img src='" + m['img-src'] + "' />"
            except Exception as e:
                marker_html = '📍'

            try:
                onclick = '.on("click", function(evt) {window.open("' + m['url'] +'", "_self");})'
            except:
                onclick = ''

            # TODO remove background color and border from marker in a better way than removing the classname
            html += 'var marker = L.marker([' + m['lat'] + ', ' + m['lng'] + '], { icon: L.divIcon({ html: "' + marker_html + '", iconSize: [32,32], iconAnchor: [16,16], className: "" })}).addTo(map)' + onclick + ';'

            html += 'marker.bindTooltip("' + marker_name + '");'

    # Markers
    except:
        pass


    # Add any GPX routes
    try:
        for r in data['routes']:
            try:
                color = ', polyline_options: { color: "' + r['color'] + '", opacity: .8 }'
            except:
                color = ''


            try:
                # TODO Fix uncaught error, seems to be related to not including js in <head>
                html += 'var route = new L.GPX("' + r['gpx-url'] + '", { async: true, markers: { startIcon: "", endIcon: "" }' + color + ' }).addTo(map);'
            except:
                pass
    except:
        pass

    html += '</script>'

    return html
