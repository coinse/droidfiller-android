# DroidFiller

## Integration with Android Test Runners (TODO)

* Should be work with Droidbot or a custom android e2e test runner

## Offline Evaluation (from a static state file)

* Input your OpenAI API key to the `.env` file (refer to the `.env.sample` file)

* Input the information of the testing context to the `config.json` file (or the name of a custom configuration file)

The example content of the configuration file is as below:
```json
{
    "state_path": "data/sample/Calendar/state_2022-11-01_172842215734.json",
    "app_name": "Calendar",
    "package_name": "com.samsung.android.calendar",
    "tester_type": "default_tester",
    "profile": "jade",
    "llm_model": "gpt-4o",
    "output_dir": "output_sample"
}
```

* Run command: `python offline_generation.py --config config.json --output_dir output_sample`

    * The output directory stated in the `config.json` is prioritized over the one given as an argument.
