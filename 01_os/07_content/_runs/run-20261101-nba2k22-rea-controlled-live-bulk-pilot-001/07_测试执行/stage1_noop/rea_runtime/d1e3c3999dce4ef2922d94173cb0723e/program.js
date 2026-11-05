'use strict';
const request={"action_id":"PLAYER_PATCH_TENDENCIES","chunk_id":"chunk-0002-team-28-player-patch-tendencies","parameters":{"batch_id":"BATCH-PILOT-STAGE1-NOOP-20261101","save_instance_id":"MyLEAGUE0003"},"team_id":28},bindingSpecs={"coach.apply_gameplan":{"abi":"win64","binding_id":"coach.apply_gameplan","evidence":["../rea_native_action/evidence/live/verified-poc/evidence.json"],"game_build_sha256":"1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5","input_layout":{"coach_bytes":352,"code_signatures":[{"bytes":426,"fnv32":2422672907,"rva":21424800}],"defense_shift":0,"defense_source":385,"input_bytes":880,"offense_shift":15,"shared_word":316},"lifecycle":["Current Coach projection; original Gameplan remains unchanged"],"object_requirements":["Fresh team/reciprocal Coach/manager objects","Three referenced slots NULL; marshal all other current settings"],"parameters":[{"name":"input_GAMEPLAN","type":"pointer"},{"name":"target_COACHDATA","type":"pointer"}],"return_type":"void","rva":21424800,"unknowns":[]},"player.get_stat_ui":{"abi":"win64","binding_id":"player.get_stat_ui","evidence":["01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/player_stat_read_getter_contract_026.json"],"game_build_sha256":"1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5","input_layout":{"code_signatures":[{"bytes":2580,"fnv32":2751660889,"rva":9929568},{"bytes":4,"fnv32":1798808928,"rva":36408044},{"bytes":4,"fnv32":1487269050,"rva":35762196}]},"lifecycle":["Pure selected Getter paths: no game memory writes or calls. Use original float conversion/rounding; no guessed JS attribute decoder"],"object_requirements":["Exact current roster PLAYER; explicit selected qualified index excluding Potential/unclassified cases"],"parameters":[{"name":"player","type":"pointer"},{"name":"stat_index","type":"int"}],"return_type":"int","rva":9929568,"unknowns":[]},"player.set_stat_ui":{"abi":"win64","binding_id":"player.set_stat_ui","evidence":["PLAYER_STAT_NATIVE_CONTRACT.md","01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/player_indexed_stat_setters_012.json","01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/player_indexed_stat_field_contract_015.json","01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/player_stat_delegate_thunk_016.json","../../config/memory_field_profile.json","../../config/state_io_native/player.json"],"game_build_sha256":"1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5","input_layout":{"code_signatures":[{"bytes":5992,"fnv32":3294578483,"rva":10029584},{"bytes":2580,"fnv32":2751660889,"rva":9929568}],"effect":"Native clamp/encoding/specific setter, UI getter and current delegate slot1248 notification; wrapper rejects values requiring clamp","return_contract":"Original callers ignore return; adapter discards the tail callback result"},"lifecycle":["Deferred GUI-thread operation; current save/phase and role grant supplied by trusted host"],"object_requirements":["Exact supplied current roster PLAYER and TEAM; supported fresh delegate method footprint"],"parameters":[{"name":"player","type":"pointer"},{"name":"stat_index","type":"int"},{"name":"value","type":"int"}],"return_type":"void","rva":10029584,"unknowns":[]},"player.stat_context":{"abi":"win64","binding_id":"player.stat_context","evidence":["PLAYER_STAT_NATIVE_CONTRACT.md","01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/player_indexed_stat_setters_012.json","01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/player_indexed_stat_field_contract_015.json","01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/player_stat_delegate_thunk_016.json","../../config/memory_field_profile.json","../../config/state_io_native/player.json"],"game_build_sha256":"1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5","input_layout":{"code_signatures":[{"bytes":22,"fnv32":1882246386,"rva":18541376},{"bytes":8,"fnv32":3017607810,"rva":18713280},{"bytes":32,"fnv32":3639587293,"rva":18823392},{"bytes":71,"fnv32":3243187489,"rva":10049296},{"bytes":71,"fnv32":2279101764,"rva":10055712},{"bytes":71,"fnv32":1008788835,"rva":10055792},{"bytes":71,"fnv32":687734794,"rva":10055536},{"bytes":71,"fnv32":1884184507,"rva":10048912},{"bytes":71,"fnv32":2741766004,"rva":10059664},{"bytes":71,"fnv32":1488594455,"rva":10060000},{"bytes":71,"fnv32":474485821,"rva":10060112},{"bytes":71,"fnv32":3970498604,"rva":10059840},{"bytes":71,"fnv32":1354805692,"rva":10047488},{"bytes":71,"fnv32":438588189,"rva":10052560},{"bytes":71,"fnv32":718559730,"rva":10052480},{"bytes":71,"fnv32":742330737,"rva":10059392},{"bytes":71,"fnv32":2614413764,"rva":10059312},{"bytes":71,"fnv32":1179898897,"rva":10051632},{"bytes":71,"fnv32":1616321608,"rva":10052800},{"bytes":71,"fnv32":2207595669,"rva":10051776},{"bytes":71,"fnv32":3649733236,"rva":10052640},{"bytes":71,"fnv32":2851639702,"rva":10048576},{"bytes":71,"fnv32":918066350,"rva":10061328},{"bytes":71,"fnv32":2724834937,"rva":10048768},{"bytes":71,"fnv32":2175641770,"rva":10051328},{"bytes":71,"fnv32":3821533940,"rva":10061232},{"bytes":71,"fnv32":2281428419,"rva":10049200},{"bytes":71,"fnv32":2255279593,"rva":10060912},{"bytes":71,"fnv32":55325782,"rva":10060992},{"bytes":71,"fnv32":2714491873,"rva":10059104},{"bytes":71,"fnv32":1320736274,"rva":10061776},{"bytes":71,"fnv32":1458022737,"rva":10061456},{"bytes":71,"fnv32":2547526848,"rva":10061152},{"bytes":71,"fnv32":1784359445,"rva":10051456},{"bytes":71,"fnv32":2229881920,"rva":10059920},{"bytes":71,"fnv32":3785682985,"rva":10052336},{"bytes":71,"fnv32":3593424932,"rva":10051536},{"bytes":71,"fnv32":2202270774,"rva":10049984},{"bytes":71,"fnv32":3259502096,"rva":10050384},{"bytes":71,"fnv32":2196740568,"rva":10049584},{"bytes":71,"fnv32":865239833,"rva":10050544},{"bytes":71,"fnv32":41153213,"rva":10050624},{"bytes":71,"fnv32":4175132097,"rva":10049664},{"bytes":71,"fnv32":1673542366,"rva":10049744},{"bytes":71,"fnv32":2324246877,"rva":10050064},{"bytes":71,"fnv32":2091457500,"rva":10050144},{"bytes":71,"fnv32":3398018942,"rva":10050224},{"bytes":71,"fnv32":2639536682,"rva":10050304},{"bytes":71,"fnv32":2952561637,"rva":10049424},{"bytes":71,"fnv32":1845710646,"rva":10049504},{"bytes":71,"fnv32":3639708517,"rva":10049824},{"bytes":71,"fnv32":601444060,"rva":10049904},{"bytes":71,"fnv32":2172209296,"rva":10050464},{"bytes":71,"fnv32":457833405,"rva":10052720},{"bytes":71,"fnv32":873156466,"rva":10052880},{"bytes":71,"fnv32":1865119514,"rva":10050896},{"bytes":71,"fnv32":1788655774,"rva":10059760}],"fields":{"attributes":{"3pt_shot":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / 3pt_shot","minimum":25,"name_known":true,"native_index":7,"offset":1062},"acceleration":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / acceleration","minimum":25,"name_known":true,"native_index":26,"offset":1081},"back_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / back_durability","minimum":25,"name_known":true,"native_index":37,"offset":1092},"ball_control":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / ball_control","minimum":25,"name_known":true,"native_index":9,"offset":1064},"block":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / block","minimum":25,"name_known":true,"native_index":18,"offset":1073},"defensive_consistency":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / defensive_consistency","minimum":25,"name_known":true,"native_index":20,"offset":1075},"defensive_rebound":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / defensive_rebound","minimum":25,"name_known":true,"native_index":13,"offset":1068},"draw_foul":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / draw_foul","minimum":25,"name_known":true,"native_index":4,"offset":1059},"driving_dunk":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / driving_dunk","minimum":25,"name_known":true,"native_index":23,"offset":1078},"driving_layup":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / driving_layup","minimum":25,"name_known":true,"native_index":0,"offset":1055},"free_throw":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / free_throw","minimum":25,"name_known":true,"native_index":8,"offset":1063},"hands":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / hands","minimum":25,"name_known":true,"native_index":54,"offset":1109},"head_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / head_durability","minimum":25,"name_known":true,"native_index":35,"offset":1090},"help_defensive_iq":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / help_defensive_iq","minimum":25,"name_known":true,"native_index":21,"offset":1076},"hustle":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / hustle","minimum":25,"name_known":true,"native_index":30,"offset":1085},"intangibles":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / intangibles","minimum":25,"name_known":true,"native_index":33,"offset":1088},"interior_defense":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / interior_defense","minimum":25,"name_known":true,"native_index":14,"offset":1069},"lateral_quickness":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / lateral_quickness","minimum":25,"name_known":true,"native_index":16,"offset":1071},"left_ankle_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / left_ankle_durability","minimum":25,"name_known":true,"native_index":46,"offset":1101},"left_elbow_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / left_elbow_durability","minimum":25,"name_known":true,"native_index":40,"offset":1095},"left_foot_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / left_foot_durability","minimum":25,"name_known":true,"native_index":48,"offset":1103},"left_hip_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / left_hip_durability","minimum":25,"name_known":true,"native_index":42,"offset":1097},"left_knee_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / left_knee_durability","minimum":25,"name_known":true,"native_index":44,"offset":1099},"left_shoulder_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / left_shoulder_durability","minimum":25,"name_known":true,"native_index":38,"offset":1093},"mid_range_shot":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / mid_range_shot","minimum":25,"name_known":true,"native_index":6,"offset":1061},"misc_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / misc_durability","minimum":25,"name_known":true,"native_index":50,"offset":1105},"neck_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / neck_durability","minimum":25,"name_known":true,"native_index":36,"offset":1091},"offensive_consistency":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / offensive_consistency","minimum":25,"name_known":true,"native_index":32,"offset":1087},"offensive_rebound":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / offensive_rebound","minimum":25,"name_known":true,"native_index":12,"offset":1067},"pass_perception":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / pass_perception","minimum":25,"name_known":true,"native_index":17,"offset":1072},"passing_accuracy":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / passing_accuracy","minimum":25,"name_known":true,"native_index":11,"offset":1066},"passing_iq":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / passing_iq","minimum":25,"name_known":true,"native_index":10,"offset":1065},"passing_vision":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / passing_vision","minimum":25,"name_known":true,"native_index":52,"offset":1107},"perimeter_defense":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / perimeter_defense","minimum":25,"name_known":true,"native_index":15,"offset":1070},"pick_and_roll_defensive_iq":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / pick_and_roll_defensive_iq","minimum":25,"name_known":true,"native_index":53,"offset":1108},"post_fadeaway":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / post_fadeaway","minimum":25,"name_known":true,"native_index":1,"offset":1056},"post_hook":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / post_hook","minimum":25,"name_known":true,"native_index":2,"offset":1057},"post_moves":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / post_moves","minimum":25,"name_known":true,"native_index":3,"offset":1058},"potential":{"blocked_reason":"Potential dispatch invokes an additional broad refresh path that is not yet qualified","callable":false,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / potential","minimum":25,"name_known":true,"native_index":34,"offset":1089},"right_ankle_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / right_ankle_durability","minimum":25,"name_known":true,"native_index":47,"offset":1102},"right_elbow_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / right_elbow_durability","minimum":25,"name_known":true,"native_index":41,"offset":1096},"right_foot_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / right_foot_durability","minimum":25,"name_known":true,"native_index":49,"offset":1104},"right_hip_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / right_hip_durability","minimum":25,"name_known":true,"native_index":43,"offset":1098},"right_knee_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / right_knee_durability","minimum":25,"name_known":true,"native_index":45,"offset":1100},"right_shoulder_durability":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / right_shoulder_durability","minimum":25,"name_known":true,"native_index":39,"offset":1094},"shot_close":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / shot_close","minimum":25,"name_known":true,"native_index":5,"offset":1060},"shot_contest":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / shot_contest","minimum":25,"name_known":true,"native_index":55,"offset":1110},"shot_iq":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / shot_iq","minimum":25,"name_known":true,"native_index":31,"offset":1086},"speed":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / speed","minimum":25,"name_known":true,"native_index":24,"offset":1079},"speed_with_ball":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / speed_with_ball","minimum":25,"name_known":true,"native_index":25,"offset":1080},"stamina":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / stamina","minimum":25,"name_known":true,"native_index":29,"offset":1084},"standing_dunk":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / standing_dunk","minimum":25,"name_known":true,"native_index":22,"offset":1077},"steal":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / steal","minimum":25,"name_known":true,"native_index":19,"offset":1074},"strength":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / strength","minimum":25,"name_known":true,"native_index":28,"offset":1083},"vertical":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_RATING","expected_raw_formula":"3*value-75","maximum":99,"meaning":"attributes / vertical","minimum":25,"name_known":true,"native_index":27,"offset":1082}},"tendencies":{"ALLEY_OOP_PASS_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"ALLEY_OOP_PASS_TENDENCY","minimum":0,"name_known":true,"native_index":148,"offset":1203},"ALLEY_OOP_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"ALLEY_OOP_TENDENCY","minimum":0,"name_known":true,"native_index":62,"offset":1117},"ATTACK_STRONG_ON_DRIVE":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"ATTACK_STRONG_ON_DRIVE","minimum":0,"name_known":true,"native_index":120,"offset":1175},"BLOCK_SHOT_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"BLOCK_SHOT_TENDENCY","minimum":0,"name_known":true,"native_index":153,"offset":1208},"CONTESTED_JUMPER_MID_RANGE":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"CONTESTED_JUMPER_MID_RANGE","minimum":0,"name_known":true,"native_index":92,"offset":1147},"CONTESTED_JUMPER_THREE":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"CONTESTED_JUMPER_THREE","minimum":0,"name_known":true,"native_index":91,"offset":1146},"CONTEST_SHOT_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"CONTEST_SHOT_TENDENCY","minimum":0,"name_known":true,"native_index":152,"offset":1207},"CRASH_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"CRASH_TENDENCY","minimum":0,"name_known":true,"native_index":64,"offset":1119},"DISH_TO_OPEN_MAN_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"DISH_TO_OPEN_MAN_TENDENCY","minimum":0,"name_known":true,"native_index":121,"offset":1176},"DRIVE_PULL_UP_MID_RANGE":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"DRIVE_PULL_UP_MID_RANGE","minimum":0,"name_known":true,"native_index":98,"offset":1153},"DRIVE_PULL_UP_THREE":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"DRIVE_PULL_UP_THREE","minimum":0,"name_known":true,"native_index":97,"offset":1152},"DRIVE_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"DRIVE_TENDENCY","minimum":0,"name_known":true,"native_index":100,"offset":1155},"DRIVING_DUNK_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"DRIVING_DUNK_TENDENCY","minimum":0,"name_known":true,"native_index":60,"offset":1115},"DRIVING_LAYUP_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"DRIVING_LAYUP_TENDENCY","minimum":0,"name_known":true,"native_index":58,"offset":1113},"EURO_STEP_LAYUP_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"EURO_STEP_LAYUP_TENDENCY","minimum":0,"name_known":true,"native_index":67,"offset":1122},"FLASHY_DUNK_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"FLASHY_DUNK_TENDENCY","minimum":0,"name_known":true,"native_index":61,"offset":1116},"FLASHY_PASS_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"FLASHY_PASS_TENDENCY","minimum":0,"name_known":true,"native_index":147,"offset":1202},"FLOATER_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"FLOATER_TENDENCY","minimum":0,"name_known":true,"native_index":68,"offset":1123},"FOUL_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"FOUL_TENDENCY","minimum":0,"name_known":true,"native_index":154,"offset":1209},"HARD_FOUL_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"HARD_FOUL_TENDENCY","minimum":0,"name_known":true,"native_index":155,"offset":1210},"HOP_STEP_LAYUP_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"HOP_STEP_LAYUP_TENDENCY","minimum":0,"name_known":true,"native_index":66,"offset":1121},"OFF_SCREEN_DRIVE_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"OFF_SCREEN_DRIVE_TENDENCY","minimum":0,"name_known":true,"native_index":102,"offset":1157},"OFF_SCREEN_SHOT_MID_RANGE":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"OFF_SCREEN_SHOT_MID_RANGE","minimum":0,"name_known":true,"native_index":77,"offset":1132},"OFF_SCREEN_SHOT_THREE":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"OFF_SCREEN_SHOT_THREE","minimum":0,"name_known":true,"native_index":85,"offset":1140},"ON_BALL_STEAL_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"ON_BALL_STEAL_TENDENCY","minimum":0,"name_known":true,"native_index":151,"offset":1206},"PASS_INTERCEPTION_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"PASS_INTERCEPTION_TENDENCY","minimum":0,"name_known":true,"native_index":149,"offset":1204},"PLAY_DISCIPLINE_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"PLAY_DISCIPLINE_TENDENCY","minimum":0,"name_known":true,"native_index":130,"offset":1185},"POST_UP_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"POST_UP_TENDENCY","minimum":0,"name_known":true,"native_index":123,"offset":1178},"PUTBACK_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"PUTBACK_TENDENCY","minimum":0,"name_known":true,"native_index":63,"offset":1118},"ROLL_VS_POP_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"ROLL_VS_POP_TENDENCY","minimum":0,"name_known":true,"native_index":124,"offset":1179},"SHOT_CLOSE_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"SHOT_CLOSE_TENDENCY","minimum":0,"name_known":true,"native_index":71,"offset":1126},"SHOT_MID_RANGE_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"SHOT_MID_RANGE_TENDENCY","minimum":0,"name_known":true,"native_index":75,"offset":1130},"SHOT_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"SHOT_TENDENCY","minimum":0,"name_known":true,"native_index":57,"offset":1112},"SHOT_THREE_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"SHOT_THREE_TENDENCY","minimum":0,"name_known":true,"native_index":83,"offset":1138},"SHOT_UNDER_BASKET_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"SHOT_UNDER_BASKET_TENDENCY","minimum":0,"name_known":true,"native_index":70,"offset":1125},"SPIN_JUMPER_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"SPIN_JUMPER_TENDENCY","minimum":0,"name_known":true,"native_index":95,"offset":1150},"SPIN_LAYUP_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"SPIN_LAYUP_TENDENCY","minimum":0,"name_known":true,"native_index":65,"offset":1120},"SPOT_UP_DRIVE_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"SPOT_UP_DRIVE_TENDENCY","minimum":0,"name_known":true,"native_index":101,"offset":1156},"SPOT_UP_SHOT_MID_RANGE":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"SPOT_UP_SHOT_MID_RANGE","minimum":0,"name_known":true,"native_index":76,"offset":1131},"SPOT_UP_SHOT_THREE":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"SPOT_UP_SHOT_THREE","minimum":0,"name_known":true,"native_index":84,"offset":1139},"STANDING_DUNK_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"STANDING_DUNK_TENDENCY","minimum":0,"name_known":true,"native_index":59,"offset":1114},"STEPBACK_JUMPER_MID_RANGE":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"STEPBACK_JUMPER_MID_RANGE","minimum":0,"name_known":true,"native_index":94,"offset":1149},"STEPBACK_JUMPER_THREE":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"STEPBACK_JUMPER_THREE","minimum":0,"name_known":true,"native_index":93,"offset":1148},"STEP_THROUGH_SHOT_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"STEP_THROUGH_SHOT_TENDENCY","minimum":0,"name_known":true,"native_index":69,"offset":1124},"TAKE_CHARGE_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"TAKE_CHARGE_TENDENCY","minimum":0,"name_known":true,"native_index":150,"offset":1205},"TOUCHES_TENDENCY":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"TOUCHES_TENDENCY","minimum":0,"name_known":true,"native_index":122,"offset":1177},"TRANSITION_PULL_UP_THREE":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"TRANSITION_PULL_UP_THREE","minimum":0,"name_known":true,"native_index":96,"offset":1151},"TRANSITION_SPOT_UP":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"TRANSITION_SPOT_UP","minimum":0,"name_known":true,"native_index":125,"offset":1180},"UNIDENTIFIED_TENDENCY_15":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_15","minimum":0,"name_known":false,"native_index":72,"offset":1127},"UNIDENTIFIED_TENDENCY_16":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_16","minimum":0,"name_known":false,"native_index":73,"offset":1128},"UNIDENTIFIED_TENDENCY_17":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_17","minimum":0,"name_known":false,"native_index":74,"offset":1129},"UNIDENTIFIED_TENDENCY_21":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_21","minimum":0,"name_known":false,"native_index":78,"offset":1133},"UNIDENTIFIED_TENDENCY_22":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_22","minimum":0,"name_known":false,"native_index":79,"offset":1134},"UNIDENTIFIED_TENDENCY_23":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_23","minimum":0,"name_known":false,"native_index":80,"offset":1135},"UNIDENTIFIED_TENDENCY_24":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_24","minimum":0,"name_known":false,"native_index":81,"offset":1136},"UNIDENTIFIED_TENDENCY_25":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_25","minimum":0,"name_known":false,"native_index":82,"offset":1137},"UNIDENTIFIED_TENDENCY_29":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_29","minimum":0,"name_known":false,"native_index":86,"offset":1141},"UNIDENTIFIED_TENDENCY_30":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_30","minimum":0,"name_known":false,"native_index":87,"offset":1142},"UNIDENTIFIED_TENDENCY_31":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_31","minimum":0,"name_known":false,"native_index":88,"offset":1143},"UNIDENTIFIED_TENDENCY_32":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_32","minimum":0,"name_known":false,"native_index":89,"offset":1144},"UNIDENTIFIED_TENDENCY_33":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_33","minimum":0,"name_known":false,"native_index":90,"offset":1145},"UNIDENTIFIED_TENDENCY_42":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_42","minimum":0,"name_known":false,"native_index":99,"offset":1154},"UNIDENTIFIED_TENDENCY_46":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_46","minimum":0,"name_known":false,"native_index":103,"offset":1158},"UNIDENTIFIED_TENDENCY_47":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_47","minimum":0,"name_known":false,"native_index":104,"offset":1159},"UNIDENTIFIED_TENDENCY_48":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_48","minimum":0,"name_known":false,"native_index":105,"offset":1160},"UNIDENTIFIED_TENDENCY_49":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_49","minimum":0,"name_known":false,"native_index":106,"offset":1161},"UNIDENTIFIED_TENDENCY_50":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_50","minimum":0,"name_known":false,"native_index":107,"offset":1162},"UNIDENTIFIED_TENDENCY_51":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_51","minimum":0,"name_known":false,"native_index":108,"offset":1163},"UNIDENTIFIED_TENDENCY_52":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_52","minimum":0,"name_known":false,"native_index":109,"offset":1164},"UNIDENTIFIED_TENDENCY_53":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_53","minimum":0,"name_known":false,"native_index":110,"offset":1165},"UNIDENTIFIED_TENDENCY_54":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_54","minimum":0,"name_known":false,"native_index":111,"offset":1166},"UNIDENTIFIED_TENDENCY_55":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_55","minimum":0,"name_known":false,"native_index":112,"offset":1167},"UNIDENTIFIED_TENDENCY_56":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_56","minimum":0,"name_known":false,"native_index":113,"offset":1168},"UNIDENTIFIED_TENDENCY_57":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_57","minimum":0,"name_known":false,"native_index":114,"offset":1169},"UNIDENTIFIED_TENDENCY_58":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_58","minimum":0,"name_known":false,"native_index":115,"offset":1170},"UNIDENTIFIED_TENDENCY_59":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_59","minimum":0,"name_known":false,"native_index":116,"offset":1171},"UNIDENTIFIED_TENDENCY_60":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_60","minimum":0,"name_known":false,"native_index":117,"offset":1172},"UNIDENTIFIED_TENDENCY_61":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_61","minimum":0,"name_known":false,"native_index":118,"offset":1173},"UNIDENTIFIED_TENDENCY_62":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_62","minimum":0,"name_known":false,"native_index":119,"offset":1174},"UNIDENTIFIED_TENDENCY_69":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_69","minimum":0,"name_known":false,"native_index":126,"offset":1181},"UNIDENTIFIED_TENDENCY_70":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_70","minimum":0,"name_known":false,"native_index":127,"offset":1182},"UNIDENTIFIED_TENDENCY_71":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_71","minimum":0,"name_known":false,"native_index":128,"offset":1183},"UNIDENTIFIED_TENDENCY_72":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_72","minimum":0,"name_known":false,"native_index":129,"offset":1184},"UNIDENTIFIED_TENDENCY_74":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_74","minimum":0,"name_known":false,"native_index":131,"offset":1186},"UNIDENTIFIED_TENDENCY_75":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_75","minimum":0,"name_known":false,"native_index":132,"offset":1187},"UNIDENTIFIED_TENDENCY_76":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_76","minimum":0,"name_known":false,"native_index":133,"offset":1188},"UNIDENTIFIED_TENDENCY_77":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_77","minimum":0,"name_known":false,"native_index":134,"offset":1189},"UNIDENTIFIED_TENDENCY_78":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_78","minimum":0,"name_known":false,"native_index":135,"offset":1190},"UNIDENTIFIED_TENDENCY_79":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_79","minimum":0,"name_known":false,"native_index":136,"offset":1191},"UNIDENTIFIED_TENDENCY_80":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_80","minimum":0,"name_known":false,"native_index":137,"offset":1192},"UNIDENTIFIED_TENDENCY_81":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_81","minimum":0,"name_known":false,"native_index":138,"offset":1193},"UNIDENTIFIED_TENDENCY_82":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_82","minimum":0,"name_known":false,"native_index":139,"offset":1194},"UNIDENTIFIED_TENDENCY_83":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_83","minimum":0,"name_known":false,"native_index":140,"offset":1195},"UNIDENTIFIED_TENDENCY_84":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_84","minimum":0,"name_known":false,"native_index":141,"offset":1196},"UNIDENTIFIED_TENDENCY_85":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_85","minimum":0,"name_known":false,"native_index":142,"offset":1197},"UNIDENTIFIED_TENDENCY_86":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_86","minimum":0,"name_known":false,"native_index":143,"offset":1198},"UNIDENTIFIED_TENDENCY_87":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_87","minimum":0,"name_known":false,"native_index":144,"offset":1199},"UNIDENTIFIED_TENDENCY_88":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_88","minimum":0,"name_known":false,"native_index":145,"offset":1200},"UNIDENTIFIED_TENDENCY_89":{"blocked_reason":null,"callable":true,"encoding":"NATIVE_UI_INTEGER_TENDENCY","expected_raw_formula":"value","maximum":100,"meaning":"UNKNOWN_SEMANTICS_NATIVE_TENDENCY_SLOT_89","minimum":0,"name_known":false,"native_index":146,"offset":1201}}},"precondition":"Generic recovered delegate stat callback; Potential excluded because it activates refresh99b670","required_slots":{"4680":18541376,"736":18713280},"root_rva":103972696},"lifecycle":["Deferred GUI-thread operation; current save/phase and role grant supplied by trusted host"],"object_requirements":["Exact supplied current roster PLAYER and TEAM; supported fresh delegate method footprint"],"parameters":[],"return_type":"LAYOUT","rva":null,"unknowns":[]}},limits={"is_live":true,"maximum_game_calls":100,"read_bytes":1048576},base=Process.mainModule.base;let readBytes=0,gameCalls=0,invoked=false;
const coachSettingSpecs={"BenchDepth":{"coach_offset":222,"enum":null,"gameplan_offset":391,"start_bit":0,"storage_bytes":1,"width":8},"BenchUtilization":{"coach_offset":312,"enum":null,"gameplan_offset":392,"start_bit":0,"storage_bytes":1,"width":8},"POEDefense":{"coach_offset":316,"enum":{"0":"NO_PREFERENCE","13":"PROTECT_PAINT","14":"NEUTRAL_DEFENSE_FOCUS","15":"LIMIT_PERIMETER_SHOTS"},"gameplan_offset":385,"start_bit":0,"storage_bytes":4,"width":5},"POEDefense2":{"coach_offset":316,"enum":{"0":"NO_PREFERENCE","16":"PLAY_CONSERVATIVE","17":"NEUTRAL_DEFENSE_TEMPO","18":"PLAY_PHYSICAL"},"gameplan_offset":386,"start_bit":5,"storage_bytes":4,"width":5},"POEDefense3":{"coach_offset":316,"enum":{"0":"NO_PREFERENCE","19":"CRASH_DEFENSIVE_BOARDS","20":"NEUTRAL_DEFENSE_REBOUND","21":"RUN_IN_TRANSITION"},"gameplan_offset":387,"start_bit":10,"storage_bytes":4,"width":5},"POEOffense":{"coach_offset":316,"enum":{"0":"NO_PREFERENCE","1":"GET_TO_BASKET","2":"GET_SHOOTERS_OPEN","3":"FEED_THE_POST","4":"PICK_AND_ROLL_OFFENSE","5":"NEUTRAL_OFFENSE_FOCUS","6":"RUN_OFFENSE_THROUGH_SCORER"},"gameplan_offset":382,"start_bit":15,"storage_bytes":4,"width":5},"POEOffense2":{"coach_offset":316,"enum":{"0":"NO_PREFERENCE","7":"PATIENT_OFFENSE","8":"NEUTRAL_OFFENSE_TEMPO","9":"SHOOT_AT_WILL"},"gameplan_offset":383,"start_bit":20,"storage_bytes":4,"width":5},"POEOffense3":{"coach_offset":316,"enum":{"0":"NO_PREFERENCE","10":"CRASH_OFFENSIVE_BOARDS","11":"NEUTRAL_OFFENSE_REBOUND","12":"LIMIT_TRANSITION"},"gameplan_offset":384,"start_bit":25,"storage_bytes":4,"width":5},"RunPlayTendency":{"coach_offset":224,"enum":null,"gameplan_offset":389,"start_bit":0,"storage_bytes":1,"width":8},"ZoneUsage":{"coach_offset":226,"enum":null,"gameplan_offset":390,"start_bit":0,"storage_bytes":1,"width":8}};
const playerContractFields=[{"bits":4,"group":"contract","name":"bird_years","offset":854,"start_bit":6},{"bits":3,"group":"contract","name":"original_contract_years","offset":833,"start_bit":4},{"bits":5,"group":"contract","meaning":"Stored base non-option years; excludes extension and optional years","name":"years_left_on_contract","native_source":"01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/player_contract_native_readback_021.json","offset":814,"start_bit":2},{"bits":2,"group":"contract","labels":{"0":"NULL","1":"TEAM_OPTION","2":"PLAYER_OPTION","3":"2_YEAR_TEAM_OPTION"},"name":"contract_option","offset":791,"start_bit":4},{"bits":1,"group":"contract","labels":{"0":"NO","1":"YES"},"name":"no_trade","offset":838,"start_bit":4},{"bits":3,"group":"contract","name":"extension_length","offset":833,"start_bit":7},{"bits":2,"group":"contract","labels":{"0":"NULL","1":"TEAM_OPTION","2":"PLAYER_OPTION","3":"2_YEAR_TEAM_OPTION"},"name":"extension_option","offset":834,"start_bit":2},{"bits":1,"group":"contract","labels":{"0":"NO","1":"YES"},"name":"extension_no_trade","offset":796,"start_bit":5},{"bits":31,"group":"contract","name":"contract_year_1","offset":420,"start_bit":0},{"bits":31,"group":"contract","name":"contract_year_2","offset":424,"start_bit":0},{"bits":31,"group":"contract","name":"contract_year_3","offset":428,"start_bit":0},{"bits":31,"group":"contract","name":"contract_year_4","offset":432,"start_bit":0},{"bits":31,"group":"contract","name":"contract_year_5","offset":436,"start_bit":0},{"bits":31,"group":"contract","name":"contract_year_6","offset":440,"start_bit":0},{"bits":3,"group":"contract","labels":{"0":"CORE","1":"HARDSHIP","2":"TWO_WAY","3":"EURO_STASH","4":"LINEUP"},"name":"contract_type","offset":836,"start_bit":3},{"bits":2,"group":"contract","name":"euro_stash_years_left","offset":659,"start_bit":5},{"bits":6,"group":"contract","name":"two_way_days_left","offset":351,"start_bit":2}];
if(Process.arch!=='x64'||Process.mainModule.name.toLowerCase()!=='nba2k22.exe')throw Error('PC22_X64_TARGET_REQUIRED');
let lastRange=null;function read(p,n){if(n<1||n>32768||readBytes+n>limits.read_bytes)throw Error('BOUNDED_READ_LIMIT');let at=p,left=n;while(left){if(!lastRange||at.compare(lastRange.base)<0||at.compare(lastRange.base.add(lastRange.size))>=0){lastRange=Process.findRangeByAddress(at);if(!lastRange||!lastRange.protection.includes('r'))throw Error('OBJECT_RANGE_UNREADABLE');}const size=Math.min(left,lastRange.base.add(lastRange.size).sub(at).toUInt32());if(size<1)throw Error('OBJECT_RANGE_END');at=at.add(size);left-=size;}readBytes+=n;return p.readByteArray(n);}
const u16=(b,o=0)=>new DataView(b).getUint16(o,true),u32=(b,o=0)=>new DataView(b).getUint32(o,true),ptrAt=(b,o=0)=>ptr('0x'+new DataView(b).getBigUint64(o,true).toString(16));
function text(b){let out='';for(let o=0;o+1<b.byteLength;o+=2){const c=u16(b,o);if(!c)break;out+=String.fromCharCode(c);}return out;}
function equal(a,b){const x=new Uint8Array(a),y=new Uint8Array(b);return x.length===y.length&&x.every((v,i)=>v===y[i]);}
function fnv(b){let h=2166136261;for(const v of new Uint8Array(b))h=Math.imul(h^v,16777619)>>>0;return h;}
for(const spec of Object.values(bindingSpecs))for(const sig of spec.input_layout.code_signatures||[])if(fnv(read(base.add(sig.rva),sig.bytes))!==sig.fnv32)throw Error('PINNED_NATIVE_CODE_CHANGED');
function getter(rva){const b=read(base.add(rva),8),v=new Uint8Array(b);if(v[0]!==0x48||v[1]!==0x8b)throw Error('ROOT_GETTER_CODE_CHANGED');return ptrAt(read(base.add(rva+7+new DataView(b).getInt32(3,true)),8));}
const roster=getter(18701792),rosterRoot=roster.sub(8),directory=read(rosterRoot.add(0x88),32),teamCount=Number(new DataView(directory).getBigUint64(0,true)),teamBase=ptrAt(directory,8);
if(teamCount<1||teamCount>1000)throw Error('TEAM_DIRECTORY_LIMIT');
function team(id){let found=null;for(let i=0;i<teamCount;i++){const p=teamBase.add(i*4696);if(u16(read(p.add(0xca8),2))===id){if(found)throw Error('DUPLICATE_TEAM_ID');found=p;}}if(!found)throw Error('TEAM_NOT_FOUND');return found;}
function rosterPlayer(t,uid){const b=read(t,4696);let found=null;for(let i=0;i<15;i++){const p=ptrAt(b,i*8);if(!p.isNull()&&u16(read(p.add(0xf4),2))===uid){if(found)throw Error('DUPLICATE_PLAYER_UID');found=p;}}if(!found)throw Error('PLAYER_NOT_ON_REQUESTED_TEAM');const b2=read(found,1264);if(!ptrAt(b2,0x60).equals(t)||!ptrAt(b2,0xa8).equals(t))throw Error('PLAYER_CURRENT_CONTRACT_TEAM_MISMATCH');return found;}
function franchiseRecord(teamId){const franchise=getter(6278620);let found=null;for(let i=0;i<36;i++){const record=franchise.add(0x19cfd0+i*0x13e70);if(u16(read(record,2))===teamId){if(found)throw Error('DUPLICATE_FRANCHISE_TEAM_RECORD');found={pointer:record,index:i};}}if(!found)throw Error('FRANCHISE_TEAM_RECORD_NOT_FOUND');return found;}
function currentDraftClass(){const at=base.add(0x1308f04+7+0x502256d),root=ptrAt(read(at,8)),klass=root.add(0x3f08),header=read(klass,16),n=new Uint8Array(header)[12];if(!u32(header)||n>150)throw Error('CURRENT_DRAFT_CLASS_NOT_READY');return {pointer:klass,count:n,pool:klass.add(16)};}
function currentProspect(uid){const d=currentDraftClass();let found=null;for(let i=0;i<d.count;i++){const p=d.pool.add(i*640),player=ptrAt(read(p,8));if(!player.isNull()&&u16(read(player.add(0xf4),2))===uid){if(found)throw Error('DUPLICATE_PROSPECT_UID');found={pointer:p,player,index:i};}}if(!found)throw Error('PROSPECT_NOT_IN_CURRENT_CLASS');return found;}
function call(bindingId,...args){const spec=bindingSpecs[bindingId];if(!spec||spec.rva===null)throw Error('UNKNOWN_NATIVE_BINDING');if(gameCalls>=limits.maximum_game_calls)throw Error('NATIVE_CALL_BUDGET');gameCalls++;send({kind:'native-call-stage',action_id:request.action_id,binding_id:bindingId,stage:'STARTED',call_number:gameCalls});const fn=new NativeFunction(base.add(spec.rva),spec.return_type,spec.parameters.map(p=>p.type),{abi:'win64',exceptions:'steal'});const result=fn(...args);send({kind:'native-call-stage',action_id:request.action_id,binding_id:bindingId,stage:'RETURNED',call_number:gameCalls,result:spec.return_type==='void'?null:spec.return_type==='pointer'?'POINTER_NOT_PUBLISHED':result});return result;}
function result(outcome,details={}){send({kind:'native-control-result',action_id:request.action_id,outcome,details,first_hand_game_calls:gameCalls,read_bytes:readBytes,automatic_retry:false,request_substitution:false,effect_verified_by_this_result:false,absolute_addresses_emitted:false});}


