# B+ Tree Visualizer

This python script can draw B+ Trees with some customization.

## Environment

Python 3.8+

`pip install -r requirements.txt`

## Settings

Open the `settings.json` file in the root folder to change the configurations

- `d`: The fanout of each node (fanout = max degree - 1)
- `color`: color of foreground (e.g. arrows, boxes)
- `background`: background color of output image

## Enter data

Open the `in.json` file in the root folder and change it to your B+ Tree array, or you can put it in any other file.

## Execution

```shell
python draw.py --input=in.json -o=out.png
```

This will generate the image using data stored in `in.json` and save the image in
`out.png`. Note that if you have Python2 installed, you should use `python3` rather than `python`
