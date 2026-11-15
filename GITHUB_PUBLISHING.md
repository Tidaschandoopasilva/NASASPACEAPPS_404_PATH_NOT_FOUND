# Create and publish the Team 404 GitHub repository

The included Windows launcher can create this **public** repository and upload the prepared codebase:

`https://github.com/Tidaschandoopasilva/NASASPACEAPPS_404_PATH_NOT_FOUND`

**No repository is created by downloading or extracting this ZIP.** The publish action happens only when you run `CREATE_AND_PUBLISH_GITHUB.cmd` locally and authenticate.

## Automatic upload on Windows

1. Extract the full ZIP.
2. Install [Git for Windows](https://git-scm.com/download/win) if you do not already have it. The helper also needs [GitHub CLI](https://cli.github.com/). When possible it offers to install the CLI using Windows Package Manager (`winget`).
3. In the extracted root, double-click **`CREATE_AND_PUBLISH_GITHUB.cmd`**.
4. Sign in through the official GitHub CLI browser flow; confirm the account shown is `Tidaschandoopasilva`.
5. The helper initializes a repository, stages all source files and **force-adds `apps/web/dist`** (needed for the standalone desktop), commits, creates the GitHub repository if missing, and pushes `main`.
6. Confirm the repository is public and that README images appear correctly on GitHub.

**Safety:** The script refuses to publish to a different account, does not force-push, and does not delete an existing repository. If the remote already has independent commits, `git push` can reject non-fast-forward history; reconcile the branches manually rather than overwriting it. Do not paste passwords or GitHub access tokens into chat.

## Manual alternative (GitHub CLI)

From a command prompt in the extracted project folder, if `gh` and `git` are installed:

```cmd
gh auth login --web
gh auth setup-git
git init -b main
git add --all
git add -f apps/web/dist
git commit -m "Publish Team 404 Mars Habitat V7"
gh repo create Tidaschandoopasilva/NASASPACEAPPS_404_PATH_NOT_FOUND --public --source . --remote origin --push
```

The automatic launcher is safer for repeat runs because it checks GitHub identity, existing remotes and push status.

## Exclusions and artifacts

The repository includes the Python code, React code, bundled models, terrain and 3D assets, screenshots, research data, package lock file, test suite, documentation, **and the compiled desktop web app**. It does not include machine-local `.venv`, `node_modules`, SQLite campaign records, API tokens or `.env` secrets. See `.gitignore`.
