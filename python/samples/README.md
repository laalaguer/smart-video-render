# Folder structure

`./sample.json` a json sample of final cut pro movie project file.

`./jsontomovie.py` a python program to convert a the `sample.json` into ffmpeg commands

`./testbatch.sh` the ffmpeg commands that generated from above.

# How to convert fcp xml to ffmpeg commands?

```
$ python jsontomovie.py >> testbatch.sh
$ ./testbatch.sh
```

