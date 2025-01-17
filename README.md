# DroidFiller: Customisable LLM-based Text Generation for Automated GUI Testing

This repository contains artifacts for the paper titled "Integrating LLM-based Text Generation with Dynamic Context Retrieval for GUI Testing". Note that the industrial GUI testing tool, STEM (Scenario-learnt Test Execution Model), and the LLM-based text input generation technique, DroidFiller, remain proprietary.

As STEM is not available for public use, we support to use DroidFiller with [DroidBot](https://github.com/honeynet/droidbot) as well, which is an open-source test automation tool for Android applications. You can add your custom tools for dynamic context retrieval to adapt DroidFiller to your own testing environment.

## Installation

### Prerequisites
* Tested on Python 3.11.2
* Install the required packages by running `pip install -r requirements.txt`
* Install [DroidBot](https://github.com/honeynet/droidbot) if you want to use DroidFiller integrated with DroidBot

### Install DroidFiller
```bash
> cd droidfiller
> pip install -e .
```


## Usage Example (w/ DroidBot)
```python
import logging
import time
from pathlib import Path

from droidbot.device import Device
from droidbot.app import App
from droidbot.input_event import SetTextEvent

from droidfiller import Agent

POST_EVENT_WAIT = 1

logging.basicConfig(level=logging.INFO) # Adjust the log level as needed

output_dir = Path('test_output_droidbot') # Directory to record the prompts/responses as well as the generated text inputs

device = Device(device_serial='emulator-5554', output_dir=output_dir, grant_perm=True, is_emulator=args.is_emulator)
device.set_up()
device.connect()

# Initialise the DroidFiller agent
agent = Agent(app_name=args.app_name, tester_type=args.tester_type, profile_name=args.profile_name, llm_model=args.llm_model, output_dir=output_path, tool_config_file_path='./example_tool_config.yml')

possible_inputs = state.get_possible_input()
for possible_input in possible_inputs:
    if isinstance(possible_input, SetTextEvent):
        state = device.get_current_state()

        # Set text suggested by DroidFiller
        possible_input.text = agent.gen_text_input(state, possible_input.view, source='droidbot')  
        device.send_event(possible_input)
        time.sleep(POST_EVENT_WAIT)

device.disconnect()
device.tear_down()
```

### Customising Tools (for Dynamic Context Retrieval)
You can use your own configurations for dynamic context retrieval by writing a YAML file similar to the `example_tool_config.yml` file. The path to the configuration file is passed to the DroidFiller's `Agent` class as a parameter. (e.g., `agent = Agent(app_name=args.app_name, tester_type=args.tester_type, profile_name=args.profile_name, llm_model=args.llm_model, output_dir=output_path, tool_config_file_path='./example_tool_config.yml')`)

The configuration should contain the textual description of the tool (e.g., content of the returned data, required parameters, etc.) and the actual Python code that defines the tool as a function definition. Each tool should have a unique name and return a stringified JSON object that contains the dynamic context that can be referred to by the LLM model when generating text inputs.

The file should be formatted as below (refer to the `example_tool_config.yml` file for the full structure):

```yaml
tools:
[...]
  get_galaxy_store_coupon_code:
    description:
      type: function
      function:
        name: get_galaxy_store_coupon_code
        description: Get an available galaxy store coupon code list when you are asked to fill in the coupon code textfield for the galaxy store app
        parameters:
          type: object
          properties: {}

    implementation: |
      def get_galaxy_store_coupon_code():
        return json.dumps({
            "coupon_code": ["ref-gf8ff4", "ref-3iwi87", "ref-d5nzrs"],
        })
```

## Evaluation Artifact for the Paper: Integrating LLM-based Text Generation with Dynamic Context Retrieval for GUI Testing

This repository contains some information that could not fit the paper due to the page limit (for example, the list of apps that are studied). It also contains scripts used to analyse the empirical evaluation results. (`RQ_*.ipynb` files)

### List of subjects for text generation quality evaluation

Below are the list of applications and textfield IDs used in our text generation quality evaluation (RQ1 ~ RQ4)

| App Name (App ID)                                      | Textfield ID                |
|------------------------------------------------|-----------------------------|
| org.koitharu.kotatsu                           | searchView_198_119          |
| AOL_News_Mail_Video_v6.47.2                    | search_edit_text_182_66     |
| de.kromke.andreas.opus1musicplayer             | search_src_text_111_71      |
| Petal_Maps‚ÄìGPS_Navigation_v2.5.0.303(002)    | search_src_text_174_1600    |
| AutoScout24_Buy_sell_cars                      | textinput_filter_edittext_188_301 |
| Tubi_Movies                                    | name_53_486                 |
| Tubi_Movies                                    | email_53_859                |
| Tubi_Movies                                    | text_year_or_age_53_674     |
| Tubi_Movies                                    | gender_593_674              |
| Tubi_Movies                                    | password_53_1047            |
| Tubi_Movies                                    | search_input_box_50_214     |
| com.velas.mobile_wallet                        | 384035467                   |
| com.velas.mobile_wallet                        | 718740312                   |
| Podcast_Addict_Podcast_player_v2022.4          | pattern_86_306              |
| de.chaosdorf.meteroid                          | hostname_44_360             |
| com.invoiceninja.app                           | _88_943                     |
| com.invoiceninja.app                           | _88_1106                    |
| com.invoiceninja.app                           | _88_1268                    |
| com.poupa.vinylmusicplayer                     | title1_44_272               |
| com.poupa.vinylmusicplayer                     | title2_44_433               |
| com.poupa.vinylmusicplayer                     | artist_44_660               |
| com.poupa.vinylmusicplayer                     | genre_44_821                |
| com.poupa.vinylmusicplayer                     | year_44_982                 |
| com.poupa.vinylmusicplayer                     | track_number_44_1143        |
| com.poupa.vinylmusicplayer                     | disc_number_44_1304         |
| com.poupa.vinylmusicplayer                     | lyrics_44_1465              |
| com.poupa.vinylmusicplayer                     | search_src_text_220_93      |
| org.billthefarmer.currency                     | edit_494_242                |
| Podcast_Player_v7.0.0-220308033.rd0a0ae8       | zk_220_93                   |
| BBC_News_v5.23.0                               | search_198_179              |
| Brave_Private_Web_Browser_v1.39.115            | url_bar_154_74              |
| Brave_Private_Web_Browser_v1.39.115            | url_bar_121_74              |
| Brave_Private_Web_Browser_v1.39.115            | 985110063                   |
| Messenger                                      | Phonenumberoremail_55_1442  |
| Messenger                                      | Password_55_1598            |
| deep.ryd.rydplayer                             | _155_1041                   |
| Plex_Stream_Movies_TV                          | 2049720230                  |
| im.status.ethereum                             | password-input_88_597       |
| im.status.ethereum                             | password-input_88_806       |
| BOTIM_Video_and_Voice_Call_v2.7.9              | search_box_22_242           |
| nl.asymmetrics.droidshows                      | search_src_text_183_81      |
| nl.asymmetrics.droidshows                      | search_text_0_220           |
| org.y20k.escapepod                             | search_src_text_248_1053    |
| OK_Social_Network_v22.6.1                      | text_login_66_448           |
| OK_Social_Network_v22.6.1                      | password_text_66_607        |
| Hulu                                           | email_66_653                |
| Hulu                                           | password_66_875             |
| org.totschnig.myexpenses                       | Payee_327_641               |
| org.totschnig.myexpenses                       | AmountEditText_459_361      |
| org.totschnig.myexpenses                       | Comment_327_1055            |
| org.totschnig.myexpenses                       | tag_edit_44_220             |
| org.totschnig.myexpenses                       | Payee_327_641               |
| org.totschnig.myexpenses                       | Label_327_227               |
| org.totschnig.myexpenses                       | Description_327_365         |
| org.totschnig.myexpenses                       | AmountEditText_459_499      |
| org.totschnig.myexpenses                       | AmountEditText_459_1327     |
| Issuu_magazines_news_books_v5.67.0             | search_src_text_154_92      |
| Firefox_Fast_Private_Browser_v101.1.1          | mozac_browser_toolbar_edit_url_view_154_1331 |
| co.appreactor.news                             | serverUrl_44_301            |
| co.appreactor.news                             | username_44_654             |
| co.appreactor.news                             | password_44_877             |
| Opera_Mini_fast_web_browser_v63.0.2254.61942   | url_field_140_231           |
| HERE_WeGo_Maps_Navigation_v4.4.200             | _44_176                     |
| Waze_Navigation_Live_Traffic_v4.84.0.2         | sideMenuSearchBox_33_621    |
| Instagram                                      | confirmation_field_77_508   |
| Instagram                                      | full_name_77_391            |
| Instagram                                      | password_77_567             |
| Instagram                                      | search_122_278              |
| Instagram                                      | full_name_77_391            |
| Instagram                                      | password_77_567             |
| Instagram                                      | email_field_77_747          |
| Instagram                                      | phone_field_293_744         |
| me.hackerchick.catima                          | storeNameEdit_199_417       |
| me.hackerchick.catima                          | cardIdView_28_613           |
| me.hackerchick.catima                          | cardId_285_408              |
| me.hackerchick.catima                          | search_src_text_176_103     |
| WhatsApp                                       | registration_phone_400_480  |
| WhatsApp                                       | registration_cc_182_480     |
| WhatsApp                                       | verify_sms_code_input_320_392 |
| WhatsApp                                       | registration_phone_400_480  |
| WhatsApp                                       | registration_cc_182_480     |
| Settings                                       | search_src_text_137_106     |
| GalaxyStore                                    | coupon_edit_89_1912         |
| GalaxyStore                                    | search_src_text_153_118     |
| GalaxyStore                                    | name_86_725                 |
| GalaxyStore                                    | phoneNumber_86_1846         |
| SmartThings                                    | inviteAccountText_63_463    |
| SmartThings                                    | search_src_text_137_178     |
| SmartThings                                    | edit_text_name_47_303       |
| Messages                                       | recipients_editor_to_58_262 |
| Messages                                       | message_edit_text_440_2154  |
| Messages                                       | search_src_text_138_106     |
| Calendar                                       | title_63_238                |
| Calendar                                       | location_167_907            |
| Calendar                                       | note_text_167_1473          |
| Gallery                                        | search_src_text_137_106     |
| Contacts                                       | forCursorEdit_158_557       |
| Contacts                                       | forCursorEdit_158_819       |
| Contacts                                       | forCursorEdit_158_1408      |
| Contacts                                       | forCursorEdit_158_1560      |
| Contacts                                       | forCursorEdit_158_1807      |
| Contacts                                       | nameEdit_144_701            |
| Contacts                                       | editOrganizationTitle_144_963 |
| Contacts                                       | editOrganizationDepartment_144_1079 |
| Contacts                                       | editOrganizationCompany_144_1195 |
| Contacts                                       | search_src_text_137_106     |
| SamsungMembers                                 | inputEditText_47_618        |
| SamsungMembers                                 | inputEditText_47_825        |
| SamsungMembers                                 | nickname_63_1622            |
| MyFiles                                        | search_src_text_137_106     |
| MyFiles                                        | search_src_text_137_106     |
| SamsungInternet                                | location_bar_edit_text_205_106 |
| Clock                                          | numberpicker_input_144_408  |
| Clock                                          | numberpicker_input_612_408  |
| Clock                                          | alarm_name_47_1388          |
| Clock                                          | worldclock_search_map_txt_find_158_140 |
| Clock                                          | hour_48_1787                |
| Clock                                          | minute_201_1787             |
| Clock                                          | second_354_1787             |
| Clock                                          | preset_name_48_1944         |
