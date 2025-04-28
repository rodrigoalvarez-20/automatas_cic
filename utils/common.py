import os
import sys


def parse_arguments():
    if len(sys.argv) != 3:
        raise Exception(
            "Instrucciones de ejecucion:\npython automaton.py <ruta_archivo_definicion> <cadena_a_evaluar>"
        )
    definition_file = sys.argv[1]
    input_string = sys.argv[2]
    if not os.path.isfile(definition_file):
        raise Exception(
            "No se ha encontrado el archivo de definicion de automata en la ruta especificada: {}".format(
                definition_file
            )
        )
    return definition_file, input_string.lower()


def update_vocab(states_def: dict):
    vocab = []
    for v in states_def.values():
        vocab += list(v.keys())
    return list(set(vocab))


def print_table(header_data, states_def):
    str_header = "\t{}".format("\t".join(header_data))
    print(str_header)
    for key in states_def.keys():
        str_row = "{}".format(key)
        for v in header_data:
            if states_def[key].get(v):
                str_row += "\t{}".format(states_def[key].get(v))
            else:
                str_row += "\t"
        print(str_row)
    print("=" * 20)


def qrip_input_trans(states_definition: dict, original_state):
    in_trans = []
    for ext_state in states_definition:
        tlist = states_definition[ext_state]
        in_trans += [
            (ext_state, {tlist_item: tlist[tlist_item]})
            for tlist_item in tlist
            if tlist.get(tlist_item) == original_state and ext_state != original_state
        ]
    return in_trans


def qrip_join_duplicate_paths(states_definition: dict):
    for mod_state in states_definition:
        if mod_state not in ["qstart"]:
            # Unir mediante +
            items_to_merge = [ x for x in states_definition[mod_state] if states_definition[mod_state][x] == mod_state ]
            if len(items_to_merge) > 1:
                merged_trans = "+".join(items_to_merge)
                states_definition[mod_state][merged_trans] = mod_state
                for itm in items_to_merge:
                    del states_definition[mod_state][itm]

def load_automata_definition(definition_file: str):
    data_archivo = open(definition_file, "r", encoding="utf-8").readlines()
    if len(data_archivo) < 3:
        raise Exception("Formato invalido de definicion de automata")
    vocab = data_archivo[0].replace("\n", "").split(",")
    accept_states = data_archivo[-1].replace("\n", "")
    states_definition = data_archivo[1:-1]
    if not accept_states.lower().startswith("f:"):
        raise Exception(
            "Por favor indique la lista de estados aceptados mediante 'F:<s1>,<s2>,...'"
        )
    if len(states_definition) == 0:
        raise Exception("El archivo no contiene una definicion válida de estados.")

    states_definition_dict = {}
    for state in states_definition:
        fmt_line = state.replace("\n", "").strip()
        state_data = fmt_line.split(":")
        state_id = state_data[0]
        state_transitions = state_data[1].split(",")
        state_trans_dict = {v: state_transitions[idx] for idx, v in enumerate(vocab)}
        states_definition_dict[state_id] = state_trans_dict
    return vocab, accept_states, states_definition_dict