const CHUNK_PAYLOAD = {
  "chunk_id": "chunk-0002-team-28-player-patch-tendencies",
  "chunk_digest": "2dffe57a8984c3db0ad1b00abf64d96740b057b481e00d89c065f6a5ea473645",
  "plan_digest": "b954fab7813cd04f47e41d85b7e10fffc4729df0254e80d206ff6c7c95aff52f",
  "team_id": 28,
  "action_id": "PLAYER_PATCH_TENDENCIES",
  "batch_id": "BATCH-PILOT-STAGE1-NOOP-20261101",
  "save_instance_id": "MyLEAGUE0003",
  "game_build_sha256": "1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5",
  "player_items": [
    {
      "intent_id": "I-NOOP-POR-2459",
      "player_id": 2459,
      "field_id": "SHOT_TENDENCY",
      "expected_before": 80,
      "value": 80,
      "is_attribute": false,
      "native_index": 57,
      "offset": 1112
    },
    {
      "intent_id": "I-NOOP-POR-2763",
      "player_id": 2763,
      "field_id": "SHOT_TENDENCY",
      "expected_before": 88,
      "value": 88,
      "is_attribute": false,
      "native_index": 57,
      "offset": 1112
    },
    {
      "intent_id": "I-NOOP-POR-4456",
      "player_id": 4456,
      "field_id": "SHOT_TENDENCY",
      "expected_before": 78,
      "value": 78,
      "is_attribute": false,
      "native_index": 57,
      "offset": 1112
    },
    {
      "intent_id": "I-NOOP-POR-2850",
      "player_id": 2850,
      "field_id": "SHOT_TENDENCY",
      "expected_before": 55,
      "value": 55,
      "is_attribute": false,
      "native_index": 57,
      "offset": 1112
    },
    {
      "intent_id": "I-NOOP-POR-4111",
      "player_id": 4111,
      "field_id": "SHOT_TENDENCY",
      "expected_before": 62,
      "value": 62,
      "is_attribute": false,
      "native_index": 57,
      "offset": 1112
    },
    {
      "intent_id": "I-NOOP-POR-2757",
      "player_id": 2757,
      "field_id": "SHOT_TENDENCY",
      "expected_before": 55,
      "value": 55,
      "is_attribute": false,
      "native_index": 57,
      "offset": 1112
    }
  ],
  "coach_items": []
};
const u8 = (b, o = 0) => new DataView(b).getUint8(o);

