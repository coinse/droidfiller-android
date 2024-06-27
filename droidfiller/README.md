# DroidFiller

## How to Run

(offline evaluation)

* `.env` 파일에 OpenAi API key 입력 (`.env.sample` 참고)

* config.json (또는 커스텀 configuration 이름) 파일에 TC 정보 입력 
```json
{
    "state_path": "data/sample/Calendar/state_2022-11-01_172842215734.json",
    "app_name": "Calendar",
    "package_name": "com.samsung.android.calendar",
    "tester_type": "default_tester",
    "profile": "jade",
    "llm_model": "gpt-3.5-turbo-0613",
    "output_dir": "output_sample"
}
```

* `python run_droidfiller.py --config config.json --output_dir output_sample`

    * `config.json` 에 output 디렉토리가 지정되어 있을 경우 argument보다 우선으로 적용됨 

## Future TODO
- [x] Adapt to the recent OpenAI version
- [x] Input-output formatting
```
도구 수행 방식 (screenshot, view-tree를 생성 후 일괄 테스트 하는 방식)
도구 수행에 필요한 파라미터를 json 또는 excel 형태로 TC 작성 
파라미터 : screenshot/view-tree path, app name, package, tester_type, profile, llm_model 등등
해당 TC파일을 input으로 도구 수행
결과는 TC별로 폴더링해서 prompt, 생성된 text 등을 저장
```
- [ ] Support GPT-4-Vision
- [ ] Support ReAct-style prompting


## Check Issues from the Midterm Report 

- [x] 위젯 속성이 같은 경우 결과 저장 이슈 => widget ID에 "bound" property 추가
- [x] App이나 현재 페이지의 인지가 부족하여 적합하지 않은 Input Text 제공 => reasoning template에 현재 페이지에 대한 inference를 먼저 수행하도록 유도
- [ ] Text 입력을 위한 Guide Text를 그대로 사용 => reasoning template을 통해 guide보다는 의미있는 텍스트 입력을 생성하도록 유도 (완벽하지는 않음)
- [x] 제공된 Profile 기준으로 Input Text 제공 => 다른 프로필을 함수 콜을 이용해  불러올 수 있도록 함
- [ ] 의미 없는 단순 테스트용 Input Text 제공 => reasoning template을 통해 의미있는 텍스트 입력을 생성하도록 유도 (완벽하지는 않음)
- [x] App의 언어와 맞지 않는 Input Text 제공 => reasoning template에 텍스트 입력의 언어를 유추하도록 하는 과정 추가
- [x] 한 페이지에 여러 필드가 있을 경우, 서로 연관성 없는 Input Text 제공 => 페이지별로 inference할 때 이전에 예측한 텍스트를 반영한 상태로 다음 텍스트 입력을 생성하도록 함 (`run_droidfiller.py`)
- [x] 응답 양식 중 "INPUT_TEXT"에 텍스트 이외 설명이 포함된 경우 => reasoning template과 프롬프트에서 요구하는 output 형식을 좀더 명확하게 제시함으로써 이런 문제가 최소화되도록 함
