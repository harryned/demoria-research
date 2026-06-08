"""Re-embed PYR (public/age_pyramid.json) and TFR (_tfr_export.json) into
dhi_globe.html. Called after override commits since these blobs are
otherwise frozen at first build."""
import json

h = open('dhi_globe.html').read()
pyr = json.load(open('public/age_pyramid.json'))
tfr = json.load(open('_tfr_export.json'))

def splice(haystack, start_tag, end_tag, new_value):
    a = haystack.find(start_tag)
    assert a >= 0, f'tag not found: {start_tag}'
    a += len(start_tag)
    b = haystack.find(end_tag, a)
    assert b > a, f'end tag not found: {end_tag}'
    return haystack[:a] + new_value + haystack[b:]

h = splice(h, 'const PYR=', ';const TFR=', json.dumps(pyr, separators=(',',':')))
h = splice(h, 'const TFR=', ';const DATA=', json.dumps(tfr, separators=(',',':')))

assert all(h.count(m)==1 for m in ('const GLOBE=','const DATA=','const PROJD=','const PYR=','const TFR=','const FCAGE=')), 'integrity check failed'
open('dhi_globe.html', 'w').write(h)
print('PYR and TFR re-embedded')
