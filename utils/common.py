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
    in_trans = [] # The array or list of the input transition elements
    # For each of the states in the states definition
    for ext_state in states_definition:
        # Select the current state transitions
        tlist = states_definition[ext_state]
        # Append to the array the (state number, transition value) if the state
        # has a transition to the desired state
        in_trans += [
            (ext_state, {tlist_item: tlist[tlist_item]})
            for tlist_item in tlist
            if tlist.get(tlist_item) == original_state and ext_state != original_state
        ]
    return in_trans


def qrip_join_duplicate_paths(states_definition: dict):
    # for every state in the current state definition
    for mod_state in states_definition:
        # Omit the qstart state, as there cant be a trasition with this state as a destination
        if mod_state not in ["qstart"]:
            # Merge using + operator
            # Unir mediante +
            # Get all the loop states
            items_to_merge = [ x for x in states_definition[mod_state] if states_definition[mod_state][x] == mod_state ]
            if len(items_to_merge) > 1: # A simple validation 
                # Concat all the items using the +
                merged_trans = "+".join(items_to_merge)
                # Add as a new transition element (R.E.) to the state
                states_definition[mod_state][merged_trans] = mod_state
                # Delete the already merged elements
                for itm in items_to_merge:
                    del states_definition[mod_state][itm]

def load_automata_definition(definition_file: str):
    # First, open the TXT file and read each line, generates an array
    data_archivo = open(definition_file, "r", encoding="utf-8").readlines()
    if len(data_archivo) < 3: # Validation for a BAD DFA definition
        raise Exception("Formato invalido de definicion de automata")
    # Check the TXT file structure
    """
        First line: The Vocabulary
        Second to n-1 lines: 
            The first element is the state number or name, must be different from vocab items
            The next ites are the state number that the DFA will reach if the vocab item in the position N is used
        Last line: The accepted states
            
    """
    # For the vocab data, read the first line and split by commas
    vocab = data_archivo[0].replace("\n", "").split(",")
    # For the accepted states, read the last line
    accept_states = data_archivo[-1].replace("\n", "")
    # Load the remaining lines, the transition table
    states_definition = data_archivo[1:-1]
    # A simple validation that the Accepted states file line must start with an f:, to avoid errors with the transition table
    if not accept_states.lower().startswith("f:"):
        raise Exception(
            "Por favor indique la lista de estados aceptados mediante 'F:<s1>,<s2>,...'"
        )
    # If there is no states definition or transition table, raise an error
    if len(states_definition) == 0:
        raise Exception("El archivo no contiene una definicion válida de estados.")

    #Create an dictionary to map the transitions table to a Python structure
    states_definition_dict = {}
    # For each line of the definition items
    for state in states_definition:
        # Remove the unnecesari elements
        fmt_line = state.replace("\n", "").strip()
        # Split the line by ":"
        state_data = fmt_line.split(":")
        # Read the first element, is the state number
        state_id = state_data[0]
        # The other elements, split by commas, generating an array
        state_transitions = state_data[1].split(",")
        # Map the vocab item to a state --> vocab_item : next_state --> Can be read as "I get to the State V, using the vocab item X"
        state_trans_dict = {v: state_transitions[idx] for idx, v in enumerate(vocab)}
        # Assign those transitions to its current state
        states_definition_dict[state_id] = state_trans_dict
        # The resulting element can be seen as:
        # In state N, I can go the state M using the vocab item X
        
    # Return the elements
    return vocab, accept_states, states_definition_dict
