#!/usr/bin/env python3

"""
Text racer game
"""

import typing_game as typing

menu = """
1. Train easy
2. Train medium
3. Train hard
4. Print stats
5. Practice mode
─────────────────
q. quit
"""

logo = r"""
   ____     __    ____     __     __ 
  /  _/__  / /__ / __/__  / /__ _/ /_
 _/ // _ \/  '_/_\ \/ _ \/ / _ `/ __/
/___/_//_/_/\_\/___/ .__/_/\_,_/\__/ 
                  /_/                
"""

running = True

def main():
    """ Main function to run the menu """
    clear_console()
    while running:
        choice()

def show_menu():
    """ Show the menu and get the user's choice """
    print(logo)
    print(menu)
    return input("--> ").lower()

def clear_console():
    """ Clear the console """
    print(chr(27) + "[2J")

def choice():
    """ Get the user's choice and run the corresponding function """
    inp = show_menu()

    if inp == "1":
        typing.start_test("easy")

    elif inp == "2":
        typing.start_test("medium")

    elif inp == "3":
        typing.start_test("hard")

    elif inp == "4":
        typing.print_high_scores()

    elif inp == "5":
        typing.start_training()

    elif inp == "q":
        global running
        running = False

    else:
        print(f"{inp} is not a valid choice")
    
    if running:
        input("\nPress any key to continue...")
        clear_console()

if __name__ == "__main__":
    main()
