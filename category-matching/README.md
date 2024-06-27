# gui-text-input-generator

## Dependencies

To satisfy prerequisite, run below commands on the project root:

```bash
> pip install -r requirements.txt 
> wget https://www.dropbox.com/s/l24p9l9q13unz0j/cc.en.300.bin # or download directly from https://www.dropbox.com/s/l24p9l9q13unz0j/cc.en.300.bin?raw=1

```

## How to run

To predict category of a textfield and possible input texts in it, we provide the script `predict_string.py` which accepts JSON files of Android screen states and produce rankings of matching categories & text input values.

```bash 
> python predict_string.py -i data/samsung_internal -o result/text_input_pred_samsung.json --predict-value --sample-value-file data/value_pool.json
```

The above script collects Android screen state files (with filenames like `state_*.json`) contained in the `data/samsung_internal` directory (refer to the existing state files in the directory), and predict text input categories & values for the contained textfields in the screen. The result is saved into `result/text_input_pred_samsung.json`.


## Customization

### Using custom value pool

If you want to use your own value pool for each concrete category (i.e., primary category with no belonging secondary categories, or the final predicted secondary category), you can modify `data/value_pool.json`, or create your own one in the form of JSON file. Then, execute the script `predict_string.py` with the option `--sample-value-file <your_value_pool_file_path>`.

### Changing pruning count, or weights of the global context
There are some options in `predict_string.py`, such as `--pruning-count`, `--w-glob-primary`, and `--w-glob-secondary` that can be tuned. You can decide on how much emphasize the global context when predicting primary/secondary categories. For more detail, refer to the description of each option.

## Maintainer
Contact to @greenmonn (juyeon.yoon@kaist.ac.kr) if you have any problem or question about this repository.