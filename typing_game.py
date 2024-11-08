""" Typing game module """

#import os
import time
import random
from operator import itemgetter

#root_path = os.path.dirname(os.path.abspath(__file__))
root_path = ""
using_path = ""

ascii_upper_lower_punctuation = """
abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~
"""

difficulties = {
    "easy": root_path + "easy.txt",
    "medium": root_path + "medium.txt",
    "hard": root_path + "hard.txt"
}

# Min exclusive, max inclusive
wpm_map = {
    (0, 5): "Sloth",
    (5, 15): "Snail",
    (15, 30): "Manatee",
    (30, 40): "Human",
    (40, 50): "Gazelle",
    (50, 60): "Ostrich",
    (60, 70): "Cheetah",
    (70, 80): "Swordfish",
    (80, 90): "Spur-winged goose",
    (90, 100): "White-throated needletail",
    (100, 120): "Golden eagle",
    (120, float("inf")): "Peregrine falcon"
}

# Game functions

def start_test(difficulty: str) -> None:
    """ Starts a typing test of given difficulty """
    global using_path
    using_path = difficulties[difficulty]
    
    running = True
    answers = []
    lines = get_file_lines(using_path)

    start_time = time.time()

    while running:
        clear_console()
        for line in lines:
            time_elapsed = time.time() - start_time
            print_stats(answers, time_elapsed)
            print(line)
            inp = input("")
            answers.append(inp)
            clear_console()
        
        running = False
    
    end_time = time.time()
    time_elapsed = end_time - start_time

    input("Test finished!\n Press anything to see stats...")
    clear_console()
    print_stats(answers, time_elapsed, True)

    name = input("Enter your name: ").replace(" ", "_")
   
    word_precision = calculate_precisions(answers)['word_precision']
    save_test_stats(name, word_precision, difficulty)

def start_training() -> None:
    """ Starts a training session """
    training_time_seconds = int(input("How long do you want to train for? (in seconds): "))
    start_time = time.time()
    end_time = start_time + training_time_seconds
    
    char_amount = 0
    incorrect_amount = 0
    incorrect_chars = {}

    running = True
    while running:
        clear_console()
        random_char = random.choice(ascii_upper_lower_punctuation)
        print(random_char)

        inputted_char = input("")
        if inputted_char != random_char:
            incorrect_chars[random_char] = incorrect_chars.get(random_char, 0) + 1
            incorrect_amount += 1

        char_amount += 1

        if time.time() >= end_time:
            running = False
    
    sorted_chars = sort_incorrect_chars(incorrect_chars)
    precision = round(incorrect_amount / char_amount * 100, 2)
    chars_per_minute = round(char_amount / training_time_seconds * 60, 2)

    clear_console()
    print("Training complete!")
    print(f"You got {precision}% wrong")
    print(f"CPM: {chars_per_minute}")

    print("Wrong characters:")
    for key, value in sorted_chars.items():
        print(f"{key}: {value}")

# Utility functions

def clear_console() -> None:
    """ Clears the console """
    print(chr(27) + "[2J")

def get_highscores_from_file() -> list:
    """ Gets highscores from score file and sorts them """

    user_stats = []
    try:
        with open("score.txt", "r+") as filehandle:
            content = filehandle.readlines()

            for line in content:
                line = line.split(" ")
                user_stat_dict = {
                    'word_precision': float(line[0]),
                    'difficulty': line[1],
                    'name': line[2].strip()
                }
                user_stats.append(user_stat_dict)
    except FileNotFoundError:
        with open("score.txt", "w") as filehandle:
            pass
    
    return user_stats

def save_test_stats(name: str, word_precision: float, difficulty: str) -> None:
    """ Saves the test stats to a file """

    user_stats = get_highscores_from_file()

    user_stat = {
        'word_precision': float(word_precision),
        'difficulty': difficulty,
        'name': name
    }

    user_stats.append(user_stat)
    user_stats.sort(key=sort_key_scoreboard)

    with open("score.txt", "w") as filehandle:
        for score in user_stats:
            filehandle.write(
                str(score['word_precision']) + " " +
                score['difficulty'] + " " +
                score['name'] + "\n"
            )

def get_file_lines(file_path: str) -> list:
    """ Returns the lines of a file """
    with open(file_path, "r") as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            lines[i] = line.rstrip()
    return lines

def get_animal(wpm: float) -> str:
    """ Returns animal based on WPM """
    for (min_wpm, max_wpm), animal in wpm_map.items():
        if min_wpm < wpm <= max_wpm:
            return animal
    return "Animal representation not found"
        
def get_wpm_minutes(time_elapsed: float) -> int:
    """ Returns the amount of minutes for WPM calculation """
    minutes = time_elapsed / 60
    minutes_fraction = minutes - int(minutes)

    if minutes_fraction >= 0.5:
        minutes = int(minutes) + 1
    else:
        if int(minutes) == 0:
            minutes = 1
        else:
            minutes = int(minutes)
            
    return minutes
        
def calculate_gross_wpm(answers: list, time_elapsed: float) -> float:
    """ Calculates gross WPM of the test """
    if not answers:
        return 0

    word_amount = 0

    for line in answers:
        for word in line.split(" "):
            if word:
                word_amount += 1

    minutes = get_wpm_minutes(time_elapsed)
    gross_wpm = round(word_amount / minutes, 2)

    return gross_wpm

