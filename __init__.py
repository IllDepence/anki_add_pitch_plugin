""" Anki plugin to add pitch accent indicators to cards.

    This plugin makes use of data from Wadoku by Ulrich Apel.
    (See file wadoku_parse.py for more details.)
    Wadoku license information is available on the web:

    http://www.wadoku.de/wiki/display/WAD/Wörterbuch+Lizenz
    http://www.wadoku.de/wiki/display/WAD/%28Vorschlag%29+Neue+Wadoku-Daten+Lizenz
"""

import json
import os
import re
import time
from aqt import mw, gui_hooks
from aqt.utils import showInfo, chooseList, getOnlyText
from aqt.qt import *
from anki.storage import Collection

def add_pitch_dialog():
    # environment
    collection_path = mw.col.path
    plugin_dir_name = __name__

    user_dir_path = os.path.split(collection_path)[0]
    anki_dir_path = os.path.split(user_dir_path)[0]
    plugin_dir_path = os.path.join(anki_dir_path, 'addons21', plugin_dir_name)

    # plugin utils import
    pa_util = __import__('{}.util'.format(plugin_dir_name), fromlist=('foo'))

    # load pitch dict
    pitch_csv_path = os.path.join(plugin_dir_path, 'wadoku_pitchdb.csv')
    acc_dict = pa_util.get_accent_dict(pitch_csv_path)

    # figure out collection structure
    deck_id = pa_util.select_deck_id('Which deck would you like to extend?')
    note_type_ids = pa_util.get_note_type_ids(deck_id)
    if len(note_type_ids) > 1:
        note_type_id = pa_util.select_note_type(note_type_ids)
    elif len(note_type_ids) < 1:
        showInfo('No cards found.')
        return
    else:
        note_type_id = note_type_ids[0]
    note_ids = pa_util.get_note_ids(deck_id, note_type_id)
    expr_idx, rdng_idx, out_idx = pa_util.select_note_fields_all(note_ids[0])

    # extend notes
    nf_lst, n_updt, n_adone, n_sfail = pa_util.add_pitch(
        acc_dict, plugin_dir_name, note_ids, expr_idx, rdng_idx, out_idx
        )
    showInfo(('done :)\n'
        'skipped {} already annotated notes\n'
        'updated {} notes\n'
        'failed to generate {} annotations\n'
        'could not find {} expressions').format(
            n_adone, n_updt, n_sfail, len(nf_lst)
            )
        )

def remove_pitch_dialog():
    # environment
    collection_path = mw.col.path
    plugin_dir_name = __name__

    user_dir_path = os.path.split(collection_path)[0]
    anki_dir_path = os.path.split(user_dir_path)[0]
    plugin_dir_path = os.path.join(anki_dir_path, 'addons21', plugin_dir_name)

    # plugin utils import
    pa_util = __import__('{}.util'.format(plugin_dir_name), fromlist=('foo'))

    # figure out collection structure
    deck_id = pa_util.select_deck_id(
        'From which deck would you like to remove?'
        )
    note_type_ids = pa_util.get_note_type_ids(deck_id)
    if len(note_type_ids) > 1:
        note_type_id = pa_util.select_note_type(note_type_ids)
    elif len(note_type_ids) < 1:
        showInfo('No cards found.')
        return
    else:
        note_type_id = note_type_ids[0]
    note_ids = pa_util.get_note_ids(deck_id, note_type_id)
    del_idx = pa_util.select_note_fields_del(note_ids[0])

    # remove from notes
    n_adone, n_updt  = pa_util.remove_pitch(note_ids, del_idx)
    showInfo(('done :)\n'
        'skipped {} notes w/o accent annotation\n'
        'updated {} notes').format(
            n_adone, n_updt
            )
        )

def set_pitch_dialog(editor):
    # get user input
    hira = getOnlyText('Enter the reading to be set. (Example: はな)')
    LH_patt = getOnlyText('Enter the pitch accent pattern as a sequence of \'H\'s and \'L\'s. (Example: LHL)')

    # get note data
    data = [
        (fld, editor.mw.col.media.escapeImages(val)) for fld, val in editor.note.items()
    ]

    # remove existing patt
    acc_patt = re.compile(r'<!-- accent_start -->.+<!-- accent_end -->', re.S)
    old_field_val = data[editor.web.editor.currentField][1]
    old_field_val_clean = re.sub(acc_patt, '', old_field_val)

    # generate SVG
    plugin_dir_name = __name__
    draw_pitch = __import__(
        '{}.draw_pitch'.format(plugin_dir_name), fromlist=('foo')
        )
    svg = draw_pitch.pitch_svg(hira, LH_patt)
    if len(old_field_val_clean) > 0:
        separator = '<br><hr><br>'
    else:
        separator = ''
    new_field_val = (
        '{}<!-- accent_start -->{}{}<!-- accent_end -->'
        ).format(old_field_val_clean, separator, svg)

    # add new patt
    data[editor.web.editor.currentField] = (
        data[editor.web.editor.currentField][0],            # leave field name as is
        new_field_val                                       # update field value
    )
    js = 'setFields(%s); setFonts(%s); setNoteId(%s)' % (
        json.dumps(data),
        json.dumps(editor.fonts()),
        json.dumps(editor.note.id)
    )
    editor.web.eval(js)

def addPitchButton(buttons, editor):
    # environment
    collection_path = mw.col.path
    plugin_dir_name = __name__

    user_dir_path = os.path.split(collection_path)[0]
    anki_dir_path = os.path.split(user_dir_path)[0]
    plugin_dir_path = os.path.join(anki_dir_path, 'addons21', plugin_dir_name)
    icon_path = os.path.join(plugin_dir_path, 'icon.png')

    btn = editor.addButton(icon_path,
                         'foo',
                         set_pitch_dialog,
                         tip='set pitch accent')
    buttons.append(btn)

# add menu items
pa_menu = QMenu('Pitch Accent', mw)
pa_menu_add = pa_menu.addAction('add')
pa_menu_remove = pa_menu.addAction('remove')
# add triggers
pa_menu_add.triggered.connect(add_pitch_dialog)
pa_menu_remove.triggered.connect(remove_pitch_dialog)
# and add it to the tools menu
mw.form.menuTools.addMenu(pa_menu)
# add editor button
gui_hooks.editor_did_init_buttons.append(addPitchButton)
