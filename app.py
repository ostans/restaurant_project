import sys
from src import RestaurantManagerCLI, log


def main():
    app: RestaurantManagerCLI = RestaurantManagerCLI()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Program interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n ❌ Fatal error: {str(e)} \n")
        log.error(f"Fatal error: {str(e)}")
        sys.exit(1)
