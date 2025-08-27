
URL="https://www.amfiindia.com/spages/NAVAll.txt"
OUTPUT_FILE="amfi_data.tsv"
TEMP_FILE="nav_temp.txt"
DEBUG_FILE="debug_log.txt"

check_dependencies() {
    command -v curl >/dev/null 2>&1 || { echo "Error: curl is required but not installed."; exit 1; }
    command -v awk >/dev/null 2>&1 || { echo "Error: awk is required but not installed."; exit 1; }
}

cleanup() {
    [ -f "$TEMP_FILE" ] && rm -f "$TEMP_FILE"
    [ -f "$DEBUG_FILE" ] && rm -f "$DEBUG_FILE"
}

trap cleanup EXIT

check_dependencies

echo "Downloading data from $URL..."
if ! curl -s -f "$URL" -o "$TEMP_FILE"; then
    echo "Error: Failed to download file from $URL"
    exit 1
fi

if [ ! -s "$TEMP_FILE" ]; then
    echo "Error: Downloaded file is empty"
    exit 1
fi

head -n 10 "$TEMP_FILE" > "$DEBUG_FILE"
echo "First 10 lines of downloaded file saved to $DEBUG_FILE for inspection"

echo -e "Scheme Name\tAsset Value" > "$OUTPUT_FILE"

awk -F';' '
BEGIN { OFS="\t"; valid_records=0 }
NF >= 5 && $4 != "" && $5 != "" && $4 !~ /Scheme Name/ {
    # Trim whitespace and escape tabs in Scheme Name
    gsub(/^[ \t]+|[ \t]+$/, "", $4)
    gsub(/\t/, " ", $4)
    # Validate Asset Value is numeric (integer or decimal)
    if ($5 ~ /^[0-9]+(\.[0-9]*)?$/) {
        print $4, $5
        valid_records++
    }
}
END { print "Processed", NR, "lines, found", valid_records, "valid records" > "/dev/stderr" }
' "$TEMP_FILE" >> "$OUTPUT_FILE"

if [ $(wc -l < "$OUTPUT_FILE") -le 1 ]; then
    echo "Error: No valid data extracted. Check $DEBUG_FILE for file structure."
    echo "Possible issues: Field positions changed or no valid numeric NAV values."
    exit 1
fi

echo "Data extracted successfully to $OUTPUT_FILE"