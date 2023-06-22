# app-chyrondetection

General user instruction for CLAMS apps is available at [CLAMS Apps documentation](https://apps.clams.ai/clamsapp/).

## System requirments

This chyron detector relies on the Tesseract library for OCR within the chyron boxes. The various libraries required for Tesseract are visible within the `Containerfile`. Ensure that Tesseract4, as well as which language data you are using, are properly installed (the Container image will do this for you).

## Configurable runtime parameter

The runtime parameters of this app are described in its metadata. In order to use these arguments, simply pass them through the POST request. For instance, the following increases the minimum number of frames that will be labeled as a chyron to 20:

```bash
curl -X POST -d @path/to/target/mmif http://0.0.0.0:5000?minFrameCount=20
```