function executeAction() {
  const results = [];
  let chunkHalted = false;
  let haltReason = null;

  // Resolve team
  let t = null;
  try {
    t = team(CHUNK_PAYLOAD.team_id);
  } catch (e) {
    send({
      kind: 'chunk-execution-result',
      chunk_id: CHUNK_PAYLOAD.chunk_id,
      chunk_digest: CHUNK_PAYLOAD.chunk_digest,
      plan_digest: CHUNK_PAYLOAD.plan_digest,
      action_id: CHUNK_PAYLOAD.action_id,
      batch_id: CHUNK_PAYLOAD.batch_id,
      save_instance_id: CHUNK_PAYLOAD.save_instance_id,
      outcome: 'EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY',
      error: 'TEAM_NOT_RESOLVED:' + String(e),
      receipts: []
    });
    return;
  }

  // 1. Player items execution
  if (CHUNK_PAYLOAD.player_items.length > 0) {
    const layout = bindingSpecs['player.stat_context'] ? bindingSpecs['player.stat_context'].input_layout : { root_rva: 0x5109b88, required_slots: {0: 0x978360, 8: 0x990a10} };
    const delegate = ptrAt(read(base.add(layout.root_rva), 8));
    if (delegate.isNull()) throw Error('PLAYER_STAT_DELEGATE_NOT_READY');
    const vtable = ptrAt(read(delegate, 8));
    if (!Object.entries(layout.required_slots).every(([slot, rva]) => ptrAt(read(vtable.add(Number(slot)), 8)).equals(base.add(rva)))) {
      throw Error('UNRECOVERED_PLAYER_STAT_DELEGATE');
    }

    const playerGroups = {};
    for (const item of CHUNK_PAYLOAD.player_items) {
      const pid = item.player_id;
      if (!playerGroups[pid]) playerGroups[pid] = [];
      playerGroups[pid].push(item);
    }

    for (const pidStr of Object.keys(playerGroups)) {
      if (chunkHalted) break;
      const pid = Number(pidStr);
      const items = playerGroups[pidStr];
      let player = null;
      try {
        player = rosterPlayer(t, pid);
      } catch (e) {
        chunkHalted = true;
        haltReason = 'PLAYER_ROSTER_NOT_RESOLVED_' + pid;
        for (const item of items) {
          results.push({
            intent_id: item.intent_id,
            team_id: CHUNK_PAYLOAD.team_id,
            player_id: item.player_id,
            field_id: item.field_id,
            expected_before: item.expected_before,
            requested: item.value,
            outcome: 'NOT_EXECUTED',
            reason: haltReason
          });
        }
        break;
      }

      let beforeBytes = new Uint8Array(read(player.add(0x41f), 156));
      let flagsBefore = u32(read(player.add(0x31c), 4));

      for (const item of items) {
        if (chunkHalted) {
          results.push({
            intent_id: item.intent_id,
            team_id: CHUNK_PAYLOAD.team_id,
            player_id: item.player_id,
            field_id: item.field_id,
            expected_before: item.expected_before,
            requested: item.value,
            outcome: 'NOT_EXECUTED',
            reason: 'CHUNK_HALTED_PREVIOUS_FAILURE'
          });
          continue;
        }

        const currentVal = call('player.get_stat_ui', player, item.native_index);

        if (currentVal !== item.expected_before) {
          results.push({
            intent_id: item.intent_id,
            team_id: CHUNK_PAYLOAD.team_id,
            player_id: item.player_id,
            field_id: item.field_id,
            expected_before: item.expected_before,
            getter_before: currentVal,
            requested: item.value,
            outcome: 'CAS_EXPECTED_BEFORE_MISMATCH',
            reason: 'Expected ' + item.expected_before + ', observed ' + currentVal
          });
          chunkHalted = true;
          haltReason = 'CAS_MISMATCH';
          continue;
        }

        if (currentVal === item.value) {
          results.push({
            intent_id: item.intent_id,
            team_id: CHUNK_PAYLOAD.team_id,
            player_id: item.player_id,
            field_id: item.field_id,
            expected_before: item.expected_before,
            getter_before: currentVal,
            requested: item.value,
            getter_after: currentVal,
            outcome: 'UNCHANGED_ALREADY_TARGET',
            unaltered_fields_check: true
          });
          continue;
        }

        try {
          call('player.set_stat_ui', player, item.native_index, item.value);
          const afterBytes = new Uint8Array(read(player.add(0x41f), 156));
          const flagsAfter = u32(read(player.add(0x31c), 4));
          const afterVal = call('player.get_stat_ui', player, item.native_index);
          const rawByte = u8(read(player.add(item.offset), 1));
          const expectedRaw = item.is_attribute ? (item.value * 3 - 75) : item.value;
          const targetOffsetIn156 = item.offset - 0x41f;

          let untouchedPreserved = true;
          for (let bIdx = 0; bIdx < 156; bIdx++) {
            if (bIdx === targetOffsetIn156) {
              if (afterBytes[bIdx] !== expectedRaw) untouchedPreserved = false;
            } else {
              if (afterBytes[bIdx] !== beforeBytes[bIdx]) untouchedPreserved = false;
            }
          }

          const expectedFlags = item.is_attribute ? ((flagsBefore & 0xffffffbf) >>> 0) : flagsBefore;
          const flagsMatch = (flagsAfter === expectedFlags);

          if (!untouchedPreserved) {
            throw Error('UNREQUESTED_STAT_BYTE_CHANGED');
          }
          if (!flagsMatch) {
            throw Error('PLAYER_STAT_CACHE_FLAG_MISMATCH');
          }
          if (afterVal !== item.value || rawByte !== expectedRaw) {
            throw Error('AFTER_GETTER_MISMATCH');
          }

          results.push({
            intent_id: item.intent_id,
            team_id: CHUNK_PAYLOAD.team_id,
            player_id: item.player_id,
            field_id: item.field_id,
            expected_before: item.expected_before,
            getter_before: currentVal,
            requested: item.value,
            getter_after: afterVal,
            raw_after: rawByte,
            outcome: 'SUCCESS_APPLIED',
            unaltered_fields_check: true
          });
          beforeBytes = afterBytes;
          flagsBefore = flagsAfter;
        } catch (err) {
          results.push({
            intent_id: item.intent_id,
            team_id: CHUNK_PAYLOAD.team_id,
            player_id: item.player_id,
            field_id: item.field_id,
            expected_before: item.expected_before,
            getter_before: currentVal,
            requested: item.value,
            outcome: 'UNKNOWN_EXECUTION_OUTCOME',
            reason: String(err)
          });
          chunkHalted = true;
          haltReason = 'SETTER_EXCEPTION:' + String(err);
        }
      }
    }
  }

  // 2. Coach items execution
  if (CHUNK_PAYLOAD.coach_items.length > 0 && !chunkHalted) {
    // Coach chunked mutation is explicitly unsupported for live execution
    if (CHUNK_PAYLOAD.action_id === 'COACH_SET_KNOWN_CURRENT_SETTINGS' && limits.is_live) {
      chunkHalted = true;
      haltReason = 'COACH_CONTRACT_UNSUPPORTED_FOR_LIVE';
      for (const item of CHUNK_PAYLOAD.coach_items) {
        results.push({
          intent_id: item.intent_id,
          team_id: CHUNK_PAYLOAD.team_id,
          field_id: item.field_id,
          expected_before: item.expected_before,
          requested: item.value,
          outcome: 'NOT_EXECUTED',
          reason: 'COACH_CONTRACT_UNSUPPORTED_FOR_LIVE'
        });
      }
    } else {
      try {
        const coach = ptrAt(read(t.add(0xce8), 8));
        const rawCoach = read(coach, 352);
        const m = franchiseRecord(CHUNK_PAYLOAD.team_id).pointer;
        const gp = m.add(0x7854);
        const originalGp = read(gp, 880);

        for (const item of CHUNK_PAYLOAD.coach_items) {
          if (chunkHalted) {
            results.push({
              intent_id: item.intent_id,
              team_id: CHUNK_PAYLOAD.team_id,
              field_id: item.field_id,
              expected_before: item.expected_before,
              requested: item.value,
              outcome: 'NOT_EXECUTED',
              reason: 'CHUNK_HALTED_PREVIOUS_FAILURE'
            });
            continue;
          }

          const currentVal = u8(read(gp.add(item.gameplan_offset), 1));
          if (currentVal !== item.expected_before) {
            results.push({
              intent_id: item.intent_id,
              team_id: CHUNK_PAYLOAD.team_id,
              field_id: item.field_id,
              expected_before: item.expected_before,
              getter_before: currentVal,
              requested: item.value,
              outcome: 'CAS_EXPECTED_BEFORE_MISMATCH',
              reason: 'Expected ' + item.expected_before + ', observed ' + currentVal
            });
            chunkHalted = true;
            haltReason = 'CAS_MISMATCH';
            continue;
          }

          if (currentVal === item.value) {
            results.push({
              intent_id: item.intent_id,
              team_id: CHUNK_PAYLOAD.team_id,
              field_id: item.field_id,
              expected_before: item.expected_before,
              getter_before: currentVal,
              requested: item.value,
              getter_after: currentVal,
              outcome: 'UNCHANGED_ALREADY_TARGET',
              unaltered_fields_check: true
            });
            continue;
          }

          // Apply coach projection
          const inputBuf = Memory.alloc(880);
          inputBuf.writeByteArray(read(gp, 880));
          inputBuf.add(item.gameplan_offset).writeU8(item.value);
          call('coach.apply_gameplan', inputBuf, coach);
          const afterVal = u8(read(gp.add(item.gameplan_offset), 1));

          results.push({
            intent_id: item.intent_id,
            team_id: CHUNK_PAYLOAD.team_id,
            field_id: item.field_id,
            expected_before: item.expected_before,
            getter_before: currentVal,
            requested: item.value,
            getter_after: afterVal,
            outcome: 'SUCCESS_APPLIED',
            unaltered_fields_check: true
          });
        }
      } catch (err) {
        chunkHalted = true;
        haltReason = 'COACH_SETTING_EXCEPTION:' + String(err);
      }
    }
  }

  send({
    kind: 'chunk-execution-result',
    chunk_id: CHUNK_PAYLOAD.chunk_id,
    chunk_digest: CHUNK_PAYLOAD.chunk_digest,
    plan_digest: CHUNK_PAYLOAD.plan_digest,
    action_id: CHUNK_PAYLOAD.action_id,
    batch_id: CHUNK_PAYLOAD.batch_id,
    save_instance_id: CHUNK_PAYLOAD.save_instance_id,
    outcome: chunkHalted ? 'CHUNK_HALTED' : 'CHUNK_SUCCESS',
    halt_reason: haltReason,
    receipts: results
  });
}

