import argparse
import re
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process QTC file and format output.")
    parser.add_argument("-f", required=True, help="Input file to read from")
    parser.add_argument("-o", required=True, help="Output file to append to")
    parser.add_argument("-r", required=True, help="Receiver callsign")
    parser.add_argument("-s", required=True, help="Sender callsign")
    return parser.parse_args()

def read_and_validate_input(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]  # Remove empty lines
    
    qtc_line = next((line for line in lines if "QTC" in line), None)
    if not qtc_line:
        raise ValueError("QTC line not found in file.")

    match = re.search(r"QTC (\d+)/(\d+)", qtc_line)
    if not match:
        raise ValueError("Invalid QTC format in file.")

    current_qtc, total_qtc = int(match.group(1)), int(match.group(2))
    qtc_start_index = lines.index(qtc_line) + 1
    qtc_lines = lines[qtc_start_index:]

    if len(qtc_lines) != total_qtc:
        raise ValueError(f"Expected {total_qtc} QTC lines, but found {len(qtc_lines)}.")
    
    freq_match = re.search(r"RX (\d+)", qtc_line)
    if not freq_match:
        raise ValueError("Frequency information missing in QTC line.")

    frequency = f"{int(freq_match.group(1)) / 1000:.3f}"
    return qtc_line, qtc_lines, frequency, current_qtc, total_qtc

def format_output(qtc_line, qtc_lines, sender, receiver, frequency, current_qtc, total_qtc, output_file):
    date_time_match = re.search(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})Z", qtc_line)
    if not date_time_match:
        raise ValueError("Date and time format in QTC line is invalid.")
    
    date, time = date_time_match.groups()
    mode = "RY"
    time_formatted = time.replace(":", "")
    
    with open(output_file, 'a') as out_file:
        for qtc in qtc_lines:
            # Adjusted regex to capture lines like "0152-W6ZD-27"
            qtc_info_match = re.findall(r"(\d{4}-[A-Za-z0-9]+-\d+)", qtc)
            if not qtc_info_match:
                continue
            qtc_info = qtc_info_match[1]
            formatted_line = f"QTC: {frequency} {mode} {date} {time_formatted} {sender:10} {current_qtc:03}/{total_qtc} {receiver:10} {qtc_info}"
            print(f"{formatted_line}")
            out_file.write(formatted_line + "\n")

def main():
    args = parse_arguments()
    try:
        qtc_line, qtc_lines, frequency, current_qtc, total_qtc = read_and_validate_input(args.f)
        format_output(qtc_line, qtc_lines, args.r, args.s, frequency, current_qtc, total_qtc, args.o)
        print("Output successfully written.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

