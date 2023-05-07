""" Utility functions.
"""

import os
import re
from aqt import mw
from aqt.utils import Qt, QDialog, QVBoxLayout, QLabel, QListWidget,\
                      QDialogButtonBox
from anki.utils import strip_html
from functools import lru_cache
from .draw_pitch import pitch_svg
from ._constants import re_ja_patt, re_hira_patt, re_variation_selectors_patt,\
                        re_bracketed_content_patt


def get_qt_version():
    """ Return the version of Qt used by Anki.
    """

    qt_ver = 5  # assume 5 for now

    if Qt.__module__ == 'PyQt5.QtCore':
        # PyQt5
        # tested on aqt[qt5]
        qt_ver = 5
    elif Qt.__module__ == 'PyQt6.QtCore':
        # PyQt6
        # tested on aqt[qt6]
        qt_ver = 6

    # NOTE
    # when Anki runs with the temporary Qt5 compatibility
    # shims, Qt.__module__ is 'PyQt6.sip.wrappertype', but
    # then it should also be no problem to defer to 5

    return qt_ver


def get_plugin_dir_path():
    """ Determine and return the path of the plugin directory.
    """

    collection_path = mw.col.path
    plugin_dir_name = __name__.split('.')[0]  # remove “.util”

    user_dir_path = os.path.split(collection_path)[0]
    anki_dir_path = os.path.split(user_dir_path)[0]
    plugin_dir_path = os.path.join(anki_dir_path, 'addons21', plugin_dir_name)

    return plugin_dir_path


def customChooseList(msg, choices, startrow=0):
    """ Copy of https://github.com/ankitects/anki/blob/main/
        qt/aqt/utils.py but with a cancel button and title
        parameter added.
    """

    parent = mw.app.activeWindow()
    d = QDialog(parent)
    if get_qt_version() == 6:
        d.setWindowModality(Qt.WindowModality.WindowModal)
    else:
        d.setWindowModality(Qt.WindowModal)
    # d.setWindowTitle('TODO'  # added
    l = QVBoxLayout()
    d.setLayout(l)
    t = QLabel(msg)
    l.addWidget(t)
    c = QListWidget()
    c.addItems(choices)
    c.setCurrentRow(startrow)
    l.addWidget(c)
    if get_qt_version() == 6:
        buts = QDialogButtonBox.StandardButton.Ok | \
               QDialogButtonBox.StandardButton.Cancel
    else:
        buts = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
    bb = QDialogButtonBox(buts)
    l.addWidget(bb)
    bb.accepted.connect(d.accept)
    bb.rejected.connect(d.reject)
    l.addWidget(bb)
    if get_qt_version() == 6:
        ret = d.exec()  # 1 if Ok, 0 if Cancel or window closed
    else:
        ret = d.exec_()  # 1 if Ok, 0 if Cancel or window closed
    if ret == 0:
        return None  # can't be False b/c False == 0
    return c.currentRow()


def select_deck_id(msg):
    """ UI dialog that prints <msg> as a prompt to
        the user shows a list of all decks in the
        collection.
        Returns the ID of the selected deck or None
        if dialog is cancelled.
    """

    decks = mw.col.decks.all()
    choices = [d['name'] for d in decks]
    choice_idx = customChooseList(msg, choices)
    if choice_idx is None:
        return None
    return decks[choice_idx]['id']


def select_note_type_id(note_type_ids):
    """ UI dialog that prompts the user to select a
        note type.
        Returns the ID of the selected name type or
        None if dialog is cancelled.
    """

    note_types = mw.col.models.all()
    choices = [
        {'id': nt['id'], 'name': nt['name']}
        for nt in note_types
        if nt['id'] in note_type_ids
    ]
    choice_idx = customChooseList(
        'Select a note type.',
        [c['name'] for c in choices]
    )
    if choice_idx is None:
        return None
    return choices[choice_idx]['id']


@lru_cache(maxsize=1)
def get_accent_dict(path=None):

    if path is None:
        # load the default pitch accent dict
        path = os.path.join(
            get_plugin_dir_path(),
            'wadoku_pitchdb.csv'
        )

    acc_dict = {}
    with open(path, encoding='utf8') as f:
        for line in f:
            orths_txt, hira, hz, accs_txt, patts_txt = line.strip().split(
                '\u241e'
            )
            orth_txts = orths_txt.split('\u241f')
            if clean_orth(orth_txts[0]) != orth_txts[0]:
                orth_txts = [clean_orth(orth_txts[0])] + orth_txts
            patts = patts_txt.split(',')
            patt_common = patts[0]  # TODO: extend to support variants?
            if is_katakana(orth_txts[0]):
                hira = hira_to_kata(hira)
            for orth in orth_txts:
                if orth not in acc_dict:
                    acc_dict[orth] = []
                new = True
                for patt in acc_dict[orth]:
                    if patt[0] == hira and patt[1] == patt_common:
                        new = False
                        break
                if new:
                    acc_dict[orth].append((hira, patt_common))
    return acc_dict