// Deferred runtime: resolve the game's own visible-window thread, invoke once.
const user=Process.getModuleByName('user32.dll'),cell=Memory.alloc(4),title=Memory.alloc(256);let selected=null,hook=null;
const threadOf=new NativeFunction(user.getExportByName('GetWindowThreadProcessId'),'uint',['pointer','pointer'],'win64'),visible=new NativeFunction(user.getExportByName('IsWindowVisible'),'int',['pointer'],'win64'),titleOf=new NativeFunction(user.getExportByName('GetWindowTextW'),'int',['pointer','pointer','int'],'win64');
const enumerate=new NativeCallback((h,l)=>{const tid=threadOf(h,cell);if(cell.readU32()===Process.id&&visible(h)){const n=titleOf(h,title,128);if(n&&/NBA/i.test(title.readUtf16String(n)))selected={handle:h,thread:tid};}return 1;},'int',['pointer','pointer'],'win64');new NativeFunction(user.getExportByName('EnumWindows'),'int',['pointer','pointer'],'win64')(enumerate,ptr(0));
if(!selected){result('EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY',{reason:'GAME_WINDOW_THREAD_NOT_FOUND'});}else{hook=Interceptor.attach(user.getExportByName('PeekMessageA'),{onLeave(){if(invoked||Process.getCurrentThreadId()!==selected.thread)return;invoked=true;try{executeAction();}catch(e){result('EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY',{reason:String(e).replace(/0x[0-9a-f]+/gi,'[address]')});}finally{hook.detach();}}});new NativeFunction(user.getExportByName('PostMessageW'),'int',['pointer','uint','pointer','pointer'],'win64')(selected.handle,0,ptr(0),ptr(0));setTimeout(()=>{if(!invoked){hook.detach();result('EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY',{reason:'GAME_THREAD_NOT_ENTERED'});}},4000);}
