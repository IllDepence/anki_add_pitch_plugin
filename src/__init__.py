""" Anki plugin to add pitch accent indicators to cards.

    This plugin makes use of data from Wadoku by Ulrich Apel.
    (See file wadoku_parse.py for more details.)
    Wadoku license information is available on the web:

    http://www.wadoku.de/wiki/display/WAD/Wörterbuch+Lizenz
    http://www.wadoku.de/wiki/display/WAD/%28Vorschlag%29+Neue+Wadoku-Daten+Lizenz
"""

__author__ = 'Tarek Saier'
__credits__ = ['kclisp', 'Peter Maxwell']
__license__ = 'MIT'

import json
import os
import re
from aqt import mw, gui_hooks
from aqt.utils import showInfo, showText, getText
from aqt.qt import QMenu
from ._version import __version__
from ._constants import re_all_hira_patt
from .util import add_pitch, remove_pitch, get_accent_dict, get_note_type_ids,\
                  get_note_ids, get_user_accent_dict, select_deck_id,\
                  select_note_type_id, select_note_fields_add,\
                  select_note_fields_del, get_plugin_dir_path,\
                  get_acc_patt, clean_japanese_from_note_field
from .draw_pitch import pitch_svg


def about_dialog():
    """ Popup displaying information about the add-on.
    """

    gh_link = 'https://github.com/IllDepence/anki_add_pitch_plugin'
    aw_link = 'https://ankiweb.net/shared/info/148002038'
    license_link = gh_link + '/blob/master/LICENSE'

    info_text = (
        '<center>'
        '<h3>Japanese Pitch Accent</h3>'
        '<p><b>Version</b><br>{version}</p>'
        '<p><b>License</b><br>'
        '<a href="{license_link}">{license_name}</a>'
        '</p>'
        '<p><b>Maintainer</b><br>{author}</p>'
        '<p><b>Contributors</b><br>{contrib}</p>'
        '<p><a href="{gh_link}">GitHub</a>'
        '&nbsp;<b>&middot;</b>&nbsp;'
        '<a href="{aw_link}">AnkiWeb</a></p>'
        '</center>'
    ).format(
        version=__version__,
        license_link=license_link,
        license_name=__license__,
        author=__author__,
        contrib='<br>'.join(__credits__),
        gh_link=gh_link,
        aw_link=aw_link
    )

    showText(
        info_text,
        title='About',
        type='rich',
        minWidth=0,
        minHeight=0,
    )


def add_pitch_dialog():
    """ Dialog for bulk adding pitch accent illustrations to notes.
    """

    # load pitch dict
    acc_dict = get_accent_dict()

    # load user pitch dict if present
    acc_dict.update(
        get_user_accent_dict()
    )

    # figure out collection structure
    deck_id = select_deck_id('Which deck would you like to extend?')
    if deck_id is None:
        return
    note_type_ids = get_note_type_ids(deck_id)
    if len(note_type_ids) > 1:
        note_type_id = select_note_type_id(note_type_ids)
    elif len(note_type_ids) < 1:
        showInfo('No cards found in deck.')
        return
    else:
        note_type_id = note_type_ids[0]
    if note_type_id is None:
        return
    note_ids = get_note_ids(deck_id, note_type_id)
    if len(note_ids) == 0:
        showInfo('No cards found for selected note type.')
        return
    expr_idx, rdng_idx, out_idx = select_note_fields_add(note_type_id)
    if None in [expr_idx, rdng_idx, out_idx]:
        return

    # extend notes
    nf_lst, n_updt, n_adone, n_sfail = add_pitch(
        acc_dict, note_ids, expr_idx, rdng_idx, out_idx
    )
    report_text = (
        'done :)\n'
        'skipped {} already annotated notes\n'
        'updated {} notes\n'
        'failed to generate {} annotations\n'
        'could not find {} expressions'
    ).format(
        n_adone, n_updt, n_sfail, len(nf_lst)
    )
    showInfo(
        report_text,
        title='Bulk add results'
    )