@lru_cache(maxsize=1)
def get_user_accent_dict(path=None):

    if path is None:
        # load the user custom pitch accent dict
        path = os.path.join(
            get_plugin_dir_path(),
            'user_pitchdb.csv'
        )
        if not os.path.isfile(path):
            return {}

    acc_dict = {}
    with open(path, encoding='utf8') as f:
        for line in f:
            orth, hira, patt = line.strip().split('\t')
            if orth in acc_dict:
                acc_dict[orth].append((hira, patt))
            else:
                acc_dict[orth] = [(hira, patt)]
    return acc_dict


def get_note_type_ids(deck_id):
    """ Return a list of the IDs of note types used
        in a deck.
    """

    card_ids = mw.col.decks.cids(deck_id)
    note_type_ids = set(
        [mw.col.get_card(cid).note_type()['id'] for cid in card_ids]
    )
    return list(note_type_ids)


def get_note_ids(deck_id, note_type_id):
    """ Return a list of the IDs of notes, given a
        deck ID and note type ID.
    """

    note_ids = []
    deck_card_ids = mw.col.decks.cids(deck_id)
    for cid in deck_card_ids:
        c = mw.col.get_card(cid)
        if c.note_type()['id'] == note_type_id and c.nid not in note_ids:
            note_ids.append(c.nid)
    return note_ids


def select_note_fields_add(note_type_id):
    """ For a given note type, prompt the user to select which field
        - contain the Japanese expression
        - contain the reading
        - the pitch accent should be shown in
        and return the respective indices of those fields in the note
        type’s list of fields.
    """

    choices = [nt['name'] for nt in mw.col.models.get(note_type_id)['flds']]
    expr_idx = customChooseList(
        'Which field contains the Japanese expression?', choices
    )
    if expr_idx is None:
        return None, None, None
    reading_idx = customChooseList(
        'Which field contains the reading?', choices
    )
    if reading_idx is None:
        return None, None, None
    output_idx = customChooseList(
        'Which field should the pitch accent be shown in?', choices
    )
    if output_idx is None:
        return None, None, None
    return expr_idx, reading_idx, output_idx


def select_note_fields_del(note_type_id):
    """ For a given note type, prompt the user to select which field
        the pitch accent should be removed from, and return the respective
        index of this field in the note type’s list of fields.
    """
    choices = [nt['name'] for nt in mw.col.models.get(note_type_id)['flds']]
    del_idx = customChooseList(
        'Which field should the pitch accent be removed from?', choices
    )
    return del_idx


def remove_bracketed_content(dirty):
    """ Remove backets and their contents.
    """

    clean = re_bracketed_content_patt.sub('', dirty)
    return clean


def remove_variation_selectors(dirty):
    """ Remove backets and their contents.
    """

    clean = re_variation_selectors_patt.sub('', dirty)
    return clean


def clean_japanese_from_note_field(dirty):
    """ Perform heuristic cleaning of an note field and return
        - the first consecutive string of Japanese if present
        - None otherwise
    """

    # heuristic cleaning
    no_html = strip_html(dirty)
    no_brack_html = remove_bracketed_content(no_html)
    no_varsel_brack_html = remove_variation_selectors(no_brack_html)
    # look for Japanese writing in expression field
    ja_match = re_ja_patt.search(no_varsel_brack_html)
    if ja_match:
        # return rist consecutive match
        return ja_match.group(0)
    # no Japanese text in field
    return None


def get_acc_patt(expr_field, reading_field, dicts):
    """ Determine the accept pattern for a note given its
        - expression field
        - reading field
        - accent pattern dictionaries to use for lookup
    """

    def select_best_patt(reading_field, patts):
        best_pos = 9001
        best = patts[0]  # default
        for patt in patts:
            hira, _ = patt
            try:
                pos = reading_field.index(hira)
                if pos < best_pos:
                    best = patt
                    best_pos = pos
            except ValueError:
                continue
        return best
    expr_guess = clean_japanese_from_note_field(expr_field)
    if expr_guess is None:
        return False
    # look for hiragana in reading field
    hira_match = re_hira_patt.search(reading_field)
    if hira_match:
        reading_guess = hira_match.group(0)
    else:
        reading_guess = ''
    # dictionary lookup
    for dic in dicts:
        patts = dic.get(expr_guess, False)
        if patts:
            return select_best_patt(reading_guess, patts)
    return False


