# B+ Tree Visualizer

This python script draws graphs of B+ Trees.

## Environment

Python 3.10+, Pillow 9+

`pip install -r requirements.txt`

## Settings

Open the `settings.json` file in the root folder to change the configurations

`d`: The degree/order/fanout of each node.

## Enter data

Open the `in.json` file in the root folder and change it to your B+ Tree array, or you can put it in any other file.

## Execution

Open the terminal and enter the following command:

```shell
python draw.py <INPUT_FILE> -o <OUTPUT_FILE>
```

where `<INPUT_FILE>` is the json file containing the B+ Tree array and `<OUTPUT_FILE>` is the output PNG file. For example,

```shell
python draw.py in.json -o out.png
```

will generate the image using data stored in `in.json` and save the image in `out.png`. Note that if you are using a Windows system then you should replace `python` with `python3`.
