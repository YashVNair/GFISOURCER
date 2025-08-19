import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import threading

class ScraperGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Smart Protein Scraper")
        self.master.geometry("900x600")
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # File paths
        self.scraper_script_path = os.path.join(os.path.dirname(__file__), "scraper.py")
        self.companies_file_path = os.path.join(os.path.dirname(__file__), "companies.txt")

        self.create_widgets()
        self.load_companies()

    def create_widgets(self):
        # Main layout frames
        left_frame = ttk.Frame(self, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        right_frame = ttk.Frame(self, padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Left Frame: Company Management ---
        ttk.Label(left_frame, text="Companies to Scrape", font=("Arial", 12, "bold")).pack(pady=(0, 5))

        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.company_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, height=15)
        self.company_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.company_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.company_listbox.config(yscrollcommand=scrollbar.set)

        # Add/Remove buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.remove_button = ttk.Button(button_frame, text="Remove Selected", command=self.remove_company)
        self.remove_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        add_frame = ttk.Frame(left_frame)
        add_frame.pack(fill=tk.X, pady=5)

        self.new_company_entry = ttk.Entry(add_frame)
        self.new_company_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=2)

        self.add_button = ttk.Button(add_frame, text="Add", command=self.add_company)
        self.add_button.pack(side=tk.RIGHT, padx=(5, 0))

        # --- Right Frame: Output and Controls ---
        ttk.Label(right_frame, text="Scraper Output", font=("Arial", 12, "bold")).pack(pady=(0, 5), anchor="w")

        self.output_text = tk.Text(right_frame, wrap=tk.WORD, state=tk.DISABLED, height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.run_button = ttk.Button(right_frame, text="Run Scraper", command=self.start_scraper_thread)
        self.run_button.pack(pady=10, fill=tk.X)

    def load_companies(self):
        self.company_listbox.delete(0, tk.END)
        try:
            with open(self.companies_file_path, 'r', encoding='utf-8') as f:
                companies = [line.strip() for line in f if line.strip()]
            for company in companies:
                self.company_listbox.insert(tk.END, company)
        except FileNotFoundError:
            messagebox.showerror("Error", f"companies.txt not found at {self.companies_file_path}")

    def save_companies(self):
        companies = self.company_listbox.get(0, tk.END)
        with open(self.companies_file_path, 'w', encoding='utf-8') as f:
            for company in companies:
                f.write(f"{company}\n")

    def add_company(self):
        new_company = self.new_company_entry.get().strip()
        if new_company:
            self.company_listbox.insert(tk.END, new_company)
            self.new_company_entry.delete(0, tk.END)
            self.save_companies()
        else:
            messagebox.showwarning("Warning", "Company name cannot be empty.")

    def remove_company(self):
        selected_index = self.company_listbox.curselection()
        if selected_index:
            self.company_listbox.delete(selected_index)
            self.save_companies()
        else:
            messagebox.showwarning("Warning", "Please select a company to remove.")

    def start_scraper_thread(self):
        self.run_button.config(state=tk.DISABLED, text="Scraping...")
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

        # Run scraper in a separate thread to keep GUI responsive
        thread = threading.Thread(target=self.execute_scraper, daemon=True)
        thread.start()

    def execute_scraper(self):
        try:
            process = subprocess.Popen(
                ["python3", self.scraper_script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                bufsize=1
            )

            # Read and display output line by line
            for line in iter(process.stdout.readline, ''):
                self.master.after(0, self.append_to_output, line)

            process.stdout.close()
            process.wait()

        except Exception as e:
            self.master.after(0, self.append_to_output, f"\n--- An error occurred ---\n{e}\n")
        finally:
            self.master.after(0, self.finalize_scraper_run)

    def append_to_output(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def finalize_scraper_run(self):
        self.run_button.config(state=tk.NORMAL, text="Run Scraper")
        messagebox.showinfo("Success", "Scraping process completed!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperGUI(master=root)
    app.mainloop()
