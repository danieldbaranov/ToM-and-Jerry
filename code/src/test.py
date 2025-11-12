import random
import csv
import tqdm
import argparse
import dotenv
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from utils import push_data, get_num_items, get_vars_from_out

dotenv.load_dotenv()

letters = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]
DATA_DIR = "../../data"
PROMPT_DIR = "../prompt_instructions"
PROMPT_FILENAME = "test.txt"
REPO_URL = "https://github.com/cicl-stanford/marple_text"
CSV_DIR = "tomandjerry"
CSV_NAME = "test.csv"

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, default="gpt-4", help="model name")
parser.add_argument("--temperature", type=float, default=0.5, help="temperature")
parser.add_argument("--max_tokens", type=int, default=450, help="max tokens")
# change num completions to 10
parser.add_argument(
    "--num_completions", type=int, default=1, help="number of completions"
)
parser.add_argument("--num_shots", type=int, default=3, help="number of shots")
parser.add_argument(
    "--num_stories", type=int, default=1, help="number of stories to generate"
)
parser.add_argument("--verbose", action="store_true", help="verbose")


def get_llm(args):
    llm = ChatOpenAI(
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        n=args.num_completions,
        request_timeout=180,
    )
    return llm


def gen_chat(args):
    response_template = """Here is the story:
Story: {story}
Aware of event: {awarenes}
Not aware of event: {not_aware}
Action given new state: {action_new}
Action given initial state: {action_init}
Reasoning Question: {reasoning_question}
Future Action Question: {future_action_question}
Belief Aware: {belief_answer_aware}
Desire Aware: {desire_answer_aware}
Action Aware: {action_answer_aware}
Belief not Aware: {belief_answer_not_aware}
Desire not Aware: {desire_answer_not_aware}
Action not Aware: {action_answer_not_aware}
Random Event: {random_event}
Aware of random event: {aware_of_random_event}
Not aware of random event: {not_aware_of_random_event}"""
    llm = get_llm(args)
    with open(f"{PROMPT_DIR}/{PROMPT_FILENAME}", "r") as f:
        instruction_text = f.read()
    system_message = SystemMessage(content=instruction_text)
    # 2-shots by default
    human_message_0 = HumanMessage(content="Generate a story")
    letter = random.choice(letters)
    human_message_1 = HumanMessage(
        content=f"Generate another story, using a different context, object states, and names than the examples did. The name must start with {letter}."
    )

    examples = []
    template_var = [
        "story",
        "awarenes",
        "not_aware",
        "action_new",
        "action_init",
        "reasoning_question",
        "future_action_question",
        "belief_answer_aware",
        "desire_answer_aware",
        "action_answer_aware",
        "belief_answer_not_aware",
        "desire_answer_not_aware",
        "action_answer_not_aware",
        "random_event",
        "aware_of_random_event",
        "not_aware_of_random_event",
    ]

    csv_file = f"{DATA_DIR}/{CSV_DIR}/{CSV_NAME}"

    prompt_tokens_used = 0
    completion_tokens_used = 0

    # run loop with n stories, increase by num_completions
    for n_story in tqdm.tqdm(range(0, args.num_stories, args.num_completions)):
        letter = random.choice(letters)
        human_message_1 = HumanMessage(
            content=f"Generate another story, using a different context, object states, and names than the examples did. The name must start with {letter}."
        )

        # read examples from csv file every iteration to add generated samples to the pool of seed examples
        if args.verbose:
            print(
                f"Reading examples from {csv_file} with existing {get_num_items(csv_file)} examples"
            )
        # read a few examples from the csv file (use csv.reader and guard against malformed/empty lines)
        try:
            with open(csv_file, "r", newline="") as f:
                reader = csv.reader(f, delimiter=";")
                for params in reader:
                    # skip empty rows
                    if not any([p.strip() for p in params]):
                        continue
                    if len(params) < len(template_var):
                        if args.verbose:
                            print(
                                f"Skipping malformed example (expected {len(template_var)} fields, got {len(params)}): {params}"
                            )
                        continue
                    example = {k: params[v].strip() for v, k in enumerate(template_var)}
                    examples.append(example)
        except FileNotFoundError:
            if args.verbose:
                print(f"CSV file not found: {csv_file} - continuing with no seed examples")
        random.shuffle(examples)

        # 3-shots by default
        messages = [system_message]
        for i in range(args.num_shots):
            messages.append(human_message_0)
            messages.append(AIMessage(content=response_template.format(**examples[i])))
        messages.append(human_message_1)

        if args.verbose:
            print(f"------ messages ------")
            print(messages)

        responses = llm.generate([messages])
        prompt_tokens_used += responses.llm_output["token_usage"]["prompt_tokens"]
        completion_tokens_used += responses.llm_output["token_usage"][
            "completion_tokens"
        ]
        price = (prompt_tokens_used * 0.03 + completion_tokens_used * 0.06) / 1000.0
        # update tqdm progress bar with price
        tqdm.tqdm.write(
            f"Price: {price:.2f} USD, Price per story: {price/(n_story+args.num_completions):.2f} USD"
        )

        for g, generation in enumerate(responses.generations[0]):
            # TODO: account for multiple completions
            if args.verbose:
                print(f"------ Generated Story {n_story+g} ------")
                print(generation.text)
                print("------------ Fin --------------")
            list_var = [
                "Story",
                "Aware of event",
                "Not aware of event",
                "Action given new state",
                "Action given initial state",
                "Reasoning Question",
                "Future Action Question",
                "Belief Aware",
                "Desire Aware",
                "Action Aware",
                "Belief not Aware",
                "Desire not Aware",
                "Action not Aware",
                "Random Event",
                "Aware of random event",
                "Not aware of random event",
            ]
            out_vars = get_vars_from_out(generation.text, list_var)
            data = [out_vars[k] for k in list_var]
            data += ["auto", 0]
            # write to csv file (sanitize embedded newlines and use newline='' on open)
            story_file = f"{DATA_DIR}/{CSV_DIR}/{CSV_NAME}"
            # sanitize fields to avoid embedded newlines in CSV fields (which create multi-line records)
            data_sanitized = [d.replace("\r", " ").replace("\n", " ") if isinstance(d, str) else d for d in data]
            # ensure parent directory exists
            os.makedirs(os.path.dirname(story_file), exist_ok=True)
            # if file exists, normalize trailing newlines so there is exactly one newline between entries
            need_prepend_newline = False
            if os.path.exists(story_file):
                try:
                    with open(story_file, 'rb+') as fb:
                        fb.seek(0, os.SEEK_END)
                        size = fb.tell()
                        if size == 0:
                            # empty file -- no newline needed
                            need_prepend_newline = False
                        else:
                            # check last byte
                            fb.seek(size - 1)
                            last = fb.read(1)
                            if last not in (b'\n', b'\r'):
                                # file ends with non-newline; we need to prepend a newline before appending
                                need_prepend_newline = True
                            else:
                                # file has one or more trailing newlines; truncate to a single newline after last content
                                pos = size - 1
                                while pos >= 0:
                                    fb.seek(pos)
                                    b = fb.read(1)
                                    if b not in (b'\n', b'\r'):
                                        break
                                    pos -= 1
                                if pos == -1:
                                    # file contains only newlines -> truncate to empty
                                    fb.truncate(0)
                                else:
                                    # desired length = position of last non-newline + 1 (keep that char) + 1 newline
                                    desired_len = pos + 2
                                    if desired_len < size:
                                        fb.truncate(desired_len)
                                need_prepend_newline = False
                except OSError:
                    # if any error reading/truncating file, fall back to appending with a newline
                    need_prepend_newline = True

            with open(story_file, "a", newline="") as csvfile:
                # if the existing file didn't end with a newline, write one so the new row starts on a fresh line
                if need_prepend_newline and csvfile.tell() > 0:
                    csvfile.write("\n")
                writer = csv.writer(csvfile, delimiter=";", lineterminator="\n")
                writer.writerow(data_sanitized)
    # push to github
    # push_data(DATA_DIR, REPO_URL)


if __name__ == "__main__":
    args = parser.parse_args()
    print(f"Generating {args.num_stories} stories")
    if args.verbose:
        print(args)
    gen_chat(args)
