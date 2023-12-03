import json
import aiohttp
import os, datetime, re


class Utils:
    @staticmethod
    async def open_file(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ValueError(f"Error {response.status}: {response.reason}")
                return await response.json()  # Parse JSON and return the content

    @staticmethod
    def read_file(file_path):
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

    @staticmethod
    def save_file(file_name, content, folder_name="data", extension="json"):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{file_name}_{current_time}.{extension}"
        file_path = os.path.join(folder_name, file_name)
        with open(file_path, "w") as file:
            file.write(content)

        return file_path

    @staticmethod
    def transform_to_json(text):
        # Load the string as JSON
        data = json.loads(text)

        # Parse the internal stringified JSON objects
        for obj in data:
            for key, value in obj.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, str):
                            try:
                                # Replace escaped double quotes and load as JSON
                                value[subkey] = json.loads(subvalue.replace('\\"', '"'))
                            except json.JSONDecodeError:
                                pass  # Handle the case where the string is not a valid JSON

        return data
