import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import threading
import database
import concurrent.futures
import sys
import csv
import file_exporter
import platform_detector # Import the new module

class ScraperGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Smart Protein Scraper")
        self.master.geometry("1200x700")
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.project_dir = os.path.join(os.path.dirname(__file__), "product_scraper")
        self.companies_file_path = os.path.join(os.path.dirname(__file__), "companies.csv")

        self.create_widgets()
        self.load_companies_to_treeview()

    def create_widgets(self):
        # ... (same as before)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.scraper_control_tab = ttk.Frame(self.notebook, padding=10)
        self.data_viewer_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.scraper_control_tab, text="Scraper Control")
        self.notebook.add(self.data_viewer_tab, text="Data Viewer")
        self.create_scraper_control_widgets(self.scraper_control_tab)
        self.create_data_viewer_widgets(self.data_viewer_tab)

    def create_scraper_control_widgets(self, parent_tab):
        # ... (same as before, with the new button)
        left_frame = ttk.Frame(parent_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        right_frame = ttk.Frame(parent_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        ttk.Label(left_frame, text="Manage Companies", font=("Arial", 12, "bold")).pack(anchor="w")
        company_tree_frame = ttk.Frame(left_frame)
        company_tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # The 'type' column is still needed for the scraper, but we hide it from the user.
        self.company_tree = ttk.Treeview(company_tree_frame, columns=("Name", "Type", "URL"), show='headings', height=10)
        self.company_tree.heading("Name", text="Company Name")
        self.company_tree.heading("URL", text="Website URL")
        self.company_tree.column("Name", width=200)
        self.company_tree.column("URL", width=400)
        # Hide the 'Type' column
        self.company_tree["displaycolumns"] = ("Name", "URL")

        self.company_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        company_scrollbar = ttk.Scrollbar(company_tree_frame, orient=tk.VERTICAL, command=self.company_tree.yview)
        company_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.company_tree.config(yscrollcommand=company_scrollbar.set)

        add_frame = ttk.LabelFrame(left_frame, text="Add New Company", padding=10)
        add_frame.pack(fill=tk.X, pady=5)

        ttk.Label(add_frame, text="Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.name_entry = ttk.Entry(add_frame)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(add_frame, text="URL:").grid(row=1, column=0, sticky="w", pady=2)
        self.url_entry = ttk.Entry(add_frame)
        self.url_entry.grid(row=1, column=1, sticky="ew", pady=2)

        self.add_button = ttk.Button(add_frame, text="Add Company", command=self.add_company)
        self.add_button.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)

        self.remove_button = ttk.Button(left_frame, text="Remove Selected Company", command=self.remove_company)
        self.remove_button.pack(fill=tk.X)

        ttk.Label(right_frame, text="Scraper Log", font=("Arial", 12, "bold")).pack(anchor="w")
        log_frame = ttk.Frame(right_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.output_text = tk.Text(log_frame, wrap=tk.WORD, state=tk.DISABLED, height=20, bg="black", fg="white", font=("Courier", 9))
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=log_scrollbar.set)
        self.progress_bar = ttk.Progressbar(right_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(5,0))
        self.run_button = ttk.Button(right_frame, text="Run All Scrapers", command=self.start_scraper_thread)
        self.run_button.pack(pady=10, fill=tk.X, ipady=5)

    def create_data_viewer_widgets(self, parent_tab):
        # ... (same as before)
        top_frame = ttk.Frame(parent_tab)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(top_frame, text="Scraped Products Database", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        button_pack = ttk.Frame(top_frame)
        button_pack.pack(side=tk.RIGHT)
        self.export_button = ttk.Button(button_pack, text="Export Data", command=self.export_data)
        self.export_button.pack(side=tk.LEFT, padx=(0, 5))
        self.refresh_button = ttk.Button(button_pack, text="Refresh Data", command=self.refresh_data_view)
        self.refresh_button.pack(side=tk.LEFT)
        tree_frame = ttk.Frame(parent_tab)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("Brand", "Product Name", "Price (INR)", "Weight", "Availability", "Last Updated")
        self.data_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.data_tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False, self.data_tree))
            self.data_tree.column(col, width=150, anchor=tk.W)
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.data_tree.yview)
        vsb.pack(side='right', fill='y')
        self.data_tree.configure(yscrollcommand=vsb.set)
        hsb = ttk.Scrollbar(parent_tab, orient="horizontal", command=self.data_tree.xview)
        hsb.pack(side='bottom', fill='x')
        self.data_tree.configure(xscrollcommand=hsb.set)

    # ... (rest of the methods are the same as before)
    def export_data(self):
        products = database.get_all_products()
        if not products:
            messagebox.showinfo("Export Data", "There is no data in the database to export.")
            return
        json_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Save JSON As")
        if json_path:
            if file_exporter.write_to_json(products, json_path):
                messagebox.showinfo("Success", f"Data successfully exported to {json_path}")
            else:
                messagebox.showerror("Error", f"Failed to export data to {json_path}")
        csv_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Save CSV As")
        if csv_path:
            if file_exporter.write_to_csv(products, csv_path):
                messagebox.showinfo("Success", f"Data successfully exported to {csv_path}")
            else:
                messagebox.showerror("Error", f"Failed to export data to {csv_path}")

    def sort_treeview(self, col, reverse, tree):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        data.sort(reverse=reverse)
        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)
        tree.heading(col, command=lambda: self.sort_treeview(col, not reverse, tree))

    def refresh_data_view(self):
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        try:
            products = database.get_all_products()
            for product in products:
                row_values = [product.get(col, "") for col in self.data_tree['columns']]
                self.data_tree.insert("", tk.END, values=row_values)
        except Exception as e:
            messagebox.showerror("Database Error", "Could not fetch data from the database. The database file might be corrupted or inaccessible.")
            print(f"Database error on refresh: {e}") # Log technical error for debugging

    def load_companies_to_treeview(self):
        for item in self.company_tree.get_children():
            self.company_tree.delete(item)
        try:
            with open(self.companies_file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                for row in reader:
                    self.company_tree.insert("", tk.END, values=row)
        except FileNotFoundError:
             with open(self.companies_file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'type', 'url'])
        except Exception as e:
            messagebox.showerror("File Error", f"Could not read companies.csv.\n{e}")

    def save_companies_from_treeview(self):
        try:
            with open(self.companies_file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'type', 'url'])
                for child in self.company_tree.get_children():
                    writer.writerow(self.company_tree.item(child)['values'])
        except Exception as e:
            messagebox.showerror("File Error", f"Could not save to companies.csv.\n{e}")

    def add_company(self):
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()

        if not name or not url:
            messagebox.showwarning("Warning", "Company Name and URL are required.")
            return

        self.add_button.config(state=tk.DISABLED, text="Detecting...")
        thread = threading.Thread(target=self.run_add_company_flow, args=(name, url), daemon=True)
        thread.start()

    def run_add_company_flow(self, name, url):
        platform = platform_detector.detect_platform(url)

        def update_gui():
            self.add_button.config(state=tk.NORMAL, text="Add Company")
            if platform == 'shopify':
                self.company_tree.insert("", tk.END, values=(name, platform, url))
                self.save_companies_from_treeview()
                self.name_entry.delete(0, tk.END)
                self.url_entry.delete(0, tk.END)
                messagebox.showinfo("Success", f"'{name}' was added. It has been identified as a Shopify store.")
            elif platform == 'error':
                messagebox.showerror("Error", f"Could not connect to the URL for '{name}'. Please check the URL and your internet connection.")
            else: # 'unknown' or any other platform
                messagebox.showwarning("Unsupported Website", f"The website for '{name}' is not a supported Shopify store. The application can only scrape Shopify websites automatically.")

        self.master.after(0, update_gui)

    def remove_company(self):
        selected_item = self.company_tree.selection()
        if selected_item:
            self.company_tree.delete(selected_item)
            self.save_companies_from_treeview()
        else:
            messagebox.showwarning("Warning", "Please select a company to remove.")

    def start_scraper_thread(self):
        self.run_button.config(state=tk.DISABLED, text="Scraping...")
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.append_to_output("Starting scrapers...", newline=True)
        self.output_text.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.execute_scraper, daemon=True)
        thread.start()

    def execute_scraper(self):
        python_executable = sys.executable
        try:
            with open(self.companies_file_path, 'r', newline='', encoding='utf-8') as f:
                reader = list(csv.DictReader(f))
            if not reader:
                raise Exception("No companies have been added. Please add a company first.")
            self.master.after(0, lambda: self.progress_bar.config(maximum=len(reader), value=0))
            self.completed_tasks = 0
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_company = {executor.submit(self.run_spider, company, python_executable): company for company in reader}
                for future in concurrent.futures.as_completed(future_to_company):
                    company = future_to_company[future]
                    try:
                        future.result()
                    except Exception:
                        # Errors are handled and logged within run_spider
                        pass
                    finally:
                        self.completed_tasks += 1
                        self.master.after(0, lambda: self.progress_bar.config(value=self.completed_tasks))
        except FileNotFoundError:
             self.master.after(0, self.append_to_output, "Error: companies.csv not found. Please add a company.")
        except Exception as e:
            self.master.after(0, self.append_to_output, f"An unexpected error occurred: {e}")
        finally:
            self.master.after(0, self.finalize_scraper_run)

    def run_spider(self, company_info, python_executable):
        name = company_info['name']
        scraper_type = company_info['type']
        url = company_info['url']
        self.append_to_output(f"  - Scraping {name}... ", newline=False)
        command = [python_executable, '-m', 'scrapy', 'crawl', 'product_spider', '-a', f'name={name}', '-a', f'type={scraper_type}', '-a', f'url={url}']

        try:
            result = subprocess.run(command, cwd=self.project_dir, capture_output=True, text=True, encoding='utf-8', check=True)
            self.append_to_output("Success!", newline=True)
        except subprocess.CalledProcessError:
            self.append_to_output("Failed.", newline=True)
        except Exception as e:
            self.append_to_output(f"An unexpected error occurred: {e}", newline=True)

    def append_to_output(self, text, newline=True):
        if newline:
            text += "\n"
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def finalize_scraper_run(self):
        self.run_button.config(state=tk.NORMAL, text="Run All Scrapers")
        if self.progress_bar['value'] == self.progress_bar['maximum']:
             messagebox.showinfo("Success", "All scrapers have completed their runs!")
        else:
             messagebox.showwarning("Warning", "Some scrapers may have failed. Check the log for details.")
        self.progress_bar['value'] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperGUI(master=root)
    app.mainloop()
