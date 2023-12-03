from core import CSBehaviorAnalyzer, Utils
import os
import json

BASE_URL = f"http://localhost:{os.getenv('PORT')}"


async def resolve_generate_css_behavior(_, info, css_file_paths):
    cssBehavior = []
    for cs_file in css_file_paths:
        analyzer = CSBehaviorAnalyzer()
        analyzer.analyze_cs(cs_file)
        cssBehavior.append(analyzer.cs)

    validCsCombinationList = []
    for cs in cssBehavior:
        for cs_other in cssBehavior:
            if cs != cs_other:
                for key, value in cs.items():
                    for key_o, value_o in cs_other.items():
                        for outputs in json.loads(value["messages"])["outputs"]:
                            for inputs in json.loads(value_o["messages"])["inputs"]:
                                if outputs["output"] == inputs["message"]:
                                    validCsCombinationList.append(
                                        {
                                            "from": key,
                                            "message": inputs["message"],
                                            "to": key_o,
                                        }
                                    )

    css_behavior_file_json = Utils.save_file(
        "css_behavior",
        json.dumps(Utils.transform_to_json(json.dumps(cssBehavior)), indent=2),
    )
    valid_css_combinations_file_json = Utils.save_file(
        "valid_css_combinations",
        json.dumps(
            Utils.transform_to_json(json.dumps(validCsCombinationList)), indent=2
        ),
    )

    information = f"Two files were generated. Type css_behavior_file_json and/or valid_css_combinations_file_json to see more details."

    return {
        "css_behavior_file_json": f"{BASE_URL}/{css_behavior_file_json}",
        "valid_css_combinations_file_json": f"{BASE_URL}/{valid_css_combinations_file_json}",
        "information": f"{information}",
    }
