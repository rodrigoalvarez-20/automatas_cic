import os
import sys


def parse_arguments():
    if len(sys.argv) != 3:
        raise Exception("Instrucciones de ejecucion:\npython automaton.py <ruta_archivo_definicion> <cadena_a_evaluar>")
    definition_file = sys.argv[1]
    input_string = sys.argv[2]
    if not os.path.isfile(definition_file):
        raise Exception("No se ha encontrado el archivo de definicion de automata en la ruta especificada: {}".format(definition_file))
    return definition_file, input_string.lower()


def load_automata_definition(definition_file: str):
    data_archivo = open(definition_file, "r", encoding="utf-8").readlines()
    if len(data_archivo) < 3:
        raise Exception("Formato invalido de definicion de automata")
    vocab = data_archivo[0].replace("\n", "").split(",")
    accept_states = data_archivo[-1].replace("\n", "")
    states_definition = data_archivo[1:-1]
    if not accept_states.lower().startswith("f:"):
        raise Exception("Por favor indique la lista de estados aceptados mediante 'F:<s1>,<s2>,...'")
    if len(states_definition) == 0:
        raise Exception("El archivo no contiene una definicion válida de estados.")
    states_definition_dict = {}
    for state in states_definition:
        fmt_line = state.replace("\n", "").strip()
        state_data = fmt_line.split(":")
        state_id = state_data[0]
        state_transitions = state_data[1].split(",")
        state_trans_dict = { v: state_transitions[idx] for idx, v in enumerate(vocab) }
        states_definition_dict[state_id] = state_trans_dict
    return vocab, accept_states, states_definition_dict