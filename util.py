""" Utility functions.
"""

import json
import re
import time
from aqt import mw
from aqt.utils import chooseList
from anki.utils import stripHTML
from .draw_pitch import pitch_svg

def select_deck_id(msg):
    decks = []
    for row in mw.col.db.execute('SELECT id, name FROM decks'):
        d_id = row[0]
        d_name = row[1]
        decks.append((d_id, d_name))
    choices = [deck[1] for deck in decks]
    choice = chooseList(msg, choices)
    return decks[choice][0]

def select_note_type(note_type_ids):
    note_types = []
    for row in  mw.col.db.execute('SELECT id, name FROM notetypes'):
        n_id = row[0]
        n_name = row[1]
        note_types.append((n_id, n_name))
    choices = [note_type[1] for note_type in note_types]
    choice = chooseList(
        'Select a note type.',
        choices
        )
    return note_types[choice][0]

def get_accent_dict(path):
    acc_dict = {}
    with open(path, encoding='utf8') as f:
        for line in f:
            orths_txt, hira, hz, accs_txt, patts_txt = line.strip().split('\u241e')
            orth_txts = orths_txt.split('\u241f')
            if clean_orth(orth_txts[0]) != orth_txts[0]:
                orth_txts = [clean_orth(orth_txts[0])] + orth_txts
            patts = patts_txt.split(',')
            patt_common = patts[0]  # TODO: extend to support variants?
            if is_katakana(orth_txts[0]):
                hira = hira_to_kata(hira)
            for orth in orth_txts:
                if not orth in acc_dict:
                    acc_dict[orth] = []
                new = True
                for patt in acc_dict[orth]:
                    if patt[0] == hira and patt[1] == patt_common:
                        new = False
                        break
                if new:
                    acc_dict[orth].append((hira, patt_common))
    return acc_dict

def get_user_accent_dict(path):
    acc_dict = {}
    with open(path, encoding='utf8') as f:
        for line in f:
            orth, hira, patt = line.strip().split('\t')
            acc_dict[orth] = [(hira, patt)]
    return acc_dict

def get_note_type_ids(deck_id):
    note_type_ids = []
    for row in mw.col.db.execute(
        'SELECT distinct mid FROM notes WHERE id IN (SELECT nid FROM'
        ' cards WHERE did = ?) ORDER BY id', deck_id):
        mid = row[0]
        note_type_ids.append(mid)
    return note_type_ids

def get_note_ids(deck_id, note_type):
    note_ids = []
    for row in mw.col.db.execute(
        'SELECT id FROM notes WHERE mid = ? AND id IN (SELECT nid FROM'
        ' cards WHERE did = ?) ORDER BY id', note_type, deck_id):
        nid = row[0]
        note_ids.append(nid)
    return note_ids

def select_note_fields_all(note_id):
    example_row = mw.col.db.first(
        'SELECT flds FROM notes WHERE id = ?', note_id)
    example_flds = example_row[0].split('\x1f')
    choices = ['[{}] {}'.format(i, fld[:20]) for i, fld
               in enumerate(example_flds)]
    expr_idx = chooseList(
        'Which field contains the Japanese expression?', choices
        )
    reading_idx = chooseList(
        'Which field contains the reading?', choices
        )
    output_idx = chooseList(
        'Which field should the pitch accent be shown in?', choices
        )
    return expr_idx, reading_idx, output_idx

def select_note_fields_del(note_id):
    example_row = mw.col.db.first(
        'SELECT flds FROM notes WHERE id = ?', note_id)
    example_flds = example_row[0].split('\x1f')
    choices = ['[{}] {}'.format(i, fld[:20]) for i, fld
               in enumerate(example_flds)]
    del_idx = chooseList(
        'Which field should the pitch accent be removed from?', choices
        )
    return del_idx

def clean(s):
    # remove HTML
    s = stripHTML(s)
    # remove everyhing in brackets
    s = re.sub(r'[\[\(\{][^\]\)\}]*[\]\)\}]', '', s)
    return s.strip()