def calculate_net_wpm(answers: list, time_elapsed: float) -> float:
    """ Calculates net WPM of the test """
    if not answers:
        return 0

    wrong_words = 0
    lines_inputted = answers
    lines_correct = get_file_lines(using_path)

    for i, line_inputted in enumerate(lines_inputted):
        if line_inputted == "":
            continue
        words_correct = lines_correct[i].split(" ")
        words_inputted = line_inputted.split(" ")

        if len(words_inputted) > len(words_correct):
            wrong_words += len(words_inputted) - len(words_correct)
        elif len(words_inputted) < len(words_correct):
            words_inputted.extend([""] * (len(words_correct) - len(words_inputted)))

        for j, word_correct in enumerate(words_correct):
            
            if words_inputted[j].strip() != word_correct and words_inputted[j]:
                wrong_words += 1

    minutes = get_wpm_minutes(time_elapsed)
    gross_wpm = calculate_gross_wpm(answers, time_elapsed)
    net_wpm = round(gross_wpm - (wrong_words / minutes), 2)

    return net_wpm

def calculate_accuracy(net_wpm: float, gross_wpm: float) -> float:
    """ Calculates the accuracy of the test """
    if gross_wpm != 0:
        accuracy = round(net_wpm / gross_wpm * 100, 2)
    else:
        accuracy = 0
    return accuracy

def calculate_precisions(answers: list) -> dict:
    """ Calculates word precision of the test """
    if not answers:
        return {"word_precision": 100, "char_precision": 100, "incorrect_chars": {}}

    lines_inputted = answers
    lines_correct = get_file_lines(using_path)
    words_correct = []

    for line in lines_correct:
        words_correct += line.split(" ")

    correct_word_count = len(words_correct)
    total_word_count = len(words_correct)
    total_char_count = 0

    for line in lines_correct:
        for char in line:
            if char != " ":
                total_char_count += 1

    correct_char_count = total_char_count
    incorrect_chars = {}

    for i, line_inputted in enumerate(lines_inputted):
        words_correct = lines_correct[i].split(" ")
        words_inputted = line_inputted.split(" ")
        words_inputted.extend([""] * (len(words_correct) - len(words_inputted)))
    
        for j, correct_word in enumerate(words_correct):
            
            if words_inputted[j] != correct_word:
                correct_word_count -= 1

                for k, correct_char in enumerate(correct_word):
                    try:
                        given_char = words_inputted[j][k]
                    except IndexError:
                        correct_char_count -= 1
                        incorrect_chars[correct_char] = incorrect_chars.get(correct_char, 0) + 1
                        continue
                    
                    if given_char != correct_char:
                        correct_char_count -= 1
                        incorrect_chars[correct_char] = incorrect_chars.get(correct_char, 0) + 1

    word_precision = round(correct_word_count / total_word_count * 100, 2)
    char_precision = round(correct_char_count / total_char_count * 100, 2)

    return {"word_precision": word_precision, "char_precision": char_precision, "incorrect_chars": incorrect_chars}

def sort_incorrect_chars(incorrect_chars: dict) -> dict:
    """ Sorts the incorrect characters """
    return dict(sorted(incorrect_chars.items(), key=itemgetter(1, 0), reverse=True))

def sort_key_scoreboard(user_stat: dict) -> tuple:
    """ Custom key for sorting difficulties """
    difficulties_map = {'easy': 2, 'medium': 1, 'hard': 0}
    return (difficulties_map[user_stat['difficulty']], -user_stat['word_precision']) # - reverses order so its 100 - 0

# Print functions

def print_high_scores() -> None:
    """ Loops through highscores and prints them in a nice way """

    clear_console()
    print("High scores: \n")

    user_stats = get_highscores_from_file()
    user_stats.sort(key=sort_key_scoreboard)

    for user_stat in user_stats:
        word_prec_length = len(str(user_stat['word_precision']))

        print(f"{user_stat['word_precision']}%", end="")

        if word_prec_length < 6:
            for _ in range(6 - word_prec_length):
                print(" ", end="")

        print(f"| {user_stat['difficulty']}", end="")

        difficulty_length = len(user_stat['difficulty'])
        if difficulty_length < 7:
            for _ in range(7 - difficulty_length):
                print(" ", end="")

        print(f"| {user_stat['name']}")

def print_stats(answers: list, time_elapsed: float, last_print: bool = False) -> None:
    """ Prints stats of the test """

    precisions = calculate_precisions(answers)
    word_precision = precisions['word_precision']
    char_precision = precisions['char_precision']
    gross_wpm = calculate_gross_wpm(answers, time_elapsed)
    net_wpm = calculate_net_wpm(answers, time_elapsed)
    accuracy = calculate_accuracy(net_wpm, gross_wpm)

    print(f"Ordprecision: {word_precision}%")
    print(f"Teckenprecision: {char_precision}%\n")
    print("Felstavade tecken:")
    sorted_char_dict = sort_incorrect_chars(precisions['incorrect_chars'])
    for key, value in sorted_char_dict.items():
        print(f"{key}: {value}")
    print()
    
    minutes = int(time_elapsed // 60)
    seconds = round(time_elapsed % 60, 2)
    print(f"Timer: {minutes} minutes and {seconds} seconds\n")
    print(f"Gross WPM: {gross_wpm}")
    print(f"Net WPM: {net_wpm}")
    print(f"Accuracy: {accuracy}%")
    if last_print:
        print(f"\nYou're fast as a {get_animal(net_wpm)}")
    print("\n─────────────────\n")
