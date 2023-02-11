from src.modules import BaseModule


class Validator(BaseModule):
    name = 'Validator'
    description = 'Plugin Description.'

    def __init__(self, client, output):
        # Add anything you want here.
        super().__init__(client, output)

    def run(self) -> None:
        pass

    def close(self) -> None:
        pass