def get_acc_patt(expr_field, reading_field, dicts):
    def select_best_patt(reading_field, patts):
        best_pos = 9001
        best = patts[0]  # default
        for patt in patts:
            hira, p = patt
            try:
                pos = reading_field.index(hira)
                if pos < best_pos:
                    best = patt
                    best_pos = pos
            except ValueError:
                continue
        return best
    expr_field = clean(expr_field)
    reading_field = clean(reading_field)
    if len(expr_field) == 0:
        return False
    for dic in dicts:
        patts = dic.get(expr_field, False)
        if patts:
            return select_best_patt(reading_field, patts)
        guess = expr_field.split(' ')[0]
        patts = dic.get(guess, False)
        if patts:
            return select_best_patt(reading_field, patts)
        guess = re.sub('[<&]', ' ', expr_field).split(' ')[0]
        patts = dic.get(guess, False)
        if patts:
            return select_best_patt(reading_field, patts)
    return False

def add_pitch(acc_dict, plugin_dir_name, note_ids, expr_idx, reading_idx,
              output_idx):
    not_found_list = []
    num_updated = 0
    num_already_done = 0
    num_svg_fail = 0
    for nid in note_ids:
        row = mw.col.db.first(
            'SELECT flds FROM notes WHERE id = ?', nid
            )
        flds_str = row[0]
        fields = flds_str.split('\x1f')
        if ('<!-- accent_start -->' in fields[output_idx] or
            '<!-- user_accent_start -->' in fields[output_idx]):
            # already has pitch accent image
            num_already_done += 1
            continue
        expr_field = fields[expr_idx].strip()
        reading_field = fields[reading_idx].strip()
        patt = get_acc_patt(expr_field, reading_field, [acc_dict])
        if not patt:
            not_found_list.append([nid, expr_field])
            continue
        hira, LlHh_patt = patt
        LH_patt = re.sub(r'[lh]', '', LlHh_patt)
        svg = pitch_svg(hira, LH_patt)
        if not svg:
            num_svg_fail += 1
            continue
        if len(fields[output_idx]) > 0:
            separator = '<br><hr><br>'
        else:
            separator = ''
        fields[output_idx] = (
            '{}<!-- accent_start -->{}{}<!-- accent_end -->'
            ).format(fields[output_idx], separator, svg)  # add svg
        new_flds_str = '\x1f'.join(fields)
        mod_time = int(time.time())
        mw.col.db.execute(
            'UPDATE notes SET usn = ?, mod = ?, flds = ? WHERE id = ?',
            -1, mod_time, new_flds_str, nid
            )
        num_updated += 1
    return not_found_list, num_updated, num_already_done, num_svg_fail

def remove_pitch(note_ids, del_idx, user_set=False):
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
        row = mw.col.db.first('SELECT flds FROM notes WHERE id = ?', nid)
        flds_str = row[0]
        fields = flds_str.split('\x1f')
        if ' {}accent_start'.format(tag_prefix) not in fields[del_idx]: #FIXME
            # has no pitch accent image
            num_already_done += 1
            continue
        fields[del_idx] = re.sub(acc_patt, '', fields[del_idx])
        new_flds_str = '\x1f'.join(fields)
        mod_time = int(time.time())
        mw.col.db.execute(
            'UPDATE notes SET usn = ?, mod = ?, flds = ? WHERE id = ?',
            -1, mod_time, new_flds_str, nid)
        num_updated += 1
    return num_already_done, num_updated

def hira_to_kata(s):
    return ''.join(
        [chr(ord(ch) + 96) if ('ぁ' <= ch <= 'ゔ') else ch for ch in s]
        )

def is_katakana(s):
    num_ktkn = 0
    for ch in s:
        if ch == 'ー' or ('ァ' <= ch <= 'ヴ'):
            num_ktkn += 1
    return num_ktkn / max(1, len(s)) > .5

def clean_orth(orth):
    orth = re.sub('[()△×･〈〉{}]', '', orth)  # 
    orth = orth.replace('…', '〜')  # change depending on what you use
    return orth
