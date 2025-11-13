#### Mind in the Machine Team Notes:
Create a .env file in the root directory with the following content with your open ai key assigned to the variable OPENAI_API_KEY.

Checklist for changing the shape of the dataset (test.csv):
* Update `response_template` variable in `code/src/test.py` to include/exclude desired fields.
* Update `template_var` variable in `code/src/test.py` to include/exclude desired fields.
* Update `list_var` variable in `code/src/test.py` to include/exclude desired fields.
* Update the prompt file at `code/prompt_instructions/test.txt` to include/exclude desired fields. Be verbose and follow the format of existing fields.
* The most tedious part: Because the generation of new data requires looking at examples (which come from the existing data), you must update the data in `test.csv` to include/exclude desired fields. It must match exactly the order in `list_var` in `code/src/test.py`. You can do this manually or paste the data into an LLM or something and explicitly describe the changes you want.

Preliminary Data Fields for Tom and Jerry:
*Will need to add some field(s) later for future action question answers
1. Story (Causal Event portion will double as the answer for level 3 reasoning question)
2. Aware of event (Doubles as the answer for level 2 reasoning question, Percept Implicit Aware)
3. Not aware of event (Doubles as the answer for level 2 reasoning question, Percept Implicit Not Aware)
4. Action given new state
5. Action given initial state
6. Reasoning Question (for level 1, 2, and 3 reasoning)
7. State Change Question (initial question for level 3 reasoning)
8. Future Action Question (not used yet)
9. Belief Explicit Aware (for level 1 reasoning)
10. State Implicit Aware (for level 3 reasoning, this only answers if something in the environment changed)
11. Belief Explicit Not Aware
12. State Implicit Not Aware
13. Random Event
14. Aware of random event
15. Not aware of random event

##  

A Domain-Agnostic Method for Procedurally Generating LLM Evaluations

![Causal Template -> Prompt Template -> Test Items](./assets/generation.jpg)


### 🧐 What is this?
This is a supporting repository for our paper titled "Understanding Social Reasoning in LLMs with LLMs".
We develop a method that uses large language models (LLMs) to procedurally generate evaluations for other LLMs. We apply this method to assess the performance of LLMs in a subdomain of social reasoning (Theory-of-Mind). Please checkout our [paper](https://sites.google.com/view/social-reasoning-lms) for further details.


### 📂 Repo structure
```
├── code                 
│   └── analysis
│   └── prolific-exp-1
│   └── prolific-exp-2
│   └── prompt_instructions
│   └── scripts
│   └── src 
├── data   
│   ├── bigtom    
│   └── expert_data
│   └── social_iqa
│   └── prolific
├── .gitignore
├── LICENSE            
└── requirements.txt
```

### 🚀 Getting started 
#### Using miniconda
1. `curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh`
2. `bash Miniconda3-latest-MacOSX-x86_64.sh`
3. close and reopen terminal
4. `source ~/.bashrc` or `source ~/.zshrc`
5. `conda create --name name-of-my-env python==3.10`
6. `conda activate name-of-my-env`
7. `pip install -r requirements.txt` 

#### Generating BigToM
Prompt for generating BigToM is in `code/prompt_instructions/bigtom.txt` and the python script is at `code/src/bigtom.py`. To generate BigToM, run the following commands:
1. `cd code/src`
2. `python bigtom.py`
3. `python generate_conditions.py`

#### Human Experiments
We provide code to run Human experiments of 3 kinds:
1. Expert Ratings: `code/src/expert_evaluate.py`
2. Prolific Experiment for Rating Generated Stories: `code/prolific-exp-1`
3. Prolific Experiment for Testing Human Participants: `code/prolific-exp-2`

#### Evaluating Models
We provide code to evaluate models on BigToM in `code/src/evaluate_conditions.py`. More specific experiment scripts are available in `code/scripts`.
