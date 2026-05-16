# Development Tasks

* Improve maintainability
    * Add type hints (WIP)
    * Add unit tests
    * Add E2E tests
* Work on feature requests

# Feature requests

## Dividing line opt-out

Option to not add a dividing line (`<hr>`) above accent illustration.

**Current behavior**
* Field empty -> no line
* Field non empty -> add line (prepends `<br><hr><br>`)

**How to address**
* (a) Make separator hideable via CSS (put inside a span with a class, hide with `display: none`)
    * `+` Makes it possible to quickly change between showing/hiding separators without the need not re-generate accent illustrations
* (b) Add option toggle to add/not add separator
    * `-` Would require development of user preferences

-> go with option (a)

## Remember choice of bulk add fields

Remember deck choice as well or just fields per deck (and note type)?

**How to address**
* (a) Automatically save and reuse, with option to reset
    * Comparatively easy to implement but bad UX if wrong fields selected
* (b) Add button "reuse previously selected fields
    * Requires saving field choice per deck and note type
* (c) Some more sophisticated preference scheme
    * Would require lots of extra implementation

-> go with option (b)

## Option to automatically annotate new cards

Things to consider
* How are the decks determined for which auto annotation runs?
    * All that have been bulk added to? (And not bulk removed after the last bulk add?)
* How to handle a new note type being added to a deck for which auto annotation runs?
* Is auto annotation run on every note add (and edit?), or only in buld on start up?
* ...

## Support note format X

E.g. expression fields using HTML ruby notation.

-> should consider adding fallback parsers for common formats.

## Pitch accent type based styling

**How to address**  
1. Determine accent type from pattern
    * last high → heiban
    * first high → atamadaka
    * first low and ends with high low  → odaka
    * first low and ends with low low → nakadaka
2. Add CSS class indicating the accent type to illustration
    * SVG element currently has class `pitch`, add a second class indicating pitch type (values are above four plus "other" as fallback)
