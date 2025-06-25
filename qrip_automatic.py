import os
import sys

from utils.common import load_automata_definition, update_vocab, print_table, qrip_input_trans, qrip_join_duplicate_paths

def parse_arguments():
    if len(sys.argv) != 2:
        raise Exception("Instrucciones de ejecucion:\npython qrip_automatic.py <ruta_archivo_definicion>")
    definition_file = sys.argv[1]
    if not os.path.isfile(definition_file):
        raise Exception("No se ha encontrado el archivo de definicion de automata en la ruta especificada: {}".format(definition_file))
    return definition_file


def main(automata_def):
    # Load the Vocab, Accepted States and Definition values --> Check the function definition
    vocab, accepted_states, states_definition = load_automata_definition(automata_def)
    # As for the Qrip method, yuu need to add a new initial and final state
    # First map the current states, which are defined as Keys in the diccionary
    all_states = list(states_definition.keys())
    # Add the new start state (qstart) and define an epsilon transition to the original initial state
    states_definition["qstart"] = { "€": all_states[0] }
    # Add the new final state (qend). This state dont have any transitions
    states_definition["qend"] = {}
    # Use the original final (accepted states) 
    final_states = accepted_states[2:].split(",")
    # For each of them, add the epsilon transition to connect with the new final state
    for fstate in final_states:
        states_definition[fstate]["€"] = "qend"
    # Update the variable value
    all_states = list(states_definition.keys())
    # Reflect the changes in the vocab with the new transitions (Epsilon elements)
    vocab = update_vocab(states_definition)
    print("Initial Transitions table")
    print_table(vocab, states_definition) # Print a simple view of the initial table
    
    # Copy the original definition state to avoid lossing the original definition
    states_definition_cpy = states_definition.copy()
    # Select only the states to delete
    node_elements = [ x for x in states_definition_cpy.keys() if x not in ["qstart", "qend"] ]
    # For each one of them
    for idx, original_state in enumerate(node_elements):
        # Load the vocab definition. After the initial iteration, there must be some R.E. as transition values
        vocab = update_vocab(states_definition_cpy)
        # Extract the state to delete
        out_trans = states_definition_cpy.pop(original_state)
        print("Iteration #{} - Node to delete: {}".format((idx + 1), original_state))
        # Print the current table
        print_table(vocab, states_definition_cpy)
        # Select the input transition elements of the current state, avoiding the self-loops
        # Agregar todas aquellas coincidentes con "Estado_Destino == Estado Actual" exceptuando los self-loops
        in_trans = qrip_input_trans(states_definition_cpy, original_state) # Check implementation
        #loops_trans = [] # Prepare for the self-loops array

        # The QRip method can be seen as a Cross product with the input transitions of the state to eliminate with its output transitions
        # Realizar producto cruz de Incoming X Outgoing y agregarlos a la tabla de transiciones
        # For every transition in the input transition
        for inc_state, inc_transitions in in_trans:
            # Select the state name in the incoming or input transition of the array
            # Always will be of length 1, so you only select the 0 item
            base_transition = list(inc_transitions.keys())[0]
            # For every item in the actual  states definition, select only the output transitions of the current state
            for out_state in out_trans:
                # First, map the self-loops (Destination state == actual state)
                if out_trans[out_state] == original_state:
                    if "+" in out_state:
                        base_transition += "({})*".format(out_state)
                    else:
                        base_transition += "({}*)".format(out_state)
            # Same loop, but now map the Concatenation items
            for out_state in out_trans:
                # if the destination state is different from the current state
                if out_trans[out_state] != original_state:
                    str_transition = "({}{})".format(base_transition, out_state)
                    #print("{}[{}] --> {}".format(inc_state, str_transition, out_trans[out_state]))
                    # add the new "transition" (R.E. value) to the output states. Literal, qrip the state
                    states_definition_cpy[inc_state][str_transition] = out_trans[out_state]

        # Unir caminos dobles
        # In case there are double paths (from a --> b and b --> a)
        # Merge the path as a 
        qrip_join_duplicate_paths(states_definition_cpy)

        # Una vez eliminado el estado, eliminar las referencias de las transiciones existentes
        # Once we delete the state, the refs to the current or existing transitions are deleted
        # This is to avoid loops in the qrip algorithm and cleanse the transitions table
        for origin_state, transition in in_trans:
            del states_definition_cpy[origin_state][list(transition.keys())[0]]

        # Clean the qstart transitions
        # Delete the original or actual transitions and add the R.E. transitions
        qstart_elements = states_definition_cpy["qstart"]
        transitions_to_delete = []
        transitions_to_append = []
        for qe in qstart_elements.values():
            tvalues = [ x for x in qstart_elements.keys() if qstart_elements[x] == qe ]
            if len(tvalues) > 1:
                # Combine using the + operator all the states that are a posible path from qstart
                merged_trans = "(" + "+".join(tvalues) + ")"
                # Add the merged transition to the array
                transitions_to_append.append((merged_trans, qe))
                #states_definition_cpy["qstart"][merged_trans] = qe
                # Add the same values or transitions values to the "Delete" array
                transitions_to_delete += tvalues

        # Remove duplicates from the transitions_to_delete list (raises an error if the property or key dont exists when deleting)
        transitions_to_delete = list(set(transitions_to_delete))

        # Remove the transitions
        for tdel in transitions_to_delete:
            del states_definition_cpy["qstart"][tdel]
        # Add the new transitions to the current states definition or transitions table
        for tapp in transitions_to_append:
            states_definition_cpy["qstart"][tapp[0]] = tapp[1]
        #Repeat until there is only 2 states: qstart and qend. The resulting transition is the R.E.
    
    # Last update of the vocab, to add the R.E. expression
    vocab = update_vocab(states_definition_cpy)
    # Print the table
    print_table(vocab, states_definition_cpy)
    
    # Remove the epsilon letter from the R.E.
    qstart_keys = list(states_definition_cpy["qstart"].keys())
    qstart_keys = sorted(qstart_keys)
    regex = qstart_keys[0].replace("€", "")
    
    print("Resulting REGEX")
    print(regex)
    
if __name__ == "__main__":
    def_file = parse_arguments()    
    main(def_file)