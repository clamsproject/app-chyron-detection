# app-chyrondetection

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

## System requirments

This chyron detector relies on the Tesseract library for OCR within the chyron boxes. The various libraries required for Tesseract are visible within the `Containerfile`. Ensure that Tesseract4, as well as which language data you are using, are properly installed (the Container image will do this for you).

## Configurable runtime parameter

The runtime parameters of this app are described in its metadata. In order to use these arguments, simply pass them through the POST request. For instance, the following increases the minimum number of frames that will be labeled as a chyron to 20:

```bash
curl -X POST -d @path/to/target/mmif http://0.0.0.0:5000?minFrameCount=20
```
