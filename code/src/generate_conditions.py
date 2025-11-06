import os
import csv

DATA_DIR = '../../data'
CONDITION_DIR = os.path.join(DATA_DIR, 'conditions')
CSV_NAME = os.path.join(DATA_DIR, 'bigtom/bigtom.csv')
INITIAL_BELIEF = [0, 1] # 0 hide initial belief, 1 show initial belief
VARIABLES = ['forward_belief', 'forward_action', 'backward_belief', 'percept_to_belief']
VARIABLES = ['level_1', 'level_2', 'level_3', 'percept_to_belief']

CONDITIONS = ['true_belief', 'false_belief', 'true_control', 'false_control']

def get_completions():
    with open(CSV_NAME, "r") as f:
        reader = csv.reader(f, delimiter=";")
        completions = list(reader)
    return completions

def generate_conditions(completions):
    list_var = ["Story", "Aware of event", "Not Aware of event", "Action aware", "Action not aware", "Belief Question",   "Reasoning Question", "Action Question",
                "Belief Answer Aware", "Percept Answer Aware", "Action Answer Aware", "Belief Answer not Aware",
                "Percept Answer not Aware", "Action Answer not Aware", "Random Event", "Aware of random event", "Not aware of random event"]

    for completion_idx, completion in enumerate(completions):

        # Create a dictionary mapping the different parts of the scenario, to their values in the LLM generated output
        # Looks like: {'Story': 'Noor is working as a ...', 'Aware of event': 'Noor sees her coworker ...', ...}
        dict_var = {list_var[i]: completion[i] for i in range(len(list_var))}
        
        # Loop for each type of initial belief
        # Loops 2 times
        for init_belief in INITIAL_BELIEF:

            # Loop for each type of variable
            # Variables are the different types of scenarios we want to create
            for variable in VARIABLES:  

                if variable == "percept_to_belief":
                    question = dict_var["Belief Question"]
                    answers = [dict_var["Belief Answer Aware"], dict_var["Belief Answer not Aware"]]
                    # story and parts 
                    story = dict_var["Story"]
                    story_parts = dict_var["Story"].split(".")
                    
                    if init_belief == 1:
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." 


                elif variable == "backward_belief":
                    question = dict_var["Belief Question"]
                    answers = [dict_var["Belief Answer Aware"], dict_var["Belief Answer not Aware"]]
                    awareness = [dict_var["Aware of event"], dict_var["Not Aware of event"]]
                    actions = [dict_var["Action aware"], dict_var["Action not aware"]]
                    awareness_random = [dict_var["Aware of random event"], dict_var["Not aware of random event"]]

                    story_parts = dict_var["Story"].split(".")
                    
                    # If initial belief is 0 (not present), remove the sentence in the story that indicates the character's belief
                    if init_belief == 0:
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." + story_parts[4] + "."
                        story_parts = story.split(".")
                        story_control = ".".join(story_parts[:3] + [" " + dict_var["Random Event"]])

                    # If initial belief is 1 (present), keep all sentences in the story
                    elif init_belief == 1:
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." +  story_parts[3] + "." + story_parts[4] + "."
                        story_parts = story.split(".")
                        story_control = ".".join(story_parts[:4] + [" " + dict_var["Random Event"]])
                        
                
                # Need to create an alternative story generation file to bigtom.py for generate_conditions.py to get the right components to build properly

                # Level 1 Reasoning: Causes of action are directly directly stated 
                elif variable == "level_1":
                    question = dict_var["Reasoning Question"]
                    answers = [dict_var["Belief Answer Aware"], dict_var["Belief Answer not Aware"]]
                    awareness = [dict_var["Aware of event"], dict_var["Not Aware of event"]]
                    actions = [dict_var["Action aware"], dict_var["Action not aware"]]
                    awareness_random = [dict_var["Aware of random event"], dict_var["Not aware of random event"]]

                    story_parts = dict_var["Story"].split(".")
                    
                    # If initial belief is 0 (not present), remove the sentence in the story that indicates the character's belief
                    if init_belief == 0:
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." + story_parts[4] + "."
                        story_parts = story.split(".")
                        story_control = ".".join(story_parts[:3] + [" " + dict_var["Random Event"]])

                    # If initial belief is 1 (present), keep all sentences in the story
                    elif init_belief == 1: 
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." +  story_parts[3] + "." + story_parts[4] + "."
                        story_parts = story.split(".")
                        story_control = ".".join(story_parts[:4] + [" " + dict_var["Random Event"]])


                # Level 2 Reasoning: The LLM needs to bridge information from different parts of the text
                # Changes from Level 1: 
                #   - Removed the 'Awareness' list from the story construction
                #   - Change the type of answer to a Percept Answer
                elif variable == "level_2":
                    question = dict_var["Reasoning Question"]
                    answers = [dict_var["Percept Answer Aware"], dict_var["Percept Answer not Aware"]]
                    actions = [dict_var["Action aware"], dict_var["Action not aware"]]
                    awareness_random = [dict_var["Aware of random event"], dict_var["Not aware of random event"]]

                    story_parts = dict_var["Story"].split(".")
                    
                    # If initial belief is 0 (not present), remove the sentence in the story that indicates the character's belief
                    if init_belief == 0:
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." + story_parts[4] + "."
                        story_parts = story.split(".")
                        story_control = ".".join(story_parts[:3] + [" " + dict_var["Random Event"]])

                    # If initial belief is 1 (present), keep all sentences in the story
                    elif init_belief == 1: 
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." +  story_parts[3] + "." + story_parts[4] + "."
                        story_parts = story.split(".")
                        story_control = ".".join(story_parts[:4] + [" " + dict_var["Random Event"]])
                        
                # Level 3 Reasoning: The LLM needs to make inferences beyond the text
                # Changes from Level 2:
                #  - Remove the 'Causal Event' from the story construction (last sentence)
                #  - The answer will be open response and should describe something similar to the causal event which was removed
                elif variable == "level_3":
                    question = dict_var["Reasoning Question"]
                    actions = [dict_var["Action aware"], dict_var["Action not aware"]]
                    awareness_random = [dict_var["Aware of random event"], dict_var["Not aware of random event"]]

                    story_parts = dict_var["Story"].split(".")
                    
                    answers = [story_parts[4].strip(), "An incorrect answer."] # Figure out how to do this later

                    # If initial belief is 0 (not present), remove the sentence in the story that indicates the character's belief
                    if init_belief == 0:
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "."
                        story_parts = story.split(".")
                        story_control = ".".join(story_parts[:3] + [" " + dict_var["Random Event"]])

                    # If initial belief is 1 (present), keep all sentences in the story
                    elif init_belief == 1:
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." + story_parts[3] + "."
                        story_parts = story.split(".")
                        story_control = ".".join(story_parts[:4] + [" " + dict_var["Random Event"]])


                # Loop for each condition
                for condition in CONDITIONS:

                    # Write the row to the CSV file based on the condition and variable
                    if variable == "percept_to_belief":
                        if condition == "true_belief" and init_belief == 1:
                            if not os.path.exists(os.path.join(CONDITION_DIR, f'{init_belief}_{variable}_{condition}')):
                                os.makedirs(os.path.join(CONDITION_DIR, f'{init_belief}_{variable}_{condition}'))
                            new_csv_file = os.path.join(CONDITION_DIR, f'{init_belief}_{variable}_{condition}/stories.csv')
                            
                            with open(new_csv_file, "a" if completion_idx > 0 else "w", newline='') as csvfile:
                                writer = csv.writer(csvfile, delimiter=";")
                                writer.writerow([f"{story}", question, answers[0], answers[1]])
                          
                    elif variable != "percept_to_belief":
                        # Check if the new file needs to be created or appended
                        if not os.path.exists(os.path.join(CONDITION_DIR, f'{init_belief}_{variable}_{condition}')):
                            os.makedirs(os.path.join(CONDITION_DIR, f'{init_belief}_{variable}_{condition}'))

                        new_csv_file = os.path.join(CONDITION_DIR, f'{init_belief}_{variable}_{condition}/stories.csv')

                        with open(new_csv_file, "a" if completion_idx > 0 else "w", newline='') as csvfile:
                            writer = csv.writer(csvfile, delimiter=";")

                            if condition == "true_belief":
                                if variable == "backward_desire":
                                    writer.writerow([f"{story} {awareness[0]} {actions[0]}", question, answers[0], answers[1]])
                                elif variable == "backward_belief":
                                    writer.writerow([f"{story} {actions[0]}", question, answers[0], answers[1]])
                                # True Belief Level 1
                                # Story + Aware of event + Action aware + Question + Belief Answer Aware + Belief Answer not Aware
                                elif variable == "level_1":
                                    writer.writerow([f"{story} {awareness[0]} {actions[0]}", question, answers[0], answers[1]])
                                # True Belief Level 2
                                # Story + Action aware + Question + Percept Answer Aware + Percept Answer not Aware
                                elif variable == "level_2":
                                    writer.writerow([f"{story} {actions[0]}", question, answers[0], answers[1]])
                                # True Belief Level 3
                                # Story - Causal Event + Question + Open Answer (Correct) + Open Answer (Incorrect)
                                elif variable == "level_3":
                                    writer.writerow([f"{story}", question, answers[0], answers[1]])


                            elif condition == "false_belief":
                                if variable == "backward_desire":
                                    writer.writerow([f"{story} {awareness[1]} {actions[1]}", question, answers[1], answers[0]])
                                elif variable == "backward_belief":
                                    writer.writerow([f"{story} {actions[1]}", question, answers[1], answers[0]])
                                # False Belief Level 1
                                # Story + Not Aware of event + Action Not aware + Question + Belief Answer Aware + Belief Answer not Aware
                                elif variable == "level_1":
                                    writer.writerow([f"{story} {awareness[1]} {actions[1]}", question, answers[1], answers[0]])
                                # False Belief Level 2
                                # story + Not Aware of event + Question + Percept Answer Aware + Percept Answer not Aware 
                                elif variable == "level_2":
                                    writer.writerow([f"{story} {actions[1]}", question, answers[1], answers[0]])
                                # False Belief Level 3
                                # Story - Causal Event + Question + Open Answer (Correct) + Open Answer (Incorrect)
                                elif variable == "level_3":
                                    writer.writerow([f"{story}", question, answers[1], answers[0]])

                            elif condition == "true_control":
                                if variable == "backward_desire":
                                    writer.writerow([f"{story_control} {awareness_random[0]} {actions[1]}", question, answers[1], answers[0]])
                                elif variable == "backward_belief":
                                    writer.writerow([f"{story_control} {actions[1]}", question, answers[1], answers[0]])
                                else:
                                    writer.writerow([f"{story_control} {awareness_random[0]}", question, answers[1], answers[0]])

                            elif condition == "false_control":
                                if variable == "backward_desire":
                                    writer.writerow([f"{story_control} {awareness_random[1]} {actions[1]}", question, answers[1], answers[0]])
                                elif variable == "backward_belief":
                                    writer.writerow([f"{story_control} {actions[1]}", question, answers[1], answers[0]])
                                else:
                                    writer.writerow([f"{story_control} {awareness_random[1]}", question, answers[1], answers[0]])


if __name__ == "__main__":  
    completions = get_completions()
    generate_conditions(completions)