def add_pitch(acc_dict, note_ids, expr_idx, reading_idx, output_idx):
    """ Add pitch accent illustration to notes.

        Returns stats on how it went.
    """

    not_found_list = []
    num_updated = 0
    num_already_done = 0
    num_svg_fail = 0
    for nid in note_ids:
        # set up note access
        note = mw.col.get_note(nid)
        expr_fld = note.keys()[expr_idx]
        reading_fld = note.keys()[reading_idx]
        output_fld = note.keys()[output_idx]
        # check for existing illustrations
        has_auto_accent = '<!-- accent_start -->' in note[output_fld]
        has_manual_accent = '<!-- user_accent_start -->' in note[output_fld]
        if has_auto_accent or has_manual_accent:
            # already has a pitch accent illustration
            num_already_done += 1
            continue
        # determine accent pattern
        expr_field = note[expr_fld].strip()
        reading_field = note[reading_fld].strip()
        patt = get_acc_patt(expr_field, reading_field, [acc_dict])
        if not patt:
            not_found_list.append([nid, expr_field])
            continue
        hira, LlHh_patt = patt
        LH_patt = re.sub(r'[lh]', '', LlHh_patt)
        # generate SVG for accent pattern
        svg = pitch_svg(hira, LH_patt)
        if not svg:
            num_svg_fail += 1
            continue
        if len(note[output_fld]) > 0:
            separator = '<br><hr><br>'
        else:
            separator = ''
        # extend and save note
        note[output_fld] = (
            '{}<!-- accent_start -->{}{}<!-- accent_end -->'
            ).format(note[output_fld], separator, svg)  # add svg
        mw.col.update_note(note)
        num_updated += 1
    return not_found_list, num_updated, num_already_done, num_svg_fail


def remove_pitch(note_ids, del_idx, user_set=False):
    """ Remove pitch accent illustrations from a specified field.

        Returns stats on how that went.
    """

    # determine accent pattern to search for
    if user_set:
        tag_prefix = 'user_'
    else:
        tag_prefix = ''
    acc_patt = re.compile(
        r'<!-- {}accent_start -->.+<!-- {}accent_end -->'.format(
            tag_prefix, tag_prefix
        ),
        re.S
    )
    num_updated = 0
    num_already_done = 0
    for nid in note_ids:
        # set up note access
        note = mw.col.get_note(nid)
        del_fld = note.keys()[del_idx]
        # check for cards w/o accent illustrations
        if ' {}accent_start'.format(tag_prefix) not in note[del_fld]:
            # has no pitch accent illustration
            num_already_done += 1
            continue
        # update and save note
        note[del_fld] = re.sub(acc_patt, '', note[del_fld])
        mw.col.update_note(note)
        num_updated += 1
    return num_already_done, num_updated


def hira_to_kata(s):
    """ Convert hiragana to katakana.
    """

    return ''.join(
        [chr(ord(ch) + 96) if ('ぁ' <= ch <= 'ゔ') else ch for ch in s]
        )


def is_katakana(s):
    """ Determine if more than half of the characters in a
        string are katakana.
    """

    num_ktkn = 0
    for ch in s:
        if ch == 'ー' or ('ァ' <= ch <= 'ヴ'):
            num_ktkn += 1
    return num_ktkn / max(1, len(s)) > .5


def clean_orth(orth):
    """ Remove symbols from a string (used such that the remainder
        ideally is a clean word that can be looked up in the
        dictionary).
    """

    # remove characters used in Wadoku orthography notation
    # that likely won't appear on Anki cards
    orth = re.sub('[()△×･〈〉{}]', '', orth)
    # change affix indicator from ellipsis (as used in Wadoku)
    # to wave dash (as used by the author in Anki)
    # (NOTE: the current preprocessing used for Japanese expressions
    #  is done in clean_japanese_from_note_field using the pattern
    #  re_ja_patt, which does not include '…' and '〜'. This means
    #  the replacement below does have no effect. Keeping it in for
    #  the moment anyway in case affix markers become relevant in
    #  the future)
    orth = orth.replace('…', '〜')
    return orth
