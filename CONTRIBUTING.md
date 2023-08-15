# Contributing

To contribute to this project, please fork the repository and open a pull request with your changes.

Also, see our Contributors Code of Conduct [here](./.github/CONTRIBUTING.md).

## Updating the dependencies

```bash
task update
```

## Running the tests

```bash
task test
```

## Troubleshooting

If you're troubleshooting the results of any of the tasks, you can add `-v` to enable debug `task` logging, for instance:

```bash
task -v build
```

If you're troubleshooting a `goat` failure (you aren't the first one), you can pass one of the log levels as defined
[here](https://github.com/SeisoLLC/goat#debugging):

```bash
task lint -- debug
```
