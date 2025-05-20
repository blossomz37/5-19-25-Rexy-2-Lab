# Rexy 2 CSV Converter

A utility for generating prompt and stage files for the Rexy 2 system from CSV data.

## Overview

This tool reads a CSV file with defined columns and generates two types of output files:
1. `.txt` files containing prompts
2. `.json` files containing stage configuration data

The generated files follow a specific naming convention based on the input CSV and include placeholders for chapter numbers and references to other files.

## CSV Format

The input CSV should contain the following columns:
- `file_ID`: Unique identifier for the file
- `chapter_number`: Optional chapter number 
- `name`: Template for the file name (can include `{chapter}` placeholder)
- `prompt`: The text content for the prompt file
- `ai_model`: The AI model to use for processing
- `output`: Output filename template
- `output_mode`: Processing mode (e.g., "write", "append")
- `quantity`: Number of files to generate in a sequence
- `increment`: Increment to add to file_ID for each file in a sequence

## Development Setup

This project uses a Python virtual environment. To set up:

1. Create a virtual environment: `python3 -m venv myenv`
2. Activate it: `source myenv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`

VS Code users: A `.vscode/settings.json` file is included that configures the correct Python interpreter. If running the script via the VS Code "Run" button, this will ensure the correct environment is used.

## Usage

1. Activate your virtual environment:
   ```
   source myenv/bin/activate
   ```

2. Run the script:
   ```
   python main/CSV\ to\ Rexy\ 2.py
   ```

3. When prompted, select your input CSV file using the file dialog.

4. The script will process the CSV and generate:
   - A timestamped output directory
   - Prompt files (.txt) in the `prompts` subdirectory
   - Stage files (.json) in the `stages` subdirectory

## Output Structure

For each row in the CSV, the script generates:
- A text file with the prompt content
- A JSON file with stage configuration data

Example output directory structure:
```
output_YYYY-MM-DD_HH-MM-SS/
├── prompts/
│   ├── 1010-Story Ideas.txt
│   ├── 1020-Story Concept.txt
│   └── ...
└── stages/
    ├── 1010-Story Ideas.json
    ├── 1020-Story Concept.json
    └── ...
```

## Logging

The script logs all operations to `generation_log.txt` in the root directory.

## File ID System

The script uses a file ID system to organize related files:
- Plan files: Base ID
- Draft files: Base ID + 10
- Edit files: Base ID + 20
- Final files: Base ID + 30

## Requirements

- Python 3.10+
- pandas
- tkinter (included with most Python installations)