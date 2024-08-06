# SignLLaVA Demo Frontend

This folder contains the demo frontend (built on React) which provides the user interface for the whole system and communicates with the backend server through an HTTP API.

> **Note:** If you've never seen the Node.js ecosystem, scroll down to the last section where I've put a quick explanation with references to analogous systems in the Python ecosystem.


## After cloning

You need to have [node.js](https://nodejs.org/) intalled. I recommend the [Node version manager](https://github.com/nvm-sh/nvm) tool. You can install the latest node version, but it works for me with `20.12.2`. If the project won't compile due to some strange internal exception, try upgrading node.

After cloning the repository:

```bash
npm ci # installs packages from package-lock.json at EXACT versions
```

Start the Parcel development server and you are ready to go:

```bash
npm run start
```

Openning http://localhost:1234 in your browser should now show the frontend app.


## Before committing changes

```bash
# run linter and formatter
npm run lint
npm run prettier-write

# also try building for production,
# because parcel production is more strict and may fail
# even if development compiled fine:
npm run clean
npm run build
```


## Using prettier to format code

```bash
# just see what files fail
npm run prettier-check

# format all files
npm run prettier-write

# or you can just format one file:
npx prettier src/MyFile.jsx --write

# or just see what the formatted file would look like
npx prettier src/MyFile.jsx
```

Prettier is configured in `.prettierrc` and it's empty on purpose! See the [prettier philosophy](https://prettier.io/docs/en/option-philosophy).


## Building for production

After cloning the repository:

```bash
npm ci # installs packages from package-lock.json at EXACT versions
```

Build the website and run a static webserver:

```bash
npm run clean # remove build data
npm run build # build the website into dist folder
npm run serve -- -p 1234 # start a static webserver within the dist folder
```


## Quick frontend techstack explainer for ML people

Hello, you are an ML person and you know what `python`, `pip` and `requirements.txt` are. The tech stack that frontend web developers use is quite similar:

- `javascript`: This is the programming language that web browsers understand. It's a dynamic language analogous to Python.
- `typescript`: This is an extension of JavaScript that adds type annotations. Python also has [type annotations](https://realpython.com/python-type-checking/#function-annotations), although not as elaborate.
- `node`: The shell command is `node`, the program name is [Node.js](https://nodejs.org/). This is analogous to the `python3` command that runs Python code, except, this interprets JavaScript code. The developer tools used in the frontend community are often built to run on Node (kinda like Python's `setuptools` are built to run on Python, while processing *other* Python code).
- `npm`: This is the *Node Package Manager*, i.e. the `pip3` command for the Node.js world.
- `npmjs.com`: The repository where most Node packages live (https://www.npmjs.com/). Analogous to Python's PyPi repository (https://pypi.org/).
- `package.json`: Analogous to `requirements.txt`, defines all dependencies for your project. Usually defines dependencies softly, kinda like saying `numpy >= 1.0`.
- `package-lock.json`: Lists the precise version of all packages actually installed in your project. Kinda analogous to having a `requirements.txt` file, where all versions are precisely frozen (like `numpy == 1.26.0rc1`). This is useful when you want to precisely replicate the state of all dependencies, say during deployment.
- `parcel`: A Node.js development tool, that compiles Typescript and optimizes Javascript and produces a compressed, optimized, and backwards-compatible snapshot of your codebase that even old web browsers can understand (browsers don't understand typescript, for example). A somewhat analogous tool would be `setuptools`, but [Parcel](https://parceljs.org/) does much more (like running a development server with hot-reload and such).
- `npm run XYZ`: The `package.json` file also defines a set of commands that you can call like this. These commands typically compile the code, or start the development server. The analogous system I use in the backend server is a `Makefile` with a set of command that I run `make start` (so basically `make start == npm run start`).