def add_user_pitch_dialog():
    """ Popup explaining how to manually set pitch accent illustrations.
    """

    icon_img = (
        'data:image/svg+xml;base64,PHN2ZwogICB2aWV3Qm94PSIwIDAgMjIuNSAyMi41Igo'
        'gICBoZWlnaHQ9IjIyLjUiCiAgIHdpZHRoPSIyMi41IgogICBjbGFzcz0icGl0Y2giPgog'
        'IDxwYXRoCiAgICAgaWQ9InBhdGg4NTIiCiAgICAgc3R5bGU9ImZpbGw6bm9uZTtzdHJva'
        '2U6IzAwMDAwMDtzdHJva2Utd2lkdGg6MS41IgogICAgIGQ9Ik0gMi41LDE3LjUgMjAsNS'
        'IgLz4KICA8Y2lyY2xlCiAgICAgaWQ9ImNpcmNsZTg1NCIKICAgICBzdHlsZT0ib3BhY2l'
        '0eToxO2ZpbGw6IzAwMDAwMDtzdHJva2Utd2lkdGg6MSIKICAgICBjeT0iMTcuNSIKICAg'
        'ICBjeD0iMi41IgogICAgIHI9IjIuNSIgLz4KICA8Y2lyY2xlCiAgICAgaWQ9ImNpcmNsZ'
        'Tg1NiIKICAgICBzdHlsZT0ib3BhY2l0eToxO2ZpbGw6IzAwMDAwMDtzdHJva2Utd2lkdG'
        'g6MSIKICAgICBjeT0iNSIKICAgICBjeD0iMjAiCiAgICAgcj0iMi41IiAvPgogIDxjaXJ'
        'jbGUKICAgICBpZD0iY2lyY2xlODU4IgogICAgIHN0eWxlPSJvcGFjaXR5OjE7ZmlsbDoj'
        'ZmZmZmZmO3N0cm9rZS13aWR0aDoxIgogICAgIGN5PSI1IgogICAgIGN4PSIyMCIKICAgI'
        'CByPSIxLjYyNSIgLz4KPC9zdmc+Cg=='
    )

    info_text = (
        '<p>When adding or editing cards, click the pitch accent icon located '
        'on the right hand side of the text formatting buttons to manually '
        'insert, overwrite, or remove the pitch accent.<br></p>'
        '<table><tr>'
        '<td align="left" valign="middle">'
        '<img src="{}"></td>'
        '<td valign="middle" align="center">&nbsp;&larr; icon to look for</td>'
        '</tr></table>'
    ).format(
        icon_img
    )

    showInfo(
        info_text,
        title='Manually add/edit/remove',
        textFormat='rich'
    )


def show_custom_db_path_dialog():
    """ Popup explaining the user custom dictionary.
    """

    user_pitch_csv_path = os.path.join(
        get_plugin_dir_path(),
        'user_pitchdb.csv'
    )

    custom_db_text = (
        'You can extend and overwrite pitch accent patterns using the'
        ' file "{}". The file has to be three columns (expression,'
        ' reading, pitch accent pattern) separated by TAB characters.'
    ).format(
        user_pitch_csv_path
    )
    showInfo(
        custom_db_text,
        title='Custom DB path'
    )


def remove_user_pitch_dialog():
    """ Dialog for bulk removing user added custom pitch accent
        illustrations from nodes.
    """

    return remove_pitch_dialog(user_set=True)


def remove_pitch_dialog(user_set=False):
    """ Dialog for bulk removing pitch accent illustrations from nodes.
    """

    # figure out collection structure
    deck_id = select_deck_id(
        'From which deck would you like to remove?'
    )
    if deck_id is None:
        return
    note_type_ids = get_note_type_ids(deck_id)
    if len(note_type_ids) > 1:
        note_type_id = select_note_type_id(note_type_ids)
    elif len(note_type_ids) < 1:
        showInfo('No cards found in deck.')
        return
    else:
        note_type_id = note_type_ids[0]
    if note_type_id is None:
        return
    note_ids = get_note_ids(deck_id, note_type_id)
    if len(note_ids) == 0:
        showInfo('No cards found for selected note type.')
        return
    del_idx = select_note_fields_del(note_type_id)
    if del_idx is None:
        return

    # remove from notes
    n_adone, n_updt = remove_pitch(note_ids, del_idx, user_set)
    report_text = (
        'done :)\n'
        'skipped {} notes w/o accent annotation\n'
        'updated {} notes'
    ).format(
        n_adone,
        n_updt
    )
    showInfo(
        report_text,
        title='Bulk remove results'
    )


def set_pitch_manually_dialog(editor):
    """ Dialog for manually setting the pitch accent illustration
        in the currently selected editor field.
    """

    if editor.web.editor.currentField is None:
        showInfo('A field needs to be selected')
        return

    # get user input
    hira, hira_succeeded = getText(
        'Enter the reading to be set. (Example: はな)'
    )
    if not hira_succeeded:
        return

    LH_patt, LH_patt_succeeded = getText(
        ('Enter the pitch accent pattern as a sequence of \'H\'s and \'L\'s. '
         '(Example: LHL)')
    )
    if not LH_patt_succeeded:
        return

    set_pitch(editor, hira, LH_patt)


