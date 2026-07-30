from __future__ import annotations

import codecs
import json


sample = {"location": "$.含中文"}
false_output = json.dumps(sample, ensure_ascii=False)
none_output = json.dumps(sample, ensure_ascii=None)

proof = {
    "ensure_ascii": {
        "false_is_falsey": bool(False) is False,
        "none_is_falsey": bool(None) is False,
        "representative_outputs_equal": false_output == none_output,
        "output": false_output,
    },
    "encoding": {
        "lowercase_codec": codecs.lookup("utf-8").name,
        "uppercase_codec": codecs.lookup("UTF-8").name,
        "same_codec": codecs.lookup("utf-8") == codecs.lookup("UTF-8"),
    },
    "classification": "equivalent_for_the_exercised_stdlib_semantics",
}

assert proof["ensure_ascii"]["representative_outputs_equal"]
assert proof["encoding"]["same_codec"]
print(json.dumps(proof, ensure_ascii=False, indent=2))
