# Conveyor

Welcome, diggers, welcome, to our newly-developed startup specializing in gold and ML conveyors!

To get started with testing out our product's beta, all you need is a computing device with [Python](https://www.python.org/) and [Poetry](https://python-poetry.org/) installed, using which you could launch the example client script ([scripts/client.py](./scripts/client.py)) by executing:

```sh
poetry install && poetry run conveyor-client {IP} 12378
```

It should call our services to dig out some fresh gold, mix it up into some alloys, and train a basic linear model on the resulting alloy, weight and fineness data! Should you need a more thorough look through our available features, simply check them out in the data conveyor and model conveyor sources: [conveyor/data.py](./conveyor/data.py) and [conveyor/model.py](./conveyor/model.py), respectively.
