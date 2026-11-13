# Learning Labs: Secure-by-default agent workflows

This is the sample repo for the Chainguard Learning Lab on secure-by-default agent workflows. You'll make your own copy of it, add [Chainguard Checks](https://www.chainguard.dev/products/checks) to it, and watch your CI run in an isolated microVM next to the existing GitHub Actions workflow.

The app is a small bookshelf REST API written in Python with Flask. The app itself isn't the point; the CI is.

## What you need

- A GitHub account where you can create repositories. A personal account is fine.
- [Git](https://git-scm.com/downloads), and optionally the [GitHub CLI](https://cli.github.com/) (`gh`).
- `chainctl`, Chainguard's command-line tool: [install instructions](https://www.chainguard.dev/docs/chainguard/chainctl-usage/how-to-install-chainctl/).

Everything in this lab runs on Chainguard's free Starter plan. You don't need a coding agent or a credit card.

## The steps

### 1. Make your own copy of this repo

Use the template rather than forking. Forks have GitHub Actions turned off by default, and pull requests from a fork go to the original repo.

```shell
gh repo create my-agent-workflows-lab --template chainguard-demo/learning-labs-agent-workflows --public --clone
cd my-agent-workflows-lab
```

No `gh`? Click **Use this template** at the top of this page, create the repo, then `git clone` it.

### 2. Set up Chainguard

From inside your copy, run:

```shell
chainctl develop init
```

You'll log in, pick or create an organization, accept the agreements, and link GitHub. Two things to know:

- Your browser may ask you to **authorize Chainguard more than once**. After each one, come back to your terminal; it won't remind you.
- When GitHub asks which repositories the Chainguard App can access, **include your copy of this repo**.

### 3. Create a branch first

```shell
git switch -c add-chainguard-checks
```

### 4. Add the Checks configuration

```shell
mkdir -p .chainguard
cp workshop/ci.yaml .chainguard/ci.yaml
chainctl checks validate .
```

`ok: the document lowers` means the configuration is valid.

Have a look at [`.chainguard/ci.yaml`](workshop/ci.yaml). Each check lists the packages it needs, the commands it runs, and the hosts it may reach under `network.egress`. A check can't connect to anything else.

### 5. Push and open a pull request

```shell
git add .chainguard
git commit -m "Add Chainguard Checks"
git push -u origin add-chainguard-checks
```

Then open the pull request in your browser, in your own repo.

### 6. Watch it run

On the pull request you'll see two kinds of checks:

- **GitHub Actions** (`CI / ...`): the existing workflow in [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
- **Chainguard Checks (presubmit)**: a summary of the checks you just added. "Presubmit" means they run on the pull request, before merge.

Compare how long each takes. Then open the `egress-demo` check: it tries to reach `example.com`, which isn't on its list, and the connection is refused.

### 7. Optional: require the checks before merging

In your repo's **Settings > Rules > Rulesets**, add a rule for your default branch that requires the status check **Chainguard Checks (presubmit)**.

## What just happened

- Each check ran in its own fresh microVM, defined by a file in your repo.
- No long-lived secrets were stored anywhere. A check that needs cloud access asks for short-lived credentials instead.
- Each check could only reach the hosts it listed. Anything else was refused.

You can also run the same checks from your terminal with `chainctl checks run . --watch`, and inside a [Chainguard Workspace](https://www.chainguard.dev/products/workspaces) with `run-ci`.

## If you're stuck

- **No Chainguard checks appear on the pull request.** The Chainguard App probably can't see your repo. Check the repositories it can access in your GitHub settings under **Integrations > Applications**, and add your copy.
- **No GitHub Actions run appears.** Check that Actions are enabled under your repo's **Settings > Actions**.
- **`chainctl` asks which organization to use.** Pick the one `chainctl develop init` created or chose for you.

It's fine not to finish during the session: these steps work just the same afterwards.

## Learn more

- [Chainguard Checks docs](https://www.chainguard.dev/docs/chainguard/checks/overview/)
- [Chainguard Workspaces docs](https://www.chainguard.dev/docs/chainguard/workspaces/overview/)
- Questions: #checks-questions and #workspaces-questions in the [Chainguard community Slack](https://join.slack.com/t/chainguardcommunity/shared_invite/zt-3nttdr807-V9BJHayWvsB0KbHsfZO5Rw)

## Running the app yourself

```shell
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m bookshelf
```

The API listens on `http://127.0.0.1:8000`: try `/health` and `/books`.

This repo is a demo for a Chainguard Learning Lab. It's licensed under [Apache-2.0](LICENSE).
