try:  # Python 2
    from startup import run
except ImportError:  # Python 3
    from .startup import run


def main():
    run()


if __name__ == '__main__':
    run()