def set_pitch_automatically(editor):
    """ Automatically set the pitch accent illustration
        in the currently selected editor field.
    """

    # try to determine note fields
    expr_guess = None
    reading_guess = None
    for fld, val_unesc in editor.note.items():
        val = editor.mw.col.media.escapeImages(val_unesc)
        ja_expr = clean_japanese_from_note_field(val)
        if ja_expr is None:
            # no Japanese, next
            continue
        if expr_guess is None:
            # assume expression field comes before others,
            # so only set once (and don’t overwrite later
            # with content that might be in subsequent fields)
            expr_guess = ja_expr
        all_hira_match = re_all_hira_patt.search(ja_expr)
        if all_hira_match and reading_guess is None:
            # if first continuous block is all hiragana, treat as reading
            # and don’t override afterwards
            reading_guess = all_hira_match.group(0)
        if expr_guess is not None and reading_guess is not None:
            # found all that we needed
            break
    if expr_guess is None:
        showInfo(
            'Could not identify expression',
            title='Card parsing failure'
        )
        return
    if reading_guess is None:
        # could imagine user that just does expr to meaning (with no
        # field for reading) and then wants to add pitch accent illustrations
        reading_guess = ''

    # load pitch dict
    acc_dict = get_accent_dict()
    # load user pitch dict if present
    acc_dict.update(
        get_user_accent_dict()
    )
    patt = get_acc_patt(expr_guess, reading_guess, [acc_dict])
    if not patt:
        showInfo(
            'Could not find pitch for expression “{}”'.format(
                expr_guess
            ),
            title='Card parsing failure'
        )
        return
    hira, LlHh_patt = patt
    LH_patt = re.sub(r'[lh]', '', LlHh_patt)

    set_pitch(editor, hira, LH_patt)


def set_pitch(editor, hira, LH_patt):
    """ Set the pitch accent illustration in the editor’s current
        selected field according to the hiragana and low-high pattern
        given.
    """

    # get note data
    data = [
        (fld, editor.mw.col.media.escapeImages(val))
        for fld, val in editor.note.items()
    ]

    # remove existing patt
    acc_patt = re.compile(
        r'<!-- (user_)?accent_start -->.+<!-- (user_)?accent_end -->',
        re.S
    )
    old_field_val = data[editor.web.editor.currentField][1]
    old_field_val_clean = re.sub(acc_patt, '', old_field_val)

    # generate SVG
    svg = pitch_svg(hira, LH_patt)
    if len(old_field_val_clean) > 0:
        separator = '<br><hr><br>'
    else:
        separator = ''
    new_field_val = (
        '{}<!-- user_accent_start -->{}{}<!-- user_accent_end -->'
        ).format(old_field_val_clean, separator, svg)
    if hira == '' and LH_patt == '':
        new_field_val = old_field_val_clean

    # add new patt
    data[editor.web.editor.currentField] = (
        data[editor.web.editor.currentField][0],       # leave field name as is
        new_field_val                                  # update field value
    )
    js = 'setFields(%s); setFonts(%s); focusField(%s); setNoteId(%s)' % (
        json.dumps(data),
        json.dumps(editor.fonts()),
        json.dumps(editor.web.editor.currentField),
        json.dumps(editor.note.id)
    )
    js = gui_hooks.editor_will_load_note(js, editor.note, editor)
    editor.web.eval(js)


def add_set_pitch_buttons(buttons, editor):
    """ Add pitch buttons to editor menu.
    """

    # manual mode
    icon_path_m = os.path.join(get_plugin_dir_path(), 'icon_manual.png')
    m_btn = editor.addButton(
        icon_path_m,
        'manualpitch',
        set_pitch_manually_dialog,
        tip='set pitch accent manually'
    )
    buttons.append(m_btn)
    # auto mode
    icon_path_a = os.path.join(get_plugin_dir_path(), 'icon_auto.png')
    a_btn = editor.addButton(
        icon_path_a,
        'autopitch',
        set_pitch_automatically,
        tip='set pitch accent automatically'
    )
    buttons.append(a_btn)


def pre_load_pitch_data(col):
    """ Pre-load pitch accent dictionaries (will get cached)
    """

    _ = get_accent_dict()
    _ = get_user_accent_dict()

    return None


# add menu items
pa_menu = QMenu('Pitch Accent', mw)
pa_menu_add = pa_menu.addAction('bulk add')
pa_menu_remove = pa_menu.addAction('bulk remove')
pa_menu_add_user = pa_menu.addAction('manually add/edit/remove')
pa_menu_remove_user = pa_menu.addAction('remove all manually set')
pa_menu_custom_db_path = pa_menu.addAction('show custom DB path')
pa_menu_about = pa_menu.addAction('about')
# add triggers
pa_menu_add.triggered.connect(add_pitch_dialog)
pa_menu_remove.triggered.connect(remove_pitch_dialog)
pa_menu_add_user.triggered.connect(add_user_pitch_dialog)
pa_menu_remove_user.triggered.connect(remove_user_pitch_dialog)
pa_menu_custom_db_path.triggered.connect(show_custom_db_path_dialog)
pa_menu_about.triggered.connect(about_dialog)
# and add it to the tools menu
mw.form.menuTools.addMenu(pa_menu)
# add editor button
gui_hooks.editor_did_init_buttons.append(add_set_pitch_buttons)

# # pre-load pitch accent dicts once collection is loaded
# gui_hooks.collection_did_load.append(pre_load_pitch_data)
# # commented out for the moment because presumably for most people
# # starting Anki is *way* more frequent than starting Anki and
# # working with the bulk add function
