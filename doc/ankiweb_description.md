---

# Purpose

Automatically adds pitch accent information to cards.


---

# Basic Usage

① Tools → Pitch Accent → bulk add  
![](https://raw.githubusercontent.com/IllDepence/anki_add_pitch_plugin/master/doc/ankiweb_img/menu.png)

② Choose a deck  
③ Select a note type (is skipped if whole deck is one note type)  
④ Select the field containing the Japanese expression  
![](https://raw.githubusercontent.com/IllDepence/anki_add_pitch_plugin/master/doc/ankiweb_img/dialog_1.png)

⑤ Select the field containing the reading  
⑥ Select the field to which the pitch accent info will be added  
⑦ Done  
![](https://raw.githubusercontent.com/IllDepence/anki_add_pitch_plugin/master/doc/ankiweb_img/dialog_2.png)

Result  
![](https://raw.githubusercontent.com/IllDepence/anki_add_pitch_plugin/master/doc/ankiweb_img/output.jpg)



---

# Additional Features

Add, edit, or remove pitch annotations of single cards with the card editor's pitch accent buttons.  
![](https://raw.githubusercontent.com/IllDepence/anki_add_pitch_plugin/master/doc/ankiweb_img/editor_1.jpg)&emsp;![](https://raw.githubusercontent.com/IllDepence/anki_add_pitch_plugin/master/doc/ankiweb_img/editor_2.jpg)

Annotations sync to mobile (e.g. AnkiDroid) as well as AnkiWeb  
![](https://raw.githubusercontent.com/IllDepence/anki_add_pitch_plugin/master/doc/ankiweb_img/plattforms.jpg)

Annotations are customizable via CSS  
![](https://raw.githubusercontent.com/IllDepence/anki_add_pitch_plugin/master/doc/ankiweb_img/css.jpg)

**Example usage**

```css
svg.pitch { height: 150px; width: auto; }
svg.pitch text { font-weight: bold !important; }
svg.pitch > path { stroke: #fa7 !important; }
svg.pitch > circle[r="5"] { fill: #fa7 !important; }
svg.pitch > circle[r="3.25"] { fill: #cf9 !important; }
```

If you’re using **night mode**, use the following style to invert the pitch accent color.

```css
.nightMode svg.pitch {
    filter: invert(1);
}
```

For further details on styling, see [Pitch accent annotation styling](https://github.com/IllDepence/anki_add_pitch_plugin/blob/master/doc/styling.md) on Github.

---

# Limitations

① Does only support words (and some expressions), but not whole sentences.  
② If the field in a card with the Japanese expression contains additional text, pitch accent lookup might fail (e.g. “&lt;数字&gt;頭” in a card for the counter of large animals).  
③ When an expression has several possible readings (e.g. 汚れ) the script tries to determine which one is used by inspecting the reading field of the card. This does not always work.



---

# Report Issues & Make Suggestions

→ [GitHub](https://github.com/IllDepence/anki_add_pitch_plugin/issues)



---

# Changelog

(details: [source code](https://github.com/IllDepence/anki_add_pitch_plugin))

2026/09/14 -- Fix pitch adding in card editor on Anki 26.08 upwards. Make it more easy to style/hide the separator line (*only applies to annotations added with this or later versions; [details here](https://github.com/IllDepence/anki_add_pitch_plugin/blob/a58e2a732f14d1397b6db306ea0151200890b720/doc/styling.md#quick-guide--examples))  
2023/05/07 -- Add function to automatically set single pitch. Make add-on Qt6 compatible. Various stability, performance and UI improvements.  
2022/03/26 -- Fix bugs concerning functionality to manually add/edit/remove annotations. (Thanks kclisp)  
2022/01/23 -- Update pitch accent DB (from roughly 100k to 200k entries).  
2021/08/22 -- Add cancel buttons to selection dialogs.  
2021/01/26 -- Add support for successive bulk adding of annotations to different fields of notes.  
2020/10/05 -- Add functionality to manually add/edit/remove annotations.  
2020/08/02 -- Make code compatible with new Anki 2.1.29 DB schema.  
2019/09/22 -- Add support for multiple note types within a single deck.
