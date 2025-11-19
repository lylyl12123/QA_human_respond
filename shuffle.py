import json
import random

input_file = "data_human_respond.json"
output_file = "data_human_respond_shuffled.json"


random.seed(42)

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

random.shuffle(data)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done! Shuffled data saved to: {output_file}")
