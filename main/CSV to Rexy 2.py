# -----------------------------------------------
# CSV to Rexy 2 Prompt/Stage File Generator
#
# This script reads a CSV file and generates text
# and JSON files for each row, using a GUI interface.
#
# REQUIREMENTS:
# - Only one external library is required: pandas
# - Install with: pip install pandas
# - Or use: pip install -r requirements.txt
#
# Users can modify the CSV file and rerun the script
# to generate updated prompts and stages.
# -----------------------------------------------
import pandas as pd
import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
from datetime import datetime
import sys
# Configure logging to write to a file
logging.basicConfig(
    filename="generation_log.txt",
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
# Redirect standard error to the log file
sys.stderr = open("generation_log.txt", "a")
def select_csv():
    try:
        # Display file dialog to select CSV file
        csv_path = filedialog.askopenfilename(title="Select the source CSV file", filetypes=[("CSV Files", "*.csv")])
        # Exit if no file was selected
        if not csv_path:
            logging.error("No CSV file selected. Exiting.")
            messagebox.showerror("Error", "No CSV file selected. Exiting.")
            return
        # Close the GUI window after file selection
        root.destroy()
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_path)
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_root = os.path.join(os.path.dirname(csv_path), f"output_{timestamp}")
        # Create subdirectories for prompts and stages
        prompt_dir = os.path.join(output_root, "prompts")
        stages_dir = os.path.join(output_root, "stages")
        os.makedirs(prompt_dir, exist_ok=True)
        os.makedirs(stages_dir, exist_ok=True)
        # Process each row in the CSV file
        for index, row in df.iterrows():
            # Extract values from the current row
            csv_file_id = int(row['file_ID'])
            csv_quantity = int(row['quantity'])
            csv_increment = int(row['increment'])
            csv_name_template = row['name']
            
            # Determine the actual Plan ID for Chapter 1 of this sequence
            # This is used as the baseline for calculating all related file IDs (Draft, Edit, Final)
            offset_to_plan_id = 0
            if "Final" in csv_name_template:
                offset_to_plan_id = -30
            elif "Edit" in csv_name_template:
                offset_to_plan_id = -20
            elif "Draft" in csv_name_template:
                offset_to_plan_id = -10
            # If "Plan" or no keyword, offset is 0, meaning csv_file_id is assumed to be Plan ID for Ch1.
            
            master_plan_id_ch1 = csv_file_id + offset_to_plan_id

            # Initialize chapter counter for the second loop (used for placeholder replacement)
            chapter = 1 
            # Create dictionaries to store all filenames by chapter number
            # This allows us to reference files across different chapters
            all_plan_filenames = {}
            all_draft_filenames = {}
            all_edit_filenames = {}
            all_final_filenames = {}
            # First pass: Generate all filenames and store them in dictionaries
            for i in range(csv_quantity): # i is 0-indexed
                curr_chapter = i + 1 # 1-indexed chapter number for this sequence
                
                # Calculate IDs for different file types based on the master_plan_id_ch1
                # and the universal increment for this sequence.
                actual_plan_id = master_plan_id_ch1 + (i * csv_increment)
                actual_draft_id = actual_plan_id + 10
                actual_edit_id = actual_plan_id + 20
                actual_final_id = actual_plan_id + 30
                
                # Store the filenames by chapter number
                all_plan_filenames[curr_chapter] = f"{actual_plan_id}-Chapter {curr_chapter} Plan"
                all_draft_filenames[curr_chapter] = f"{actual_draft_id}-Chapter {curr_chapter} Draft"
                all_edit_filenames[curr_chapter] = f"{actual_edit_id}-Chapter {curr_chapter} Edit"
                all_final_filenames[curr_chapter] = f"{actual_final_id}-Chapter {curr_chapter} Final"
            # Second pass: Generate the actual files with correct references
            for i in range(csv_quantity):
                # Get prompt text from the CSV
                prompt_text = row['prompt']
                # Replace placeholders in the prompt text
                prompt_text = prompt_text.replace("{chapter}", str(chapter))
                # Replace chapter file references with the correct filenames
                # This ensures cross-references between files are correct
                prompt_text = prompt_text.replace("{current_chapter_plan}", all_plan_filenames[chapter])
                prompt_text = prompt_text.replace("{current_chapter_draft}", all_draft_filenames[chapter])
                prompt_text = prompt_text.replace("{current_chapter_edit}", all_edit_filenames[chapter])
                prompt_text = prompt_text.replace("{current_chapter_final}", all_final_filenames[chapter])
                # Add references to previous chapter files if they exist
                if chapter > 1:
                    prompt_text = prompt_text.replace("{previous_chapter_plan}", all_plan_filenames[chapter-1])
                    prompt_text = prompt_text.replace("{previous_chapter_draft}", all_draft_filenames[chapter-1])
                    prompt_text = prompt_text.replace("{previous_chapter_edit}", all_edit_filenames[chapter-1])
                    prompt_text = prompt_text.replace("{previous_chapter_final}", all_final_filenames[chapter-1])
                # Extract other needed values from CSV row
                ai_model = row['ai_model']
                output_mode = row['output_mode']
                csv_output_filename_template = row['output'] # Read the output filename template from CSV

                # Create filenames for the current chapter files
                name_with_chapter = csv_name_template.replace("{chapter}", str(chapter)) # Use csv_name_template
                safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name_with_chapter).strip()
                # Use the csv_file_id for the base ID of the output file being generated.
                # This ID corresponds to the type of file defined by csv_name_template for chapter 1
                # and steps by csv_increment for subsequent chapters.
                current_id = csv_file_id + (i * csv_increment) # Use csv_file_id and csv_increment
                filename_base = f"{current_id}-{safe_name}"
                
                # Resolve the output filename using the template from CSV and current chapter
                actual_output_filename = csv_output_filename_template.replace("{chapter}", str(chapter))

                # Write prompt text to file
                prompt_filename = os.path.join(prompt_dir, f"{filename_base}.txt")
                with open(prompt_filename, "w", encoding="utf-8") as f:
                    f.write(prompt_text)
                # Create and write stage JSON data
                stage_data = {
                    "title": name_with_chapter,
                    "description": f"Create {name_with_chapter}",
                    "prompts": [filename_base],
                    "output": actual_output_filename, # Use the resolved filename from CSV
                    "output_mode": output_mode,
                    "ai_profile": ai_model
                }
                json_filename = os.path.join(stages_dir, f"{filename_base}.json")
                with open(json_filename, "w", encoding="utf-8") as f:
                    json.dump(stage_data, f, indent=4)
                # Increment chapter counter for next iteration
                chapter += 1
        # Log success and show completion message
        logging.info("All files have been generated successfully.")
        messagebox.showinfo("Done", "All files have been generated successfully.")
    except Exception as e:
        # Log and display any errors that occur
        logging.exception("An unexpected error occurred.")
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
# Create the main GUI window
root = tk.Tk()
root.title("CSV Converter")
root.geometry("400x200")
root.configure(bg="#2c2c2e")
root.attributes("-topmost", True)
# Add a label to the window
label = tk.Label(root, text="Convert CSV file for Rexy 2", bg="#2c2c2e", fg="white", font=("Helvetica", 14))
label.pack(pady=30)
# Add a button to trigger file selection
button = tk.Button(root, text="Select CSV File", command=select_csv, font=("Helvetica", 12), padx=10, pady=5)
button.pack()
# Start the GUI event loop
root.mainloop()