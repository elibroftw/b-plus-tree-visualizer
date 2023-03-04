# B+ Tree Visualizer
 This python script draws graphs of B+ Trees.

## Environment:

Python 3.10+, pillow 9+

## Settings:

Open the `settings.json` file in the root folder to change the configurations. The meaning of each of them is straight forward, so I will not explain it here.

## Enter data:

Open the `in.json` file in the root folder and change it to your B+ Tree array, or you can put it in any other file.

## Execution:

open the terminal and enter the following command:

```shell
python draw.py <INPUT_FILE> -o <OUTPUT_FILE>
```

where `<INPUT_FILE>` is the json file containing the B+ Tree array and `<OUTPUT_FILE>` is the output PNG file. For example,

```shell
python draw.py in.json -o out.png
```

will generate the image using data stored in `in.json` and save the image in `out.png`.
