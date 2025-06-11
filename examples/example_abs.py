from tsdgenerator import generate_types

package_name = "resolve-dir"
# Generates dts files for npm package "abs" under "./output/declarations/abs"
generate_types(package_name, extract=True, generate=False, fix=True, work_path="output")