import re
import pytesseract
import PIL.Image
my_config = r"-l fra --psm 11 --oem 3"
tesseract_output = pytesseract.image_to_string(PIL.Image.open("passport.jpeg"),config=my_config)

# Read Tesseract output from a file

# Split the output into lines and get the last three lines (to handle empty lines in between)
last_two_lines = tesseract_output.strip().split("\n")[-3:]

# Filter out any empty lines
last_two_lines = [line for line in last_two_lines if line.strip()]

# Check if we now have exactly two lines
if len(last_two_lines) != 2:
    print("Error: MRZ data is incomplete or improperly formatted. Expected 2 lines.")
    print(f"Extracted lines: {last_two_lines}")
    exit(1)  # Exit the program if the MRZ is not properly extracted

# Combine the two lines into a single MRZ string
mrz = "\n".join(last_two_lines)

def parse_mrz(mrz):
    # Split MRZ lines
    lines = mrz.splitlines()

    # Ensure that we have exactly two lines in the MRZ
    if len(lines) != 2:
        print("Error: MRZ should have exactly 2 lines.")
        print(f"Extracted MRZ: {lines}")
        return None

    # Parse the first line
    document_type = lines[0][0]  # 'P' for passport
    issuing_country = lines[0][2:5]  # Issuing country code (e.g., 'MAR')

    # Parse surname and given names
    name = lines[0][5:].replace('<', ' ').strip()

    # Handle cases where '<<' delimiter is missing
    if '<<' in name:
        surname, given_names = name.split('<<', 1)
    else:
        surname = name  # Assign entire name to surname if '<<' is missing
        given_names = ''  # Leave given names empty if missing

    surname = surname.replace('<', ' ').strip()
    given_names = given_names.replace('<', ' ').strip()

    # Parse the second line with corrected slicing
    passport_number = lines[1][0:9]
    passport_check_digit = lines[1][9]
    nationality = lines[1][10:13]
    birth_date = lines[1][13:19]
    birth_date_check_digit = lines[1][19]
    gender = lines[1][20]
    expiration_date = lines[1][21:27]
    expiration_date_check_digit = lines[1][27]
    personal_number = lines[1][28:35]
    personal_number_check_digit = lines[1][35]

    # Collect parsed data in a dictionary
    parsed_data = {
        'Document Type': document_type,
        'Issuing Country': issuing_country,
        'Surname': surname,
        'Passport Number': passport_number,
        'Nationality': nationality,
        'Birth Date': f"{birth_date[:2]}-{birth_date[2:4]}-{birth_date[4:6]}",
        'Gender': gender,
        'Expiration Date': f"{expiration_date[:2]}-{expiration_date[2:4]}-{expiration_date[4:6]}",
        'Expiration Date Check Digit': expiration_date_check_digit,
        'Personal Number': personal_number,
    }

    return parsed_data

# Example MRZ input

parsed_mrz = parse_mrz(mrz)
if parsed_mrz:
    for key, value in parsed_mrz.items():
        print(f"{key}: {value}")
