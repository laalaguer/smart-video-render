# translate from fcp xml special effect to ffmpeg filter

# Input a dict object, which is a fcp special effect
# Output a filter string, which is a ffmpeg filter

translate_table = {
    'adjust-crop': {'name': 'crop', 'values': ['iw/2', 'ih', '0', '0'], 'kwvalues': {}},
    'filter-video': {'name': 'hue', 'values': [], 'kwvalues': {'s': '0'}},
}
