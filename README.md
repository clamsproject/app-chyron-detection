# BURN AFTER READING

Delete this section of the document once the app development is done, before publishing the repository. 

---
This skeleton code is a scaffolding for Python-based CLAMS app development. Specifically, it contains 

1. `app.py` and `metadata.py` to write the app 
1. `requirements.txt` to specify python dependencies
1. `Containerfile` to containerize the app and specify system dependencies
1. `.gitignore` and `.dorckrignore` files listing commonly ignored files
1. an empty `LICENSE` file to replace with an actual license information of the app
1. `CLAMS-generic-readme.md` file with basic instructions of app installation and execution
1. This `README.md` file for additional information not specified in the generic readme file. 
1. A number of GitHub Actions workflows for issue/bug-report management 
1. A GHA workflow to publish app images upon any push of a git tag
   * **NOTE**: All GHA workflows included are designed to only work in repositories under `clamsproject` organization.

Before pushing your first commit, please make sure to delete this section of the document.

Then use the following section to document any additional information specific to this app. If your app works significantly different from what's described in the generic readme file, be as specific as possible. 

---

## User instruction

General user instruction for CLAMS apps is available at [CLAMS Apps documentation](https://apps.clams.ai/clamsapp/).

We provide a `Containerfile`. If you want to run this app as a docker container (not worrying about dependencies), build 
an image from the `Containerfile` via the following command in the app directory:

```bash
docker build . -f Containerfile -t chyrons
```

Then, run the image with the target directory mounted to `/data`. Just MAKE SURE that target directory is writable by others (`chmod o+w $TARGET_DIR`):

```bash
docker run -v path/to/target/data:/data -p 5000:5000
```

From here, the app can be run through the terminal, by posting a mmif file to the host port:

```bash
curl -X POST -d @path/to/target/mmif http://0.0.0.0:5000
```

### System requirments

(Any system-level software required to run this app)

### Configurable runtime parameter

(Parameters should be already well-described in the app metadata. But you can use this space to show examples, for instance.)