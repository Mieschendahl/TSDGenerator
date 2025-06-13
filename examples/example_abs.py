from tsdgenerator import generate_types

# Generates dts files for npm package "abs" under "./output/declarations/abs"
generate_types("abs", model_name="gpt-4o-mini", work_path="output")