# Publish on GitHub

GitHub account: Haneof
Suggested name: BusinessOS
Visibility: PUBLIC
Initialize with a README: YES (to make branch creation possible)
Do not create a Codespace; existing AIOS Codespaces are unrelated.

1. Open https://github.com/new
2. Choose owner `Haneof`, repository `BusinessOS`, Public, and Add README.
3. Create repository.
4. Transfer this starter's source files into the repo using Git or the connected GitHub integration; include hidden `.github` and `.gitignore` folders.
5. Verify Actions > CI completes on standard hosted runner.
6. Do not add model tokens or credentials to repository files, issues or Actions logs.

With Git on a trusted local computer, after extracting this archive:

```bash
git clone https://github.com/Haneof/BusinessOS.git
cp -a /path/to/extracted/starter/. /path/to/BusinessOS/
cd /path/to/BusinessOS
git add .
git commit -m "chore: bootstrap BusinessOS V0.1 offline governance skeleton"
git push origin main
```

Alternatively, once the repo is created, request that the GitHub connector commit the files on a feature branch and create a Draft PR for review. The GitHub connection used to prepare this project currently cannot create a new repository itself.
