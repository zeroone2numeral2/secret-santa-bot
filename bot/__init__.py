from .utils import utils
from .bot import Bot


bot = Bot()


def main():
    utils.load_logging_config('logging.json')

    bot.start()


if __name__ == '__main__':
    main()
