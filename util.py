""" Utility functions.
"""

import json
import re
import time
from aqt import mw
from aqt.utils import chooseList

def select_deck_id(msg):
    decks = []
    for row in mw.col.db.execute('SELECT decks FROM col'):
        deks = json.loads(row[0])
        for key in deks:
            d_id = deks[key]['id']
            d_name = deks[key]['name']
            decks.append((d_id, d_name))
    choices = [deck[1] for deck in decks]
    choice = chooseList(msg, choices)
    return decks[choice][0]

def get_accent_dict(path):
    acc_dict = {}
    with open(path) as f:
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

def get_note_ids(deck_id):
    note_ids = []
    for row in mw.col.db.execute(
        'SELECT id FROM notes WHERE id IN (SELECT nid FROM'
        ' cards WHERE did = :did) ORDER BY id', did=deck_id):
        nid = row[0]
        note_ids.append(nid)
    return note_ids

def select_note_fields(note_id):
    example_row = mw.col.db.first(
        'SELECT flds FROM notes WHERE id = :nid', nid=note_id)
    example_flds = example_row[0].split('\x1f')
    choices = [fld[:20] for fld in example_flds if len(fld) > 0]
    expr_idx = chooseList(
        'Which field contains the Japanese expression?', choices
        )
    reading_idx = chooseList(
        'Which field contains the reading?', choices
        )
    return expr_idx, reading_idx

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
    expr_field = expr_field.replace('[\d]', '')
    expr_field = expr_field.replace('[^\d]', '')
    expr_field = expr_field.strip()
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

def add_pitch(acc_dict, plugin_dir_name, note_ids, expr_idx, reading_idx):
    draw_pitch = __import__(
        '{}.draw_pitch'.format(plugin_dir_name), fromlist=('foo')
        )
    not_found_list = []
    num_updated = 0
    num_already_done = 0
    num_svg_fail = 0
    for nid in note_ids:
        row = mw.col.db.first(
            'SELECT flds FROM notes WHERE id = :nid', nid=nid
            )
        flds_str = row[0]
        if '<!-- accent_start -->' in flds_str:
            # already has pitch accent image
            num_already_done += 1
            continue
        fields = flds_str.split('\x1f')
        expr_field = fields[expr_idx].strip()
        reading_field = fields[reading_idx].strip()
        patt = get_acc_patt(expr_field, reading_field, [acc_dict])
        if not patt:
            not_found_list.append([nid, expr_field])
            continue
        hira, LlHh_patt = patt
        LH_patt = re.sub(r'[lh]', '', LlHh_patt)
        svg = draw_pitch.pitch_svg(hira, LH_patt)
        if not svg:
            num_svg_fail += 1
            continue
        fields[reading_idx] = (
            '{}<!-- accent_start --><br><hr><br>{}<!-- accent_end -->'
            ).format(fields[reading_idx], svg)  # add svg
        new_flds_str = '\x1f'.join(fields)
        mod_time = int(time.time())
        mw.col.db.execute(
            'UPDATE notes SET usn = ?, mod = ?, flds = ? WHERE id = ?',
            -1, mod_time, new_flds_str, nid
            )
        num_updated += 1
    return not_found_list, num_updated, num_already_done, num_svg_fail

def remove_pitch(note_ids, expr_idx, reading_idx):
    acc_patt = re.compile(r'<!-- accent_start -->.+<!-- accent_end -->', re.S)
    num_updated = 0
    num_already_done = 0
    for nid in note_ids:
        row = mw.col.db.first('SELECT flds FROM notes WHERE id = :nid', nid=nid)
        flds_str = row[0]
        if 'accent_start' not in flds_str:
            # has no pitch accent image
            num_already_done += 1
            continue
        fields = flds_str.split('\x1f')
        fields[reading_idx] = re.sub(acc_patt, '', fields[reading_idx])
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
    cardCount = mw.col.cardCount()
    ret = chooseList('prompt', ['a', 'b', 'c'])
    showInfo('ret: {}'.format(ret))
