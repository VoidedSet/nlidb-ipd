import sys
from colorama import init, Fore, Style
from dotenv import load_dotenv

from agents.router import route_query
from agents.sql_agent import SQLAgent
from agents.eda_agent import EDAAgent

init(autoreset=True)
load_dotenv()

def print_header():
    print(Fore.CYAN + Style.BRIGHT + "=" * 60)
    print(Fore.CYAN + Style.BRIGHT + "       QUERIFY 2.0 - INTELLIGENCE CORE (PROTOTYPE)")
    print(Fore.CYAN + Style.BRIGHT + "=" * 60)
    print(Fore.YELLOW + "Connected to Local MySQL Database")
    print(Fore.WHITE + "Type 'exit' or 'quit' to stop.")
    print("-" * 60 + "\n")

def main():
    print_header()

    try:
        sql_bot = SQLAgent()
        eda_bot = EDAAgent()
    except Exception as e:
        print(Fore.RED + f"CRITICAL ERROR: Could not connect to Database. {e}")
        return

    while True:
        try:
            user_input = input(Fore.GREEN + Style.BRIGHT + "You: " + Fore.RESET).strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print(Fore.CYAN + "\nGoodbye! Keep building.")
                sys.exit(0)
            
            if not user_input:
                continue

            print(Fore.MAGENTA + "   [Router] Analyzing request...")
            route_decision = route_query(user_input)
            print(Fore.MAGENTA + f"   [Router] Directed to: {route_decision}")

            if route_decision == "SQL_QUERY":
                response = sql_bot.run(user_input)
                print(Fore.BLUE + f"\n[SQL Agent]: {response}\n")
                
            elif route_decision == "EDA_TASK":
                response = eda_bot.run(user_input)
                print(Fore.YELLOW + f"\n[EDA Agent]: {response}\n")
            
            else:
                print(Fore.RED + "   [Error] Router returned unknown path.")

        except KeyboardInterrupt:
            print("\n")
            print(Fore.CYAN + "Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(Fore.RED + f"\n[System Error]: {e}\n")

if __name__ == "__main__":
    main()