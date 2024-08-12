import markdown

md = markdown.Markdown(extensions=["mdx_map"])
print(md.convert("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
</head>
<body>

# Markdown map test file

- first { and last } are optional

<map>
"settings": {
  "initial-lat": "61.87492817694598",
  "initial-lng": "9.744873046875002",
  "initial-zoom": "11",
  "width": "600px",
  "height": "400px"
},
"markers": [
  {
    "name": "Spranget",
    "lat": "61.83489",
    "lng": "9.7312",
    "html": "🅿️"
  },
  {
    "name": "Rondvassbu",
    "lat": "61.87897",
    "lng": "9.79621",
    "html": "🏠️"
  },
  {
    "img-src": "thumbnail.png",
    "url": "large_photo.jpg",
    "lat": "61.90663270777034",
    "lng": "9.76066589355469"
  }
],
"routes": [
  {
    "gpx-url": "Spranget - Rondvassbu.gpx",
    "color": "red"
  }
]
</map>

</body>
</html>"""))
