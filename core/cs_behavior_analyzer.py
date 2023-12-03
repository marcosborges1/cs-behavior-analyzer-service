import re
import json
import os
from core.utils import Utils


class CSBehaviorAnalyzer:
    def __init__(self):
        self.cs = {}
        self.results = {}

    def read_file(self, file_path):
        """
        Reads all content from the specified file and returns it.
        """
        try:
            with open(file_path, "r") as file:
                return file.read()
        except FileNotFoundError:
            return "File not found."
        except Exception as e:
            return f"An error occurred: {e}"

    def analyze_cs(self, cs_file):
        cs = {}
        cs_name = self.extract_cs_name(cs_file)
        content = self.read_file(cs_file)
        cs["variables"] = self.extract_variables_and_properties(content)
        cs["input_output"] = self.extract_input_output(content)
        cs["messages"] = self.extract_messages(content)
        self.cs[cs_name] = cs

    def extract_cs_name(self, cs_file):
        basename = os.path.basename(cs_file)
        name, _ = os.path.splitext(basename)  # Splits the filename from the extension
        return name

    def extract_variables_and_properties(self, text):
        data = {}
        type_properties = {}

        lines = text.split("!")
        for line in lines:
            line = line.strip()

            # Match 'use [variable] with type [type]'
            use_match = re.match(r"use (\w+) with type (\w+)", line)
            if use_match:
                var, var_type = use_match.groups()
                data[var] = {"type": var_type, "properties": {}}

                # If properties for the type exist, add them to the variable
                if var_type in type_properties:
                    data[var]["properties"] = type_properties[var_type]
                continue

            # Match 'A [Type] has a [Property]'
            type_prop_match = re.match(r"A (\w+) has a (\w+)", line)
            if type_prop_match:
                type, prop = type_prop_match.groups()
                if type not in type_properties:
                    type_properties[type] = {}
                type_properties[type][prop] = None
                continue

            # Match 'the range of [Type]'s [Property] is [Type]'
            range_match = re.match(r"the range of (\w+)'s (\w+) is (\w+)", line)
            if range_match:
                type, prop, prop_type = range_match.groups()
                if type in type_properties and prop in type_properties[type]:
                    type_properties[type][prop] = prop_type

                    # Update already added variables of this type
                    for var in data:
                        if data[var]["type"] == type:
                            data[var]["properties"][prop] = prop_type

        return json.dumps(data, indent=2)

    def extract_info(self, text):
        pattern = r"\s*the range of (.+)'s (.+) is (.+)"
        match = re.match(pattern, text)
        if match:
            return match.groups()
        else:
            return None, None, None

    def extract_input_output(self, text):
        data = {"input": {}, "output": {}}

        lines = text.split("!")
        for line in lines:
            line = line.strip()

            # Match output details
            if "generates output" in line:
                parts = line.split(" with type ")
                if len(parts) == 2:
                    output_component, output_type = parts[0].split()[-1], parts[1]
                    data["output"][output_component] = {
                        "type": output_type,
                        "properties": {},
                    }

            # Match input details
            elif "accepts input" in line:
                parts = line.split(" with type ")
                if len(parts) == 2:
                    input_component, input_type = parts[1], parts[0].split()[-1]
                    data["input"][input_type] = {
                        "type": input_component,
                        "properties": {},
                    }

            # Match properties of the input type
            elif "the range of" in line:
                component, prop, type = self.extract_info(line)
                for key, value in data["input"].items():
                    if value["type"] == component:
                        value["properties"][prop] = type
                for key, value in data["output"].items():
                    if value["type"] == component:
                        value["properties"][prop] = type

        return json.dumps(data, indent=2)

    def extract_messages(self, text):
        data = {"transitions": [], "inputs": [], "outputs": []}

        lines = text.split("!")
        for line in lines:
            line = line.strip()

            # Match transitions
            transition_match = re.match(r"from (\w+) go to (\w+)", line)
            if transition_match:
                from_state, to_state = transition_match.groups()
                data["transitions"].append({"from": from_state, "to": to_state})

            # Match actions
            action_match = re.match(r"after (\w+) output (\w+)", line)
            if action_match:
                state, output = action_match.groups()
                data["outputs"].append({"state": state, "output": output})

            # Match conditional transitions
            conditional_transition_match = re.match(
                r"when in (\w+) and receive (\w+) go to (\w+)", line
            )
            if conditional_transition_match:
                from_state, event, to_state = conditional_transition_match.groups()
                data["inputs"].append(
                    {
                        "from": from_state,
                        "message": event,
                        "to": to_state,
                    }
                )

        return json.dumps(data, indent=2)

    def save_file(self, file_name="css_behavior_file_json"):
        return Utils.save_file(file_name, json.dumps(self.content_json, indent=4))
