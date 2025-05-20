# -----------------# Import the standard tkinter GUI toolkit and alias it as 'tk' for creating windows and widgets
import tkinter as tk
# Import the filedialog submodule to prompt the user to open/save files,
# and the messagebox submodule to display popup alerts and error/info dialogs
from tkinter import filedialog, messagebox
# Import logging to track events and errors during execution
import logging
# Import datetime to create timestamped output folders
from datetime import datetime
# Import sys to redirect error output
import sys
# Configure logging to write to a file---------------------
# CSV to Rexy 2 Prompt/Stage File Generator
#
# This script reads a CSV file and generates text
# and JSON files for each row, using a GUI interface.
# The generated files are used for automated content
# generation in the Rexy 2 system.
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
# Import the standard tkinter GUI toolkit and alias it as ‘tk’ for creating windows and widgets.
# Import the filedialog submodule to prompt the user to open/save files,
# and the messagebox submodule to display popup alerts and error/info dialogs.
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
# Redirect standard error to append to the log file
# This ensures that any errors are captured in the log file instead of just showing in the console
sys.stderr = open("generation_log.txt", "a")

def select_csv():
    """
    Main function that handles CSV selection, processing, and file generation.
    This function is called when the user clicks the 'Select CSV File' button.
    """
    try:
        # Display a file dialog to let the user select a CSV file
        # The filetypes parameter restricts selection to only CSV files
        csv_path = filedialog.askopenfilename(title="Select the source CSV file", filetypes=[("CSV Files", "*.csv")])
        # Exit the function if the user cancels file selection
        if not csv_path:
            logging.error("No CSV file selected. Exiting.")
            messagebox.showerror("Error", "No CSV file selected. Exiting.")
            return
            
        # Close the GUI window after file selection since we no longer need it
        root.destroy()
        
        # Read the CSV file into a pandas DataFrame
        # This converts the CSV data into a table-like structure that's easy to work with
        df = pd.read_csv(csv_path)
        
        # Create a timestamped output directory to store generated files
        # This ensures unique output folders for each run of the script
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_root = os.path.join(os.path.dirname(csv_path), f"output_{timestamp}")
        
        # Create subdirectories for prompts (.txt files) and stages (.json files)
        prompt_dir = os.path.join(output_root, "prompts")
        stages_dir = os.path.join(output_root, "stages")
        os.makedirs(prompt_dir, exist_ok=True)  # Create directories if they don't exist
        os.makedirs(stages_dir, exist_ok=True)
        # Process each row in the CSV file to generate the prompt and stage files
        for index, row in df.iterrows():
            # Extract values from the current row that we'll need for processing
            csv_file_id = int(row['file_ID'])       # Base file ID number
            csv_quantity = int(row['quantity'])     # How many files to generate in this sequence
            csv_increment = int(row['increment'])   # How much to increase the ID for each chapter
            csv_name_template = row['name']         # Template for the filename
            
            # Determine the actual Plan ID for Chapter 1 of this sequence
            # The Rexy 2 system uses a standardized file ID system:
            # - Plan files: Base ID
            # - Draft files: Base ID + 10
            # - Edit files: Base ID + 20
            # - Final files: Base ID + 30
            #
            # This calculation ensures we always know the Plan ID regardless of which file type
            # is specified in the CSV
            offset_to_plan_id = 0
            if "Final" in csv_name_template:
                offset_to_plan_id = -30     # If this is a Final file, subtract 30 to get the Plan ID
            elif "Edit" in csv_name_template:
                offset_to_plan_id = -20     # If this is an Edit file, subtract 20 to get the Plan ID
            elif "Draft" in csv_name_template:
                offset_to_plan_id = -10     # If this is a Draft file, subtract 10 to get the Plan ID
            # If "Plan" or no keyword, offset is 0, meaning csv_file_id is already the Plan ID for Ch1.
            
            # Calculate the base Plan ID for Chapter 1, which is our reference point for all IDs
            master_plan_id_ch1 = csv_file_id + offset_to_plan_id

            # Initialize chapter counter for the second loop (used for placeholder replacement)
            chapter = 1 
            
            # Create dictionaries to store all filenames by chapter number
            # This allows us to reference files across different chapters in prompts
            # For example, we can reference "previous chapter plan" in Chapter 2's prompt
            all_plan_filenames = {}
            all_draft_filenames = {}
            all_edit_filenames = {}
            all_final_filenames = {}
            
            # ---- FIRST PASS ----
            # Generate all filenames and store them in dictionaries
            # We do this first so that we can reference any chapter's files 
            # in any other chapter's prompt text
            for i in range(csv_quantity): # i is 0-indexed
                curr_chapter = i + 1      # 1-indexed chapter number for this sequence
                
                # Calculate IDs for different file types based on the master_plan_id_ch1
                # and applying the increment for each chapter in the sequence
                actual_plan_id = master_plan_id_ch1 + (i * csv_increment)  # Plan ID (base)
                actual_draft_id = actual_plan_id + 10                      # Draft = Plan + 10
                actual_edit_id = actual_plan_id + 20                       # Edit = Plan + 20
                actual_final_id = actual_plan_id + 30                      # Final = Plan + 30
                
                # Store the filenames by chapter number in our dictionaries for later reference
                all_plan_filenames[curr_chapter] = f"{actual_plan_id}-Chapter {curr_chapter} Plan"
                all_draft_filenames[curr_chapter] = f"{actual_draft_id}-Chapter {curr_chapter} Draft"
                all_edit_filenames[curr_chapter] = f"{actual_edit_id}-Chapter {curr_chapter} Edit"
                all_final_filenames[curr_chapter] = f"{actual_final_id}-Chapter {curr_chapter} Final"
                
            # ---- SECOND PASS ----
            # Now that we have all filenames in our dictionaries, we can generate 
            # the actual files with correct references to other chapters
            for i in range(csv_quantity):
                # Get the prompt template text from the CSV
                prompt_text = row['prompt']
                
                # Replace the {chapter} placeholder with the current chapter number
                prompt_text = prompt_text.replace("{chapter}", str(chapter))
                
                # Replace file reference placeholders with the actual filenames
                # This allows prompts to reference specific files by name
                # For example, a prompt might say "Use {current_chapter_plan} to write..."
                prompt_text = prompt_text.replace("{current_chapter_plan}", all_plan_filenames[chapter])
                prompt_text = prompt_text.replace("{current_chapter_draft}", all_draft_filenames[chapter])
                prompt_text = prompt_text.replace("{current_chapter_edit}", all_edit_filenames[chapter])
                prompt_text = prompt_text.replace("{current_chapter_final}", all_final_filenames[chapter])
                # Add references to previous chapter files if they exist
                # This is useful for continuity between chapters
                if chapter > 1:
                    prompt_text = prompt_text.replace("{previous_chapter_plan}", all_plan_filenames[chapter-1])
                    prompt_text = prompt_text.replace("{previous_chapter_draft}", all_draft_filenames[chapter-1])
                    prompt_text = prompt_text.replace("{previous_chapter_edit}", all_edit_filenames[chapter-1])
                    prompt_text = prompt_text.replace("{previous_chapter_final}", all_final_filenames[chapter-1])
                    
                # Extract other needed values from CSV row
                ai_model = row['ai_model']                            # AI model to use (e.g., "openai.json")
                output_mode = row['output_mode']                      # How to write output (e.g., "write", "append")
                csv_output_filename_template = row['output']          # Output filename template from CSV

                # Process filename for the current chapter
                # Replace {chapter} placeholder in the name template
                name_with_chapter = csv_name_template.replace("{chapter}", str(chapter))
                
                # Create a "safe" name by removing any characters that might cause issues in filenames
                # Only allow alphanumeric characters, spaces, hyphens, and underscores
                safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name_with_chapter).strip()
                
                # Calculate the current file ID by adding the increment for each chapter
                current_id = csv_file_id + (i * csv_increment)
                
                # Combine the ID and safe name to create the base filename
                # Example: "2010-Chapter 1 Plan"
                filename_base = f"{current_id}-{safe_name}"
                
                # Resolve the output filename using the template from CSV and current chapter
                actual_output_filename = csv_output_filename_template.replace("{chapter}", str(chapter))
                
                # For Plan, Draft, and Edit files, use the same filename_base for output as for prompts
                # This ensures consistency between prompt and output filenames
                if "Plan" in csv_name_template or "Draft" in csv_name_template or "Edit" in csv_name_template:
                    actual_output_filename = f"{filename_base}.txt"

                # ---- WRITE FILES ----
                
                # Write the prompt text (.txt) file
                prompt_filename = os.path.join(prompt_dir, f"{filename_base}.txt")
                with open(prompt_filename, "w", encoding="utf-8") as f:
                    f.write(prompt_text)
                
                # Create and write the stage configuration (.json) file
                # This JSON file tells Rexy 2 how to process the prompt
                stage_data = {
                    "title": name_with_chapter,                # Title displayed in the UI
                    "description": f"Create {name_with_chapter}", # Description for the task
                    "prompts": [filename_base],                # List of prompt files to use
                    "output": actual_output_filename,          # Where to write the output
                    "output_mode": output_mode,                # How to write (e.g., write/append)
                    "ai_profile": ai_model                     # Which AI model to use
                }
                
                # Save the JSON data to a file
                json_filename = os.path.join(stages_dir, f"{filename_base}.json")
                with open(json_filename, "w", encoding="utf-8") as f:
                    json.dump(stage_data, f, indent=4)  # Pretty-print with indentation
                
                # Increment chapter counter for next iteration
                chapter += 1
        # Log success message to the log file and display a success popup
        logging.info("All files have been generated successfully.")
        messagebox.showinfo("Done", "All files have been generated successfully.")
    except Exception as e:
        # If any error occurs during processing, log it and show an error message
        logging.exception("An unexpected error occurred.")
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# ---- GUI SETUP ----
# Create the main application window
root = tk.Tk()
root.title("CSV Converter")             # Set the window title
root.geometry("400x200")                # Set window dimensions (width x height)
root.configure(bg="#2c2c2e")            # Set background color (dark gray)
root.attributes("-topmost", True)       # Keep window on top of others

# Add a heading label to the window
label = tk.Label(root, 
                text="Convert CSV file for Rexy 2", 
                bg="#2c2c2e",           # Background color (matching window)
                fg="white",             # Text color
                font=("Helvetica", 14)) # Font family and size
label.pack(pady=30)                     # Add padding above and below

# Add a button that triggers the file selection and processing
button = tk.Button(root, 
                  text="Select CSV File",   
                  command=select_csv,       # Function to call when clicked
                  font=("Helvetica", 12),   # Font family and size
                  padx=10, pady=5)          # Padding inside the button
button.pack()

# Start the GUI event loop - this makes the window appear and respond to user input
# The program will stay in this loop until the window is closed
root.mainloop()