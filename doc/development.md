# Development Tasks

* Improve maintainability
    * Add unit tests
    * Add E2E tests
* Work on feature requests

# Feature requests

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
