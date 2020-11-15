from dataclasses import dataclass, field


@dataclass
class Site:
    title: str
    alt: str = field(init=False)
    image_path: str

    def __post_init__(self):
        self.alt = f'{self.title.lower()} logo'
